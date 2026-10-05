# Foodys

foodys is a database-driven food redistribution platform that connects food donors, NGOs or recipient organizations, and delivery volunteers. It is designed as a two-person academic DBMS project and prioritizes a correct relational database, reliable transactions, and a complete end-to-end workflow over unnecessary product complexity.

Restaurants, bakeries, hostels, college cafeterias, caterers, event organizers, and other food providers can announce usable surplus food. NGOs can discover and reserve that supply, or publish food requests that donors can answer. Once a donation and recipient are matched, a volunteer completes pickup and delivery.

The platform supports both directions of discovery:

```text
SUPPLY → DEMAND: donor posts food → NGO reserves it
DEMAND → SUPPLY: NGO posts a request → donor responds
```

Its primary societal alignment is **SDG 2 — Zero Hunger**. It also supports **SDG 12 — Responsible Consumption and Production** by helping reduce avoidable food waste.

## Project status

The repository is currently at the initialization stage:

- the React/Vite frontend scaffold is installed and passes linting;
- the Python virtual environment and initial backend dependencies are installed locally;
- product, engineering, security, and collaboration decisions are documented;
- database schema, FastAPI routes, application pages, and tests are still to be implemented.

Planned functionality in this document must not be presented as completed until it exists and has been tested.

## Problem statement

Usable surplus food is often discarded while nearby NGOs and recipient organizations still need food. The problem is not only availability; it is timely coordination among current supply, current demand, donors, NGOs, volunteers, reservations, deliveries, expiry times, and transaction history.

foodys provides one structured system to:

- publish time-sensitive surplus food;
- publish specific food requirements;
- match supply with demand in either direction;
- prevent duplicate reservations;
- coordinate volunteer pickup and delivery;
- preserve reliable donation and delivery history;
- calculate impact from real database records;
- demonstrate core relational DBMS concepts in a working application.

## MVP objectives

The MVP must allow:

- users to register and log in with one of three valid roles;
- donors to create, view, edit, cancel, and track their donations;
- NGOs to browse and reserve available food;
- NGOs to create, manage, and track food requests;
- donors to browse and answer open NGO requests;
- volunteers to accept delivery tasks and update valid delivery states;
- all roles to see data appropriate to their role;
- the backend and database to protect ownership, state, and transaction consistency;
- both project members to demonstrate meaningful database work.

## User roles

The application has exactly three primary roles:

```text
DONOR
NGO
VOLUNTEER
```

Admin functionality is optional and is not an MVP priority.

### Donor

A donor may be a restaurant, bakery, hostel, college cafeteria, catering service, event organizer, food business, or another organization with safe surplus food.

A donor can:

- register and log in;
- create a food donation;
- view their own donations;
- edit or cancel their own available donations;
- browse open NGO food requests;
- filter requests by area or food type;
- respond to an open request using an available donation;
- view active matches and pickups;
- view completed donation history.

### NGO / recipient organization

An NGO can:

- register and log in;
- browse currently available, unexpired food;
- filter donations by area or food type;
- reserve an available donation;
- create a food request with quantity and deadline;
- view, edit, or cancel its own open requests;
- view active matches and incoming deliveries;
- view received-food history.

### Volunteer

A volunteer can:

- register and log in;
- browse available delivery tasks;
- accept one available delivery safely;
- view pickup and recipient details for an assigned delivery;
- mark the delivery as picked up, in transit, and delivered;
- view their delivery history.

Role and ownership rules must be enforced in FastAPI. Hiding a button or route in React is not authorization.

## Core workflows

### Supply-first workflow

The donor already has surplus food:

```text
DONOR
  ↓
CREATE DONATION
  ↓
AVAILABLE
  ↓
NGO BROWSES AND RESERVES
  ↓
MATCH CREATED
  ↓
DELIVERY CREATED
  ↓
VOLUNTEER ACCEPTS
  ↓
PICKED_UP
  ↓
IN_TRANSIT
  ↓
DELIVERED
```

