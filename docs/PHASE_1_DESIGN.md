# P.U.L.S.E - Phase 1 Design Document
## Meal Logging & Nutrition Analysis System

---

## 1. Executive Summary

**Project Name:** P.U.L.S.E (Personal Unified Lifestyle & Sustenance Engine)  
**Phase:** Phase 1 - Meal Logging & Macro/Calorie Analysis  
**Timeline:** Initial Development Phase  
**Objective:** Create a user-friendly web application for logging meals and automatically analyzing macronutrient and calorie content using AI-powered agentic code.

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Web UI)                        │
│              Built with UV (Python Web Framework)            │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐   ┌──────────┐   ┌─────────────┐
    │ Meal    │   │ Analysis │   │ Dashboard   │
    │ Logging │   │ View     │   │ & Reports   │
    │ Forms   │   │          │   │             │
    └────┬────┘   └────┬─────┘   └─────┬───────┘
         │             │               │
         └─────────────┼───────────────┘
                       │
         ┌─────────────▼───────────────┐
         │    FastAPI Backend Server    │
         │  (Python with FastAPI)       │
         └─────────────┬───────────────┘
                       │
         ┌─────────────┼───────────────┐
         │             │               │
         ▼             ▼               ▼
    ┌─────────┐  ┌──────────┐   ┌─────────────┐
    │ REST    │  │ Agentic  │   │ Data        │
    │ APIs    │  │ Processing   │ Validation  │
    │         │  │ (LLM-based)  │             │
    └────┬────┘  └────┬─────┘   └─────┬───────┘
         │             │               │
         └─────────────┼───────────────┘
                       │
         ┌─────────────▼───────────────┐
         │   SQLite Database           │
         │  (Structured OOP Models)    │
         └─────────────────────────────┘
```

---

## 3. Data Model - Object-Oriented Design

### 3.1 Core Entities

#### **3.1.1 User Entity**
```python
class User:
    - user_id: UUID (Primary Key)
    - username: str (unique)
    - email: str (unique)
    - password_hash: str
    - created_at: datetime
    - updated_at: datetime
    - dietary_preferences: JSON (vegetarian, vegan, keto, etc.)
    - daily_calorie_goal: int (optional)
    - macro_targets: MacroTargets (reference)
```

#### **3.1.2 MealEntry Entity**
```python
class MealEntry:
    - meal_id: UUID (Primary Key)
    - user_id: UUID (Foreign Key → User)
    - meal_type: enum (BREAKFAST, LUNCH, DINNER, SNACK)
    - meal_description: str (raw user input)
    - meal_date: date
    - meal_time: time
    - is_processed: bool
    - original_log: str (raw input before processing)
    - created_at: datetime
    - updated_at: datetime
    - meal_items: [MealItem] (one-to-many)
```

#### **3.1.3 MealItem Entity**
```python
class MealItem:
    - item_id: UUID (Primary Key)
    - meal_id: UUID (Foreign Key → MealEntry)
    - food_name: str
    - quantity: float
    - unit: enum (GRAMS, ML, CUPS, PIECES, OUNCES)
    - calories: float
    - macros: Macronutrients (reference)
    - is_verified: bool
    - source: enum (USER_INPUT, AGENTIC_IDENTIFIED, MANUAL_CORRECTION)
    - confidence_score: float (0.0-1.0, for agentic processing)
```

#### **3.1.4 Macronutrients Entity**
```python
class Macronutrients:
    - macro_id: UUID (Primary Key)
    - item_id: UUID (Foreign Key → MealItem)
    - protein_grams: float
    - carbs_grams: float
    - fat_grams: float
    - fiber_grams: float
    - sugar_grams: float
    - sodium_mg: float
    - created_at: datetime
```

#### **3.1.5 FoodDatabase Entity**
```python
class FoodDatabase:
    - food_id: UUID (Primary Key)
    - food_name: str (unique per serving_size)
    - serving_size: float
    - serving_unit: enum
    - calories_per_serving: float
    - macros: Macronutrients (reference)
    - category: enum (FRUIT, VEGETABLE, PROTEIN, GRAIN, DAIRY, etc.)
    - verified_by_usda: bool
    - created_at: datetime
```

#### **3.1.6 MacroTargets Entity**
```python
class MacroTargets:
    - target_id: UUID (Primary Key)
    - user_id: UUID (Foreign Key → User)
    - daily_calorie_goal: int
    - protein_percent: float (% of calories)
    - carbs_percent: float (% of calories)
    - fat_percent: float (% of calories)
    - created_at: datetime
    - updated_at: datetime
```

#### **3.1.7 DailyNutritionSummary Entity**
```python
class DailyNutritionSummary:
    - summary_id: UUID (Primary Key)
    - user_id: UUID (Foreign Key → User)
    - date: date (unique per user)
    - total_calories: float
    - total_protein: float
    - total_carbs: float
    - total_fat: float
    - total_fiber: float
    - meal_count: int
    - created_at: datetime
    - updated_at: datetime
