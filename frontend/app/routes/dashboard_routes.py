"""Dashboard routes"""

from starlette.routing import Route
from starlette.responses import JSONResponse, FileResponse
from starlette.requests import Request
from datetime import date
from pathlib import Path
from app.utils import get_api_client

BASE_DIR = Path(__file__).resolve().parent.parent.parent


async def dashboard_page(request: Request):
    """Serve dashboard page"""
    if not request.session.get("access_token"):
        return FileResponse(BASE_DIR / "app/templates/login.html")
    return FileResponse(BASE_DIR / "app/templates/dashboard.html")


async def get_daily_summary(request: Request):
    """Get daily nutrition summary"""
    try:
        token = request.session.get("access_token")
        if not token:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
        today = date.today()
        api = get_api_client()
        
        # Get daily nutrition from backend
        response = await api.get(
            f"/api/nutrition/daily/{today}",
            token=token
        )
        
        await api.close()
        
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def get_weekly_summary(request: Request):
    """Get weekly nutrition summary"""
    try:
        token = request.session.get("access_token")
        if not token:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
        api = get_api_client()
        
        # Get weekly nutrition from backend
        response = await api.get(
            "/api/nutrition/weekly",
            token=token
        )
        
        await api.close()
        
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


routes = [
    Route("/", endpoint=dashboard_page, methods=["GET"]),
    Route("/daily-summary", endpoint=get_daily_summary, methods=["GET"]),
    Route("/weekly-summary", endpoint=get_weekly_summary, methods=["GET"]),
]
