"""Run every existing-database update required by the current application.

Run this command from the backend directory after pulling new code:

    python update_database.py

The script uses DATABASE_URL from backend/.env. Each update is idempotent, so
it is safe to run the command again after it has completed successfully.
"""

from sqlalchemy import inspect

from database.database import engine
from database.update_delivery_schema import update_delivery_schema
from database.update_donation_schema import update_donation_schema
from database.update_user_schema import update_user_schema


REQUIRED_TABLES = {
    "users",
    "donations",
    "food_requests",
    "matches",
    "deliveries",
}

UPDATES = (
    ("users", update_user_schema),
    ("donations", update_donation_schema),
    ("deliveries", update_delivery_schema),
)


def validate_database() -> None:
    """Fail before updating if the configured database is not ready."""

    if engine.dialect.name != "postgresql":
        raise RuntimeError(
            "Database updates require PostgreSQL. Check DATABASE_URL in .env."
        )

    existing_tables = set(inspect(engine).get_table_names())
    missing_tables = REQUIRED_TABLES - existing_tables

    if missing_tables:
        missing_names = ", ".join(sorted(missing_tables))
        raise RuntimeError(
            "Database update stopped because these tables are missing: "
            f"{missing_names}. Initialize a fresh database with schema.sql."
        )


def run_updates() -> None:
    validate_database()

    safe_url = engine.url.render_as_string(hide_password=True)
    print(f"Updating database: {safe_url}")

    for name, update_function in UPDATES:
        print(f"Applying {name} schema update...")
        update_function()

    print("All database schema updates completed successfully.")


if __name__ == "__main__":
    run_updates()
