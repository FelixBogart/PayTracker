from backend.app.main import app as backend_app


# ASGI wrapper: strip leading '/api' prefix if present, then forward to
# the backend ASGI app. This handles Vercel variants that preserve the
# '/api' prefix when invoking the serverless function.
async def app(scope, receive, send):
	if scope.get("type") == "http":
		path = scope.get("path", "")
		if path.startswith("/api/"):
			# mutate the scope path in-place so the backend matches routes
			scope["path"] = path[len("/api"):]
		elif path == "/api":
			scope["path"] = "/"
	await backend_app(scope, receive, send)
