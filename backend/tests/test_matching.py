from datetime import datetime, timedelta, timezone
import os
import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker


os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-matching-tests")

from database.database import Base
from models.deliveries import Deliveries
from models.donation import Donation
from models.food_request import FoodRequest
from models.match import Match
from models.user import User
from schemas.match import (
    DirectReservationCreate,
    RequestAcceptanceCreate,
    RequestMatchCreate,
)
from routers.donations import list_donations
from routers.matches import accept_request, reserve_donation, respond_to_request
from routers.requests import list_open_requests


class MatchModelTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")

        @event.listens_for(self.engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
            del connection_record
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        self.donor = User(
            name="Donor",
            email="matching-donor@example.com",
            password_hash="test-hash",
            phone="9876543210",
            role="donor",
            donor_type="individual",
            location="Vellore",
        )
        self.ngo_member = User(
            name="NGO Member",
            organization_name="Hope Foundation",
            email="matching-ngo@example.com",
            password_hash="test-hash",
            phone="9876543211",
            role="ngo",
            location="Vellore",
        )
        self.db.add_all([self.donor, self.ngo_member])
        self.db.commit()

        now = datetime.now(timezone.utc)
        self.donation = Donation(
            donor_id=self.donor.id,
            food_name="Vegetable rice",
            category="Cooked",
            quantity=100,
            unit="meals",
            prepared_at=now,
            expiry_time=now + timedelta(hours=6),
            pickup_address="Vellore",
            status="available",
        )
        self.food_request = FoodRequest(
            ngo_id=self.ngo_member.id,
            food_name="Cooked meals",
            category="Cooked",
            quantity=70,
            unit="meals",
            location="Vellore",
            needed_before=now + timedelta(hours=5),
            status="open",
        )
        self.db.add_all([self.donation, self.food_request])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_direct_reservation_allows_nullable_request(self):
        match = Match(
            donation_id=self.donation.id,
            request_id=None,
            ngo_id=self.ngo_member.id,
            allocated_quantity=25,
            status="active",
        )
        self.db.add(match)
        self.db.commit()

        self.assertIsNone(match.request_id)
        self.assertEqual(match.allocated_quantity, 25)

    def test_multiple_matches_can_share_donation_and_request(self):
        first_match = Match(
            donation_id=self.donation.id,
            request_id=self.food_request.id,
            ngo_id=self.ngo_member.id,
            allocated_quantity=30,
            status="active",
        )
        second_match = Match(
            donation_id=self.donation.id,
            request_id=self.food_request.id,
            ngo_id=self.ngo_member.id,
            allocated_quantity=20,
            status="active",
        )
        self.db.add_all([first_match, second_match])
        self.db.commit()

        self.assertNotEqual(first_match.id, second_match.id)
        self.assertEqual(
            first_match.allocated_quantity + second_match.allocated_quantity,
            50,
        )

    def test_database_rejects_non_positive_allocation(self):
        match = Match(
            donation_id=self.donation.id,
            request_id=self.food_request.id,
            ngo_id=self.ngo_member.id,
            allocated_quantity=0,
            status="active",
        )
        self.db.add(match)

        with self.assertRaises(IntegrityError):
            self.db.commit()

        self.db.rollback()

    def test_database_rejects_invalid_status(self):
        match = Match(
            donation_id=self.donation.id,
            request_id=self.food_request.id,
            ngo_id=self.ngo_member.id,
            allocated_quantity=10,
            status="invalid",
        )
        self.db.add(match)

        with self.assertRaises(IntegrityError):
            self.db.commit()

        self.db.rollback()

    def test_database_rejects_missing_foreign_keys(self):
        match = Match(
            donation_id=9999,
            request_id=None,
            ngo_id=self.ngo_member.id,
            allocated_quantity=10,
            status="active",
        )
        self.db.add(match)

        with self.assertRaises(IntegrityError):
            self.db.commit()

        self.db.rollback()

    def test_schemas_require_positive_ids_and_quantity(self):
        with self.assertRaises(ValidationError):
            DirectReservationCreate(
                donation_id=0,
                allocated_quantity=10,
            )

        with self.assertRaises(ValidationError):
            RequestMatchCreate(
                donation_id=self.donation.id,
                request_id=self.food_request.id,
                allocated_quantity=0,
            )

    def test_ngo_reservation_creates_match_and_assigned_delivery(self):
        match = reserve_donation(
            DirectReservationCreate(
                donation_id=self.donation.id,
                allocated_quantity=25,
            ),
            self.db,
            self.ngo_member,
        )

        delivery = self.db.query(Deliveries).filter_by(match_id=match.id).one()

        self.assertIsNone(match.request_id)
        self.assertEqual(match.ngo_id, self.ngo_member.id)
        self.assertEqual(delivery.assigned_ngo_member_id, self.ngo_member.id)
        self.assertEqual(delivery.status, "assigned")
        self.assertEqual(self.donation.status, "available")

    def test_full_reservation_marks_donation_matched(self):
        reserve_donation(
            DirectReservationCreate(
                donation_id=self.donation.id,
                allocated_quantity=self.donation.quantity,
            ),
            self.db,
            self.ngo_member,
        )

        self.db.refresh(self.donation)
        self.assertEqual(self.donation.status, "matched")

    def test_reservation_rejects_quantity_above_remaining_supply(self):
        with self.assertRaises(HTTPException) as context:
            reserve_donation(
                DirectReservationCreate(
                    donation_id=self.donation.id,
                    allocated_quantity=self.donation.quantity + 1,
                ),
                self.db,
                self.ngo_member,
            )

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(self.db.query(Match).count(), 0)
        self.assertEqual(self.db.query(Deliveries).count(), 0)

    def test_partial_reservation_reports_remaining_donation_quantity(self):
        reserve_donation(
            DirectReservationCreate(
                donation_id=self.donation.id,
                allocated_quantity=25,
            ),
            self.db,
            self.ngo_member,
        )

        results = list_donations(
            category=None,
            pickup_address=None,
            db=self.db,
            current_user=self.ngo_member,
        )

        self.assertEqual(results[0].remaining_quantity, 75)

    def test_donor_response_creates_match_for_request_owner(self):
        match = respond_to_request(
            RequestMatchCreate(
                donation_id=self.donation.id,
                request_id=self.food_request.id,
                allocated_quantity=self.food_request.quantity,
            ),
            self.db,
            self.donor,
        )

        delivery = self.db.query(Deliveries).filter_by(match_id=match.id).one()

        self.db.refresh(self.food_request)
        self.assertEqual(match.request_id, self.food_request.id)
        self.assertEqual(match.ngo_id, self.food_request.ngo_id)
        self.assertEqual(delivery.assigned_ngo_member_id, self.food_request.ngo_id)
        self.assertEqual(self.food_request.status, "matched")

    def test_accept_request_creates_donation_match_and_delivery(self):
        match = accept_request(
            RequestAcceptanceCreate(
                request_id=self.food_request.id,
                allocated_quantity=25,
            ),
            self.db,
            self.donor,
        )

        donation = self.db.get(Donation, match.donation_id)
        delivery = self.db.query(Deliveries).filter_by(match_id=match.id).one()

        self.db.refresh(self.food_request)
        self.assertEqual(donation.donor_id, self.donor.id)
        self.assertEqual(donation.food_name, self.food_request.food_name)
        self.assertEqual(donation.quantity, 25)
        self.assertEqual(donation.pickup_address, self.donor.location)
        self.assertEqual(donation.expiry_time, self.food_request.needed_before)
        self.assertEqual(donation.status, "matched")
        self.assertEqual(delivery.assigned_ngo_member_id, self.food_request.ngo_id)
        self.assertEqual(self.food_request.status, "open")

    def test_accept_request_full_quantity_locks_request_as_matched(self):
        accept_request(
            RequestAcceptanceCreate(
                request_id=self.food_request.id,
                allocated_quantity=self.food_request.quantity,
            ),
            self.db,
            self.donor,
        )

        self.db.refresh(self.food_request)
        self.assertEqual(self.food_request.status, "matched")

    def test_accept_request_rejects_quantity_above_remaining(self):
        with self.assertRaises(HTTPException) as context:
            accept_request(
                RequestAcceptanceCreate(
                    request_id=self.food_request.id,
                    allocated_quantity=self.food_request.quantity + 1,
                ),
                self.db,
                self.donor,
            )

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(self.db.query(Donation).count(), 1)
        self.assertEqual(self.db.query(Match).count(), 0)

    def test_partial_response_reports_remaining_request_quantity(self):
        respond_to_request(
            RequestMatchCreate(
                donation_id=self.donation.id,
                request_id=self.food_request.id,
                allocated_quantity=20,
            ),
            self.db,
            self.donor,
        )

        results = list_open_requests(
            category=None,
            location=None,
            db=self.db,
            current_user=self.donor,
        )

        self.assertEqual(results[0].remaining_quantity, 50)

    def test_donor_response_rejects_mismatched_units(self):
        self.food_request.unit = "packets"
        self.db.commit()

        with self.assertRaises(HTTPException) as context:
            respond_to_request(
                RequestMatchCreate(
                    donation_id=self.donation.id,
                    request_id=self.food_request.id,
                    allocated_quantity=10,
                ),
                self.db,
                self.donor,
            )

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(self.db.query(Match).count(), 0)
        self.assertEqual(self.db.query(Deliveries).count(), 0)

    def test_donor_cannot_match_another_donors_donation(self):
        other_donor = User(
            name="Other Donor",
            email="other-matching-donor@example.com",
            password_hash="test-hash",
            phone="9876543212",
            role="donor",
            donor_type="individual",
            location="Katpadi",
        )
        self.db.add(other_donor)
        self.db.commit()

        with self.assertRaises(HTTPException) as context:
            respond_to_request(
                RequestMatchCreate(
                    donation_id=self.donation.id,
                    request_id=self.food_request.id,
                    allocated_quantity=10,
                ),
                self.db,
                other_donor,
            )

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(self.db.query(Match).count(), 0)
        self.assertEqual(self.db.query(Deliveries).count(), 0)


if __name__ == "__main__":
    unittest.main()