### Demand-first workflow

The NGO publishes a requirement first:

```text
NGO
  ↓
CREATE FOOD REQUEST
  ↓
OPEN
  ↓
DONOR BROWSES AND RESPONDS
  ↓
DONATION + MATCH CREATED
  ↓
DELIVERY CREATED
  ↓
VOLUNTEER ACCEPTS
  ↓
PICKED_UP
  ↓
IN_TRANSIT
  ↓
DELIVERED
```

Both workflows are required. Bidirectional matching is a defining foodys feature.

## Required technology stack

| Layer | Technology |
|---|---|
| Frontend | React with Vite |
| Frontend language | JavaScript / JSX |
| Frontend routing | React Router |
| Styling | CSS and optionally Bootstrap |
| Backend | FastAPI |
| Backend language | Python |
| API | REST over HTTP/JSON |
| Database | PostgreSQL |
| Database access | SQLAlchemy and/or parameterized SQL |
| Validation | Pydantic plus database constraints |
| Password hashing | bcrypt / Passlib-compatible hashing |
| Version control | Git and GitHub |
| API testing | Swagger UI, Postman, or Bruno |
| Primary environment | Localhost |

Do not replace this stack with Next.js, Firebase, MongoDB, Supabase Auth, GraphQL, microservices, Redis, Kubernetes, message queues, or complex Docker orchestration unless both project members explicitly change the scope. PostgreSQL is a core learning component.

## System architecture

```text
+-------------------------------+
| React + Vite frontend         |
|                               |
| Login / registration          |
| Donor dashboard               |
| NGO dashboard                 |
| Volunteer dashboard           |
| Forms, lists, status views    |
+---------------+---------------+
                |
                | REST / JSON
                ↓
+-------------------------------+
| FastAPI backend               |
|                               |
| Authentication               |
| Role and ownership checks     |
| Pydantic validation           |
| Donation/request APIs         |
| Matching transactions         |
| Delivery state machine        |
+---------------+---------------+
                |
                | SQLAlchemy / SQL
                ↓
+-------------------------------+
| PostgreSQL                    |
|                               |
| users                         |
| donations                     |
| food_requests                 |
| matches                       |
| deliveries                    |
+-------------------------------+
```

The backend and database are authoritative. The frontend must refresh from a successful API response instead of inventing reservation or status changes locally.

## Repository layout

The intended working layout is:

```text
foodys/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── database/
│   ├── schema.sql
│   └── seed.sql
├── .editorconfig
├── .gitignore
└── README.md
```

Some planned directories are created only when their implementation begins. Keep the structure straightforward and avoid abstraction that hides database behavior.

## Relational database design

The MVP centers on five tables:

```text
users
donations
food_requests
matches
deliveries
```

Conceptual relationships:

```text
                 USERS
                   |
          +--------+--------+
          |                 |
          ↓                 ↓
      DONATIONS       FOOD_REQUESTS
          \                 /
           \               /
            +--- MATCHES --+
                    |
                    ↓
               DELIVERIES
                    |
                    ↓
             VOLUNTEER USER
```

### `users`

Expected fields:

```text
user_id
name
email
password_hash
role
organization_name
phone
area
created_at
```

Important rules:

- `user_id` is the primary key;
- `email` is unique and required;
- `password_hash` is required and never returned by APIs;
- `role` is restricted to `DONOR`, `NGO`, or `VOLUNTEER`;
- only the minimum required personal information is stored.

### `donations`

Expected fields:

```text
donation_id
donor_id
food_name
food_type
quantity
unit
description
area
prepared_at
expires_at
status
created_at
updated_at
```

`donor_id` references `users.user_id`. The referenced user must exist and have the `DONOR` role.

Allowed statuses:

