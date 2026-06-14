from fastapi import FastAPI, HTTPException
import logging
from fastapi.middleware.cors import CORSMiddleware
from .calc import calculate_daily_pay
from .schemas import ShiftCreate, ShiftCalculated, PayPeriod
from . import db
import os

app = FastAPI(title="Pay Tracker API")

# Auth config: read from env or use safe defaults for local dev
ADMIN_PASSWORD = os.getenv('BACKEND_ADMIN_PASSWORD') or os.getenv('ADMIN_PASSWORD') or 'admin'
JWT_SECRET = os.getenv('BACKEND_JWT_SECRET') or os.getenv('JWT_SECRET') or os.getenv('SUPABASE_KEY') or 'dev-secret'
JWT_ALGO = 'HS256'
TOKEN_EXPIRE_SECONDS = int(os.getenv('BACKEND_TOKEN_EXPIRE_SECONDS') or 7*24*3600)

# Authentication removed for this iteration; endpoints are public

# Dev CORS - allow frontend dev server to call the API. Restrict in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shifts/", response_model=dict)
def create_shift(shift: ShiftCreate):
    payload = shift.dict()
    # ensure dates are JSON serializable for the Supabase client
    if isinstance(payload.get("shift_date"), (bytes,)):
        payload["shift_date"] = payload["shift_date"].decode()
    elif hasattr(payload.get("shift_date"), "isoformat"):
        payload["shift_date"] = payload["shift_date"].isoformat()
    try:
        inserted = db.insert_shift(payload)
    except Exception as e:
        logging.exception("Error inserting shift")
        raise HTTPException(status_code=500, detail=str(e))
    return {"inserted": inserted}


@app.post("/payperiods/", response_model=dict)
def create_pay_period(period: PayPeriod):
    payload = period.dict()
    # ensure date fields are JSON serializable
    if hasattr(payload.get("period_start"), "isoformat"):
        payload["period_start"] = payload["period_start"].isoformat()
    if hasattr(payload.get("period_end"), "isoformat"):
        payload["period_end"] = payload["period_end"].isoformat()
    try:
        inserted = db.insert_pay_period(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"inserted": inserted}


@app.get("/shifts/{start_date}/{end_date}")
def get_shifts(start_date: str, end_date: str):
    try:
        rows = db.get_shifts_between(start_date, end_date)
    except Exception as e:
        logging.exception("Error fetching shifts")
        raise HTTPException(status_code=500, detail=str(e))

    results = []
    for r in rows:
        # determine point_value: prefer shift value, otherwise lookup pay period
        pv = r.get("point_value")
        if pv is None or float(pv) == 0:
            try:
                pp = db.get_pay_period_for_date(r.get("shift_date"))
                pv = float(pp.get("point_value")) if pp else 0.0
            except Exception:
                pv = 0.0

        calc = calculate_daily_pay(
            points=int(r.get("points", 0) or 0),
            tipped_hours=float(r.get("tipped_hours", 0) or 0),
            untipped_hours=float(r.get("untipped_hours", 0) or 0),
            point_value=float(pv or 0),
        )
        merged = {**r, **calc}
        results.append(merged)
    return {"rows": results}


@app.delete("/shifts/{shift_id}")
def delete_shift(shift_id: str):
    try:
        deleted = db.delete_shift(shift_id)
    except Exception as e:
        logging.exception("Error deleting shift")
        raise HTTPException(status_code=500, detail=str(e))
    return {"deleted": deleted}


from .schemas import ShiftCreate, ShiftCalculated, PayPeriod, ShiftUpdate


@app.patch("/shifts/{shift_id}")
def patch_shift(shift_id: str, shift: ShiftUpdate):
    payload = shift.dict(exclude_unset=True)
    # ensure dates are JSON serializable
    if hasattr(payload.get("shift_date"), "isoformat"):
        payload["shift_date"] = payload["shift_date"].isoformat()
    try:
        updated = db.update_shift(shift_id, payload)
    except Exception as e:
        logging.exception("Error updating shift")
        raise HTTPException(status_code=500, detail=str(e))
    return {"updated": updated}


@app.get("/summary/{year_month}")
def summary(year_month: str):
    try:
        s = db.summary_for_month(year_month)
    except Exception as e:
        logging.exception("Error computing summary")
        raise HTTPException(status_code=500, detail=str(e))
    return s


# login removed


@app.get("/_supabase_debug")
def supabase_debug():
    """Lightweight debug endpoint to verify SUPABASE_URL and table access.

    NOTE: This endpoint returns limited info and should be removed after debugging.
    """
    import os
    from supabase import create_client

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return {"ok": False, "error": "SUPABASE_URL or SUPABASE_KEY not set in environment"}

    try:
        base_url = url
        if '/rest/v1' in base_url:
            base_url = base_url.split('/rest/v1')[0]
        base_url = base_url.rstrip('/')
        client = create_client(base_url, key)
        resp = client.table("shift_logs").select("*").limit(1).execute()
        # resp.data may be None or a list; resp.error may contain details
        data = getattr(resp, 'data', None)
        error = getattr(resp, 'error', None)
        return {"ok": True, "supabase_url": base_url, "sample_rows": data or [], "error": str(error) if error else None}
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "trace": traceback.format_exc()[:2000]}


