# Vercel deployment — Supabase env mapping and quick tests

1. Map your Supabase values to these env vars in Vercel (Project → Settings → Environment Variables):

- `SUPABASE_URL` = your Supabase project URL (e.g. `https://xyzcompany.supabase.co`). If you have a value called `NEXT_URL`, use the project URL value from Supabase.
- `SUPABASE_KEY` = a server key for backend access. Prefer the *service_role* key from Supabase (Project → Settings → API). If you only have an anon key (often named `NEXT_PUBLIC_SUPABASE_ANON_KEY`), it may work for public read operations but can fail for server-restricted endpoints.

2. Where to set them:
- Add them in Vercel for `Development`, `Preview`, and `Production` as needed.
- After changing env vars, redeploy the project.

3. Test the connection with the app debug endpoint (added to the API in `backend/app/main.py`):

```bash
curl -s https://<your-vercel-domain>/api/_supabase_debug | jq .
```

The endpoint returns the resolved `supabase_url` and either sample rows or an error/trace. If it shows a different project URL or an authentication error, update the env vars in Vercel.

4. Common fixes for 404s:
- Ensure `SUPABASE_URL` is the project base URL (not a URL that includes `/rest/v1`).
- Use the service role key for server-side functions if your DB has RLS or requires higher privileges.
- Confirm the `shift_logs` table exists and that keys have required permissions.

5. Optional: set frontend `VITE_API_BASE` to `/api` (already added in `frontend/react-app/.env.production`).

If you want, share your Vercel deployment URL and I will call the `_supabase_debug` endpoint and interpret the response.
