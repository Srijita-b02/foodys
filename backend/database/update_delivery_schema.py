"""Align an existing deliveries table with the current PostgreSQL model.

This migration is idempotent. It preserves existing delivery timestamps while
renaming the original ``deliveries_time`` column to ``delivery_time``. It also
repairs donation and request statuses left stale by older delivery code.
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

        connection.execute(
            text(
                """
                UPDATE donations AS donation
                SET status = 'delivered', updated_at = CURRENT_TIMESTAMP
                WHERE donation.status NOT IN ('cancelled', 'expired')
                  AND donation.quantity <= (
                      SELECT COALESCE(SUM(match.allocated_quantity), 0)
                      FROM matches AS match
                      JOIN deliveries AS delivery
                        ON delivery.match_id = match.id
                      WHERE match.donation_id = donation.id
                        AND match.status != 'cancelled'
                        AND delivery.status = 'delivered'
                  )
                """
            )
        )

        connection.execute(
            text(
                """
                UPDATE food_requests AS food_request
                SET status = 'fulfilled', updated_at = CURRENT_TIMESTAMP
                WHERE food_request.status NOT IN ('cancelled', 'expired')
                  AND food_request.quantity <= (
                      SELECT COALESCE(SUM(match.allocated_quantity), 0)
                      FROM matches AS match
                      JOIN deliveries AS delivery
                        ON delivery.match_id = match.id
                      WHERE match.request_id = food_request.id
                        AND match.status != 'cancelled'
                        AND delivery.status = 'delivered'
                  )
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
