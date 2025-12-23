# P.U.L.S.E - Personal Unified Lifestyle & Sustenance Engine

A comprehensive health app for tracking meals, analyzing macronutrients, and managing nutritional goals with AI-powered meal parsing.

## 🎉 Project Status: Phase 1 Complete ✅

All 4 development stages are complete and the application is ready for use!

**P.U.L.S.E** is a multi-phase health and nutrition tracking application with intelligent meal logging powered by AI agents.

### Phase 1: Meal Logging & Nutrition Analysis ✅ COMPLETE
- ✅ Backend API with FastAPI (25+ endpoints)
- ✅ SQLite database with 7 ORM entities
- ✅ User authentication (JWT with bcrypt)
- ✅ Meal logging & management
- ✅ Daily/weekly nutrition summaries
- ✅ AI-powered meal parsing (Ollama/LLM integration)
- ✅ Frontend UI with Starlette (responsive design)

### Features Implemented

**Stage 1: Foundation** ✅
- FastAPI server setup
- SQLite database with relationships
- JWT authentication
- User registration & login

**Stage 2: Meal Logging** ✅
- RESTful meal management APIs
- Meal item tracking
- Nutrition aggregation
- Food database with search
- Daily summaries

**Stage 3: Agentic Processing** ✅
- Local LLM integration (Ollama)
- Natural language meal parsing
- Automatic macro/calorie extraction
- Confidence scoring system
- Multi-provider LLM abstraction (local/OpenAI/Anthropic)
- Meal validation & enrichment

**Stage 4: Frontend UI** ✅
- Starlette ASGI web framework
- User authentication pages (login/register)
- Dashboard with nutrition stats
- Meal logging interface (AI & manual)
- Meal history view
- User settings panel
- Bootstrap 5 responsive design
- Custom CSS styling
- JavaScript API client with token management

## Quick Start

### Prerequisites
- Python 3.9+
- SQLite3
- Ollama (for local LLM) - [Download](https://ollama.ai)
- pip or UV package manager

### Setup Ollama (For AI Features)

```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull llama2
```

### Installation

```bash
# Navigate to the workspace
cd /Users/saloni/GIT/P.U.L.S.E

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -e .
cd ..

# Install frontend dependencies
cd frontend
pip install -e .
cd ..
```

### Running the Application

```bash
# Start backend server (Terminal 1)
cd backend
python main.py
# Server runs on http://localhost:8000
# API docs: http://localhost:8000/docs

# Start frontend server (Terminal 2)
cd frontend
python -m uvicorn app:app --port 8001
python -m uvicorn app:app --host 0.0.0.0 --port 8001
# Frontend runs on http://localhost:8001
```

## Project Structure

```
P.U.L.S.E/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── core/                # Config, security, database, LLM
│   │   ├── models/              # SQLAlchemy ORM (7 entities)
│   │   ├── schemas/             # Pydantic validation
│   │   ├── routes/              # API endpoints
│   │   │   ├── __init__.py      # Auth routes
│   │   │   ├── meals.py         # Meal CRUD
│   │   │   ├── meals_ai.py      # AI meal parsing
│   │   │   ├── nutrition.py     # Analytics
│   │   │   └── foods.py         # Food database
│   │   ├── services/            # Business logic
│   │   │   ├── meal_service.py
│   │   │   ├── nutrition_service.py
│   │   │   ├── validation_service.py
│   │   │   └── meal_processing_service.py
│   │   ├── agents/              # LLM meal parsing
│   │   └── utils/
│   ├── main.py                  # FastAPI app
│   ├── requirements.txt          # Dependencies
│   ├── .env.example             # Config template
│   └── pyproject.toml
│
├── frontend/                     # Starlette ASGI web framework (Stage 4) ✅
│   ├── app/
│   │   ├── routes/              # Request handlers
│   │   │   ├── auth_routes.py   # Login/register/logout
│   │   │   ├── dashboard_routes.py
│   │   │   ├── meal_routes.py
│   │   │   └── settings_routes.py
│   │   ├── templates/           # Jinja2 HTML templates
│   │   │   ├── base.html        # Layout template
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   ├── dashboard.html
│   │   │   ├── meal.html        # Meal logging
│   │   │   ├── meal_history.html
│   │   │   └── settings.html
│   │   ├── static/              # Assets
│   │   │   ├── css/
│   │   │   │   └── style.css    # Custom styling
│   │   │   └── js/
│   │   │       └── app.js       # Frontend logic & API client
│   │   └── utils/
│   │       └── __init__.py      # AsyncAPIClient
│   ├── app.py                   # Starlette ASGI app
│   ├── requirements.txt
│   └── .env.example
│
├── docs/                        # Documentation
│   ├── PHASE_1_DESIGN.md        # Full system design
│   ├── STAGE_1_COMPLETE.md      # Auth & foundation
│   ├── STAGE_2_COMPLETE.md      # Meal logging
│   ├── STAGE_3_COMPLETE.md      # AI parsing
│   ├── STAGE_3_SUMMARY.md       # Quick reference
│   └── DESIGN_SUMMARY.md
│
└── .github/
    └── copilot-instructions.md
```

## API Documentation

Interactive API docs available at `http://localhost:8000/docs`

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@example.com","password":"pass123"}'

# Login (get token)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'
```

### AI Meal Logging
```bash
TOKEN="your_token_here"

# Log meal with natural language (AI parsing)
curl -X POST http://localhost:8000/api/meals-ai/log-ai \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "meal_description": "Scrambled eggs with whole wheat toast and orange juice",
    "meal_type": "BREAKFAST",
    "meal_date": "2025-12-23"
  }'