```

---

## 4. Agentic Code Architecture

### 4.1 Meal Processing Pipeline

The agentic system processes user meal logs to extract structured nutritional data:

```
User Input (Text)
       ↓
┌──────────────────────────────────────┐
│  Meal Parsing Agent                  │
│  - Identify meal items               │
│  - Extract quantities & units        │
│  - Normalize food names              │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Nutrition Lookup Agent              │
│  - Search food database              │
│  - Match similar foods               │
│  - Fetch macro data                  │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Validation & Correction Agent       │
│  - Verify accuracy                   │
│  - Flag uncertainties                │
│  - Suggest corrections               │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Data Storage Agent                  │
│  - Store in MealEntry & MealItem     │
│  - Update daily summary              │
│  - Maintain consistency              │
└──────────────────────────────────────┘
```

### 4.2 Agentic Processing Features

- **Natural Language Understanding:** Parse free-form meal descriptions
- **Intelligent Matching:** Find foods in database with fuzzy matching
- **Macro Calculation:** Auto-calculate nutritional content from quantities
- **Confidence Scoring:** Track accuracy of automated identifications
- **User Feedback Loop:** Allow corrections to improve future parsing
- **Context Awareness:** Learn user preferences and common meals

---

## 5. Backend API Specification (FastAPI)

### 5.1 Core Endpoints

#### **Authentication**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Token refresh

#### **Meal Management**
- `POST /api/meals/log` - Log a new meal (triggers agentic processing)
- `GET /api/meals/all` - Get all meals for user
- `GET /api/meals/{meal_id}` - Get specific meal details
- `PUT /api/meals/{meal_id}` - Update meal entry
- `DELETE /api/meals/{meal_id}` - Delete meal entry

#### **Meal Item Management**
- `GET /api/meals/{meal_id}/items` - Get items in meal
- `POST /api/meals/{meal_id}/items` - Add item to meal
- `PUT /api/meals/{meal_id}/items/{item_id}` - Update meal item
- `DELETE /api/meals/{meal_id}/items/{item_id}` - Delete meal item

#### **Analysis & Reporting**
- `GET /api/nutrition/daily/{date}` - Get daily nutrition summary
- `GET /api/nutrition/weekly` - Get weekly summary
- `GET /api/nutrition/stats` - Get user nutrition statistics
- `GET /api/macros/today` - Get today's macro progress

#### **User Settings**
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `GET /api/user/targets` - Get macro targets
- `PUT /api/user/targets` - Update macro targets

#### **Food Database**
- `GET /api/foods/search?q={query}` - Search food database
- `GET /api/foods/{food_id}` - Get food details
- `POST /api/foods` - Add new food to database (admin)

---

## 6. Frontend UI Components (UV Framework)

### 6.1 Pages & Components

1. **Dashboard/Home**
   - Daily nutrition summary
   - Progress toward goals
   - Quick meal logging button
   - Recent meals list

2. **Meal Logging Page**
   - Free-form text input for meal description
   - Auto-processing indicator
   - Identified items list
   - Quantity & unit selectors
   - Macro breakdown display
   - Confirm & Save button

3. **Meal History Page**
   - Filterable list of all logged meals
   - Search functionality
   - Edit/delete options
   - Meal details view

4. **Analytics Page**
   - Daily/weekly/monthly charts
   - Macro distribution pie charts
   - Calorie trend graphs
   - Goal progress visualization

5. **Settings Page**
   - User profile management
   - Daily calorie & macro targets
   - Dietary preferences
   - Account management

6. **Food Database Page**
   - Search and browse foods
   - View macro information
   - Suggest new foods

---

## 7. Database Schema (SQLite)

### 7.1 Tables

```sql
-- Users Table
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    dietary_preferences JSON,
    daily_calorie_goal INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Macro Targets Table
