# React Frontend (Vite)

Quickstart

1. Install dependencies:

```bash
cd frontend/react-app
npm install
```

2. Run dev server:

```bash
npm run dev
```

3. Open the URL shown by Vite (usually http://localhost:5173).

Notes
- Set the backend URL via `VITE_API_BASE` if different from `http://localhost:8000`:

```bash
npm run dev -- --host --open
# or set environment variable
VITE_API_BASE=http://192.168.1.100:8000 npm run dev
```

- Ensure backend allows CORS for the dev origin (see backend CORS middleware in README).
