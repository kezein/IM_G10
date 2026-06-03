# Flask Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Flask + Python backend that connects the existing frontend to the MySQL `profriends_inc` database, exposing full CRUD for the 6 tables plus session login and a reports endpoint.

**Architecture:** Modular Flask blueprints. `app.py` is the entry point/app factory; `db.py` holds the MySQL connection + query helpers; `config.py` loads `.env`. One blueprint per resource under `routes/`. Raw parameterized SQL via `mysql-connector-python` (no ORM — SQL stays visible). A copy of `uiux.txt` is served as `templates/index.html` and wired to the API; the original `uiux.txt` is never modified.

**Tech Stack:** Python 3, Flask, mysql-connector-python, python-dotenv. MySQL 8 (`profriends_inc`). Vanilla JS frontend (fetch API).

---

## File Structure

```
backend/
  app.py                # entry point + app factory, JSON error handlers, serves index.html
  config.py             # loads .env: DB creds, admin creds, secret key
  db.py                 # get_connection(), query_all(), query_one(), execute()
  requirements.txt      # Flask, mysql-connector-python, python-dotenv
  .env.example          # template (no secrets) -> teammates copy to .env
  README.md             # setup + run instructions
  test_api.py           # plain-Python smoke test (no framework)
  routes/
    __init__.py         # empty (marks package)
    auth.py             # POST /api/login, POST /api/logout, GET /api/me
    buyers.py           # CRUD /api/buyers
    spouse.py           # CRUD /api/spouse
    beneficiaries.py    # CRUD /api/beneficiaries
    employment.py       # CRUD /api/employment
    household.py        # CRUD /api/household
    loans.py            # CRUD /api/loans
    reports.py          # GET /api/reports/q1..q10
  templates/
    index.html          # COPY of uiux.txt, wired to the API
.gitignore              # ignore venv, .env, __pycache__
```

**Conventions used by every endpoint:**
- Success: HTTP 200, body `{ "ok": true, "data": <result> }`
- Error: body `{ "ok": false, "error": "<message>" }` with an appropriate HTTP status
- All SQL uses `%s` placeholders (parameterized) — never string formatting.
- Every file is commented for teammates.

---

## Task 1: Backend scaffold + DB connection + health check

**Files:**
- Create: `.gitignore`
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/config.py`
- Create: `backend/db.py`
- Create: `backend/routes/__init__.py`
- Create: `backend/app.py`
- Create: `backend/README.md`

- [ ] **Step 1: Create `.gitignore`** (repo root)

```gitignore
# Python
__pycache__/
*.pyc
backend/venv/
venv/

# Secrets — never commit real DB passwords
backend/.env
.env
```

- [ ] **Step 2: Create `backend/requirements.txt`**

```
Flask==3.0.3
mysql-connector-python==9.0.0
python-dotenv==1.0.1
```

- [ ] **Step 3: Create `backend/.env.example`** (committed template; real `.env` is gitignored)

```
# Copy this file to ".env" and fill in your local MySQL password.
# Each teammate has their own .env; it is never committed.

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=profriends_inc

# Admin login for the portal (demo credentials, change if you like)
ADMIN_USER=admin
ADMIN_PASS=admin123

# Flask session signing key (any random string)
SECRET_KEY=change-me-to-any-random-string
```

- [ ] **Step 4: Create `backend/config.py`**

```python
"""
config.py
Loads all settings from the .env file so no secret (DB password, admin
password, session key) is ever hard-coded or committed to git.

Each teammate copies .env.example -> .env and fills in their own values.
"""
import os
from dotenv import load_dotenv

# Read the .env file in this folder into environment variables.
load_dotenv()


class Config:
    # --- MySQL connection settings ---
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "profriends_inc")

    # --- Portal admin login (buyers log in differently, see auth.py) ---
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

    # --- Flask session signing key ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-key")
```

- [ ] **Step 5: Create `backend/db.py`**

```python
"""
db.py
One place for talking to MySQL. Other files import these helpers instead of
opening their own connections. Every helper opens a connection, runs the SQL,
and always closes the connection (even if an error happens).

All SQL passed in uses %s placeholders so values are sent separately from the
query text -> this prevents SQL injection.
"""
import mysql.connector
from mysql.connector import Error
from config import Config


def get_connection():
    """Open and return a new MySQL connection using the .env settings."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )


def query_all(sql, params=None):
    """Run a SELECT and return ALL rows as a list of dicts."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)   # dictionary=True -> rows come back as dicts
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        conn.close()


def query_one(sql, params=None):
    """Run a SELECT and return the FIRST row as a dict, or None if no rows."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchone()
    finally:
        conn.close()


def execute(sql, params=None):
    """
    Run an INSERT / UPDATE / DELETE. Commits the change and returns how many
    rows were affected. Raises mysql.connector.Error on DB problems so the
    route can turn it into a clean JSON error.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
```

- [ ] **Step 6: Create `backend/routes/__init__.py`** (empty file — marks `routes` as a package)

```python
# This file is intentionally empty. It makes Python treat "routes" as a package
# so we can do "from routes.buyers import buyers_bp".
```

- [ ] **Step 7: Create `backend/app.py`**

```python
"""
app.py
Entry point. Builds the Flask app, registers every blueprint (one per
resource), serves the frontend, and defines shared JSON error responses so
the frontend always receives the same { ok, error } shape.

Run with:  python app.py   ->  http://localhost:5000
"""
from flask import Flask, jsonify, render_template
from mysql.connector import Error as MySQLError