CREATE TABLE macro_targets (
    target_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    daily_calorie_goal INTEGER,
    protein_percent REAL,
    carbs_percent REAL,
    fat_percent REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Meal Entries Table
CREATE TABLE meal_entries (
    meal_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    meal_description TEXT NOT NULL,
    meal_date DATE NOT NULL,
    meal_time TIME,
    is_processed BOOLEAN DEFAULT FALSE,
    original_log TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Meal Items Table
CREATE TABLE meal_items (
    item_id TEXT PRIMARY KEY,
    meal_id TEXT NOT NULL,
    food_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    calories REAL,
    is_verified BOOLEAN DEFAULT FALSE,
    source TEXT,
    confidence_score REAL DEFAULT 1.0,
    FOREIGN KEY (meal_id) REFERENCES meal_entries(meal_id)
);

-- Macronutrients Table
CREATE TABLE macronutrients (
    macro_id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL,
    protein_grams REAL,
    carbs_grams REAL,
    fat_grams REAL,
    fiber_grams REAL,
    sugar_grams REAL,
    sodium_mg REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES meal_items(item_id)
);

-- Food Database Table
CREATE TABLE food_database (
    food_id TEXT PRIMARY KEY,
    food_name TEXT NOT NULL,
    serving_size REAL NOT NULL,
    serving_unit TEXT NOT NULL,
    calories_per_serving REAL,
    category TEXT,
    verified_by_usda BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(food_name, serving_size)
);

-- Daily Nutrition Summary Table
CREATE TABLE daily_nutrition_summary (
    summary_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    total_calories REAL DEFAULT 0,
    total_protein REAL DEFAULT 0,
    total_carbs REAL DEFAULT 0,
    total_fat REAL DEFAULT 0,
    total_fiber REAL DEFAULT 0,
    meal_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

## 8. Technology Stack Summary

### Backend
- **Framework:** FastAPI (Python)
- **Database:** SQLite with ORM (SQLAlchemy)
- **Authentication:** JWT tokens
- **AI/Agentic Processing:** Local LLM model (modular design for easy switching)
- **Validation:** Pydantic
- **Async Support:** asyncio

**Modularity:** All LLM integrations abstracted behind service interface for easy provider switching (Claude → GPT → Local → etc.)

### Frontend
- **Framework:** UV (Python Web Framework)
- **UI Library:** Bootstrap or Tailwind CSS
- **HTTP Client:** Fetch API / axios
- **State Management:** Simple state management or Context API equivalent

### Development Tools
- **Package Manager:** pip / uv
- **Version Control:** Git
- **Environment:** Python 3.9+
- **Database Tools:** sqlite3 CLI / DB Browser
- **LLM Tools:** Ollama or similar for local model serving

---

## 9. Phase 1 Implementation Roadmap

### Stage 1: Foundation (Week 1)
- [ ] Set up FastAPI backend structure
- [ ] Create SQLite database schema
- [ ] Implement user authentication (register/login)
- [ ] Set up ORM models (SQLAlchemy)

### Stage 2: Meal Logging (Week 2)
- [ ] Build meal logging REST API endpoints
- [ ] Implement basic meal validation
- [ ] Create meal history retrieval
- [ ] Build food search API

### Stage 3: Agentic Processing (Week 3)
- [ ] Integrate LLM for meal parsing
- [ ] Build macro calculation engine
- [ ] Implement confidence scoring
- [ ] Add data validation layer

### Stage 4: Frontend UI (Week 4)
- [ ] Set up UV frontend project
- [ ] Build meal logging form
- [ ] Create dashboard with summary
- [ ] Implement navigation & layout

### Stage 5: Analytics & Polish (Week 5)
- [ ] Build daily/weekly summaries
- [ ] Create visualization components
- [ ] Implement error handling
- [ ] Add user feedback mechanisms

### Stage 6: Testing & Deployment (Week 6)
- [ ] Unit tests for backend
- [ ] Integration tests
- [ ] UI testing
- [ ] Documentation & deployment prep

---

## 10. Key Assumptions & Constraints

### Assumptions
1. Users will input meal descriptions in natural language (English)
2. The LLM will have sufficient accuracy for macro identification
3. Users have access to standard food database information
4. Phase 1 focuses on single-user experience (multi-user in future phases)

### Constraints
1. SQLite suitable for Phase 1; migration to PostgreSQL in Phase 2
2. No offline functionality in Phase 1
3. Basic UI without advanced analytics in Phase 1
4. No mobile app in Phase 1 (web-only)
5. Rate limiting on agentic processing to manage LLM costs

---

## 11. Success Metrics (Phase 1)

- ✅ User can log meals via text description
- ✅ System accurately identifies macros for 80%+ of common foods
- ✅ Daily nutrition summary calculates correctly
- ✅ UI is responsive and user-friendly
- ✅ System handles 100+ meal entries per user
- ✅ Response time < 2 seconds for meal processing

---

## 12. Questions for Approval

✅ **APPROVED DECISIONS:**

1. **Technology Stack:** FastAPI + SQLite + UV with modular architecture
2. **LLM Integration:** Local LLM model (Ollama or similar) with modular service interface
3. **Food Database:** Start empty - users create food items as needed
4. **Implementation:** Begin Stage 1 immediately

**IMPLEMENTATION NOTES:**
- All LLM integrations abstracted behind service interface for easy switching
- All external service integrations use dependency injection for modularity
- Database schema supports adding pre-populated data in future phases
- Food database grows organically as users log meals

---

**Document Version:** 1.1  
**Last Updated:** December 23, 2025  
**Status:** ✅ APPROVED - Implementation Started
