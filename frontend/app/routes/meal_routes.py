"""Meal routes"""

from starlette.routing import Route
from starlette.responses import JSONResponse, FileResponse
from starlette.requests import Request
from pathlib import Path
from app.utils import get_api_client

BASE_DIR = Path(__file__).resolve().parent.parent.parent


async def meal_page(request: Request):
    """Serve meal logging page"""
    if not request.session.get("access_token"):
        return FileResponse(BASE_DIR / "app/templates/login.html")
    return FileResponse(BASE_DIR / "app/templates/meal.html")


async def meal_history_page(request: Request):
    """Serve meal history page"""
    if not request.session.get("access_token"):
        return FileResponse(BASE_DIR / "app/templates/login.html")
    return FileResponse(BASE_DIR / "app/templates/meal_history.html")


async def log_meal_ai(request: Request):
    """Log meal using AI"""
    try:
        token = request.session.get("access_token")
        if not token:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
        data = await request.json()
        api = get_api_client()
        
        # Call backend AI meal logging
        response = await api.post(
            "/api/meals-ai/log-ai",
            data,
            token=token
        )
        
        await api.close()
        
        return JSONResponse({
            "success": True,
            "message": "Meal logged successfully",
            "meal": response
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


async def log_meal_manual(request: Request):
    """Log meal manually"""
    try:
        token = request.session.get("access_token")
        if not token:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
        data = await request.json()
        api = get_api_client()
        
        # Call backend manual meal logging
        response = await api.post(
            "/api/meals-ai/log-manual",
            data,
            token=token
        )
        
        await api.close()
        
        return JSONResponse({
            "success": True,
            "message": "Meal logged successfully",
            "meal": response
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


async def get_meals(request: Request):
    """Get all meals for user"""
    try:
        token = request.session.get("access_token")
        if not token:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
        api = get_api_client()
        
        # Get meals from backend
        response = await api.get(
            "/api/meals/all",
            token=token
        )
        
        await api.close()
        
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


routes = [
    Route("/", endpoint=meal_page, methods=["GET"]),
    Route("/history", endpoint=meal_history_page, methods=["GET"]),
    Route("/log-ai", endpoint=log_meal_ai, methods=["POST"]),
    Route("/log-manual", endpoint=log_meal_manual, methods=["POST"]),
    Route("/list", endpoint=get_meals, methods=["GET"]),
]
