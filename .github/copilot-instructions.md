# P.U.L.S.E Copilot Instructions

**Phase:** Phase 1 Complete | **Status:** Production Ready  
P.U.L.S.E is a health/nutrition tracking app with AI-powered meal logging. This document guides AI agents through the architecture, patterns, and workflows essential for productive development.

## Quick Architecture

```
Frontend (Starlette/Python)    ←→    Backend (FastAPI)    ←→    SQLite + LLM
     Templates                         REST API (25+)              7 ORM entities
     Bootstrap 5                       JWT Auth                    Ollama/OpenAI
     Form handling                     Services layer              Multi-provider
```

## Critical Data Flow: Meal Logging to Nutrition Summary

**AI-Powered Meal Entry:**
1. User submits `/api/meals-ai/log-ai` with natural language (e.g., "2 eggs, oatmeal, banana")
2. `MealProcessingService.process_meal_with_agent()` calls `MealParsingAgent.parse_meal()`
3. Agent sends meal description to LLM (Ollama default) via `LLMService.generate()`
4. LLM returns JSON array: `[{food_name, quantity, unit, estimated_calories, confidence_score}]`
5. `MealValidationService.parse_and_enrich_meal()` enriches with FoodDatabase matches, adjusts confidence
6. Items inserted as `MealItem` with `Macronutrients` relationship; `MealEntry.is_processed=True`
7. `NutritionService` updates `DailyNutritionSummary` (aggregates daily totals)

**Manual Entry:** Uses `/api/meals-ai/log-manual` with explicit items, skips agent parsing.

## Project Structure

```
backend/app/
├── core/
│   ├── database.py          # SQLAlchemy session, Base class, init_db()
│   ├── llm_service.py       # Multi-provider LLM abstraction (Local/OpenAI/Anthropic)
│   ├── security.py          # JWT token creation/validation, password hashing (bcrypt)
│   └── settings.py          # Pydantic Settings from .env (database_url, secret_key, llm_*)
├── models/                  # SQLAlchemy ORM entities
│   └── __init__.py          # User, MealEntry, MealItem, Macronutrients, FoodDatabase, MacroTargets, DailyNutritionSummary
├── routes/                  # FastAPI routers
│   ├── __init__.py          # Auth (login, register, token refresh)
│   ├── meals.py             # CRUD: POST/GET/PUT/DELETE meal entries
│   ├── meals_ai.py          # AI endpoints: /log-ai, /log-manual
│   ├── nutrition.py         # Daily/weekly summaries
│   └── foods.py             # Search/add FoodDatabase entries
├── services/
│   ├── meal_processing_service.py   # Orchestrates agent + validation + DB writes
│   ├── meal_service.py              # Meal CRUD operations
│   ├── nutrition_service.py         # Calculates daily totals, summaries
│   └── validation_service.py        # Meal parsing, confidence scoring, enrichment
├── agents/
│   └── __init__.py          # MealParsingAgent: parse_meal(), enrich_with_nutrition()
│                            # Outputs FoodItemParsed, MealParseResult
└── schemas/                 # Pydantic models for request/response
    └── __init__.py          # UserCreate, MealEntryCreate, MealItemResponse, etc.

frontend/
├── app.py                   # Starlette ASGI entry (no longer used, see app/__init__.py)
└── app/
    ├── __init__.py          # Starlette app setup, CORS, static files, route includes
    ├── routes/
    │   ├── auth_routes.py   # GET /login, POST /register, GET /logout
    │   ├── meal_routes.py   # GET meal history, POST new meal (form), AI logging
    │   ├── dashboard_routes.py  # GET dashboard with daily nutrition
    │   └── settings_routes.py   # User preferences, macro targets
    └── templates/
        ├── base.html        # Bootstrap 5 layout, nav, JS API client
        ├── login.html, register.html
        ├── dashboard.html   # Daily totals, charts (Chart.js)
        └── meal.html        # Manual + AI meal logging forms

tests/
├── conftest.py              # Pytest fixtures: client, db_session, in-memory SQLite, LLM stubbing
├── test_auth_flow.py        # JWT, bcrypt, token validation
├── test_meal_crud.py        # Meal + item creation, updates
├── test_routes.py           # API endpoint tests
└── test_foods.py            # Food search, database
```

## Key Patterns & Conventions

### 1. **Async Service Layer Pattern**
All services expose static async methods that orchestrate DB operations and external calls:
```python
@staticmethod
async def process_meal_with_agent(db: Session, user_id: str, ...) -> MealEntry:
    # Always: parse/validate → create DB record → update summaries
```
**When adding features:** Keep services stateless; pass `db: Session` explicitly (no session caching).

### 2. **Confidence Scoring & Source Tracking**
- `MealItem.confidence_score` (0.0-1.0): How trusted is the agentic extraction?
- `MealItem.source`: "USER_INPUT" | "AGENTIC_IDENTIFIED" | "DATABASE_MATCHED"
- Rule: If food found in `FoodDatabase`, increase confidence +0.2, set source="DATABASE_MATCHED"
- **When enriching:** Always compute confidence; validation service flags items with score <0.6 for user review

