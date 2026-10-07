from database.database import Base, engine
from models import User, Donation, FoodRequest

print("Creating missing database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables are ready.")