```text
AVAILABLE
RESERVED
MATCHED
ASSIGNED
PICKED_UP
IN_TRANSIT
DELIVERED
CANCELLED
EXPIRED
```

Important rules include `quantity > 0` and `expires_at > prepared_at`.

### `food_requests`

Expected fields:

```text
request_id
ngo_id
food_name
food_type
quantity
unit
description
area
needed_before
status
created_at
updated_at
```

`ngo_id` references `users.user_id`. The referenced user must exist and have the `NGO` role.

Allowed statuses:

```text
OPEN
MATCHED
FULFILLED
CANCELLED
EXPIRED
```

Important rules include `quantity > 0` and a future `needed_before` value on creation.

### `matches`

Expected fields:

```text
match_id
donation_id
request_id
ngo_id
status
created_at
```

Relationships:

- `donation_id` references `donations.donation_id`;
- `request_id` references `food_requests.request_id` and may be null when an NGO directly reserves a donation;
- `ngo_id` references `users.user_id`.

Allowed statuses:

```text
ACTIVE
COMPLETED
CANCELLED
```

### `deliveries`

Expected fields:

```text
delivery_id
match_id
volunteer_id
status
assigned_at
pickup_time
delivery_time
```

Relationships:

- `match_id` references `matches.match_id`;
- `volunteer_id` references `users.user_id` and is nullable until accepted.

Allowed statuses:

```text
AVAILABLE
ASSIGNED
PICKED_UP
IN_TRANSIT
DELIVERED
CANCELLED
```

## Database requirements

This project must visibly demonstrate:

- primary keys;
- foreign keys;
- `NOT NULL`, `UNIQUE`, and `CHECK` constraints;
- referential integrity;
- normalization without unnecessary duplication;
- useful indexes;
- database-side filtering;
- multi-table joins;
- aggregate queries;
- transactions, commit, and rollback;
- concurrency protection;
- consistent status transitions.

Validation belongs in both Pydantic and PostgreSQL where appropriate. React validation is only a usability layer.

### Recommended indexes

Create focused indexes for the main listing queries:

```sql
CREATE INDEX idx_donations_status ON donations(status);
CREATE INDEX idx_donations_area ON donations(area);
CREATE INDEX idx_food_requests_status ON food_requests(status);
CREATE INDEX idx_food_requests_area ON food_requests(area);
```

Do not add indexes without a real filtering, joining, or sorting use case.

### Area-based discovery

Location is deliberately simple for the MVP. Store an `area`, such as `Katpadi`, `Vellore`, `Gandhi Nagar`, or `Bagayam`.

Donation discovery should be performed in PostgreSQL:

```sql
SELECT *
FROM donations
WHERE status = 'AVAILABLE'
  AND area = :area
  AND expires_at > NOW()
ORDER BY expires_at ASC;
```

Request discovery should follow the same principle:

```sql
SELECT *
FROM food_requests
WHERE status = 'OPEN'
  AND area = :area
  AND needed_before > NOW()
ORDER BY needed_before ASC;
```

Do not load an entire table and filter it in React. GPS, maps, and distance calculations are deferred.

## Transaction and concurrency rules

### NGO reserves an available donation

Reservation is one atomic operation:

```text
BEGIN
  conditionally change donation from AVAILABLE
  create match
  create AVAILABLE delivery
COMMIT
```

On failure, roll back all related writes.

A plain read followed later by an update is unsafe because two NGOs could both see `AVAILABLE`. Use locking or a conditional update:

```sql
UPDATE donations
SET status = 'RESERVED', updated_at = NOW()
WHERE donation_id = :donation_id
  AND status = 'AVAILABLE'
  AND expires_at > NOW();
```

If no row changes, return `409 Conflict`. Only one concurrent reservation may succeed.

This workflow demonstrates atomicity, consistency, isolation, and durability.

### Donor responds to an NGO request

The backend must atomically:

