"""P.U.L.S.E Frontend Application

This file is the main entry point for the frontend application.
It is now located in `frontend/app/__init__.py`.
"""

import os
from pathlib import Path
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
BASE_DIR = Path(__file__).resolve().parent

# Import routes
from .routes import auth_routes, dashboard_routes, meal_routes, settings_routes


# Route handlers
async def homepage(request):
    """Homepage route"""
    # Redirect to dashboard if logged in, otherwise to login
    if request.session.get("access_token"):
        return FileResponse(BASE_DIR / "templates/dashboard.html")
    else:
        return FileResponse(BASE_DIR / "templates/login.html")


async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({"status": "healthy"})


# Define routes
routes = [
    Route("/", endpoint=homepage, methods=["GET"]),
    Route("/health", endpoint=health_check, methods=["GET"]),
    Mount("/api/auth", routes=auth_routes.routes),
    Mount("/api/dashboard", routes=dashboard_routes.routes),
    Mount("/api/meals", routes=meal_routes.routes),
    Mount("/api/settings", routes=settings_routes.routes),
]

# Create Starlette app
app = Starlette(
    debug=DEBUG,
    routes=routes,
)

# Add middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-in-production")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# This block is for direct execution, which may not work correctly with package-relative imports.
# The recommended way to run the application is with `uvicorn app:app`.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8001,
        reload=DEBUG,
    )
