from fastapi import FastAPI
import os
from supabase import create_client

app = FastAPI()


@app.get("/")
def debug_root():
    url = os.getenv("SUPABASE_URL")
    # allow Vercel to store the service role key under this name
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return {"ok": False, "error": "SUPABASE_URL or SUPABASE_KEY not set"}

    try:
        base_url = url
        if '/rest/v1' in base_url:
            base_url = base_url.split('/rest/v1')[0]
        base_url = base_url.rstrip('/')
        client = create_client(base_url, key)
        resp = client.table("shift_logs").select("*").limit(1).execute()
        data = getattr(resp, 'data', None)
        error = getattr(resp, 'error', None)
        return {"ok": True, "supabase_url": base_url, "sample_rows": data or [], "error": str(error) if error else None}
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "trace": traceback.format_exc()[:2000]}
