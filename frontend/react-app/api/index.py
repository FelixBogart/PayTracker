from backend.app.main import app as backend_app

# Vercel's python serverless builder will look for a WSGI/ASGI `app` variable.
app = backend_app
