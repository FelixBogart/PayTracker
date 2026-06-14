from backend.app.main import app as backend_app


# ASGI wrapper: strip leading '/api' prefix if present, then forward to
# the backend ASGI app. This handles Vercel variants that preserve the
# '/api' prefix when invoking the serverless function.
async def app(scope, receive, send):
	if scope.get("type") == "http":
		path = scope.get("path", "")
		if path.startswith("/api/"):
			# mutate the scope path in-place so the backend matches routes
			new_path = path[len("/api"):]
			scope["path"] = new_path
			# also update raw_path (bytes) if present
			if scope.get("raw_path") is not None:
				try:
					scope["raw_path"] = new_path.encode("utf-8")
				except Exception:
					pass
		elif path == "/api":
			scope["path"] = "/"
			if scope.get("raw_path") is not None:
				try:
					scope["raw_path"] = b"/"
				except Exception:
					pass
	await backend_app(scope, receive, send)