```text
verify request is OPEN and unexpired
verify donation is AVAILABLE and unexpired
create match
mark request MATCHED
mark donation MATCHED
create AVAILABLE delivery
commit
```

Any failure must roll back the entire operation.

### Volunteer accepts a delivery

Acceptance must also prevent two volunteers from receiving the same task. Conditionally update only an `AVAILABLE` delivery and return `409 Conflict` if another volunteer already accepted it.

## Delivery state machine

Only these forward transitions are valid:

```text
AVAILABLE
   ↓
ASSIGNED
   ↓
PICKED_UP
   ↓
IN_TRANSIT
   ↓
DELIVERED
```

Examples that must be rejected include:

```text
AVAILABLE → DELIVERED
ASSIGNED → IN_TRANSIT
ASSIGNED → DELIVERED
DELIVERED → PICKED_UP
```

Only the assigned volunteer may update an active assigned delivery.

When a delivery reaches `DELIVERED`, one transaction should update:

```text
delivery.status = DELIVERED
delivery.delivery_time = current time
match.status = COMPLETED
donation.status = DELIVERED
food_request.status = FULFILLED, when a request is linked
```

## Expiry rules

If a donation has `expires_at <= current time` while it is still `AVAILABLE`, set it to `EXPIRED`. If a request has `needed_before <= current time` while it is still `OPEN`, set it to `EXPIRED`.

Expired records remain in the database for history. They must not appear in active listings and must not be reservable or matchable. They are not automatically deleted.

## Authentication and authorization

The MVP uses email/password authentication:

```text
user submits email and password
  ↓
FastAPI finds the user by email
  ↓
stored password hash is verified
  ↓
user identity and role are established
  ↓
authorized role-specific operation continues
```

Required security baseline:

- hash every password before storage;
- never store plaintext passwords;
- never expose password hashes through response models;
- keep database credentials and secrets in ignored `.env` files;
- commit only `.env.example` placeholders;
- authorize roles and record ownership in FastAPI;
- use SQLAlchemy or parameterized SQL;
- return `401` when unauthenticated and `403` when authenticated but forbidden;
- store only the minimum user information required by the application.

OAuth, MFA, email verification, CAPTCHA, advanced encryption infrastructure, security monitoring, rate limiting, and dedicated secret-management platforms are not required for this academic MVP.

## REST API plan

Expected endpoint areas are `/auth`, `/donations`, `/requests`, `/matches`, and `/deliveries`.

### Authentication

```text
POST /auth/register
POST /auth/login
```

### Donations

```text
GET    /donations
POST   /donations
GET    /donations/{id}
PUT    /donations/{id}
DELETE /donations/{id}
```

### Food requests

```text
GET    /requests
POST   /requests
GET    /requests/{id}
PUT    /requests/{id}
DELETE /requests/{id}
```

### Matches

```text
GET  /matches
POST /matches/reserve
POST /matches/respond
GET  /matches/{id}
```

### Deliveries

```text
GET   /deliveries
GET   /deliveries/available
POST  /deliveries/{id}/accept
PATCH /deliveries/{id}/status
```

Use clear Pydantic request and response models. Return meaningful statuses:

| Status | Meaning |
|---|---|
| `200` | Successful request |
| `201` | Resource created |
| `400` | Invalid business operation |
| `401` | Authentication required |
| `403` | Wrong role, ownership, or permission |
| `404` | Referenced record does not exist |
| `409` | State conflict, such as an existing reservation |
| `422` | Request validation failed |

Never report a failed business operation as `200 OK`.

## Relational query requirements

At least one meaningful delivery-history query should join matches, donations, donor users, NGO users, deliveries, and volunteer users:

