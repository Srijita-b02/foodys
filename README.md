# Foodys

Foodys is a small database-driven food redistribution platform built for an academic DBMS project. It connects food donors with NGO members so usable surplus food can reach people instead of being wasted.

The project primarily supports **SDG 2 — Zero Hunger** and also contributes to **SDG 12 — Responsible Consumption and Production**.

## What the system does

Foodys supports two matching directions:

```text
Donor posts available food
        ↓
NGO member reserves it
        ↓
Match and delivery are created
```

```text
NGO member posts a food request
        ↓
Donor responds using an available donation
        ↓
Match and delivery are created
```

The assigned NGO member handles pickup and updates the delivery until it is completed.

## Roles

The application has two roles.

### Donor

A donor may be an individual or a restaurant. A donor can:

- register and log in;
- create a donation;
- view, edit, or cancel their own available donations;
- browse open food requests;
- respond to a request using one of their donations;
- view their matches.

### NGO member

Each NGO member has their own user account. A separate organizations table or organization ID is not used in this MVP. `organization_name` is stored only as profile information.

An NGO member can:

- register and log in;
- browse available donations;
- reserve available food;
- create food requests;
- view, edit, or cancel their own open requests;
- see other open requests to avoid duplicate requests;
- view their matches;
- view and update only deliveries assigned to them.

There is no separate volunteer role. The NGO member assigned to a match is also responsible for pickup and delivery updates.

## Technology stack

| Part | Technology |
| --- | --- |
| Frontend | React and Vite |
| Backend | FastAPI and Python |
| Database | PostgreSQL |
| Database access | SQLAlchemy and parameterized SQL |
| Validation | Pydantic |
| Styling | CSS |
| Version control | Git and GitHub |

## Project structure

```text
resQfood/
├── backend/
│   ├── database/       # Database connection and update scripts
│   ├── models/         # SQLAlchemy tables
│   ├── routers/        # FastAPI endpoints
│   ├── schemas/        # Pydantic request and response models
│   ├── tests/          # Backend tests
│   ├── .env.example
│   ├── init_db.py
│   ├── main.py
│   └── requirements.txt
├── database/
│   └── schema.sql      # Complete PostgreSQL schema for a fresh database
├── frontend/
│   └── src/
└── README.md
```

## Database design

The project uses five main relational tables.

### `users`

Stores donor and NGO-member accounts.

Important fields:

```text
id, name, email, password_hash, phone, role,
donor_type, organization_name, location,
created_at, updated_at
```

- `email` is unique.
- Passwords are stored only as hashes.
- `role` is either `donor` or `ngo`.
- `donor_type` is used only for donors.
- `organization_name` is profile text used only for NGO members.

### `donations`

Stores food offered by donors.

```text
id, donor_id, food_name, description, category,
quantity, unit, prepared_at, expiry_time,
pickup_address, status, created_at, updated_at
```

`donor_id` is a foreign key to `users.id`.

### `food_requests`

Stores food requirements posted by NGO members.

```text
id, ngo_id, food_name, category, quantity, unit,
description, location, needed_before, status,
created_at, updated_at
```

`ngo_id` is a foreign key to the NGO member's `users.id`.

### `matches`

Connects a donation to an NGO member and, when applicable, a food request.

```text
id, donation_id, request_id, ngo_id,
allocated_quantity, status, created_at, updated_at
```

`request_id` is nullable because an NGO member may directly reserve an available donation without first creating a request. Partial quantities can be matched.

### `deliveries`

Stores delivery ownership and progress.

```text
id, match_id, assigned_ngo_member_id, status,
assigned_at, pickup_time, delivery_time,
created_at, updated_at
```

- One match has one delivery.
- `assigned_ngo_member_id` references `users.id`.
- Only the assigned NGO member can view or update that delivery.

## Status flow

### Donation

```text
available → reserved/matched → assigned → picked_up
          → in_transit → delivered
```

A donation may also become `cancelled` or `expired` when allowed.

### Food request

```text
open → matched → fulfilled
```

A request may also become `cancelled` or `expired` when allowed.

### Delivery

```text
assigned → picked_up → in_transit → delivered
```

Skipped or backward delivery transitions are rejected.

When a delivery becomes `delivered`, the backend completes the related match and updates the donation. If the full request quantity has been delivered, the food request becomes `fulfilled`.

## Transactions and concurrency

Matching is handled as a database transaction.

When an NGO member reserves food, the backend:

