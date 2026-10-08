"""Apply donation constraints and indexes to an existing PostgreSQL database.

Back up the database before running this script. Existing rows must satisfy the
new constraints, otherwise PostgreSQL will reject the migration.
"""

from sqlalchemy import text

from database.database import engine


def update_donation_schema():
    statements = (
        "ALTER TABLE donations DROP CONSTRAINT IF EXISTS ck_donations_quantity_positive",
        "ALTER TABLE donations DROP CONSTRAINT IF EXISTS ck_donations_expiry_after_prepared",
        "ALTER TABLE donations DROP CONSTRAINT IF EXISTS ck_donations_status",
        "ALTER TABLE donations DROP CONSTRAINT IF EXISTS donations_donor_id_fkey",
        "ALTER TABLE donations DROP CONSTRAINT IF EXISTS fk_donations_donor_id",
        """
        ALTER TABLE donations
        ADD CONSTRAINT ck_donations_quantity_positive CHECK (quantity > 0)
        """,
        """
        ALTER TABLE donations
        ADD CONSTRAINT ck_donations_expiry_after_prepared
        CHECK (expiry_time > prepared_at)
        """,
        """
        ALTER TABLE donations
        ADD CONSTRAINT ck_donations_status
        CHECK (
            status IN (
                'available', 'reserved', 'matched', 'picked_up',
                'assigned', 'in_transit', 'delivered', 'cancelled', 'expired'
            )
        )
        """,
        """
        ALTER TABLE donations
        ADD CONSTRAINT fk_donations_donor_id
        FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE RESTRICT
        """,
        "CREATE INDEX IF NOT EXISTS ix_donations_category ON donations (category)",
        "CREATE INDEX IF NOT EXISTS ix_donations_pickup_address ON donations (pickup_address)",
    )

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

    print("Donation constraints and indexes updated successfully.")


if __name__ == "__main__":
    update_donation_schema()
