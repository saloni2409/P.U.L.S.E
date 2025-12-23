"""Authentication routes"""

from starlette.routing import Route
from starlette.responses import JSONResponse, FileResponse
from starlette.requests import Request
from pathlib import Path
from app.utils import get_api_client

BASE_DIR = Path(__file__).resolve().parent.parent.parent


async def login_page(request: Request):
    """Serve login page"""
    return FileResponse(BASE_DIR / "app/templates/login.html")


async def register_page(request: Request):
    """Serve registration page"""
    return FileResponse(BASE_DIR / "app/templates/register.html")


async def login(request: Request):
    """Handle login request"""
    try:
        data = await request.json()
        api = get_api_client()
        
        # Call backend login
        response = await api.post(endpoint="/api/auth/login", data=data)
        
        # Store token in session
        request.session["access_token"] = response["access_token"]
        request.session["token_type"] = response.get("token_type", "bearer")
        
        await api.close()
        
        return JSONResponse({
            "success": True,
            "message": "Login successful",
            "redirect": "/api/dashboard"
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


async def register(request: Request):
    """Handle registration request"""
    try:
        data = await request.json()
        api = get_api_client()
        
        # Call backend register
        response = await api.post(endpoint="/api/auth/register", data=data)
        
        await api.close()
        
        return JSONResponse({
            "success": True,
            "message": "Registration successful. Please login.",
            "redirect": "/login"
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)


async def logout(request: Request):
    """Handle logout"""
    request.session.clear()
    return JSONResponse({
        "success": True,
        "message": "Logged out successfully",
        "redirect": "/login"
    })


routes = [
    Route("/login", endpoint=login_page, methods=["GET"]),
    Route("/register", endpoint=register_page, methods=["GET"]),
    Route("/login", endpoint=login, methods=["POST"]),
    Route("/register", endpoint=register, methods=["POST"]),
    Route("/logout", endpoint=logout, methods=["POST"]),
]