```sql
SELECT
    d.food_name,
    donor.name AS donor_name,
    ngo.name AS ngo_name,
    volunteer.name AS volunteer_name,
    dl.status,
    dl.pickup_time,
    dl.delivery_time
FROM matches AS m
JOIN donations AS d
  ON m.donation_id = d.donation_id
JOIN users AS donor
  ON d.donor_id = donor.user_id
JOIN users AS ngo
  ON m.ngo_id = ngo.user_id
JOIN deliveries AS dl
  ON dl.match_id = m.match_id
LEFT JOIN users AS volunteer
  ON dl.volunteer_id = volunteer.user_id;
```

Required aggregate examples include:

```sql
SELECT COUNT(*)
FROM donations
WHERE status = 'DELIVERED';

SELECT COALESCE(SUM(quantity), 0)
FROM donations
WHERE status = 'DELIVERED';

SELECT COUNT(*)
FROM food_requests
WHERE status = 'FULFILLED';

SELECT volunteer_id, COUNT(*) AS completed_deliveries
FROM deliveries
WHERE status = 'DELIVERED'
GROUP BY volunteer_id;
```

## Frontend plan

Minimum pages:

- Login;
- Register;
- Donor Dashboard;
- Create/Edit Donation;
- NGO Dashboard;
- Create/Edit Food Request;
- Volunteer Dashboard;
- Delivery Status and History.

Suggested dashboard content:

| Dashboard | Content |
|---|---|
| Donor | Post Food, My Donations, Requests in My Area, Active Matches, Active Pickups, Completed Donations |
| NGO | Create Request, Available Food, My Open Requests, Active Matches, Incoming Deliveries, Received Food |
| Volunteer | Available Deliveries, Current Assignment, Pickup Details, Recipient Details, Status Actions, History |

Use functional components, React Router, `useState`, `useEffect`, and `fetch` or Axios. Keep components small. Redux, Zustand, and other global-state frameworks are unnecessary unless a real requirement appears.

Each page should show loading, empty, success, and error states. After a mutation, use the API result and refresh authoritative data rather than faking a local status change.

## Local development

### Prerequisites

- Git;
- PostgreSQL;
- Python 3 with `venv` and `pip`;
- Node.js compatible with the installed Vite version (`^20.19.0` or `>=22.12.0`);
- npm.

Expected local services:

| Service | URL |
|---|---|
| React frontend | `http://localhost:5173` |
| FastAPI backend | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| PostgreSQL | Local installation/configured development instance |

### Clone

```bash
git clone https://github.com/Srijita-b02/foodys.git
cd foodys
```

### Configure PostgreSQL

Create a local database named `foodys`. Copy the safe template:

```powershell
Copy-Item backend/.env.example backend/.env
```

On Linux/macOS:

```bash
cp backend/.env.example backend/.env
```

Update `backend/.env` with local credentials. Never commit it.

Example format:

```dotenv
DATABASE_URL=postgresql://username:password@localhost:5432/foodys
SECRET_KEY=replace-with-a-long-random-development-secret
FRONTEND_ORIGIN=http://localhost:5173
```

### Backend setup