from config import Config


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY

    # --- Register blueprints (added in later tasks) ---
    from routes.auth import auth_bp
    from routes.buyers import buyers_bp
    from routes.spouse import spouse_bp
    from routes.beneficiaries import beneficiaries_bp
    from routes.employment import employment_bp
    from routes.household import household_bp
    from routes.loans import loans_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(buyers_bp)
    app.register_blueprint(spouse_bp)
    app.register_blueprint(beneficiaries_bp)
    app.register_blueprint(employment_bp)
    app.register_blueprint(household_bp)
    app.register_blueprint(loans_bp)
    app.register_blueprint(reports_bp)

    # --- Frontend: serve the wired copy of Andre's UI ---
    @app.route("/")
    def index():
        return render_template("index.html")

    # --- Health check: confirms the server AND the database are reachable ---
    @app.route("/api/health")
    def health():
        from db import query_one
        try:
            query_one("SELECT 1 AS ok")
            return jsonify(ok=True, data={"db": "connected"})
        except MySQLError as e:
            return jsonify(ok=False, error=f"Database unavailable: {e}"), 503

    # --- Shared error handlers: every error becomes clean JSON ---
    @app.errorhandler(404)
    def not_found(_):
        return jsonify(ok=False, error="Not found"), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify(ok=False, error="Unexpected server error"), 500

    return app


if __name__ == "__main__":
    # debug=True auto-reloads on code changes while developing.
    create_app().run(host="0.0.0.0", port=5000, debug=True)
```

> NOTE: `app.py` imports blueprints that are created in Tasks 2-9. Until those exist, the app will not start. That is expected — Step 8 below verifies only after the blueprints exist is misleading, so for THIS task we temporarily comment out the blueprint imports/registrations to verify the scaffold + DB. Re-enable them as each is added. (The implementing engineer: comment the 8 `from routes...` import lines and the 8 `register_blueprint` lines, verify health, then uncomment them one per task as you create each blueprint.)

- [ ] **Step 8: Create `backend/README.md`**

```markdown
# Profriends Inc — Backend (Flask)

Connects the frontend to the MySQL `profriends_inc` database.

## Run it locally

1. `cd backend`
2. `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (Mac/Linux)
4. `pip install -r requirements.txt`
5. `copy .env.example .env` (Windows) / `cp .env.example .env` (Mac/Linux), then edit `.env` and put your MySQL password
6. Make sure `database/profriends_inc.sql` is imported into MySQL
7. `python app.py`
8. Open http://localhost:5000

## Check it works
- Open http://localhost:5000/api/health -> should show `{"ok": true, "data": {"db": "connected"}}`
- Run the smoke test: `python test_api.py`

## API summary
- `POST /api/login`, `POST /api/logout`, `GET /api/me`
- CRUD: `/api/buyers`, `/api/spouse`, `/api/beneficiaries`, `/api/employment`, `/api/household`, `/api/loans`
- Reports (Izy's queries): `GET /api/reports/q1` .. `q10`
```

- [ ] **Step 9: Install deps and verify health** (blueprint imports commented out per Step 7 note)

Run:
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Edit `.env`, set `DB_PASSWORD`. Then:
```
python app.py
```
In a browser/another terminal, hit `http://localhost:5000/api/health`.
Expected: `{"ok": true, "data": {"db": "connected"}}`. If 503, fix `.env` / start MySQL.

- [ ] **Step 10: Commit**

```bash
git add .gitignore backend/
git commit -m "feat(backend): scaffold Flask app, config, db helpers, health check

Adds the backend skeleton: app factory, .env-based config, MySQL connection
helpers (query_all/query_one/execute), health-check endpoint, requirements,
.env.example and run instructions. SQL helpers use parameterized queries.

How to run: see backend/README.md."
git push
```

---

## Task 2: Auth blueprint (login / logout / me)

**Files:**
- Create: `backend/routes/auth.py`
- Modify: `backend/app.py` (uncomment the auth import + register line)

- [ ] **Step 1: Create `backend/routes/auth.py`**

```python
"""
auth.py
Login for two kinds of users:
  - Admin: matches the ADMIN_USER / ADMIN_PASS from .env.
  - Buyer: matches a BuyerID + the buyer's last name found in the buyer table.
On success we store who they are in the Flask session (a signed cookie).

No new database table is needed. Buyer "password" = last word of BuyerName
(simple/demo-grade, agreed in the design spec).
"""
from flask import Blueprint, request, jsonify, session
from config import Config
from db import query_one

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    role = body.get("role")          # "admin" or "buyer"
    username = body.get("username")  # admin user, or BuyerID for buyers
    password = body.get("password")  # admin pass, or last name for buyers

    if not role or not username or not password:
        return jsonify(ok=False, error="role, username and password are required"), 400

    if role == "admin":
        if username == Config.ADMIN_USER and password == Config.ADMIN_PASS:
            session["role"] = "admin"
            session["user_id"] = "admin"
            return jsonify(ok=True, data={"role": "admin", "name": "Administrator"})
        return jsonify(ok=False, error="Invalid admin credentials"), 401

    if role == "buyer":
        # Look the buyer up by ID, then check the last name matches.
        buyer = query_one(
            "SELECT BuyerID, BuyerName FROM buyer WHERE BuyerID = %s",
            (username,),
        )
        if buyer is None:
            return jsonify(ok=False, error="Buyer ID not found"), 401
        last_name = buyer["BuyerName"].strip().split()[-1].lower()
        if password.strip().lower() == last_name:
            session["role"] = "buyer"
            session["user_id"] = buyer["BuyerID"]
            return jsonify(ok=True, data={"role": "buyer", "name": buyer["BuyerName"]})
        return jsonify(ok=False, error="Invalid buyer credentials"), 401

    return jsonify(ok=False, error="Unknown role"), 400


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify(ok=True, data={"loggedOut": True})


@auth_bp.route("/api/me", methods=["GET"])
def me():
    """Tell the frontend who (if anyone) is logged in."""
    if "role" not in session:
        return jsonify(ok=False, error="Not logged in"), 401
    return jsonify(ok=True, data={"role": session["role"], "user_id": session["user_id"]})
```

- [ ] **Step 2: In `backend/app.py`, ensure auth is registered** (uncomment if you commented it in Task 1)

The lines `from routes.auth import auth_bp` and `app.register_blueprint(auth_bp)` must be active.

- [ ] **Step 3: Verify** — restart `python app.py`, then:

```bash
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d "{\"role\":\"admin\",\"username\":\"admin\",\"password\":\"admin123\"}"
```
Expected: `{"ok": true, "data": {"role": "admin", "name": "Administrator"}}`

