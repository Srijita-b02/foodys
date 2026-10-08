-- Foodys PostgreSQL schema
--
-- This file creates a fresh application schema. It intentionally contains no
-- DROP statements so running it cannot silently destroy an existing database.
-- Run it against an empty PostgreSQL database with stop-on-error enabled:
--
--   psql -v ON_ERROR_STOP=1 -1 -d foodys_db -f database/schema.sql
--
-- Role-specific foreign-key rules (for example, ensuring donations.donor_id
-- points to a donor account) are enforced by the FastAPI authorization layer.
-- PostgreSQL CHECK constraints cannot safely inspect another table.

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'donor',
    donor_type VARCHAR(20),
    organization_name VARCHAR(150),
    location VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_role
        CHECK (role IN ('donor', 'ngo')),
    CONSTRAINT ck_users_donor_type
        CHECK (
            donor_type IS NULL
            OR donor_type IN ('individual', 'restaurant')
        ),
    CONSTRAINT ck_users_role_fields
        CHECK (
            (
                role = 'donor'
                AND donor_type IS NOT NULL
                AND organization_name IS NULL
            )
            OR
            (
                role = 'ngo'
                AND donor_type IS NULL
                AND organization_name IS NOT NULL
            )
        )
);

CREATE TABLE donations (
    id SERIAL PRIMARY KEY,
    donor_id INTEGER NOT NULL,
    food_name VARCHAR(150) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit VARCHAR(30) NOT NULL,
    prepared_at TIMESTAMPTZ NOT NULL,
    expiry_time TIMESTAMPTZ NOT NULL,
    pickup_address VARCHAR(500) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'available',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_donations_donor_id
        FOREIGN KEY (donor_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,
    CONSTRAINT ck_donations_quantity_positive
        CHECK (quantity > 0),
    CONSTRAINT ck_donations_expiry_after_prepared
        CHECK (expiry_time > prepared_at),
    CONSTRAINT ck_donations_status
        CHECK (
            status IN (
                'available',
                'reserved',
                'matched',
                'assigned',
                'picked_up',
                'in_transit',
                'delivered',
                'cancelled',
                'expired'
            )
        )
);

CREATE TABLE food_requests (
    id SERIAL PRIMARY KEY,
    ngo_id INTEGER NOT NULL,
    food_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit VARCHAR(30) NOT NULL,
    description TEXT,
    location VARCHAR(500) NOT NULL,
    needed_before TIMESTAMPTZ NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_food_requests_ngo_id
        FOREIGN KEY (ngo_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,
    CONSTRAINT ck_food_requests_quantity_positive
        CHECK (quantity > 0),
    CONSTRAINT ck_food_requests_deadline_after_creation
        CHECK (needed_before > created_at),
    CONSTRAINT ck_food_requests_status
        CHECK (
            status IN (
                'open',
                'matched',
                'fulfilled',
                'cancelled',
                'expired'
            )
        )
);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    donation_id INTEGER NOT NULL,
    request_id INTEGER,
    ngo_id INTEGER NOT NULL,
    allocated_quantity INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_matches_donation_id
        FOREIGN KEY (donation_id)
        REFERENCES donations(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_matches_request_id
        FOREIGN KEY (request_id)
        REFERENCES food_requests(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_matches_ngo_id
        FOREIGN KEY (ngo_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,
    CONSTRAINT ck_matches_allocated_quantity_positive
        CHECK (allocated_quantity > 0),
    CONSTRAINT ck_matches_status
        CHECK (status IN ('active', 'completed', 'cancelled'))
);

-- request_id is nullable for direct NGO reservations. Partial allocations and
-- total remaining quantities are protected by row-locked FastAPI transactions
-- because those rules depend on sums across multiple match rows.

CREATE TABLE deliveries (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL,
    assigned_ngo_member_id INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'assigned',
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pickup_time TIMESTAMPTZ,
    delivery_time TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_deliveries_match_id UNIQUE (match_id),
    CONSTRAINT fk_deliveries_match_id
        FOREIGN KEY (match_id)
        REFERENCES matches(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_deliveries_assigned_ngo_member_id
        FOREIGN KEY (assigned_ngo_member_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,
    CONSTRAINT ck_deliveries_status
        CHECK (
            status IN (
                'assigned',
                'picked_up',
                'in_transit',
                'delivered',
                'cancelled'
            )
        )
);

-- User and role lookup indexes
CREATE INDEX ix_users_role ON users(role);

-- Donation discovery and ownership indexes
CREATE INDEX ix_donations_donor_id ON donations(donor_id);
CREATE INDEX ix_donations_category ON donations(category);
CREATE INDEX ix_donations_expiry_time ON donations(expiry_time);
CREATE INDEX ix_donations_pickup_address ON donations(pickup_address);
CREATE INDEX ix_donations_status ON donations(status);

-- Food-request discovery and ownership indexes
CREATE INDEX ix_food_requests_ngo_id ON food_requests(ngo_id);
CREATE INDEX ix_food_requests_category ON food_requests(category);
CREATE INDEX ix_food_requests_location ON food_requests(location);
CREATE INDEX ix_food_requests_needed_before ON food_requests(needed_before);
CREATE INDEX ix_food_requests_status ON food_requests(status);

-- Matching and delivery workflow indexes
CREATE INDEX ix_matches_donation_id ON matches(donation_id);
CREATE INDEX ix_matches_request_id ON matches(request_id);
CREATE INDEX ix_matches_ngo_id ON matches(ngo_id);
CREATE INDEX ix_matches_status ON matches(status);
CREATE INDEX ix_deliveries_assigned_ngo_member_id
    ON deliveries(assigned_ngo_member_id);
CREATE INDEX ix_deliveries_status ON deliveries(status);
