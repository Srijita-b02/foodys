from sqlalchemy import text

from database.database import engine


with engine.begin() as connection:
    connection.execute(
        text(
            """
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS donor_type VARCHAR(20);
            """
        )
    )

    connection.execute(
        text(
            """
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS ngo_id INTEGER;
            """
        )
    )

    connection.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_users_ngo_id
            ON users (ngo_id);
            """
        )
    )

    connection.execute(
        text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'fk_users_ngo_id'
                ) THEN
                    ALTER TABLE users
                    ADD CONSTRAINT fk_users_ngo_id
                    FOREIGN KEY (ngo_id)
                    REFERENCES users(id)
                    ON DELETE SET NULL;
                END IF;
            END
            $$;
            """
        )
    )

print("USER DATABASE SCHEMA UPDATED")