# Pay Tracker

Lightweight backend and DB schema for tracking daily shifts, points, and calculated pay.

Repository layout
- `db/schema.sql` — Supabase/Postgres schema for `shift_logs`.
- `backend/` — FastAPI backend (calculation logic, API, Dockerfile, tests).

Quickstart (backend)

1. Create a Python virtual environment and install dependencies:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

2. Provide Supabase credentials by copying `.env.example` to `.env` and filling values.

3. Run the API locally:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Health check:

```powershell
curl http://localhost:8000/health
```

Apply the database schema

- Supabase dashboard: open SQL editor and run the contents of `db/schema.sql`.
- psql:

```powershell
psql "postgresql://<user>:<pass>@<host>:<port>/<db>" -f "db/schema.sql"
```

Docker (backend)

Build and run the backend container from the `backend` folder:

```powershell
docker build -t pay-tracker-backend:latest .
docker run --env-file ./.env -p 8000:8000 pay-tracker-backend:latest
```

Tests

Install test dependencies and run pytest from `backend`:

```powershell
pip install -r requirements.txt
pytest -q tests
```

Example requests

See `backend/examples/requests.md` for sample curl commands to exercise the API.

Notes & next steps
- Keep secrets out of source control; use a secret manager for production.
- Consider enabling Row Level Security (RLS) in Supabase and adding policies.
- Next: scaffold a frontend (mobile/web) to enter shifts and display analytics.