```

### Get Daily Nutrition
```bash
curl -X GET http://localhost:8000/api/nutrition/daily/2025-12-23 \
  -H "Authorization: Bearer $TOKEN"
```

See `docs/STAGE_*.md` for complete API examples.

## Design Document

Complete system design available at: [`docs/PHASE_1_DESIGN.md`](./docs/PHASE_1_DESIGN.md)

## Development Status

### Completed ✅
- **Stage 1:** Backend foundation, authentication, database setup
- **Stage 2:** Meal logging, nutrition tracking, food database
- **Stage 3:** AI meal parsing, LLM abstraction, validation

### In Progress ⏳
- **Stage 4:** Frontend UI with UV framework

### Documentation
- [Phase 1 Design](./docs/PHASE_1_DESIGN.md) - Complete system design
- [Stage 1 Complete](./docs/STAGE_1_COMPLETE.md) - Auth & foundation details
- [Stage 2 Complete](./docs/STAGE_2_COMPLETE.md) - Meal logging API examples
- [Stage 3 Complete](./docs/STAGE_3_COMPLETE.md) - AI parsing & LLM integration
- [Stage 3 Summary](./docs/STAGE_3_SUMMARY.md) - Quick reference guide

## Technology Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **AI/LLM:** Ollama (local), with OpenAI & Anthropic support
- **Authentication:** JWT + bcrypt
- **Frontend:** UV framework (Stage 4)
- **Database:** SQLite with 7 ORM entities
- **Async:** Python asyncio for non-blocking operations

## Features

### Meal Tracking
- ✅ Natural language meal logging
- ✅ Automatic item extraction
- ✅ Manual item entry
- ✅ Calorie & macro tracking
- ✅ Meal history

### AI Integration
- ✅ Local LLM via Ollama
- ✅ Multi-provider support (easy switching)
- ✅ Confidence scoring
- ✅ Database matching & enrichment
- ✅ Graceful fallbacks

### Analytics
- ✅ Daily nutrition summaries
- ✅ Weekly/monthly trends
- ✅ Macro breakdowns
- ✅ Progress tracking

### Data Integrity
- ✅ User isolation (JWT scoped)
- ✅ Data validation
- ✅ Macro-calorie consistency checks
- ✅ Range validation

## Next Steps

Phase 1 is complete! Future enhancements include:
- **Phase 2:** Advanced analytics, meal planning, social features
- **Phase 3:** Mobile app (React Native), barcode scanning
- **Phase 4:** Recipe database, dietary plans, grocery lists
- **Phase 5:** PostgreSQL migration, production deployment

## Complete Documentation

- **[PHASE_1_COMPLETE.md](docs/PHASE_1_COMPLETE.md)** - Full Phase 1 summary
- **[PHASE_1_DESIGN.md](docs/PHASE_1_DESIGN.md)** - System design & architecture
- **[STAGE_4_COMPLETE.md](docs/STAGE_4_COMPLETE.md)** - Frontend UI details
- **[STAGE_3_COMPLETE.md](docs/STAGE_3_COMPLETE.md)** - AI processing system
- **[STAGE_2_COMPLETE.md](docs/STAGE_2_COMPLETE.md)** - Meal logging APIs
- **[STAGE_1_COMPLETE.md](docs/STAGE_1_COMPLETE.md)** - Authentication & foundation

## License

MIT License - See LICENSE file for details

## Contributing

Development follows a staged approach with documentation at each phase. New phases require design review and approval.

## Support

For technical questions or issues, refer to the relevant documentation in `/docs/` or check the API documentation at `http://localhost:8000/docs` (when running the backend).

