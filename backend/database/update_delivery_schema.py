"""Align an existing deliveries table with the current PostgreSQL model.

This migration is idempotent. It preserves existing delivery timestamps while
renaming the original ``deliveries_time`` column to ``delivery_time``.
"""

from sqlalchemy import inspect, text

from database.database import engine


def update_delivery_schema():
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_schema = current_schema()
                          AND table_name = 'deliveries'
                          AND column_name = 'deliveries_time'
                    ) AND NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_schema = current_schema()
                          AND table_name = 'deliveries'
                          AND column_name = 'delivery_time'
                    ) THEN
                        ALTER TABLE deliveries
                        RENAME COLUMN deliveries_time TO delivery_time;
                    END IF;
                END
                $$
                """
            )
        )

    columns = {
        column["name"]
        for column in inspect(engine).get_columns("deliveries")
    }

    if "delivery_time" not in columns or "deliveries_time" in columns:
        raise RuntimeError("Delivery schema update did not complete correctly.")

    print("Delivery database schema updated successfully.")


if __name__ == "__main__":
    update_delivery_schema()