Buyer test (James Velasco, B-2023-001, last name "Velasco"):
```bash
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d "{\"role\":\"buyer\",\"username\":\"B-2023-001\",\"password\":\"Velasco\"}"
```
Expected: `ok: true`, name "James Velasco".

- [ ] **Step 4: Commit**

```bash
git add backend/routes/auth.py backend/app.py
git commit -m "feat(backend): add session login for admin and buyer roles

POST /api/login (admin via .env creds; buyer via BuyerID + last name checked
against the buyer table), POST /api/logout, GET /api/me. Uses Flask session;
no new DB table needed."
git push
```

---

## Task 3: Buyers CRUD (the template all other resources follow)

**Files:**
- Create: `backend/routes/buyers.py`
- Modify: `backend/app.py` (ensure buyers import + register active)

- [ ] **Step 1: Create `backend/routes/buyers.py`**

```python
"""
buyers.py
CRUD for the `buyer` table. Primary key: BuyerID (a string like 'B-2023-001').

Endpoints:
  GET    /api/buyers        -> all buyers
  GET    /api/buyers/<id>   -> one buyer
  POST   /api/buyers        -> create
  PUT    /api/buyers/<id>   -> update
  DELETE /api/buyers/<id>   -> delete
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

buyers_bp = Blueprint("buyers", __name__)

# The exact columns of the buyer table, in order. Used to build SQL safely.
COLUMNS = [
    "BuyerID", "BuyerName", "Birthdate", "Birthplace", "GovID", "TIN",
    "Gender", "Civil_Status", "Address", "Citizenship", "Gross_MonthlyIncome",
    "Tel_Num", "Mobile_Num", "Personal_Email", "Work_Email",
    "Account_Type", "Bank_Name",
]
# Columns that must be provided when creating a buyer (match NOT NULL in schema).
REQUIRED = [
    "BuyerID", "BuyerName", "Birthdate", "Birthplace", "GovID", "TIN",
    "Gender", "Civil_Status", "Address", "Citizenship", "Gross_MonthlyIncome",
    "Mobile_Num", "Personal_Email", "Account_Type", "Bank_Name",
]


@buyers_bp.route("/api/buyers", methods=["GET"])
def list_buyers():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM buyer"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@buyers_bp.route("/api/buyers/<buyer_id>", methods=["GET"])
def get_buyer(buyer_id):
    try:
        row = query_one("SELECT * FROM buyer WHERE BuyerID = %s", (buyer_id,))
        if row is None:
            return jsonify(ok=False, error="Buyer not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@buyers_bp.route("/api/buyers", methods=["POST"])
def create_buyer():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if not body.get(c)]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400

    # Build "INSERT INTO buyer (col, col, ...) VALUES (%s, %s, ...)" safely.
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO buyer ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM buyer WHERE BuyerID = %s", (body["BuyerID"],)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Buyer '{body['BuyerID']}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@buyers_bp.route("/api/buyers/<buyer_id>", methods=["PUT"])
def update_buyer(buyer_id):
    body = request.get_json(silent=True) or {}
    # Only update columns that were actually sent (never overwrite the PK).
    fields = [c for c in COLUMNS if c != "BuyerID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400

    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [buyer_id]
    try:
        affected = execute(f"UPDATE buyer SET {set_clause} WHERE BuyerID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Buyer not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM buyer WHERE BuyerID = %s", (buyer_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@buyers_bp.route("/api/buyers/<buyer_id>", methods=["DELETE"])
def delete_buyer(buyer_id):
    try:
        affected = execute("DELETE FROM buyer WHERE BuyerID = %s", (buyer_id,))
        if affected == 0:
            return jsonify(ok=False, error="Buyer not found"), 404
        return jsonify(ok=True, data={"deleted": buyer_id})
    except IntegrityError:
        return jsonify(ok=False, error="Cannot delete: other records reference this buyer"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
```

- [ ] **Step 2: Ensure `app.py` registers `buyers_bp`** (uncomment import + register line).

- [ ] **Step 3: Verify** — restart server:

```bash
curl http://localhost:5000/api/buyers
```
Expected: `ok: true`, `data` = array of 5 buyers.
```bash
curl http://localhost:5000/api/buyers/B-2023-001
```
Expected: James Velasco's record.

- [ ] **Step 4: Commit**

```bash
git add backend/routes/buyers.py backend/app.py
git commit -m "feat(backend): add buyer CRUD API

GET list/one, POST create (validates required fields, 409 on duplicate ID),
PUT partial update, DELETE (409 if referenced). Raw parameterized SQL on the
buyer table; this file is the template the other resource endpoints follow."
git push
```

---

## Task 4: Spouse CRUD

**Files:**
- Create: `backend/routes/spouse.py`
- Modify: `backend/app.py` (ensure spouse import + register active)

- [ ] **Step 1: Create `backend/routes/spouse.py`**

```python
"""
spouse.py
CRUD for the `spouse` table. Primary key: BuyerID (1 spouse per buyer).
Most columns are optional (a single buyer has no spouse).
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

spouse_bp = Blueprint("spouse", __name__)

COLUMNS = [
    "BuyerID", "Sps_Name", "Sps_Bdate", "Sps_Bplace", "Sps_Citizenship",
    "Sps_GovID", "Sps_TIN", "Sps_TelNum", "Sps_EmailAdd", "Sps_MobNum",
    "Sps_GrossMonthlyIncome",
]
REQUIRED = ["BuyerID"]   # only the key is mandatory; spouse details are optional


@spouse_bp.route("/api/spouse", methods=["GET"])
def list_spouse():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM spouse"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@spouse_bp.route("/api/spouse/<buyer_id>", methods=["GET"])
def get_spouse(buyer_id):
    try:
        row = query_one("SELECT * FROM spouse WHERE BuyerID = %s", (buyer_id,))
        if row is None:
            return jsonify(ok=False, error="Spouse not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@spouse_bp.route("/api/spouse", methods=["POST"])
def create_spouse():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if not body.get(c)]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400

    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO spouse ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM spouse WHERE BuyerID = %s", (body["BuyerID"],)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Spouse for buyer '{body['BuyerID']}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@spouse_bp.route("/api/spouse/<buyer_id>", methods=["PUT"])
def update_spouse(buyer_id):
    body = request.get_json(silent=True) or {}
    fields = [c for c in COLUMNS if c != "BuyerID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [buyer_id]
    try:
        affected = execute(f"UPDATE spouse SET {set_clause} WHERE BuyerID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Spouse not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM spouse WHERE BuyerID = %s", (buyer_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@spouse_bp.route("/api/spouse/<buyer_id>", methods=["DELETE"])
def delete_spouse(buyer_id):
    try:
        affected = execute("DELETE FROM spouse WHERE BuyerID = %s", (buyer_id,))
        if affected == 0:
            return jsonify(ok=False, error="Spouse not found"), 404
        return jsonify(ok=True, data={"deleted": buyer_id})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
```

