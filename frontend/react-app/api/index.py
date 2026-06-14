from backend.app.main import app as backend_app


async def app(scope, receive, send):
	if scope.get("type") == "http":
		path = scope.get("path", "")
		if path.startswith("/api/"):
			scope["path"] = path[len("/api"):]
		elif path == "/api":
			scope["path"] = "/"
	await backend_app(scope, receive, send)
