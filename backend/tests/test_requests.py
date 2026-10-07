from datetime import datetime, timedelta, timezone
import os
import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-request-tests")

from database.database import Base
from models.food_request import FoodRequest
from models.user import User
from routers.requests import (
    cancel_food_request,
    create_food_request,
    expire_open_requests,
    list_my_requests,
    list_open_requests,
    update_food_request,
)
from schemas.food_request import FoodRequestCreate, FoodRequestUpdate
from utils.auth import require_roles


class FoodRequestTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        self.ngo_member = User(
            name="NGO Member One",
            organization_name="Hope Foundation",
            email="ngo-one@example.com",
            password_hash="test-hash",
            phone="9876543210",
            role="ngo",
            location="Vellore",
        )
        self.other_ngo_member = User(
            name="NGO Member Two",
            organization_name="Care Foundation",
            email="ngo-two@example.com",
            password_hash="test-hash",
            phone="9876543211",
            role="ngo",
            location="Katpadi",
        )
        self.donor = User(
            name="Donor",
            email="donor@example.com",
            password_hash="test-hash",
            phone="9876543212",
            role="donor",
            donor_type="individual",
            location="Vellore",
        )
        self.db.add_all([self.ngo_member, self.other_ngo_member, self.donor])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def request_input(self):
        return FoodRequestCreate(
            food_name="Vegetable meals",
            category="Cooked",
            quantity=25,
            unit="meals",
            description="Required for evening service",
            location="Vellore",
            needed_before=datetime.now(timezone.utc) + timedelta(hours=6),
        )

    def test_create_request_uses_authenticated_ngo(self):
        food_request = create_food_request(
            self.request_input(),
            self.db,
            self.ngo_member,
        )

        self.assertEqual(food_request.ngo_id, self.ngo_member.id)
        self.assertEqual(food_request.status, "open")
        self.assertEqual(food_request.quantity, 25)

    def test_donor_role_is_rejected_by_role_dependency(self):
        check_ngo_role = require_roles("ngo")

        with self.assertRaises(HTTPException) as context:
            check_ngo_role(current_user=self.donor)

        self.assertEqual(context.exception.status_code, 403)

    def test_other_ngo_cannot_cancel_request(self):
        food_request = create_food_request(
            self.request_input(),
            self.db,
            self.ngo_member,
        )

        with self.assertRaises(HTTPException) as context:
            cancel_food_request(
                food_request.id,
                self.db,
                self.other_ngo_member,
            )

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(self.db.get(FoodRequest, food_request.id).status, "open")

    def test_owner_can_update_open_request(self):
        food_request = create_food_request(
            self.request_input(),
            self.db,
            self.ngo_member,
        )

        updated = update_food_request(
            food_request.id,
            FoodRequestUpdate(quantity=30),
            self.db,
            self.ngo_member,
        )

        self.assertEqual(updated.quantity, 30)

    def test_donor_can_browse_only_open_matching_requests(self):
        matching_request = create_food_request(
            self.request_input(),
            self.db,
            self.ngo_member,
        )
        cancelled_request = create_food_request(
            self.request_input(),
            self.db,
            self.other_ngo_member,
        )
        cancel_food_request(
            cancelled_request.id,
            self.db,
            self.other_ngo_member,
        )

        results = list_open_requests(
            category="Cooked",
            location="Vellore",
            db=self.db,
            current_user=self.donor,
        )

        self.assertEqual([item.id for item in results], [matching_request.id])

    def test_ngo_can_list_own_requests(self):
        own_request = create_food_request(
            self.request_input(),
            self.db,
            self.ngo_member,
        )
        create_food_request(
            self.request_input(),
            self.db,
            self.other_ngo_member,
        )

        results = list_my_requests(self.db, self.ngo_member)

        self.assertEqual([item.id for item in results], [own_request.id])

    def test_matched_request_cannot_be_updated(self):
        food_request = create_food_request(
            self.request_input(),
            self.db,
            self.ngo_member,
        )
        food_request.status = "matched"
        self.db.commit()

        with self.assertRaises(HTTPException) as context:
            update_food_request(
                food_request.id,
                FoodRequestUpdate(quantity=30),
                self.db,
                self.ngo_member,
            )

        self.assertEqual(context.exception.status_code, 409)

    def test_expired_request_is_kept_as_history(self):
        now = datetime.now(timezone.utc)
        food_request = FoodRequest(
            ngo_id=self.ngo_member.id,
            food_name="Rice",
            category="Dry Food",
            quantity=10,
            unit="kg",
            location="Vellore",
            created_at=now - timedelta(hours=2),
            needed_before=now - timedelta(hours=1),
            status="open",
        )
        self.db.add(food_request)
        self.db.commit()

        expire_open_requests(self.db)

        stored = self.db.get(FoodRequest, food_request.id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.status, "expired")

    def test_past_deadline_is_rejected(self):
        with self.assertRaises(ValidationError):
            FoodRequestCreate(
                food_name="Rice",
                category="Dry Food",
                quantity=10,
                unit="kg",
                location="Vellore",
                needed_before=datetime.now(timezone.utc) - timedelta(minutes=1),
            )

    def test_non_positive_quantity_is_rejected(self):
        with self.assertRaises(ValidationError):
            FoodRequestCreate(
                food_name="Rice",
                category="Dry Food",
                quantity=0,
                unit="kg",
                location="Vellore",
                needed_before=datetime.now(timezone.utc) + timedelta(hours=1),
            )


if __name__ == "__main__":
    unittest.main()