- [ ] **Step 2: Ensure `app.py` registers `spouse_bp`.**

- [ ] **Step 3: Verify** — `curl http://localhost:5000/api/spouse` -> `ok: true`, array including B-2023-001 (Levie Velasco) and NULL-filled singles.

- [ ] **Step 4: Commit**

```bash
git add backend/routes/spouse.py backend/app.py
git commit -m "feat(backend): add spouse CRUD API

GET list/one, POST, PUT, DELETE on the spouse table (keyed by BuyerID, 1:1
with buyer). Spouse details optional; only BuyerID required."
git push
```

---

## Task 5: Beneficiaries CRUD (composite primary key)

**Files:**
- Create: `backend/routes/beneficiaries.py`
- Modify: `backend/app.py`

> NOTE: `beneficiary` has a COMPOSITE primary key (`BeneficiaryID` + `BenF_Name`),
> so single-id routes take both parts via query string for GET-one/PUT/DELETE.

- [ ] **Step 1: Create `backend/routes/beneficiaries.py`**

```python
"""
beneficiaries.py
CRUD for the `beneficiary` table.
Composite primary key: (BeneficiaryID, BenF_Name) -> one ID can list several
named beneficiaries. Single-record routes need BOTH parts, passed as query
params, e.g. /api/beneficiaries/one?id=BEN-001&name=Jemie%20Velasco
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

beneficiaries_bp = Blueprint("beneficiaries", __name__)

COLUMNS = ["BeneficiaryID", "BuyerID", "BenF_Name", "BenF_Bdate", "Relationship"]
REQUIRED = ["BeneficiaryID", "BenF_Name"]   # the two PK parts


@beneficiaries_bp.route("/api/beneficiaries", methods=["GET"])
def list_beneficiaries():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM beneficiary"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@beneficiaries_bp.route("/api/beneficiaries/one", methods=["GET"])
def get_beneficiary():
    ben_id = request.args.get("id")
    name = request.args.get("name")
    if not ben_id or not name:
        return jsonify(ok=False, error="id and name query params required"), 400
    try:
        row = query_one(
            "SELECT * FROM beneficiary WHERE BeneficiaryID = %s AND BenF_Name = %s",
            (ben_id, name),
        )
        if row is None:
            return jsonify(ok=False, error="Beneficiary not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@beneficiaries_bp.route("/api/beneficiaries", methods=["POST"])
def create_beneficiary():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if not body.get(c)]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO beneficiary ({col_list}) VALUES ({placeholders})", values)
        row = query_one(
            "SELECT * FROM beneficiary WHERE BeneficiaryID = %s AND BenF_Name = %s",
            (body["BeneficiaryID"], body["BenF_Name"]),
        )
        return jsonify(ok=True, data=row)
    except IntegrityError:
        return jsonify(ok=False, error="That beneficiary (ID + name) already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@beneficiaries_bp.route("/api/beneficiaries/one", methods=["PUT"])
def update_beneficiary():
    ben_id = request.args.get("id")
    name = request.args.get("name")
    if not ben_id or not name:
        return jsonify(ok=False, error="id and name query params required"), 400
    body = request.get_json(silent=True) or {}
    # Updatable columns = everything except the two PK parts.
    fields = [c for c in COLUMNS if c not in ("BeneficiaryID", "BenF_Name") and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [ben_id, name]
    try:
        affected = execute(
            f"UPDATE beneficiary SET {set_clause} WHERE BeneficiaryID = %s AND BenF_Name = %s",
            values,
        )
        if affected == 0:
            return jsonify(ok=False, error="Beneficiary not found"), 404
        row = query_one(
            "SELECT * FROM beneficiary WHERE BeneficiaryID = %s AND BenF_Name = %s",
            (ben_id, name),
        )
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@beneficiaries_bp.route("/api/beneficiaries/one", methods=["DELETE"])
def delete_beneficiary():
    ben_id = request.args.get("id")
    name = request.args.get("name")
    if not ben_id or not name:
        return jsonify(ok=False, error="id and name query params required"), 400
    try:
        affected = execute(
            "DELETE FROM beneficiary WHERE BeneficiaryID = %s AND BenF_Name = %s",
            (ben_id, name),
        )
        if affected == 0:
            return jsonify(ok=False, error="Beneficiary not found"), 404
        return jsonify(ok=True, data={"deleted": {"id": ben_id, "name": name}})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
```

- [ ] **Step 2: Ensure `app.py` registers `beneficiaries_bp`.**

- [ ] **Step 3: Verify** — `curl http://localhost:5000/api/beneficiaries` -> `ok: true`, 8 rows.

- [ ] **Step 4: Commit**

```bash
git add backend/routes/beneficiaries.py backend/app.py
git commit -m "feat(backend): add beneficiary CRUD API

GET list, GET/PUT/DELETE one (composite key BeneficiaryID + BenF_Name passed
as query params), POST create. Raw parameterized SQL on the beneficiary table."
git push
```

---

## Task 6: Employment CRUD

