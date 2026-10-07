from datetime import datetime, timedelta, timezone
import os
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-donation-tests")

from database.database import Base
from models.donation import Donation
from models.user import User
from routers.donations import cancel_donation, create_donation
from schemas.donation import DonationCreate


class DonationRouteTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        self.donor = User(
            name="Donor One",
            email="donor-one@example.com",
            password_hash="test-hash",
            phone="9876543210",
            role="donor",
            donor_type="individual",
            location="Katpadi",
        )
        self.other_donor = User(
            name="Donor Two",
            email="donor-two@example.com",
            password_hash="test-hash",
            phone="9876543211",
            role="donor",
            donor_type="restaurant",
            location="Vellore",
        )
        self.db.add_all([self.donor, self.other_donor])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def donation_input(self):
        prepared_at = datetime.now(timezone.utc)
        return DonationCreate(
            food_name="Vegetable rice",
            description="Prepared today",
            category="Cooked",
            quantity=20,
            unit="meals",
            prepared_at=prepared_at,
            expiry_time=prepared_at + timedelta(hours=4),
            pickup_address="Katpadi",
        )

    def test_create_donation_uses_authenticated_donor(self):
        donation = create_donation(
            self.donation_input(),
            self.db,
            self.donor,
        )

        self.assertEqual(donation.donor_id, self.donor.id)
        self.assertEqual(donation.status, "available")
        self.assertEqual(donation.quantity, 20)

    def test_other_donor_cannot_cancel_donation(self):
        donation = create_donation(
            self.donation_input(),
            self.db,
            self.donor,
        )

        with self.assertRaises(HTTPException) as context:
            cancel_donation(
                donation.id,
                self.db,
                self.other_donor,
            )

        self.assertEqual(context.exception.status_code, 403)
        stored = self.db.get(Donation, donation.id)
        self.assertEqual(stored.status, "available")


if __name__ == "__main__":
    unittest.main()
