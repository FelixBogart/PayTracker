# Supabase DB Schema

This folder contains the SQL to create the `shift_logs` table used to store raw daily entries.

Files:
- `schema.sql` — Creates the `shift_logs` table and an index on `shift_date`.

Run options:

- Supabase SQL editor: copy/paste the contents of `schema.sql` into the SQL editor in the Supabase dashboard and run.

- psql (direct to Postgres):

```powershell
psql "postgresql://<user>:<password>@<host>:<port>/<database>" -f "db/schema.sql"
```

- supabase CLI (if configured):

```powershell
supabase db reset --project-ref <ref> --file "db/schema.sql"
```

Notes:
- `pgcrypto` extension is enabled for `gen_random_uuid()`; Supabase supports this by default.
- Consider enabling Row Level Security (RLS) and creating policies for secure access.
