from fastapi import FastAPI
import os
from supabase import create_client

app = FastAPI()


@app.get("/")
def debug_root():
    # Check for presence of known Supabase env vars and report presence only
    env_checks = {}
    names = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    ]
    for n in names:
        env_checks[n] = bool(os.getenv(n))

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return {"ok": False, "error": "SUPABASE_URL or SUPABASE_KEY not set", "env": env_checks}

    try:
        base_url = url
        if '/rest/v1' in base_url:
            base_url = base_url.split('/rest/v1')[0]
        base_url = base_url.rstrip('/')
        client = create_client(base_url, key)
        resp = client.table("shift_logs").select("*").limit(1).execute()
        data = getattr(resp, 'data', None)
        error = getattr(resp, 'error', None)
        return {"ok": True, "supabase_url": base_url, "sample_rows": data or [], "error": str(error) if error else None, "env": env_checks}
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "trace": traceback.format_exc()[:2000]}
