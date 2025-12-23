"""P.U.L.S.E FastAPI Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer # Import HTTPBearer
from app.core.database import init_db
from app.core.settings import settings
from app.routes import router as auth_router
from app.routes.meals import router as meals_router
from app.routes.nutrition import router as nutrition_router
from app.routes.foods import router as foods_router
from app.routes.meals_ai import router as meals_ai_router

# Define the security scheme
security_schemes = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter your JWT token in the format 'Bearer <token>'"
    }
}

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="P.U.L.S.E API",
    description="Personal Unified Lifestyle & Sustenance Engine",
    version="0.3.0",
    openapi_extra={
        "components": {
            "securitySchemes": security_schemes
        },
        "security": [{"BearerAuth": []}]
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(auth_router)
app.include_router(meals_router)
app.include_router(nutrition_router)
app.include_router(foods_router)
app.include_router(meals_ai_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to P.U.L.S.E API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