**Files:**
- Create: `backend/routes/employment.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Create `backend/routes/employment.py`**

```python
"""
employment.py
CRUD for the `employment` table. Primary key: EmploymentID.
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

employment_bp = Blueprint("employment", __name__)

COLUMNS = [
    "EmploymentID", "BuyerID", "Emp_Type", "Emp_Name", "Emp_Address",
    "Emp_TelNum", "Emp_EmailAdd", "Occupation", "Position", "Tenure",
    "Occupation_rank",
]
REQUIRED = [
    "EmploymentID", "BuyerID", "Emp_Type", "Emp_Name", "Emp_Address",
    "Occupation", "Position", "Tenure",
]


@employment_bp.route("/api/employment", methods=["GET"])
def list_employment():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM employment"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@employment_bp.route("/api/employment/<emp_id>", methods=["GET"])
def get_employment(emp_id):
    try:
        row = query_one("SELECT * FROM employment WHERE EmploymentID = %s", (emp_id,))
        if row is None:
            return jsonify(ok=False, error="Employment record not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@employment_bp.route("/api/employment", methods=["POST"])
def create_employment():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if body.get(c) in (None, "")]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO employment ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM employment WHERE EmploymentID = %s", (body["EmploymentID"],)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Employment '{body['EmploymentID']}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@employment_bp.route("/api/employment/<emp_id>", methods=["PUT"])
def update_employment(emp_id):
    body = request.get_json(silent=True) or {}
    fields = [c for c in COLUMNS if c != "EmploymentID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [emp_id]
    try:
        affected = execute(f"UPDATE employment SET {set_clause} WHERE EmploymentID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Employment record not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM employment WHERE EmploymentID = %s", (emp_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@employment_bp.route("/api/employment/<emp_id>", methods=["DELETE"])
def delete_employment(emp_id):
    try:
        affected = execute("DELETE FROM employment WHERE EmploymentID = %s", (emp_id,))
        if affected == 0:
            return jsonify(ok=False, error="Employment record not found"), 404
        return jsonify(ok=True, data={"deleted": emp_id})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
```

- [ ] **Step 2: Ensure `app.py` registers `employment_bp`.**

- [ ] **Step 3: Verify** — `curl http://localhost:5000/api/employment` -> 5 rows.

- [ ] **Step 4: Commit**

```bash
git add backend/routes/employment.py backend/app.py
git commit -m "feat(backend): add employment CRUD API

GET list/one, POST, PUT, DELETE on the employment table (keyed by
EmploymentID). Raw parameterized SQL, consistent { ok, data/error } shape."
git push
```

---

## Task 7: Household CRUD

**Files:**
- Create: `backend/routes/household.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Create `backend/routes/household.py`**

```python
"""
household.py
CRUD for the `household` table. Primary key: HouseholdID.
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

household_bp = Blueprint("household", __name__)

COLUMNS = [
    "HouseholdID", "BuyerID", "Household_Details", "Num_children",
    "Num_parents", "Num_others", "Address", "Home_Ownership", "Length_ofStay",
]
REQUIRED = [
    "HouseholdID", "BuyerID", "Num_children", "Num_parents", "Num_others",
    "Address", "Home_Ownership",
]