1. locks and checks the donation;
2. checks the remaining quantity;
3. creates a match;
4. creates the assigned delivery;
5. updates the donation status;
6. commits all changes together.

When a donor responds to a request, the backend also locks the donation and request, validates the remaining quantities, creates the match and delivery, and updates both statuses in one transaction.

If any step fails, the transaction is rolled back. Row locking and status checks prevent duplicate or excessive reservations.

## Main API routes

The FastAPI documentation is available at `http://localhost:8000/docs` while the backend is running.

| Area | Endpoints |
| --- | --- |
| Authentication | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Donations | `POST /donations`, `GET /donations`, `GET /donations/my`, `GET/PUT/DELETE /donations/{id}` |
| Requests | `POST /requests`, `GET /requests`, `GET /requests/my`, `GET/PUT/DELETE /requests/{id}` |
| Matching | `POST /matches/reserve`, `POST /matches/respond`, `GET /matches`, `GET /matches/{id}` |
| Deliveries | `GET /deliveries/my`, `GET /deliveries/{id}`, `PATCH /deliveries/{id}/status` |

Role and ownership checks are performed by FastAPI. Hiding a button in React is not treated as authorization.

## Local setup

### Requirements

- Python 3.11 or newer
- Node.js and npm
- PostgreSQL
- Git

### 1. Create the PostgreSQL database

Create a local database, for example:

```sql
CREATE DATABASE resqfood;
```

For a fresh database, run `database/schema.sql` using pgAdmin or `psql`.

### 2. Configure the backend

From the project root:

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `backend/.env` with your local values:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/resqfood
SECRET_KEY=replace_with_a_long_random_development_secret
FRONTEND_ORIGIN=http://localhost:5173
```

Never commit `.env`.

If the tables were not created using `schema.sql`, initialize missing tables with:

```powershell
python init_db.py
```

Start the backend:

```powershell
uvicorn main:app --reload
```

Backend: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

### 3. Start the frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

## Tests

Run backend tests from the `backend` folder with the virtual environment active:

```powershell
python -m unittest discover -s tests -v
```

Run frontend checks from the `frontend` folder:

```powershell
npm run lint
npm run build
```

Tests should cover successful operations and important failures, especially:

- invalid login and role access;
- invalid quantities and dates;
- editing another user's record;
- duplicate reservation attempts;
- matching more than the remaining quantity;
- invalid delivery transitions;
- rollback when part of a transaction fails.

## Current development status

Completed backend work includes:

- registration and login with hashed passwords;
- donor and NGO authorization;
- donation CRUD and filtering;
- food-request CRUD and filtering;
- supply-first and demand-first matching;
- partial quantity matching;
- transactional match and delivery creation;
- assigned NGO-member delivery access;
- delivery state transitions and completion updates;
- PostgreSQL constraints, foreign keys, indexes, and schema documentation;
- backend automated tests.

The React pages and styling exist, but several screens still contain temporary sample data. Connecting the frontend to the FastAPI endpoints is the main remaining task.

## Two-person work division

### Person A

- users and authentication;
- donations and donor workflow;
- donation filtering and expiry;
- aggregate statistics.

### Person B

- food requests;
- matching and reservation transactions;
- deliveries and NGO-member pickup workflow;
- concurrency protection and JOIN queries.

Both members should understand the full database design and be able to explain the main transaction, constraints, and relationships during the demonstration.

## DBMS concepts demonstrated

- primary and foreign keys;
- `NOT NULL`, `UNIQUE`, and `CHECK` constraints;
- referential integrity;
- useful indexes;
- multi-table JOINs;
- aggregate queries;
- ACID transactions;
- commit and rollback;
- row locking and concurrency-safe reservations;
- database-side filtering;
- consistent delivery states;
- role-based data access.

## Security scope

This is an academic MVP. It includes the required basics:

- password hashing;
- no password hashes in API responses;
- secrets stored in `.env`;
- backend role and ownership checks;
- SQLAlchemy or parameterized SQL;
- only necessary user information.

OAuth, MFA, email verification, CAPTCHA, payment processing, GPS tracking, and complex production infrastructure are outside the MVP scope.

## Expected outcome

The completed application should demonstrate an end-to-end flow in which a donor posts food or answers a request, an NGO member accepts responsibility for the food, and the database reliably records matching, pickup, transport, and delivery.

Useful impact values should be calculated from database records rather than invented. Examples include completed donations, quantity delivered, fulfilled requests, successful deliveries, active donors, and active NGO members.
