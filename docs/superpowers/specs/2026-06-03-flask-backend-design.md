# Profriends Inc — Flask Backend Design

**Date:** 2026-06-03
**Author:** Lawrence (Flask Backend / Python)
**Subject:** Information Management — Final Project
**Team:** Izy Basco (Database & SQL), Lawrence (Flask Backend / Python), Andre Montana (Frontend), Kezia Villegas (Backend integration), Paul Correo (Documentation & Integration)

---

## 1. Purpose

The frontend (`uiux.txt`, by Andre) is a complete single-page UI but runs entirely on
**in-memory JavaScript arrays** — data resets on every page refresh and nothing is saved.

This backend makes the app **real**: a Flask + Python server that connects to the existing
MySQL database (`profriends_inc`) and exposes a REST API so the frontend reads from and
writes to a real database. The result is a working, persistent application the whole team
can run locally.

The subject focus is **Database & SQL**, so the backend deliberately uses **raw, visible,
parameterized SQL** (no ORM) — the actual queries stay readable in the code.

## 2. Scope

**In scope — Full CRUD on the 6 existing tables:**
`buyer`, `beneficiary`, `employment`, `household`, `loan`, `spouse`.

**Also in scope:**
- Session-based login (admin + buyer roles) with **no new database table**.
- A reports endpoint exposing Izy's 10 saved SQL queries
  (`database/profriends_inc_queries.sql`) for the Inventory/Reports page.
- Wiring a **copy** of the frontend to call the API.

**Out of scope (stays frontend-only mock for now):**
`users`, `properties`, `payments` — the frontend uses these but the database has no matching
tables. Adding them would mean changing Izy's schema, which we are not doing in this phase.
If the team later wants these persisted, that is a separate follow-up (and Izy is consulted first).

## 3. Constraints & ground rules

- **Do not modify teammates' contributions** unless necessary, and flag first if needed.
  - `uiux.txt` (Andre) — left **untouched**. We copy it to `backend/templates/index.html`
    and wire the copy.
  - `database/profriends_inc.sql` and `profriends_inc_queries.sql` (Izy) — left **untouched**;
    the reports endpoint reads the queries, it does not change the schema.
- **Git:** commits authored by Lawrence only (username `lauurnce`,
  email `paneslawrence8@gmail.com`). **No AI co-author trailer** on any commit.
- **Push after every change**, with descriptive commit messages teammates can understand.
- **Clean, commented code** — every file and non-obvious block has comments explaining what
  it does and why, so the team can read it.

## 4. Architecture — modular Flask blueprints

```
IM_G10/
├── uiux.txt                       # Andre's original — UNTOUCHED
├── database/
│   ├── profriends_inc.sql         # Izy's dump — UNTOUCHED
│   └── profriends_inc_queries.sql # Izy's queries — read by reports endpoint
├── backend/                       # Lawrence's work (new)
│   ├── app.py                     # entry point + Flask app factory; registers blueprints
│   ├── db.py                      # MySQL connection helper (mysql-connector-python)
│   ├── config.py                  # loads settings from .env
│   ├── requirements.txt           # Flask, mysql-connector-python, python-dotenv
│   ├── .env.example               # template teammates copy to .env (no real secrets)
│   ├── README.md                  # setup + run instructions for the team
│   ├── test_api.py                # plain-Python smoke test (no framework)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                # login / logout / session ("who am I")
│   │   ├── buyers.py              # CRUD  /api/buyers
│   │   ├── beneficiaries.py       # CRUD  /api/beneficiaries
│   │   ├── employment.py          # CRUD  /api/employment
│   │   ├── household.py           # CRUD  /api/household
│   │   ├── loans.py               # CRUD  /api/loans
│   │   ├── spouse.py              # CRUD  /api/spouse
│   │   └── reports.py             # GET   /api/reports/q1..q10 (Izy's queries)
│   └── templates/
│       └── index.html             # COPY of uiux.txt, wired to call the API
```

`.env` is gitignored (holds the DB password). `.env.example` is committed so teammates know
what to fill in.

Each route file has one clear purpose and can be read independently — this keeps files short
and reduces merge conflicts across the 5-person team.

## 5. Data flow

```
Browser (index.html)
   │  fetch('/api/buyers')  ──GET──►  Flask route (routes/buyers.py)
   │                                     │ db.py → open connection
   │                                     │ cur.execute("SELECT ... FROM buyer")
   │                                     ▼
   │                                  MySQL profriends_inc
   │  ◄──JSON { ok:true, data:[...] }────┘
   ▼
JS feeds result into Andre's existing render functions (refreshClientTable, etc.)
```

