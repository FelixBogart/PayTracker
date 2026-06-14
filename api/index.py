from fastapi import FastAPI
from backend.app.main import app as backend_app

# Create a thin wrapper app that mounts the real backend both at root
# and under /api. Some Vercel routing setups forward the full path
# (including /api) to the function; mounting at both locations ensures
# endpoints like /shifts/... work regardless.
app = FastAPI()
app.mount("/", backend_app)
app.mount("/api", backend_app)
