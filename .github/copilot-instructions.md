# P.U.L.S.E Project Copilot Instructions

## Project Context
P.U.L.S.E is a health and nutrition tracking application with AI-powered meal logging.

**Current Phase:** Phase 1 - Meal Logging & Nutrition Analysis

**Technology Stack:**
- Backend: FastAPI (Python)
- Frontend: UV (Python web framework)
- Database: SQLite with SQLAlchemy ORM
- AI Processing: LLM-based agentic system for meal parsing

## Design Document Location
Complete design document with entity models, API specifications, and implementation roadmap:
- **Path:** `docs/PHASE_1_DESIGN.md`
- **Status:** Awaiting user approval

## Development Guidelines

### Before Implementation
1. User must review and approve `docs/PHASE_1_DESIGN.md`
2. User must confirm technology choices and timeline
3. All major decisions require user confirmation before coding

### Implementation Approach
- Follow the Phase 1 design document exactly
- Implement in stages as outlined in the roadmap
- Get explicit confirmation from user before moving to next stage
- Create comprehensive docstrings and type hints
- Follow PEP 8 style guide for Python code

### Code Organization
- Backend code in `backend/app/` with modular structure
- Frontend code in `frontend/` with template-based design
- Database models in `backend/app/models/`
- API routes in `backend/app/routes/`
- Agentic code in `backend/app/agents/`

### Key Design Points
- Object-oriented database design with 7 core entities
- Multi-agent pipeline for meal processing
- REST API with JWT authentication
- SQLite for Phase 1 (migrations to PostgreSQL planned for Phase 2)
- Confidence scoring for agentic processing accuracy

## Communication Protocol
1. Design approval required before any implementation
2. Each implementation stage requires confirmation
3. Any deviations from design must be approved
4. Regular progress updates provided

## Database Models
See `docs/PHASE_1_DESIGN.md` Section 3 for complete OOP entity design:
- User
- MealEntry
- MealItem
- Macronutrients
- FoodDatabase
- MacroTargets
- DailyNutritionSummary

## API Endpoints
See `docs/PHASE_1_DESIGN.md` Section 5 for complete API specification

## When to Ask for Clarification
- Any ambiguity in design document
- Questions about phase 1 vs phase 2 scope
- Technology alternative suggestions
- Timeline concerns
