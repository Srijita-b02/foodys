from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from database.database import Base
from models.deliveries import Deliveries
from models.donation import Donation
from models.food_request import FoodRequest
from models.match import Match
from models.user import User
from routers.deliveries import (
    get_deliveries,
    list_my_delivery_details,
    list_my_deliveries,
    update_deliveries_status,
)
from schemas.deliveries import DeliveriesStatusUpdate


class DeliveriesTests(unittest.TestCase):
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
            email="deliveries-donor@example.com",
            password_hash="test-hash",
            phone="9876543210",
            role="donor",
            donor_type="individual",
            location="Vellore",
        )
        self.ngo = User(
            name="Assigned NGO Member",
            organization_name="Hope Foundation",
            email="deliveries-ngo@example.com",
            password_hash="test-hash",
            phone="9876543211",
            role="ngo",
            location="Vellore",
        )
        self.other_ngo = User(
            name="Other NGO Member",
            organization_name="Care Foundation",
            email="deliveries-other-ngo@example.com",
            password_hash="test-hash",
            phone="9876543212",
            role="ngo",
            location="Katpadi",
        )
        self.db.add_all([self.donor, self.ngo, self.other_ngo])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_donation(self, quantity=100):
        now = datetime.now(timezone.utc)
        donation = Donation(
            donor_id=self.donor.id,
            food_name="Vegetable rice",
            category="Cooked",
            quantity=quantity,
            unit="meals",
            prepared_at=now,
            expiry_time=now + timedelta(hours=6),
            pickup_address="Vellore",
            status="available",
        )
        self.db.add(donation)
        self.db.commit()
        return donation

    def create_request(self, quantity=100):
        now = datetime.now(timezone.utc)
        request = FoodRequest(
            ngo_id=self.ngo.id,
            food_name="Cooked meals",
            category="Cooked",
            quantity=quantity,
            unit="meals",
            location="Vellore",
            needed_before=now + timedelta(hours=5),
            status="open",
        )
        self.db.add(request)
        self.db.commit()
        return request

    def create_match_and_deliveries(
        self,
        allocated_quantity=25,
        request_id=None,
        donation_quantity=100,
    ):
        donation = self.create_donation(donation_quantity)
        match = Match(
            donation_id=donation.id,
            request_id=request_id,
            ngo_id=self.ngo.id,
            allocated_quantity=allocated_quantity,
            status="active",
        )
        self.db.add(match)
        self.db.commit()

        deliveries = Deliveries(
            match_id=match.id,
            assigned_ngo_member_id=self.ngo.id,
            status="assigned",
        )
        self.db.add(deliveries)
        self.db.commit()
        return donation, match, deliveries

    def test_one_match_creates_only_one_deliveries(self):
        donation, match, deliveries = self.create_match_and_deliveries()

        duplicate = Deliveries(
            match_id=match.id,
            assigned_ngo_member_id=self.ngo.id,
        )
        self.db.add(duplicate)

        with self.assertRaises(IntegrityError):
            self.db.commit()

        self.db.rollback()
        self.assertEqual(
            self.db.query(Deliveries).filter(Deliveries.match_id == match.id).count(),
            1,
        )
        self.assertEqual(deliveries.match_id, match.id)

    def test_duplicate_match_id_is_rejected(self):
        _, match, _ = self.create_match_and_deliveries()

        duplicate = Deliveries(
            match_id=match.id,
            assigned_ngo_member_id=self.ngo.id,
        )
        self.db.add(duplicate)

        with self.assertRaises(IntegrityError):
            self.db.commit()

        self.db.rollback()

    def test_assigned_ngo_can_view_own_deliveries(self):
        _, _, deliveries = self.create_match_and_deliveries()

        result = get_deliveries(deliveries.id, self.db, self.ngo)

        self.assertEqual(result.id, deliveries.id)

        results = list_my_deliveries(self.db, self.ngo)
        self.assertEqual([item.id for item in results], [deliveries.id])

    def test_delivery_details_use_multi_table_join(self):
        donation, match, deliveries = self.create_match_and_deliveries(
            allocated_quantity=25,
        )

        results = list_my_delivery_details(self.db, self.ngo)

        self.assertEqual(len(results), 1)
        details = results[0]
        self.assertEqual(details.id, deliveries.id)
        self.assertEqual(details.match_id, match.id)
        self.assertEqual(details.donation_id, donation.id)
        self.assertEqual(details.food_name, donation.food_name)
        self.assertEqual(details.allocated_quantity, 25)
        self.assertEqual(details.donor_name, self.donor.name)
        self.assertEqual(details.organization_name, self.ngo.organization_name)
        self.assertEqual(details.destination_location, self.ngo.location)

    def test_unrelated_ngo_cannot_update_deliveries(self):
        _, _, deliveries = self.create_match_and_deliveries()

        with self.assertRaises(HTTPException) as context:
            update_deliveries_status(
                deliveries.id,
                DeliveriesStatusUpdate(status="picked_up"),
                self.db,
                self.other_ngo,
            )

        self.assertEqual(context.exception.status_code, 403)

    def test_donor_cannot_update_deliveries(self):
        _, _, deliveries = self.create_match_and_deliveries()

        with self.assertRaises(HTTPException) as context:
            update_deliveries_status(
                deliveries.id,
                DeliveriesStatusUpdate(status="picked_up"),
                self.db,
                self.donor,
            )

        self.assertEqual(context.exception.status_code, 403)

    def test_assigned_to_picked_up_succeeds_and_sets_pickup_time(self):
        _, _, deliveries = self.create_match_and_deliveries()
        self.assertIsNotNone(deliveries.assigned_at)
        self.assertIsNone(deliveries.pickup_time)

        update_deliveries_status(
            deliveries.id,
            DeliveriesStatusUpdate(status="picked_up"),
            self.db,
            self.ngo,
        )

        self.db.refresh(deliveries)
        self.assertEqual(deliveries.status, "picked_up")
        self.assertIsNotNone(deliveries.pickup_time)

    def test_picked_up_to_in_transit_succeeds(self):
        _, _, deliveries = self.create_match_and_deliveries()
        update_deliveries_status(
            deliveries.id,
            DeliveriesStatusUpdate(status="picked_up"),
            self.db,
            self.ngo,
        )
        update_deliveries_status(
            deliveries.id,
            DeliveriesStatusUpdate(status="in_transit"),
            self.db,
            self.ngo,
        )

        self.db.refresh(deliveries)
        self.assertEqual(deliveries.status, "in_transit")

    def test_in_transit_to_delivered_succeeds_and_sets_delivery_time(self):
        _, match, deliveries = self.create_match_and_deliveries()
        update_deliveries_status(
            deliveries.id,
            DeliveriesStatusUpdate(status="picked_up"),
            self.db,
            self.ngo,
        )
        update_deliveries_status(
            deliveries.id,
            DeliveriesStatusUpdate(status="in_transit"),
            self.db,
            self.ngo,
        )

        update_deliveries_status(
            deliveries.id,
            DeliveriesStatusUpdate(status="delivered"),
            self.db,
            self.ngo,
        )

        self.db.refresh(deliveries)
        self.db.refresh(match)
        self.assertEqual(deliveries.status, "delivered")
        self.assertIsNotNone(deliveries.delivery_time)
        self.assertEqual(match.status, "completed")

    def test_skipped_transitions_fail(self):
        _, _, deliveries = self.create_match_and_deliveries()

        with self.assertRaises(HTTPException) as context:
            update_deliveries_status(
                deliveries.id,
                DeliveriesStatusUpdate(status="in_transit"),
                self.db,
                self.ngo,
            )

        self.assertEqual(context.exception.status_code, 409)

    def test_backward_transitions_fail(self):
        _, _, deliveries = self.create_match_and_deliveries()

        update_deliveries_status(
            deliveries.id,
            DeliveriesStatusUpdate(status="picked_up"),
            self.db,
            self.ngo,
        )

        with self.assertRaises(HTTPException) as context:
            update_deliveries_status(
                deliveries.id,
                DeliveriesStatusUpdate(status="assigned"),
                self.db,
                self.ngo,
            )

        self.assertEqual(context.exception.status_code, 409)

    def test_missing_deliveries_returns_404(self):
        with self.assertRaises(HTTPException) as context:
            get_deliveries(999999, self.db, self.ngo)

        self.assertEqual(context.exception.status_code, 404)

    def test_partial_match_does_not_complete_donation_or_request(self):
        donation = self.create_donation(quantity=100)
        request = self.create_request(quantity=100)

        match = Match(
            donation_id=donation.id,
            request_id=request.id,
            ngo_id=self.ngo.id,
            allocated_quantity=40,
            status="active",
        )
        self.db.add(match)
        self.db.commit()

        deliveries = Deliveries(
            match_id=match.id,
            assigned_ngo_member_id=self.ngo.id,
        )
        self.db.add(deliveries)
        self.db.commit()

        for target in ("picked_up", "in_transit", "delivered"):
            update_deliveries_status(
                deliveries.id,
                DeliveriesStatusUpdate(status=target),
                self.db,
                self.ngo,
            )

        self.db.refresh(donation)
        self.db.refresh(request)
        self.assertEqual(donation.status, "available")
        self.assertEqual(request.status, "open")

    def test_completing_all_allocated_quantity_updates_donation_to_delivered(self):
        donation = self.create_donation(quantity=100)

        matches = []
        for quantity in (40, 60):
            match = Match(
                donation_id=donation.id,
                request_id=None,
                ngo_id=self.ngo.id,
                allocated_quantity=quantity,
                status="active",
            )
            self.db.add(match)
            self.db.flush()
            self.db.add(
                Deliveries(
                    match_id=match.id,
                    assigned_ngo_member_id=self.ngo.id,
                )
            )
            matches.append(match)
        self.db.commit()

        for match in matches:
            deliveries = self.db.scalar(
                select(Deliveries).where(Deliveries.match_id == match.id)
            )
            for target in ("picked_up", "in_transit", "delivered"):
                update_deliveries_status(
                    deliveries.id,
                    DeliveriesStatusUpdate(status=target),
                    self.db,
                    self.ngo,
                )

        self.db.refresh(donation)
        self.assertEqual(donation.status, "delivered")

    def test_completing_full_requested_quantity_updates_request_to_fulfilled(self):
        donation = self.create_donation(quantity=100)
        request = self.create_request(quantity=100)

        matches = []
        for quantity in (30, 70):
            match = Match(
                donation_id=donation.id,
                request_id=request.id,
                ngo_id=self.ngo.id,
                allocated_quantity=quantity,
                status="active",
            )
            self.db.add(match)
            self.db.flush()
            self.db.add(
                Deliveries(
                    match_id=match.id,
                    assigned_ngo_member_id=self.ngo.id,
                )
            )
            matches.append(match)
        self.db.commit()

        for match in matches:
            deliveries = self.db.scalar(
                select(Deliveries).where(Deliveries.match_id == match.id)
            )
            for target in ("picked_up", "in_transit", "delivered"):
                update_deliveries_status(
                    deliveries.id,
                    DeliveriesStatusUpdate(status=target),
                    self.db,
                    self.ngo,
                )

        self.db.refresh(request)
        self.assertEqual(request.status, "fulfilled")

    def test_forced_failure_rolls_back_deliveries_match_donation_and_request(self):
        donation = self.create_donation(quantity=50)
        request = self.create_request(quantity=50)
        match = Match(
            donation_id=donation.id,
            request_id=request.id,
            ngo_id=self.ngo.id,
            allocated_quantity=50,
            status="active",
        )
        self.db.add(match)
        self.db.commit()

        deliveries = Deliveries(
            match_id=match.id,
            assigned_ngo_member_id=self.ngo.id,
            status="in_transit",
        )
        self.db.add(deliveries)
        self.db.commit()

        with patch(
            "routers.deliveries._recalculate_food_request",
            side_effect=RuntimeError("forced failure"),
        ):
            with self.assertRaises(RuntimeError):
                update_deliveries_status(
                    deliveries.id,
                    DeliveriesStatusUpdate(status="delivered"),
                    self.db,
                    self.ngo,
                )

        self.db.refresh(deliveries)
        self.db.refresh(match)
        self.db.refresh(donation)
        self.db.refresh(request)

        self.assertEqual(deliveries.status, "in_transit")
        self.assertIsNone(deliveries.delivery_time)
        self.assertEqual(match.status, "active")
        self.assertEqual(donation.status, "available")
        self.assertEqual(request.status, "open")

    def test_stale_status_update_cannot_succeed_twice(self):
        _, _, deliveries = self.create_match_and_deliveries()

        first = update_deliveries_status(
            deliveries.id,
            DeliveriesStatusUpdate(status="picked_up"),
            self.db,
            self.ngo,
        )
        self.assertEqual(first.status, "picked_up")

        with self.assertRaises(HTTPException) as context:
            update_deliveries_status(
                deliveries.id,
                DeliveriesStatusUpdate(status="picked_up"),
                self.db,
                self.ngo,
            )

        self.assertEqual(context.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