- Andre's render functions are reused as-is. Only the **data source** changes: instead of
  reading the in-memory `buyers = [...]` array, the JS does `await fetch('/api/buyers')` and
  passes the result to the same render code.
- Writes (add/edit/delete) → `fetch` with POST/PUT/DELETE → Flask runs parameterized SQL →
  returns the updated row or status → JS re-renders.

## 6. API endpoints

### CRUD (each of the 6 tables, keyed by its primary key)

Buyers shown as the template; the other five follow the same shape.

| Method | Path                 | SQL                                              | Returns        |
|--------|----------------------|--------------------------------------------------|----------------|
| GET    | `/api/buyers`        | `SELECT * FROM buyer`                             | list of rows   |
| GET    | `/api/buyers/<id>`   | `SELECT * FROM buyer WHERE BuyerID=%s`            | one row        |
| POST   | `/api/buyers`        | `INSERT INTO buyer (...) VALUES (%s, ...)`        | created row    |
| PUT    | `/api/buyers/<id>`   | `UPDATE buyer SET ... WHERE BuyerID=%s`           | updated row    |
| DELETE | `/api/buyers/<id>`   | `DELETE FROM buyer WHERE BuyerID=%s`              | `{ ok: true }` |

Resources and their primary keys:
- `buyers` → `buyer` (PK `BuyerID`)
- `beneficiaries` → `beneficiary` (composite PK `BeneficiaryID` + `BenF_Name`)
- `employment` → `employment` (PK `EmploymentID`)
- `household` → `household` (PK `HouseholdID`)
- `loans` → `loan` (PK `LoanID`)
- `spouse` → `spouse` (PK `BuyerID`)

### Auth (`routes/auth.py`)

| Method | Path          | Behavior                                                                 |
|--------|---------------|--------------------------------------------------------------------------|
| POST   | `/api/login`  | Admin → check hardcoded credentials. Buyer → check `BuyerID` + last name against the `buyer` table. On success, set Flask session (role + id). |
| POST   | `/api/logout` | Clear the session.                                                       |
| GET    | `/api/me`     | Return the current logged-in role/identity (used by the UI on load).     |

Admin credentials live in `.env` (e.g. `ADMIN_USER`, `ADMIN_PASS`) — not hardcoded in source,
not committed.

### Reports (`routes/reports.py`)

| Method | Path                      | Behavior                                                        |
|--------|---------------------------|----------------------------------------------------------------|
| GET    | `/api/reports/q1` … `q10` | Run each of Izy's 10 saved queries, return rows for the Reports page. |

## 7. Error handling

Consistent JSON shape so the frontend handles every case identically:

```json
{ "ok": true,  "data": [ ... ] }          // success
{ "ok": false, "error": "Buyer not found" } // error
```

| Situation                              | HTTP | Message style                                              |
|----------------------------------------|------|-----------------------------------------------------------|
| DB connection fails                    | 503  | "Database unavailable — check .env and that MySQL is running" |
| Missing/invalid fields on POST/PUT     | 400  | names the missing field                                   |
| Record not found                       | 404  | plain message                                             |
| Duplicate PK / foreign-key violation   | 409  | plain-English reason (not a raw MySQL trace)              |
| Not logged in                          | 401  | "Login required"                                          |
| Unexpected error                       | 500  | generic message to browser; full error logged to console |

- Every `cur.execute` is wrapped so a SQL error returns clean JSON instead of crashing the server.
- Connections are always closed in a `finally` block.
- Writes use parameterized queries (`%s`) — no SQL injection.

## 8. How the team runs it (also in backend/README.md)

```
1. cd backend
2. python -m venv venv  &&  venv\Scripts\activate     (Windows)
3. pip install -r requirements.txt
4. copy .env.example .env    → fill in your MySQL password
5. Make sure database/profriends_inc.sql is imported into MySQL
6. python app.py
7. Open http://localhost:5000
```

## 9. Testing

- **Smoke test** (`backend/test_api.py`): plain Python, no framework. Hits login,
  GET/POST/PUT/DELETE on one buyer, and one report; prints PASS/FAIL per endpoint.
  Teammates run `python test_api.py`.
- **Manual**: log in as admin → add/edit/delete a buyer in the UI → refresh → data persists
  (proves the DB write worked). Log in as buyer → only the buyer views are shown.
- Each endpoint is verified against the real MySQL database before being marked done.

## 10. Out of scope / future work

- Persisting `users`, `properties`, `payments` (needs new tables → consult Izy first).
- Password hashing / real account signup (current login is session-based, demo-grade).
- Deployment beyond localhost (project requirement is local).
