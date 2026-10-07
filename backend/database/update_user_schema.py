"""Update an existing development users table to the two-role model.

Run this manually after backing up any development data. Existing rows must
already use the donor/NGO model and have phone and location values before the
new constraints are enforced.
"""

from sqlalchemy import text

from database.database import engine


statements = [
    "ALTER TABLE users DROP CONSTRAINT IF EXISTS fk_users_ngo_id",
    "DROP INDEX IF EXISTS ix_users_ngo_id",
    "ALTER TABLE users DROP COLUMN IF EXISTS ngo_id",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_name VARCHAR(150)",
    """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'address'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'location'
        ) THEN
            ALTER TABLE users RENAME COLUMN address TO location;
        END IF;
    END
    $$
    """,
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR(500)",
    "ALTER TABLE users ALTER COLUMN phone SET NOT NULL",
    "ALTER TABLE users ALTER COLUMN location SET NOT NULL",
    "ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_role",
    "ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_donor_type",
    "ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_role_fields",
    """
    ALTER TABLE users
    ADD CONSTRAINT ck_users_role
    CHECK (role IN ('donor', 'ngo'))
    """,
    """
    ALTER TABLE users
    ADD CONSTRAINT ck_users_donor_type
    CHECK (donor_type IS NULL OR donor_type IN ('individual', 'restaurant'))
    """,
    """
    ALTER TABLE users
    ADD CONSTRAINT ck_users_role_fields
    CHECK (
        (role = 'donor' AND donor_type IS NOT NULL
            AND organization_name IS NULL)
        OR
        (role = 'ngo' AND donor_type IS NULL
            AND organization_name IS NOT NULL)
    )
    """,
]


def update_user_schema():
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

    print("User database schema updated successfully.")


if __name__ == "__main__":
    update_user_schema()
