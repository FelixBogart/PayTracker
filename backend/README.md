## Backend Docker instructions

Build the Docker image from the `backend` folder:

```powershell
cd backend
docker build -t pay-tracker-backend:latest .
```

Run the container (example using environment variables from `.env`):

```powershell
docker run --env-file ./.env -p 8000:8000 pay-tracker-backend:latest
```

Visit `http://localhost:8000/health` to verify the service responds.

Notes:
- Set `SUPABASE_URL` and `SUPABASE_KEY` in your `.env` before running.
- For production, use a more secure mechanism for secrets (secret manager, CI/CD secrets).