### 3. **LLM Provider Abstraction**
`LLMService` wraps multiple providers (Local/OpenAI/Anthropic). Selection via `LLM_SERVICE` env var:
```python
# In llm_service.py: set _provider based on settings.llm_service
# Prompt must return JSON for parsing (see MealParsingAgent.PARSING_PROMPT)
```
**When calling LLM:** Always parse JSON response; handle malformed output gracefully.

### 4. **JWT + Bcrypt Security**
- Passwords hashed with bcrypt in `get_password_hash()` (security.py)
- Token claims: `{"sub": user_id, "exp": expiration_time}`
- Token extraction: `get_current_user_id()` dependency injects user_id from request header
- **On new endpoints:** Always use `user_id: str = Depends(get_current_user_id)` for auth check

### 5. **Pydantic + SQLAlchemy Separation**
- Schemas (request/response): `app/schemas/__init__.py` (Pydantic models)
- ORM models: `app/models/__init__.py` (SQLAlchemy declarative)
- **Never return ORM objects directly;** convert to schema via `.dict()` or create response schema

### 6. **Relationship Management**
Models use SQLAlchemy relationships with cascade delete (e.g., `cascade="all, delete-orphan"`):
```python
class MealEntry(Base):
    meal_items = relationship("MealItem", back_populates="meal_entry", cascade="all, delete-orphan")
```
**When deleting:** Deleting a meal cascades to items → macronutrients. Update daily summary after.

### 7. **Testing Pattern**
Tests use in-memory SQLite (`test_sqlite_backend.db`) with stubbed LLM:
```python
# conftest.py stubs LLMService._provider to return [] (no network calls)
# Fixtures: client (TestClient with DB override), db_session
```
**When writing tests:** Use `client` fixture for HTTP, `db_session` for direct DB access.

## Developer Workflows

### Running Locally
```bash
# Terminal 1: Backend
cd backend && python main.py          # FastAPI on :8000

# Terminal 2: Frontend
cd frontend && python -m uvicorn app:app --port 8001  # Starlette on :8001

# Terminal 3: Ollama (if using AI)
ollama serve                          # Runs on localhost:11434

# In another terminal:
ollama pull llama2                    # Download model
```

### Testing
```bash
cd backend
pytest tests/                         # All tests with in-memory DB
pytest tests/test_meal_crud.py -v    # Specific test file
```

### Environment Configuration
Backend `.env`:
```
DATABASE_URL=sqlite:///./pulse.db
LLM_SERVICE=local|openai|anthropic
LLM_LOCAL_ENDPOINT=http://localhost:11434
LLM_LOCAL_MODEL=llama2
SECRET_KEY=<dev-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
```

## Common Tasks

### Add a New API Endpoint
1. Define Pydantic schema in `app/schemas/__init__.py`
2. Add route function in `app/routes/<domain>.py`
3. Use `get_db` and `get_current_user_id` for DI
4. Call service layer; services handle all DB/LLM logic
5. Write test in `tests/test_routes.py` using `client` fixture

### Extend Meal Parsing
1. Modify `MealParsingAgent.PARSING_PROMPT` (set LLM task)
2. Update `FoodItemParsed` schema if new fields needed
3. Call `MealValidationService.parse_and_enrich_meal()` to enrich + validate
4. Test with local Ollama: `ollama pull llama2` then run tests

### Add Nutrition Calculation
1. Add logic to `NutritionService` (computes aggregates)
2. Called automatically by `MealProcessingService` after item creation
3. Updates `DailyNutritionSummary` for user + date
4. Ensure unique constraint on (user_id, date) is respected

## Code Style & Quality
- **Python:** PEP 8, type hints on all functions, docstrings (Google style)
- **Async:** Use `async def` + `await` in services; FastAPI handles thread pool
- **Error handling:** Service methods raise `Exception(msg)`; routes catch and return 500/400
- **DB access:** Always use provided `db: Session` from DI; no global session
- **Imports:** Group as stdlib → third-party → local; use relative imports in `app/`

## When Stuck or Uncertain
1. **Architecture questions?** Check data flow diagram above and `docs/PHASE_1_DESIGN.md`
2. **API contract unclear?** Look at existing route + schema pair (e.g., `meals.py` + `MealEntryCreate`)
3. **LLM integration?** See `MealParsingAgent.parse_meal()` + `LLMService.generate()` pattern
4. **DB design?** Reference `app/models/__init__.py` and use `db.query(Model).filter()` with SQLAlchemy
5. **Confidence scoring?** See `validation_service.py` - adjust score based on source & DB matches

---

**Last Updated:** Phase 1 Complete (25+ endpoints, 7 ORM entities, multi-provider LLM)
