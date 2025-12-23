"""Settings routes"""

from starlette.routing import Route
from starlette.responses import JSONResponse, FileResponse
from starlette.requests import Request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


async def settings_page(request: Request):
    """Serve settings page"""
    if not request.session.get("access_token"):
        return FileResponse(BASE_DIR / "app/templates/login.html")
    return FileResponse(BASE_DIR / "app/templates/settings.html")


routes = [
    Route("/", endpoint=settings_page, methods=["GET"]),
]
