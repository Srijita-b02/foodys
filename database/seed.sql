-- Repeatable Foodys demonstration data.
--
-- Demo login password for every account: Demo@123
-- This script removes only records connected to the four exact demo emails
-- below. It does not delete ordinary application data.
-- Run after schema.sql against PostgreSQL:
--   psql -v ON_ERROR_STOP=1 -1 -d foodys_db -f database/seed.sql

BEGIN;

DELETE FROM deliveries
WHERE match_id IN (
    SELECT m.id
    FROM matches AS m
    JOIN donations AS d ON d.id = m.donation_id
    JOIN users AS donor ON donor.id = d.donor_id
    JOIN users AS ngo ON ngo.id = m.ngo_id
    WHERE donor.email IN ('donor1@foodys.demo', 'donor2@foodys.demo')
       OR ngo.email IN ('ngo1@foodys.demo', 'ngo2@foodys.demo')
);

DELETE FROM matches
WHERE donation_id IN (
        SELECT d.id
        FROM donations AS d
        JOIN users AS u ON u.id = d.donor_id
        WHERE u.email IN ('donor1@foodys.demo', 'donor2@foodys.demo')
    )
   OR ngo_id IN (
        SELECT id FROM users
        WHERE email IN ('ngo1@foodys.demo', 'ngo2@foodys.demo')
    );

DELETE FROM donations
WHERE donor_id IN (
    SELECT id FROM users
    WHERE email IN ('donor1@foodys.demo', 'donor2@foodys.demo')
);

DELETE FROM food_requests
WHERE ngo_id IN (
    SELECT id FROM users
    WHERE email IN ('ngo1@foodys.demo', 'ngo2@foodys.demo')
);

DELETE FROM users
WHERE email IN (
    'donor1@foodys.demo',
    'donor2@foodys.demo',
    'ngo1@foodys.demo',
    'ngo2@foodys.demo'
);

INSERT INTO users (
    name, email, password_hash, phone, role, donor_type,
    organization_name, location
)
VALUES
    (
        'Anand Restaurant',
        'donor1@foodys.demo',
        '30403efa4239ad22e160c97c06322108$e83527293c84f7194f68d92d2a4dc682ad34ca1aca1fd87a2cc3407df759f483',
        '9000000001', 'donor', 'restaurant', NULL, 'Katpadi, Vellore'
    ),
    (
        'Meera',
        'donor2@foodys.demo',
        '30403efa4239ad22e160c97c06322108$e83527293c84f7194f68d92d2a4dc682ad34ca1aca1fd87a2cc3407df759f483',
        '9000000002', 'donor', 'individual', NULL, 'Gandhi Nagar, Vellore'
    ),
    (
        'Kavya',
        'ngo1@foodys.demo',
        '30403efa4239ad22e160c97c06322108$e83527293c84f7194f68d92d2a4dc682ad34ca1aca1fd87a2cc3407df759f483',
        '9000000003', 'ngo', NULL, 'Hope Community Kitchen', 'Vellore'
    ),
    (
        'Rahul',
        'ngo2@foodys.demo',
        '30403efa4239ad22e160c97c06322108$e83527293c84f7194f68d92d2a4dc682ad34ca1aca1fd87a2cc3407df759f483',
        '9000000004', 'ngo', NULL, 'Helping Hands Trust', 'Katpadi, Vellore'
    );

INSERT INTO donations (
    donor_id, food_name, description, category, quantity, unit,
    prepared_at, expiry_time, pickup_address, status
)
VALUES
    (
        (SELECT id FROM users WHERE email = 'donor1@foodys.demo'),
        'Vegetable pulao', '[DEMO] Available food for direct reservation',
        'Cooked meals', 60, 'meals', CURRENT_TIMESTAMP - INTERVAL '30 minutes',
        CURRENT_TIMESTAMP + INTERVAL '5 hours', 'Katpadi, Vellore', 'available'
    ),
    (
        (SELECT id FROM users WHERE email = 'donor1@foodys.demo'),
        'Rice packets', '[DEMO] Partially allocated donation',
        'Cooked meals', 50, 'packets', CURRENT_TIMESTAMP - INTERVAL '1 hour',
        CURRENT_TIMESTAMP + INTERVAL '4 hours', 'Katpadi, Vellore', 'available'
    ),
    (
        (SELECT id FROM users WHERE email = 'donor2@foodys.demo'),
        'Idli meals', '[DEMO] Successfully delivered donation',
        'Cooked meals', 40, 'meals', CURRENT_TIMESTAMP - INTERVAL '3 hours',
        CURRENT_TIMESTAMP + INTERVAL '2 hours', 'Gandhi Nagar, Vellore', 'delivered'
    ),
    (
        (SELECT id FROM users WHERE email = 'donor2@foodys.demo'),
        'Bread packs', '[DEMO] Donation currently in transit',
        'Packaged food', 25, 'packs', CURRENT_TIMESTAMP - INTERVAL '2 hours',
        CURRENT_TIMESTAMP + INTERVAL '8 hours', 'Gandhi Nagar, Vellore', 'matched'
    );