@household_bp.route("/api/household", methods=["GET"])
def list_household():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM household"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@household_bp.route("/api/household/<hh_id>", methods=["GET"])
def get_household(hh_id):
    try:
        row = query_one("SELECT * FROM household WHERE HouseholdID = %s", (hh_id,))
        if row is None:
            return jsonify(ok=False, error="Household not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@household_bp.route("/api/household", methods=["POST"])
def create_household():
    body = request.get_json(silent=True) or {}
    # Note: 0 is a valid count, so check for None/"" not falsiness.
    missing = [c for c in REQUIRED if body.get(c) in (None, "")]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO household ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM household WHERE HouseholdID = %s", (body["HouseholdID"],)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Household '{body['HouseholdID']}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@household_bp.route("/api/household/<hh_id>", methods=["PUT"])
def update_household(hh_id):
    body = request.get_json(silent=True) or {}
    fields = [c for c in COLUMNS if c != "HouseholdID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [hh_id]
    try:
        affected = execute(f"UPDATE household SET {set_clause} WHERE HouseholdID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Household not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM household WHERE HouseholdID = %s", (hh_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@household_bp.route("/api/household/<hh_id>", methods=["DELETE"])
def delete_household(hh_id):
    try:
        affected = execute("DELETE FROM household WHERE HouseholdID = %s", (hh_id,))
        if affected == 0:
            return jsonify(ok=False, error="Household not found"), 404
        return jsonify(ok=True, data={"deleted": hh_id})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
```

- [ ] **Step 2: Ensure `app.py` registers `household_bp`.**

- [ ] **Step 3: Verify** — `curl http://localhost:5000/api/household` -> 5 rows.

- [ ] **Step 4: Commit**

```bash
git add backend/routes/household.py backend/app.py
git commit -m "feat(backend): add household CRUD API

GET list/one, POST, PUT, DELETE on the household table (keyed by HouseholdID).
Count fields validated allowing 0. Raw parameterized SQL."
git push
```

---

## Task 8: Loans CRUD

**Files:**
- Create: `backend/routes/loans.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Create `backend/routes/loans.py`**

```python
"""
loans.py
CRUD for the `loan` table. Primary key: LoanID.
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

loans_bp = Blueprint("loans", __name__)

COLUMNS = [
    "LoanID", "BuyerID", "UnitID", "Finance_Type", "DP_Term", "Loan_Term",
    "Purchase_Purpose", "Source_Funds", "LoanAmount", "Downpayment",
    "ReservationFee", "Sell_Price", "OrPr_Num", "OrPr_Date",
    "Booking_Officer", "ProcessingFee",
]
REQUIRED = COLUMNS   # every loan column is NOT NULL in the schema


@loans_bp.route("/api/loans", methods=["GET"])
def list_loans():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM loan"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@loans_bp.route("/api/loans/<loan_id>", methods=["GET"])
def get_loan(loan_id):
    try:
        row = query_one("SELECT * FROM loan WHERE LoanID = %s", (loan_id,))
        if row is None:
            return jsonify(ok=False, error="Loan not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@loans_bp.route("/api/loans", methods=["POST"])
def create_loan():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if body.get(c) in (None, "")]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO loan ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM loan WHERE LoanID = %s", (body["LoanID"],)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Loan '{body['LoanID']}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@loans_bp.route("/api/loans/<loan_id>", methods=["PUT"])
def update_loan(loan_id):
    body = request.get_json(silent=True) or {}
    fields = [c for c in COLUMNS if c != "LoanID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [loan_id]
    try:
        affected = execute(f"UPDATE loan SET {set_clause} WHERE LoanID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Loan not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM loan WHERE LoanID = %s", (loan_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@loans_bp.route("/api/loans/<loan_id>", methods=["DELETE"])
def delete_loan(loan_id):
    try:
        affected = execute("DELETE FROM loan WHERE LoanID = %s", (loan_id,))
        if affected == 0:
            return jsonify(ok=False, error="Loan not found"), 404
        return jsonify(ok=True, data={"deleted": loan_id})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
```

- [ ] **Step 2: Ensure `app.py` registers `loans_bp`.**

- [ ] **Step 3: Verify** — `curl http://localhost:5000/api/loans` -> 5 rows.

- [ ] **Step 4: Commit**

```bash
git add backend/routes/loans.py backend/app.py
git commit -m "feat(backend): add loan CRUD API

GET list/one, POST, PUT, DELETE on the loan table (keyed by LoanID). All
columns required on create (schema is NOT NULL). Raw parameterized SQL."
git push
```

---

## Task 9: Reports endpoint (Izy's 10 saved queries)

**Files:**
- Create: `backend/routes/reports.py`
- Modify: `backend/app.py`

> The 10 queries come from `database/profriends_inc_queries.sql`. We embed them
> here as a labeled dictionary so the reports page can request any of them by
> number. Embedding (not reading the .sql file at runtime) keeps the endpoint
> self-contained and avoids file-path issues across teammates' machines.

- [ ] **Step 1: Create `backend/routes/reports.py`**

```python
"""
reports.py
Read-only reporting endpoint. Runs the 10 queries written by Izy (see
database/profriends_inc_queries.sql) and returns the rows as JSON for the
Inventory / Reports page.

GET /api/reports          -> list of available reports (number + description)
GET /api/reports/q<n>     -> rows for report n (1..10)
"""
from flask import Blueprint, jsonify
from mysql.connector import Error as MySQLError
from db import query_all

reports_bp = Blueprint("reports", __name__)

# Each entry: number -> (human description, SQL). SQL copied from Izy's file.
REPORTS = {
    1: ("Filipino buyers: id, name, citizenship",
        "SELECT BuyerID, BuyerName, Citizenship FROM buyer WHERE Citizenship = 'Filipino'"),
    2: ("Buyers born in Manila: name, gender, civil status",
        "SELECT BuyerName, Gender, Civil_Status FROM buyer WHERE Birthplace LIKE '%Manila%'"),
    3: ("Beneficiaries born 2016-2020",
        "SELECT * FROM beneficiary WHERE YEAR(BenF_Bdate) BETWEEN 2016 AND 2020"),
    4: ("Married buyers, income 50k-90k",
        "SELECT BuyerName, Gender, Civil_Status, Gross_MonthlyIncome FROM buyer "
        "WHERE (Gross_MonthlyIncome BETWEEN 50000 AND 90000) AND Civil_Status = 'M'"),
    5: ("Finance types with avg loan > 1,000,000",
        "SELECT Finance_Type, AVG(LoanAmount) AS avg_loan_amount FROM loan "
        "GROUP BY Finance_Type HAVING AVG(LoanAmount) > 1000000"),
    6: ("Total gross income per bank (high to low)",
        "SELECT Bank_Name, SUM(Gross_MonthlyIncome) AS total_income FROM buyer "
        "GROUP BY Bank_Name ORDER BY total_income DESC"),
    7: ("Length of stay by home ownership (avg > 3 yrs)",
        "SELECT MAX(Length_ofStay) AS stay_length, AVG(Length_ofStay) AS avg_stay, "
        "Home_Ownership FROM household WHERE Length_ofStay >= 2 "
        "GROUP BY Home_Ownership HAVING AVG(Length_ofStay) > 3"),
    8: ("Buyer count per employment type (single/married, tenure >= 4)",
        "SELECT Emp_Type, COUNT(*) AS total_buyers FROM employment e "
        "JOIN buyer b ON e.BuyerID = b.BuyerID "
        "WHERE b.Civil_Status IN ('M','S') AND e.Tenure >= 4 GROUP BY Emp_Type"),
    9: ("Loans term > 5 yrs with yearly payment > 200k",
        "SELECT b.BuyerName, l.Finance_Type, l.LoanAmount, l.Loan_Term, "
        "(l.LoanAmount / l.Loan_Term) AS yearly_payment "
        "FROM buyer b JOIN loan l ON b.BuyerID = l.BuyerID "
        "WHERE l.Loan_Term > 5 AND (l.LoanAmount / l.Loan_Term) > 200000"),
    10: ("Buyers with > 1 beneficiary (youngest bdate)",
         "SELECT b.BuyerName, COUNT(be.BeneficiaryID) AS total_beneficiaries, "
         "MAX(be.BenF_Bdate) AS youngest_beneficiary_bdate "
         "FROM buyer b JOIN beneficiary be ON b.BuyerID = be.BuyerID "
         "GROUP BY b.BuyerName HAVING COUNT(be.BeneficiaryID) > 1 "
         "ORDER BY total_beneficiaries DESC"),
}


@reports_bp.route("/api/reports", methods=["GET"])
def list_reports():
    """Return the menu of available reports."""
    menu = [{"number": n, "description": desc} for n, (desc, _sql) in sorted(REPORTS.items())]
    return jsonify(ok=True, data=menu)


@reports_bp.route("/api/reports/q<int:number>", methods=["GET"])
def run_report(number):
    if number not in REPORTS:
        return jsonify(ok=False, error=f"No report #{number} (valid: 1-10)"), 404
    description, sql = REPORTS[number]
    try:
        rows = query_all(sql)
        return jsonify(ok=True, data={"description": description, "rows": rows})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
```

- [ ] **Step 2: Ensure `app.py` registers `reports_bp`.**

- [ ] **Step 3: Verify**:

```bash
curl http://localhost:5000/api/reports
curl http://localhost:5000/api/reports/q1
curl http://localhost:5000/api/reports/q6
```
Expected: q1 -> 5 Filipino buyers; q6 -> banks with summed income, highest first.

- [ ] **Step 4: Commit**

```bash
git add backend/routes/reports.py backend/app.py
git commit -m "feat(backend): add reports endpoint with Izy's 10 SQL queries

GET /api/reports lists the 10 reports; GET /api/reports/q<n> runs query n and
returns the rows. Queries mirror database/profriends_inc_queries.sql
(read-only). Powers the Inventory/Reports page."
git push
```

---

## Task 10: Smoke test script

**Files:**
- Create: `backend/test_api.py`

- [ ] **Step 1: Create `backend/test_api.py`**

```python
"""
test_api.py
A plain-Python smoke test (no testing framework). Start the server first
(`python app.py`), then in another terminal run `python test_api.py`.
It checks each endpoint and prints PASS / FAIL. It creates a temporary buyer
'B-TEST-001', edits it, then deletes it, so the database is left unchanged.
"""
import json
import urllib.request
import urllib.error

BASE = "http://localhost:5000"
passed = 0
failed = 0


def call(method, path, body=None):
    """Send an HTTP request and return (status_code, parsed_json)."""
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS - {label}")
    else:
        failed += 1
        print(f"FAIL - {label}")


# --- Health ---
status, body = call("GET", "/api/health")
check("health returns ok", status == 200 and body.get("ok") is True)

# --- Login (admin) ---
status, body = call("POST", "/api/login",
                    {"role": "admin", "username": "admin", "password": "admin123"})
check("admin login ok", status == 200 and body.get("ok") is True)

# --- Read buyers ---
status, body = call("GET", "/api/buyers")
check("list buyers ok", status == 200 and body.get("ok") and len(body["data"]) >= 5)

# --- Create temp buyer ---
new_buyer = {
    "BuyerID": "B-TEST-001", "BuyerName": "Test Person", "Birthdate": "1990-01-01",
    "Birthplace": "Test City", "GovID": "Passport", "TIN": "000-000-000-000",
    "Gender": "M", "Civil_Status": "S", "Address": "123 Test St",
    "Citizenship": "Filipino", "Gross_MonthlyIncome": 50000,
    "Mobile_Num": "09170000000", "Personal_Email": "test@test.com",
    "Account_Type": "Savings", "Bank_Name": "BDO",
}
status, body = call("POST", "/api/buyers", new_buyer)
check("create buyer ok", status == 200 and body.get("ok") is True)

# --- Update temp buyer ---
status, body = call("PUT", "/api/buyers/B-TEST-001", {"Bank_Name": "BPI"})
check("update buyer ok", status == 200 and body["data"]["Bank_Name"] == "BPI")

# --- Delete temp buyer (cleanup) ---
status, body = call("DELETE", "/api/buyers/B-TEST-001")
check("delete buyer ok", status == 200 and body.get("ok") is True)

# --- Report ---
status, body = call("GET", "/api/reports/q1")
check("report q1 ok", status == 200 and body.get("ok") is True)

print(f"\n{passed} passed, {failed} failed")
```

- [ ] **Step 2: Run it** (server must be running):

```bash
python test_api.py
```
Expected: all checks PASS, final line `7 passed, 0 failed`.

- [ ] **Step 3: Commit**

```bash
git add backend/test_api.py
git commit -m "test(backend): add plain-Python smoke test for the API

Checks health, admin login, buyer list, and create/update/delete of a temp
buyer (self-cleaning), plus one report. Run: python test_api.py. No framework
needed."
git push
```

---

## Task 11: Wire a copy of the frontend to the API

**Files:**
- Create: `backend/templates/index.html` (copy of `uiux.txt`, then wired)
- `uiux.txt` is NOT modified.

> This task converts the frontend's in-memory data arrays into API calls.
> Andre's render functions stay; only the data source changes.

- [ ] **Step 1: Copy the original UI into templates**

```bash
copy uiux.txt backend\templates\index.html   # Windows
# cp uiux.txt backend/templates/index.html    # Mac/Linux
```

- [ ] **Step 2: Read `backend/templates/index.html` fully** and locate:
  - the data arrays (`let buyers = [...]`, `spouses`, `employments`, `beneficiaries`, `loans`), around lines 386-406
  - the `renderApp()` / login handlers (`handleLogin`, `handleCreateAccount`)
  - the refresh/render functions (`refreshClientTable`, `refreshLoanTable`, etc.)
  - the add/edit/delete handlers that currently push/splice those arrays

- [ ] **Step 3: Add an API helper near the top of the `<script>` block**

Insert this block right after `<script>` (before the data arrays):

```javascript
// ============================================================
// API helper — talks to the Flask backend.
// Every call returns the parsed JSON ({ ok, data } or { ok, error }).
// Andre's render functions are unchanged; we just feed them DB data.
// ============================================================
const API = {
  async get(path) {
    const res = await fetch(path);
    return res.json();
  },
  async send(method, path, body) {
    const res = await fetch(path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    return res.json();
  },
};

// Load every dataset from the database into the existing arrays, then re-render.
async function loadAllData() {
  const [b, s, e, ben, l] = await Promise.all([
    API.get("/api/buyers"),
    API.get("/api/spouse"),
    API.get("/api/employment"),
    API.get("/api/beneficiaries"),
    API.get("/api/loans"),
  ]);
  // Replace contents in place so other code keeps its references.
  buyers.length = 0;       buyers.push(...(b.data   || []));
  spouses.length = 0;      spouses.push(...(s.data   || []));
  employments.length = 0;  employments.push(...(e.data || []));
  beneficiaries.length = 0; beneficiaries.push(...(ben.data || []));
  loans.length = 0;        loans.push(...(l.data   || []));
}
```

- [ ] **Step 4: Change the array declarations to empty arrays**

Change `let buyers = [ ...seed... ]` (and `spouses`, `employments`, `beneficiaries`, `loans`)
to empty: `let buyers = [];` etc. The seed data now comes from the database via `loadAllData()`.
(Leave `properties`, `payments`, `users`, `bookingOfficers` as-is — they remain frontend-only per the spec.)

- [ ] **Step 5: Call `loadAllData()` before the app renders**

Find where the app boots after successful login (inside `renderApp()` or right after
`handleLogin` succeeds). Make that path `await loadAllData();` before calling the first
`switchPage(...)`/render. Example wrapper to add:

```javascript
// Called once the user is logged in: pull fresh data, then show the app.
async function bootApp() {
  await loadAllData();
  renderApp();   // Andre's existing function that builds the UI
}
```
Replace the direct `renderApp()` call after a successful login with `bootApp()`.

- [ ] **Step 6: Route login through the API**

In `handleLogin`, replace the in-memory `users` check with:

```javascript
// Decide role from the existing form fields, then ask the backend.
const result = await API.send("POST", "/api/login", {
  role: selectedRole,        // "admin" or "buyer" from the login form
  username: usernameValue,   // admin username, or BuyerID
  password: passwordValue,   // admin password, or buyer last name
});
if (result.ok) {
  await bootApp();
} else {
  showMessage(result.error || "Login failed");   // Andre's existing helper
}
```
(Map `selectedRole`/`usernameValue`/`passwordValue` to the actual variable names already
read from the login form in `handleLogin`.)

- [ ] **Step 7: Make create/edit/delete write to the API**

For each table's add/edit/delete handler, replace the array mutation with an API call,
then reload. Buyer example (apply the same pattern to spouse/employment/beneficiary/loan
using their endpoints and id fields):

```javascript
// CREATE
const r = await API.send("POST", "/api/buyers", buyerFormObject);
if (!r.ok) { showMessage(r.error); return; }
await loadAllData(); refreshClientTable();

// UPDATE
const r = await API.send("PUT", "/api/buyers/" + buyerId, changedFields);
if (!r.ok) { showMessage(r.error); return; }
await loadAllData(); refreshClientTable();

// DELETE
const r = await API.send("DELETE", "/api/buyers/" + buyerId);
if (!r.ok) { showMessage(r.error); return; }
await loadAllData(); refreshClientTable();
```
(For beneficiaries, the single-record routes use query params:
`"/api/beneficiaries/one?id=" + encodeURIComponent(id) + "&name=" + encodeURIComponent(name)`.)

- [ ] **Step 8: Verify in the browser**

Run `python app.py`, open http://localhost:5000:
1. Log in as admin (admin / admin123) -> buyer table shows the 5 DB buyers.
2. Add a buyer via the UI -> appears in the table.
3. Refresh the page, log in again -> the new buyer is still there (proves DB persistence).
4. Edit then delete it -> changes persist across refresh.
5. Log in as a buyer (e.g. B-2023-001 / Velasco) -> only buyer views show.
6. Open the Reports/Inventory page -> reports return rows.

- [ ] **Step 9: Commit**

```bash
git add backend/templates/index.html
git commit -m "feat(frontend): wire UI copy to the backend API

Serves a copy of uiux.txt as templates/index.html and replaces the in-memory
data arrays with fetch() calls to the Flask API (buyers, spouse, employment,
beneficiaries, loans). Login now goes through /api/login. Andre's original
uiux.txt is untouched; render functions are reused as-is."
git push
```

---

## Task 12: Final integration check + README polish

**Files:**
- Modify: `backend/README.md` (add troubleshooting + endpoint table if anything changed)

- [ ] **Step 1: Full manual run-through** following `backend/README.md` from a clean `.env`,
      then run `python test_api.py` -> `7 passed, 0 failed`.

- [ ] **Step 2: Confirm `uiux.txt`, `database/*.sql` are unchanged** in git:

```bash
git log --oneline -- uiux.txt database/profriends_inc.sql database/profriends_inc_queries.sql
```
Expected: no new commits from this work touch those files.

- [ ] **Step 3: Update README** with a short troubleshooting section
      (MySQL not running -> 503; wrong password -> check `.env`; port 5000 busy -> change in `app.py`).

- [ ] **Step 4: Commit**

```bash
git add backend/README.md
git commit -m "docs(backend): finalize README with run-through and troubleshooting

Verified full setup from a clean .env and the smoke test passes. Adds
troubleshooting for common local issues (MySQL down, wrong password, busy port)."
git push
```

- [ ] **Step 5: Open a pull request** for the team to review/merge into main:

```bash
gh pr create --base main --head backend-lawrence --title "Flask backend: REST API + MySQL integration" --body "Adds the Python/Flask backend connecting the frontend to the profriends_inc database. Full CRUD for the 6 tables, session login, reports endpoint (Izy's queries), and a wired copy of the UI. See docs/superpowers/specs and docs/superpowers/plans for details. Andre's uiux.txt and Izy's SQL files are untouched."
```

---

## Self-Review Notes (author check against spec)

- **Spec coverage:** CRUD for all 6 tables (Tasks 3-8); auth (Task 2); reports/10 queries (Task 9); copy + wire frontend leaving uiux.txt untouched (Task 11); error shape (every task); run steps + smoke test (Tasks 1, 10, 12). Covered.
- **Out-of-scope respected:** properties/payments/users left as frontend-only (Task 11 Step 4). No schema changes.
- **Type/naming consistency:** db helpers `query_all/query_one/execute` used identically everywhere; response shape `{ ok, data/error }` everywhere; blueprint names match `app.py` registrations.
- **Known follow-ups:** Task 11 requires reading the actual frontend file to map exact variable/handler names; the plan gives the pattern and exact endpoints. The `handleCreateAccount` flow stays frontend-only (no users table) — leave as-is or disable the button; note for the team.
