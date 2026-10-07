from datetime import datetime, timedelta, timezone
import unittest

from pydantic import ValidationError

from schemas.donation import DonationCreate
from schemas.user import DonorType, UserRegister, UserRole


class UserSchemaTests(unittest.TestCase):
    def test_ngo_requires_organization_name(self):
        with self.assertRaises(ValidationError):
            UserRegister(
                name="NGO Member",
                email="member@example.com",
                password="safe-password",
                phone="9876543210",
                role=UserRole.NGO,
                location="Vellore",
            )

    def test_donor_requires_donor_type(self):
        with self.assertRaises(ValidationError):
            UserRegister(
                name="Donor",
                email="donor@example.com",
                password="safe-password",
                phone="9876543210",
                role=UserRole.DONOR,
                location="Vellore",
            )

    def test_valid_donor_registration(self):
        registration = UserRegister(
            name="Restaurant Owner",
            email="restaurant@example.com",
            password="safe-password",
            phone="9876543210",
            role=UserRole.DONOR,
            donor_type=DonorType.RESTAURANT,
            location="Vellore",
        )

        self.assertEqual(registration.role, UserRole.DONOR)


class DonationSchemaTests(unittest.TestCase):
    def test_expiry_must_be_after_preparation(self):
        prepared_at = datetime.now(timezone.utc)

        with self.assertRaises(ValidationError):
            DonationCreate(
                food_name="Rice",
                category="Cooked",
                quantity=10,
                unit="meals",
                prepared_at=prepared_at,
                expiry_time=prepared_at - timedelta(hours=1),
                pickup_address="Katpadi",
            )

    def test_positive_quantity_is_required(self):
        prepared_at = datetime.now(timezone.utc)

        with self.assertRaises(ValidationError):
            DonationCreate(
                food_name="Rice",
                category="Cooked",
                quantity=0,
                unit="meals",
                prepared_at=prepared_at,
                expiry_time=prepared_at + timedelta(hours=2),
                pickup_address="Katpadi",
            )


if __name__ == "__main__":
    unittest.main()
