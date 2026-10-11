-- Foodys DBMS demonstration queries for pgAdmin.

-- Row counts for all five principal tables.
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL
SELECT 'donations', COUNT(*) FROM donations
UNION ALL
SELECT 'food_requests', COUNT(*) FROM food_requests
UNION ALL
SELECT 'matches', COUNT(*) FROM matches
UNION ALL
SELECT 'deliveries', COUNT(*) FROM deliveries;

-- Multi-table delivery history JOIN.
SELECT
    d.id AS delivery_id,
    d.status AS delivery_status,
    d.pickup_time,
    d.delivery_time,
    m.id AS match_id,
    m.allocated_quantity,
    m.status AS match_status,
    dn.food_name,
    dn.status AS donation_status,
    fr.food_name AS requested_food,
    fr.status AS request_status,
    donor.name AS donor_name,
    ngo.name AS ngo_member_name,
    ngo.organization_name
FROM deliveries AS d
JOIN matches AS m ON m.id = d.match_id
JOIN donations AS dn ON dn.id = m.donation_id
JOIN users AS donor ON donor.id = dn.donor_id
JOIN users AS ngo ON ngo.id = m.ngo_id
LEFT JOIN food_requests AS fr ON fr.id = m.request_id
ORDER BY d.id DESC;

-- Impact aggregates calculated from relational data.
SELECT
    COALESCE(SUM(m.allocated_quantity), 0) AS delivered_quantity,
    COUNT(DISTINCT d.id) AS completed_deliveries,
    COUNT(DISTINCT m.donation_id) AS completed_donations
FROM deliveries AS d
JOIN matches AS m ON m.id = d.match_id
WHERE d.status = 'delivered';

SELECT COUNT(*) AS fulfilled_requests
FROM food_requests
WHERE status = 'fulfilled';

SELECT COUNT(DISTINCT donor_id) AS active_donors
FROM donations
WHERE status NOT IN ('cancelled', 'expired');

SELECT COUNT(DISTINCT ngo_id) AS active_ngos
FROM (
    SELECT ngo_id FROM food_requests
    UNION
    SELECT ngo_id FROM matches
) AS ngo_activity;

-- Useful indexes defined on the current database.
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('users', 'donations', 'food_requests', 'matches', 'deliveries')
ORDER BY tablename, indexname;
