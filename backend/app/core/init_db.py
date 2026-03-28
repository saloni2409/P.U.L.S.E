"""Database initialization script to create all tables"""

from app.core.database import engine, Base
from app.models import (
    User, 
    MacroTargets, 
    MealEntry, 
    MealItem, 
    Macronutrients, 
    FoodDatabase, 
    DailyNutritionSummary,
    UserGeminiKey
)


def init_db():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")
    print(f"  - Users table")
    print(f"  - MacroTargets table")
    print(f"  - MealEntries table")
    print(f"  - MealItems table")
    print(f"  - Macronutrients table")
    print(f"  - FoodDatabase table")
    print(f"  - DailyNutritionSummary table")
    print(f"  - UserGeminiKeys table (NEW - BYOK)")


if __name__ == "__main__":
    init_db()
