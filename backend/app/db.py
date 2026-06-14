import os
from typing import List, Dict, Any
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Prefer an explicitly named service role key if provided in Vercel
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def _get_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set as environment variables")
    # Accept either the project URL or a URL that accidentally includes /rest/v1
    base_url = SUPABASE_URL
    # remove any trailing '/rest/v1' or '/rest/v1/' if present
    if '/rest/v1' in base_url:
        base_url = base_url.split('/rest/v1')[0]
    base_url = base_url.rstrip('/')
    return create_client(base_url, SUPABASE_KEY)


def insert_shift(payload: Dict[str, Any]) -> Dict[str, Any]:
    client = _get_client()
    try:
        resp = client.table("shift_logs").insert(payload).execute()
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Insert error: {e}")


def get_shifts_between(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    client = _get_client()
    try:
        resp = (
            client.table("shift_logs")
            .select("*")
            .gte("shift_date", start_date)
            .lte("shift_date", end_date)
            .execute()
        )
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Query error: {e}")


def insert_pay_period(payload: Dict[str, Any]) -> Dict[str, Any]:
    client = _get_client()
    try:
        resp = client.table("pay_periods").insert(payload).execute()
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Insert pay period error: {e}")


def get_pay_period_for_date(shift_date: str) -> Dict[str, Any]:
    # returns the first pay_period that includes shift_date
    client = _get_client()
    data = None
    try:
        resp = (
            client.table("pay_periods")
            .select("*")
            .lte("period_start", shift_date)
            .gte("period_end", shift_date)
            .limit(1)
            .execute()
        )
        data = resp.data or []
    except Exception as e:
        raise RuntimeError(f"Query error: {e}")

    return data[0] if data else None


def summary_for_month(year_month: str) -> Dict[str, Any]:
    # year_month expected in YYYY-MM format
    client = _get_client()
    start = f"{year_month}-01"
    # simple approach: fetch month rows and aggregate in Python
    try:
        resp = (
            client.table("shift_logs")
            .select("*")
            .gte("shift_date", start)
            .lte("shift_date", start[:7] + "-31")
            .execute()
        )
        rows = resp.data or []
    except Exception as e:
        raise RuntimeError(f"Query error: {e}")
    total_gross = 0.0
    total_hours = 0.0
    for r in rows:
        points = r.get("points", 0) or 0
        tipped = float(r.get("tipped_hours", 0) or 0)
        untipped = float(r.get("untipped_hours", 0) or 0)
        pv = float(r.get("point_value", 0) or 0)
        driving = tipped * 5.5 + points * pv
        total = driving + untipped * 15.0
        total_gross += total
        total_hours += tipped + untipped
    avg_hourly = total_gross / total_hours if total_hours > 0 else 0.0
    return {"total_gross": total_gross, "total_hours": total_hours, "avg_hourly": avg_hourly}


def delete_shift(shift_id: str) -> int:
    """Delete a shift by id. Returns number of deleted rows (0 or 1)."""
    client = _get_client()
    try:
        resp = client.table("shift_logs").delete().eq("id", shift_id).execute()
        data = resp.data or []
        return len(data)
    except Exception as e:
        raise RuntimeError(f"Delete error: {e}")


def update_shift(shift_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update a shift by id. Returns updated rows data."""
    client = _get_client()
    # ensure payload dates are JSON serializable
    if payload.get("shift_date") and hasattr(payload.get("shift_date"), "isoformat"):
        payload["shift_date"] = payload["shift_date"].isoformat()
    try:
        resp = client.table("shift_logs").update(payload).eq("id", shift_id).execute()
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Update error: {e}")
