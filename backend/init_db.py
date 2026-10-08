from sqlalchemy import inspect

from database.database import Base, engine
from models import User, Donation, FoodRequest, Match, Deliveries


print("Creating missing database tables...")

Base.metadata.create_all(bind=engine)

required_tables = set(Base.metadata.tables)
created_tables = set(inspect(engine).get_table_names())
missing_tables = required_tables - created_tables

if missing_tables:
    missing_names = ", ".join(sorted(missing_tables))
    raise RuntimeError(f"Database initialization failed: missing {missing_names}.")

print(
    "Database tables are ready: "
    + ", ".join(sorted(required_tables))
)