```bash
cd backend
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies and, once `main.py` exists, run the API:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend setup

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Useful frontend checks:

```bash
npm run lint
npm run build
```

## Seed and demo data

Create repeatable `database/seed.sql` data after the schema is implemented. Minimum demo data:

- one donor;
- one NGO;
- one volunteer;
- two donations;
- two food requests.

Example local-only identities may use `donor@test.com`, `ngo@test.com`, and `volunteer@test.com`. Use fake credentials and store only password hashes, including in seed data.

## Two-person DBMS work division

Both members must be able to explain and demonstrate database work. The split reduces merge conflicts while preserving shared understanding.

### Person A — users, authentication, and donations

Primary ownership:

- `users` schema, constraints, and model;
- registration, password hashing, login, and user identity;
- backend role-authorization foundation;
- `donations` schema, constraints, model, and CRUD;
- donor ownership checks;
- donation expiry and filtering;
- donor-facing pages;
- aggregate statistics and related queries.

DBMS topics demonstrated:

- unique email and role constraints;
- password-hash storage;
- user-to-donation foreign key;
- donation validation and indexes;
- database-side filters;
- aggregate queries.

### Person B — requests, matching, and deliveries

Primary ownership:

- `food_requests` schema, constraints, model, and CRUD;
- `matches` and `deliveries` schemas and foreign keys;
- NGO reservation transaction;
- donor response transaction;
- duplicate reservation protection;
- volunteer acceptance concurrency protection;
- delivery state machine and completion transaction;
- delivery-history joins;
- NGO and volunteer pages.

DBMS topics demonstrated:

- multi-table relationships;
- transactions, commit, and rollback;
- conditional updates or locking;
- state consistency;
- joins and referential integrity.

### Shared responsibilities

Both members review:

- schema changes and foreign-key effects;
- API contracts used by both sides;
- shared files such as `main.py`, `database.py`, and `App.jsx`;
- integration and full workflow tests;
- seed data, demo preparation, documentation, and final viva explanation.

Ownership does not mean only one person understands a table. Each member should be able to explain the five-table model and both matching workflows.

## Recommended implementation order

1. Agree on schema and status values.
2. Create `schema.sql`, constraints, foreign keys, and indexes.
3. Create SQLAlchemy models and database connection handling.
4. Implement users, registration, login, hashing, and backend authorization.
5. Implement donation CRUD, validation, filtering, and expiry.
6. Implement food-request CRUD, validation, filtering, and expiry.
7. Implement the NGO reservation transaction and duplicate-reservation test.
8. Implement the donor-response transaction.
9. Implement delivery creation, volunteer acceptance, and the state machine.
10. Implement completion updates, joins, and aggregate queries.
11. Connect the React pages only to tested backend APIs.
12. Add seed data, complete workflow tests, UI cleanup, and demo preparation.

For a schema change, update all affected layers together:

```text
schema.sql
SQLAlchemy model
Pydantic schemas
routes/services
seed.sql
tests
frontend assumptions
```

## Git collaboration workflow

The first commit should contain the safe repository scaffold and documentation. Do not commit `venv`, `node_modules`, build output, `.env`, credentials, keys, local databases, or editor files.

Recommended branches:

```text
main
  └── development
        ├── person-a/auth
        ├── person-a/donations
        ├── person-b/requests
        ├── person-b/matching
        └── person-b/deliveries
```

Typical workflow:

```bash
git switch development
git pull
git switch -c person-a/donations
```

Before merging, pull the latest shared branch, resolve conflicts carefully, run relevant tests, and review the staged files. Merge feature branches into `development`; merge tested milestones into `main`.

Use focused commit messages such as:

```text
Initialize foodys project structure
Add user and donation database models
Implement NGO food request endpoints
Prevent duplicate donation reservations
Implement volunteer delivery state flow
```

Avoid vague messages such as `update`, `stuff`, `fix`, or `final`.

Before every commit:

```bash
git status
git diff --staged
```

Check that no `.env`, credential, generated dependency directory, or unrelated file is staged.

## Testing requirements

Every core flow needs a success case and an obvious failure case. At minimum test:

| Scenario | Expected result |
|---|---|
| Register unique valid user | User created with hashed password |
| Register duplicate email | Rejected |
| Register invalid role | Rejected |
| Create donation with `quantity <= 0` | Rejected |
| Create donation with invalid donor reference/role | Rejected |
| Create request with invalid NGO reference/role | Rejected |
| Create request with past deadline | Rejected |
| Reserve available donation | Donation updated, match and delivery created |
| Reserve expired donation | Rejected |
| Reserve same donation twice | Exactly one reservation succeeds |
| Donor answers open request | Donation/request matched and delivery created |
| Two volunteers accept one delivery | Exactly one acceptance succeeds |
| Apply invalid delivery transition | Rejected |
| Complete valid delivery sequence | Delivery, match, donation, and optional request updated |
| Access route with wrong role | `403 Forbidden` |
| Access another user's owned record | Rejected |

Test backend endpoints in Swagger before using frontend behavior to diagnose them. For transaction tests, verify both the expected records and the absence of partial writes after failure.

## Demo checklist

Before the evaluation:

1. Use a known local database and load repeatable seed data.
2. Start PostgreSQL, FastAPI, and React.
3. Verify Swagger at `http://localhost:8000/docs`.
4. Log in once as donor, NGO, and volunteer.
5. Run the supply-first workflow from creation through delivery.
6. Demonstrate that a second reservation is rejected.
7. Run or explain the demand-first workflow.
8. Show a meaningful multi-table delivery-history join.
9. Show constraints, indexes, foreign keys, and an aggregate query.
10. Keep backup demo records and avoid relying on live external services.

