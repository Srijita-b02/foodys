import os
import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-statistics-tests")

from database.database import Base
from models.deliveries import Deliveries
from models.donation import Donation
from models.food_request import FoodRequest
from models.match import Match
from models.user import User
from routers.statistics import get_impact_statistics


class ImpactStatisticsTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")

        @event.listens_for(self.engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
            del connection_record
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

        donor = User(
            name="Demo Donor",
            email="stats-donor@example.com",
            password_hash="hash",
            phone="9876543210",
            role="donor",
            donor_type="restaurant",
            location="Vellore",
        )
        ngo = User(
            name="Demo NGO Member",
            email="stats-ngo@example.com",
            password_hash="hash",
            phone="9876543211",
            role="ngo",
            organization_name="Demo NGO",
            location="Vellore",
        )
        self.db.add_all([donor, ngo])
        self.db.flush()

        now = datetime.now(timezone.utc)
        donation = Donation(
            donor_id=donor.id,
            food_name="Meals",
            category="Cooked",
            quantity=40,
            unit="meals",
            prepared_at=now - timedelta(hours=2),
            expiry_time=now + timedelta(hours=2),
            pickup_address="Vellore",
            status="delivered",
        )
        request = FoodRequest(
            ngo_id=ngo.id,
            food_name="Meals",
            category="Cooked",
            quantity=40,
            unit="meals",
            location="Vellore",
            needed_before=now + timedelta(hours=2),
            status="fulfilled",
        )
        self.db.add_all([donation, request])
        self.db.flush()

        match = Match(
            donation_id=donation.id,
            request_id=request.id,
            ngo_id=ngo.id,
            allocated_quantity=40,
            status="completed",
        )
        self.db.add(match)
        self.db.flush()
        self.db.add(
            Deliveries(
                match_id=match.id,
                assigned_ngo_member_id=ngo.id,
                status="delivered",
                pickup_time=now - timedelta(hours=1),
                delivery_time=now,
            )
        )
        self.db.commit()
        self.donor = donor

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_impact_statistics_are_calculated_by_database(self):
        result = get_impact_statistics(self.db, self.donor)

        self.assertEqual(result.delivered_quantity, 40)
        self.assertEqual(result.completed_deliveries, 1)
        self.assertEqual(result.fulfilled_requests, 1)
        self.assertEqual(result.completed_donations, 1)
        self.assertEqual(result.active_donors, 1)
        self.assertEqual(result.active_ngos, 1)


if __name__ == "__main__":
    unittest.main()
