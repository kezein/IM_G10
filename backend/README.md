# Profriends Inc — Backend (Flask)

[![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/-Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/-MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![HTML5](https://img.shields.io/badge/-HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/-CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/kezein/IM_G10)

**Developer:** Lawrence (Flask Backend / Python)
**Branch:** `backend-lawrence`

Connects Andre's frontend UI to the `profriends_inc` MySQL database via a REST API.
The app runs at `http://localhost:5000` and serves the full buyer portal.

---

## What this does

- Serves the frontend (`templates/index.html`) at `/`
- Exposes a REST API for full CRUD on all 6 database tables
- Session-based login (admin + buyer roles)
- Reports endpoint running Izy's 10 SQL queries

---

## Requirements

- Python 3.9 or higher
- MySQL 8.0 running locally (MySQL Server, XAMPP, or any local instance)
- The `profriends_inc` database imported (see step below)
- Git (to clone the repo)

---

## Setup — step by step (Windows)

### 1. Clone the repo and go to the backend folder

```powershell
git clone https://github.com/kezein/IM_G10.git
cd IM_G10\backend
```

If you already cloned it, just pull the latest:

```powershell
cd IM_G10
git pull
cd backend
```

---

### 2. Import the database into your local MySQL

Open PowerShell and run (replace the path to mysql.exe if yours is different):

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < ..\database\profriends_inc.sql
```

When prompted for password: type your MySQL root password and press Enter.
If your root has **no password**, just press Enter.

This creates the `profriends_inc` database with all 6 tables and 5 sample buyers.

**Or use MySQL Workbench:**
1. Open Workbench → connect to local instance
2. Server → Data Import → Import from Self-Contained File
3. Browse to `database\profriends_inc.sql` → Start Import

**Verify it worked:**
```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -e "USE profriends_inc; SELECT COUNT(*) FROM buyer;"
```
Should show `5`.

---

### 3. Create a Python virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt.

---

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

Installs: Flask, mysql-connector-python, python-dotenv.

---

### 5. Set up your .env file

```powershell
copy .env.example .env
notepad .env
```

Edit these lines to match your local MySQL:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=          <-- your MySQL root password (leave blank if none)
DB_NAME=profriends_inc
```

Leave the rest as-is (admin credentials and secret key are fine for local use).

Save and close.

> `.env` is gitignored — your password stays on your machine, never committed.

---

### 6. Run the backend

```powershell
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

---

### 7. Verify it works

Open in your browser:

```
http://localhost:5000/api/health
```

Should show:
```json
{"data": {"db": "connected"}, "ok": true}
```

If you see `"db": "unavailable"`: your MySQL is not running, or the password in `.env` is wrong.

Then open the full app:
```
http://localhost:5000
```

---

### 8. Login credentials

| Role  | Username     | Password                          |
|-------|--------------|-----------------------------------|
| Admin | `admin`      | `admin123`                        |
| Buyer | `B-2023-001` | `Velasco` (last name of BuyerName)|
| Buyer | `B-2024-002` | `Santos`                          |
| Buyer | `B-2024-003` | `Reyes`                           |
| Buyer | `B-2025-004` | `Gomez`                           |
| Buyer | `B-2026-005` | `Tan`                             |

Buyer login = BuyerID as username + last name as password.

---

### 9. Run the smoke test (optional)

With the server running, open a second terminal:

```powershell
cd IM_G10\backend
venv\Scripts\activate
python test_api.py
```

Expected output:
```
PASS - health returns ok
PASS - admin login ok
PASS - list buyers ok
PASS - create buyer ok
PASS - update buyer ok
PASS - delete buyer ok
PASS - report q1 ok

7 passed, 0 failed
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Database unavailable` on health check | MySQL not running, or wrong password in `.env` |
| `Access denied for user 'root'` | Wrong password — check `.env` DB_PASSWORD |
| `Address already in use` on port 5000 | Another process using 5000 — change port in `app.py` last line |
| `ModuleNotFoundError: flask` | Venv not activated — run `venv\Scripts\activate` first |
| Buyer added in UI disappears on refresh | Normal if backend is not running — must have `python app.py` running |
| Date fields blank in edit form | Restart the server after pulling latest (date fix in commit `40d4aa4`) |

---

## API Reference

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/login` | Body: `{role, username, password}`. Role: `"admin"` or `"buyer"` |
| POST | `/api/logout` | Clears session |
| GET | `/api/me` | Returns current logged-in user |

### CRUD (same pattern for all resources)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/buyers` | List all buyers |
| GET | `/api/buyers/<BuyerID>` | Get one buyer |
| POST | `/api/buyers` | Create buyer |
| PUT | `/api/buyers/<BuyerID>` | Update buyer |
| DELETE | `/api/buyers/<BuyerID>` | Delete buyer |

Same pattern for: `/api/spouse`, `/api/employment`, `/api/household`, `/api/loans`

**Beneficiaries** (composite primary key — needs both ID and name):
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/beneficiaries` | List all |
| POST | `/api/beneficiaries` | Create |
| GET | `/api/beneficiaries/one?id=X&name=Y` | Get one |
| PUT | `/api/beneficiaries/one?id=X&name=Y` | Update |
| DELETE | `/api/beneficiaries/one?id=X&name=Y` | Delete |

### Reports (Izy's 10 SQL queries)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/reports` | List all 10 reports |
| GET | `/api/reports/q1` | Run query 1 (Filipino buyers) |
| GET | `/api/reports/q2` | Run query 2 (Manila buyers) |
| ... | ... | ... up to q10 |

All responses follow this shape:
```json
{ "ok": true, "data": [ ... ] }
{ "ok": false, "error": "message" }
```

---

## File structure

```
backend/
  app.py              entry point + Flask app factory
  config.py           loads settings from .env
  db.py               MySQL connection helpers (query_all, query_one, execute)
  requirements.txt    dependencies
  .env.example        copy this to .env and fill in your password
  test_api.py         smoke test (run after starting server)
  routes/
    auth.py           login / logout / me
    buyers.py         CRUD /api/buyers
    spouse.py         CRUD /api/spouse
    beneficiaries.py  CRUD /api/beneficiaries
    employment.py     CRUD /api/employment
    household.py      CRUD /api/household
    loans.py          CRUD /api/loans
    reports.py        GET  /api/reports/q1..q10
  templates/
    index.html        wired copy of Andre's uiux.txt (original untouched)
```

---

## Known limitations (by design)

- **Loan status** (Pending/Active/Approved) is not persisted — no column in the loan table.
- **New buyer Address** defaults to `"N/A"` — no address field in the add-buyer form.
- **Properties and Payments** are frontend-only sample data — not connected to the database.
- **Create Account password** is ignored — buyers log in with BuyerID + last name.

---

## Team

| Name | Role |
|------|------|
| Izy Basco | Database & SQL |
| Lawrence | Flask Backend / Python |
| Andre Montana | Frontend (UI/UX) |
| Kezia Villegas | Backend Integration |
| Paul Correo | Documentation & Integration |

**Subject:** Information Management — Final Project
**Repo:** [github.com/kezein/IM_G10](https://github.com/kezein/IM_G10)