## Impact measurement

Do not invent impact values. Calculate metrics from database data, such as:

- total donations;
- completed donations;
- quantity of food delivered;
- fulfilled and unmet requests;
- successful deliveries;
- completed deliveries per volunteer;
- active donors, NGOs, and volunteers;
- donation completion rate;
- delivery completion rate.

Example redistribution rate:

```text
delivered donations / total donations × 100
```

### SDG 2 — Zero Hunger

foodys supports SDG 2 by improving the coordination required to move existing surplus food to NGOs and recipient organizations:

```text
AVAILABLE FOOD → MATCHING → DELIVERY → RECIPIENT ORGANIZATION
```

The software coordinates redistribution; it must not claim unmeasured reductions in hunger.

### SDG 12 — Responsible Consumption and Production

foodys supports SDG 12 by offering a redistribution path for usable surplus that might otherwise be discarded:

```text
SURPLUS FOOD → MATCHING → REDISTRIBUTION
```

## Out of scope for the MVP

Do not prioritize:

- GPS, maps, or live volunteer tracking;
- route optimization;
- OAuth, MFA, email verification, CAPTCHA, or NGO verification;
- SMS, push notifications, or chat;
- payments;
- AI matching;
- QR or OTP delivery verification;
- advanced admin dashboards;
- a mobile application;
- complex cloud infrastructure.

Possible future enhancements include latitude/longitude matching, OpenStreetMap/Leaflet, automatic matching suggestions, multilingual support, notification services, QR confirmation, and richer impact analytics. They should be considered only after the local MVP is reliable.

## Deployment principle

Localhost functionality comes first. Deployment begins only after the database, API, frontend integration, security baseline, and complete workflows work locally.

Before deployment, confirm:

- environment variables are documented;
- secrets are absent from Git;
- CORS uses a configurable frontend origin;
- the frontend API base URL is configurable;
- no API URL is duplicated across components;
- schema/seed or migration instructions are repeatable;
- production credentials differ from local credentials.

Deployment must not require redesigning the application.

## Definition of done

A feature is complete only when:

- its database impact is implemented and documented;
- relevant constraints and relationships remain valid;
- the FastAPI endpoint works;
- validation, authentication, role, and ownership checks work;
- the frontend uses the real endpoint when applicable;
- a success case and failure case pass;
- related workflows remain functional;
- no secret or unrelated generated file is included.

The MVP is complete when donor, NGO, and volunteer login works; both matching directions work; matches and deliveries are created consistently; volunteers can complete only valid transitions; duplicate reservation and acceptance are prevented; completed delivery updates all related records; joins and aggregates demonstrate the relational model; and the full workflow can be demonstrated end to end.

## Project reference files

- `README.md`: product scope, architecture, data model, setup, testing, collaboration, and demo reference.
- `.env.example`: safe configuration names and placeholders; never place real secrets in it.

## Final principle

foodys should remain:

```text
small enough to finish
simple enough to explain
database-heavy enough to demonstrate DBMS
complete enough to demo end to end
```

When choosing between a complicated solution and a straightforward relational solution, choose the straightforward relational solution.
