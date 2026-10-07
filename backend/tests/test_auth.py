import os
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-authentication-tests")

from database.database import Base
from models.donation import Donation  # noqa: F401 - registers the relationship
from models.user import User
from routers.auth import login, register
from schemas.user import DonorType, UserLogin, UserRegister, UserRole
from utils.security import verify_password


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_register_hashes_password_and_login_returns_token(self):
        registration = UserRegister(
            name="Demo Donor",
            email="donor@example.com",
            password="safe-password",
            phone="9876543210",
            role=UserRole.DONOR,
            donor_type=DonorType.INDIVIDUAL,
            location="Katpadi",
        )

        created_user = register(registration, self.db)

        self.assertNotEqual(created_user.password_hash, registration.password)
        self.assertTrue(
            verify_password(registration.password, created_user.password_hash)
        )

        result = login(
            UserLogin(
                email=registration.email,
                password=registration.password,
                role=UserRole.DONOR,
            ),
            self.db,
        )

        self.assertEqual(result["token_type"], "bearer")
        self.assertTrue(result["access_token"])
        self.assertNotIn("password_hash", result["user"])

    def test_duplicate_email_is_rejected(self):
        registration = UserRegister(
            name="Demo NGO Member",
            organization_name="Hope Foundation",
            email="ngo@example.com",
            password="safe-password",
            phone="9876543211",
            role=UserRole.NGO,
            location="Vellore",
        )

        register(registration, self.db)

        with self.assertRaises(HTTPException) as context:
            register(registration, self.db)

        self.assertEqual(context.exception.status_code, 409)

    def test_wrong_role_login_is_rejected(self):
        user = User(
            name="Demo Donor",
            email="role@example.com",
            password_hash="not-used-for-this-check",
            phone="9876543212",
            role="donor",
            donor_type="restaurant",
            location="Gandhi Nagar",
        )
        self.db.add(user)
        self.db.commit()

        with self.assertRaises(HTTPException) as context:
            login(
                UserLogin(
                    email=user.email,
                    password="safe-password",
                    role=UserRole.NGO,
                ),
                self.db,
            )

        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