INSERT INTO food_requests (
    ngo_id, food_name, category, quantity, unit, description,
    location, needed_before, status
)
VALUES
    (
        (SELECT id FROM users WHERE email = 'ngo1@foodys.demo'),
        'Rice packets', 'Cooked meals', 80, 'packets',
        '[DEMO] Partially matched request with 50 packets remaining',
        'Vellore', CURRENT_TIMESTAMP + INTERVAL '4 hours', 'open'
    ),
    (
        (SELECT id FROM users WHERE email = 'ngo1@foodys.demo'),
        'Idli meals', 'Cooked meals', 40, 'meals',
        '[DEMO] Fulfilled request', 'Vellore',
        CURRENT_TIMESTAMP + INTERVAL '2 hours', 'fulfilled'
    ),
    (
        (SELECT id FROM users WHERE email = 'ngo2@foodys.demo'),
        'Milk', 'Dairy', 20, 'litres', '[DEMO] Open unmatched request',
        'Katpadi, Vellore', CURRENT_TIMESTAMP + INTERVAL '6 hours', 'open'
    );

INSERT INTO matches (
    donation_id, request_id, ngo_id, allocated_quantity, status
)
VALUES
    (
        (SELECT id FROM donations WHERE description = '[DEMO] Partially allocated donation'),
        (SELECT id FROM food_requests WHERE description = '[DEMO] Partially matched request with 50 packets remaining'),
        (SELECT id FROM users WHERE email = 'ngo1@foodys.demo'),
        30, 'active'
    ),
    (
        (SELECT id FROM donations WHERE description = '[DEMO] Successfully delivered donation'),
        (SELECT id FROM food_requests WHERE description = '[DEMO] Fulfilled request'),
        (SELECT id FROM users WHERE email = 'ngo1@foodys.demo'),
        40, 'completed'
    ),
    (
        (SELECT id FROM donations WHERE description = '[DEMO] Donation currently in transit'),
        NULL,
        (SELECT id FROM users WHERE email = 'ngo2@foodys.demo'),
        25, 'active'
    );

INSERT INTO deliveries (
    match_id, assigned_ngo_member_id, status, assigned_at,
    pickup_time, delivery_time
)
VALUES
    (
        (
            SELECT m.id FROM matches AS m
            JOIN donations AS d ON d.id = m.donation_id
            WHERE d.description = '[DEMO] Partially allocated donation'
        ),
        (SELECT id FROM users WHERE email = 'ngo1@foodys.demo'),
        'assigned', CURRENT_TIMESTAMP - INTERVAL '20 minutes', NULL, NULL
    ),
    (
        (
            SELECT m.id FROM matches AS m
            JOIN donations AS d ON d.id = m.donation_id
            WHERE d.description = '[DEMO] Successfully delivered donation'
        ),
        (SELECT id FROM users WHERE email = 'ngo1@foodys.demo'),
        'delivered', CURRENT_TIMESTAMP - INTERVAL '2 hours',
        CURRENT_TIMESTAMP - INTERVAL '90 minutes',
        CURRENT_TIMESTAMP - INTERVAL '1 hour'
    ),
    (
        (
            SELECT m.id FROM matches AS m
            JOIN donations AS d ON d.id = m.donation_id
            WHERE d.description = '[DEMO] Donation currently in transit'
        ),
        (SELECT id FROM users WHERE email = 'ngo2@foodys.demo'),
        'in_transit', CURRENT_TIMESTAMP - INTERVAL '1 hour',
        CURRENT_TIMESTAMP - INTERVAL '30 minutes', NULL
    );

COMMIT;

-- Demo accounts:
-- donor1@foodys.demo / Demo@123
-- donor2@foodys.demo / Demo@123
-- ngo1@foodys.demo   / Demo@123
-- ngo2@foodys.demo   / Demo@123
