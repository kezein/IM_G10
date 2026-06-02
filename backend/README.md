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
