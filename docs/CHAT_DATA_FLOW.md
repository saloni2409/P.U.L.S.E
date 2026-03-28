# Chat System Data Flow & Architecture

## High-Level Data Flow

```
USER INPUT (Chat Page)
    ↓
useChat Hook (State Management)
    ↓
API Call to Backend
    ↓
Chat Routes (Authentication & Validation)
    ↓
ChatSessionService (Business Logic)
    ├→ BYOK Service (Decrypt User Key)
    │   ↓
    ├→ GoogleAIService (Call Gemini)
    │   ├→ Parse Meal Description
    │   ├→ Calculate Nutrition
    │   └→ Generate Response
    │   ↓
    ├→ Database Operations
    │   ├→ Save ChatMessage
    │   ├→ Update ChatSession
    │   └→ Save MealEntry (on confirm)
    │   ↓
API Response
    ↓
Update Chat UI
    ↓
User Sees Results
```

## Detailed Message Flow Sequence

```
┌─────────────────┐                           ┌──────────────────┐
│  Frontend (UI)  │                           │  Backend (API)   │
└────────┬────────┘                           └────────┬─────────┘
         │                                             │
    1    │── POST /api/meals-ai/chat/start ──────────→│
         │       (meal_type: "BREAKFAST")             │
         │                                             │
         │                                    Create ChatSession
         │                                    Generate greeting
         │← ChatSession created with message ─────────│
         │                                             │
         │ (User sees: "Tell me what you ate...")     │
         │                                             │
    2    │ User types: "2 eggs and toast"             │
         │                                             │
         │── POST /send-message ──────────────────────→│
         │   (message: "2 eggs and toast")            │
         │                                             │
         │                                    GoogleAIService:
         │                                    • Call Gemini API
         │                                    • Parse meal items
         │                                    • Generate response
         │                                    
         │                                    Save ChatMessage
         │                                    (role: ASSISTANT)
         │← Response: "Great! How much..." ──────────│
         │                                             │
         │ (User sees: AI asking clarification)       │
         │                                             │
    3    │ User types: "1 cup with butter"            │
         │                                             │
         │── POST /send-message ──────────────────────→│
         │   (message: "1 cup with butter")           │
         │                                             │
         │                                    • Parse quantity
         │                                    • Extract items
         │                                    • Transition state
         │                                      to CONFIRMING
         │                                    • Get nutrition
         │← Response: Change state to       ─────────│
         │   CONFIRMING with meal items               │
         │                                             │
         │ (User sees: Editable meal table)           │
         │                                             │
    4    │ User edits items (if needed)               │
         │                                             │
         │── PUT /api/meal-items ─────────────────────→│
         │   (updated items array)                    │
         │                                             │
         │                                    Update ChatSession
         │← Confirmation ─────────────────────────────│
         │                                             │
    5    │ User clicks "Save Meal"                    │
         │                                             │
         │── POST /api/save ──────────────────────────→│
         │                                             │
         │                                    Create MealEntry
         │                                    Create MealItems
         │                                    Update summaries
         │                                    State → SAVED
         │← Meal saved + redirect ────────────────────│
         │                                             │
         └── Redirect to /meals ──────────────────────→
             (User sees: Meal added to log)
```

## Database Schema Diagram

```
users (existing)
├── user_id (PK)
├── username
├── email
└── password_hash

    ↑
    │ 1:N
    │

chat_sessions (NEW)
├── session_id (PK)
├── user_id (FK) ──────→ users.user_id
├── meal_type
├── session_state
├── parsed_meal_items (JSON)
├── nutrition_data (JSON)
└── timestamps

    ↑
    │ 1:N
    │

chat_messages (NEW)
├── message_id (PK)
├── session_id (FK) ──→ chat_sessions.session_id
├── role (USER/ASSISTANT/SYSTEM)
├── content
├── message_data (JSON)
└── created_at

    ↓
    │ When saved
    │

meal_entries (existing)
├── meal_id (PK)
├── user_id (FK)
├── meal_type
├── meal_description
└── meal_items (relationship)

    ↓
    │ 1:N
    │

meal_items (existing)
├── item_id (PK)
├── meal_id (FK)
├── food_name
├── quantity
├── unit
├── calories
└── macronutrients (relationship)
```

## State Machine

```
┌──────────────┐
│  COLLECTING  │  ← Initial state
│              │
│ User provides│
│ meal details │
│ AI asks Qs   │
└──────┬───────┘
       │ [When AI has enough info]
       ↓
┌──────────────┐
│ CONFIRMING   │
│              │
│ User edits   │
│ items in UI  │
└──────┬───────┘
       │
       ├─→ [Save] ──────┐
       │                 │
       └─→ [Cancel] ────┐│
                        ││
                        ↓↓
              ┌────────────────┐
              │ SAVED/CANCELLED│
              │                │
              │ End session    │
              │ Redirect user  │
              └────────────────┘
```

## API Endpoint Request/Response Flow

### 1. Start Chat
```
REQUEST:
POST /api/meals-ai/chat/start
{
  "meal_type": "BREAKFAST"
}

→ Authentication: JWT token required
→ Validation: meal_type must be valid
→ Action: Create ChatSession, generate greeting

RESPONSE:
{
  "session_id": "uuid-123",
  "user_id": "user-456",
  "meal_type": "BREAKFAST",
  "state": "COLLECTING",
  "message": "Tell me what you ate for breakfast!"
}
```

### 2. Send Message
```
REQUEST:
POST /api/meals-ai/chat/send-message/{session_id}
{
  "message": "I had 2 eggs and toast"
}

→ Get Session & User
→ Decrypt User's Gemini API Key
→ Send to GoogleAIService:
   • Build conversation history
   • Call Gemini API
   • Parse meal description
   • Determine next state
→ Save ChatMessage (both user + assistant)
→ Update ChatSession

RESPONSE:
{
  "message_id": "msg-789",
  "role": "ASSISTANT",
  "content": "Great! How much butter?",
  "state": "COLLECTING",
  "meal_items": [],
  "nutrition": {}
}
```

### 3. Get Summary (When Ready)
```
REQUEST:
GET /api/meals-ai/chat/summary/{session_id}

→ Load ChatSession
→ Parse stored meal_items JSON
→ Calculate nutrition totals

RESPONSE:
{
  "state": "CONFIRMING",
  "meal_items": [
    {
      "food_name": "Eggs",
      "quantity": 2,
      "unit": "pieces",
      "calories": 140
    },
    {
      "food_name": "Toast with Butter",
      "quantity": 1,
      "unit": "slice",
      "calories": 200
    }
  ],
  "nutrition": {
    "totals": {
      "calories": 340,
      "protein": 18.5,
      "carbs": 28,
      "fat": 18
    }
  }
}
```

### 4. Update Meal Items
```
REQUEST:
PUT /api/meals-ai/chat/meal-items/{session_id}
{
  "meal_items": [
    {
      "food_name": "Eggs",
      "quantity": 3,
      "unit": "pieces",
      "calories": 210
    },
    {
      "food_name": "Toast",
      "quantity": 1,
      "unit": "slice",
      "calories": 100
    }
  ]
}

→ Validate items
→ Calculate nutrition
→ Update ChatSession.parsed_meal_items
→ Update ChatSession.nutrition_data

RESPONSE:
{
  "state": "CONFIRMING",
  "meal_items": [...],
  "nutrition": {...}
}
```

### 5. Save Meal
```
REQUEST:
POST /api/meals-ai/chat/save/{session_id}

→ Get ChatSession with items
→ Create MealEntry
→ Create MealItems for each item
→ Update DailyNutritionSummary
→ Update ChatSession state → SAVED

RESPONSE:
{
  "session_id": "session-uuid",
  "state": "SAVED",
  "meal_id": "meal-entry-uuid"
}
```

## Component Interaction Diagram

```
┌────────────────────────────────────────────┐
│     Frontend (Next.js/React)              │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │     Chat Page (chat/page.tsx)        │ │
│  │  - Render messages                  │ │
│  │  - Message input form               │ │
│  │  - Meal items table (editable)      │ │
│  │  - Nutrition summary                │ │
│  └───────────┬──────────────────────────┘ │
│              │                             │
│              ↓                             │
│  ┌──────────────────────────────────────┐ │
│  │     useChat Hook (useChat.ts)        │ │
│  │  - Session state management         │ │
│  │  - API call orchestration           │ │
│  │  - Error handling                   │ │
│  └───────────┬──────────────────────────┘ │
│              │                             │
└──────────────┼─────────────────────────────┘
               │ HTTP/REST
               ↓
┌────────────────────────────────────────────┐
│     Backend (FastAPI)                     │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Chat Routes (routes/chat.py)        │ │
│  │  - 7 endpoints                       │ │
│  │  - JWT auth check                   │ │
│  │  - Request validation               │ │
│  └───────────┬──────────────────────────┘ │
│              │                             │
│              ↓                             │
│  ┌──────────────────────────────────────┐ │
│  │ ChatSessionService (orchestration)   │ │
│  │  - Session lifecycle                │ │
│  │  - State transitions                │ │
│  │  - Agent coordination               │ │
│  └─────┬────────────────────────────────┘ │
│        │                                  │
│   ┌────┴──────────────────────────┐      │
│   ↓                               ↓      │
│  ┌──────────────────┐  ┌─────────────────┐ │
│  │ GoogleAIService  │  │ BYOK Service    │ │
│  │  - Gemini API    │  │  - Decrypt key  │ │
│  │  - Meal parsing  │  │  - Key mgmt     │ │
│  │  - Nutrition cal │  └─────────────────┘ │
│  └──────────────────┘                     │
│        │                                  │
│        ↓                                  │
│  ┌──────────────────────────────────────┐ │
│  │  Database Operations                 │ │
│  │  - Save ChatMessage                 │ │
│  │  - Update ChatSession               │ │
│  │  - Create MealEntry (on save)       │ │
│  └──────────────────────────────────────┘ │
│        │                                  │
└────────┼──────────────────────────────────┘
         ↓
   ┌──────────────────┐
   │   SQLite DB     │
   │  ├─ users       │
   │  ├─ chat_sesh   │
   │  ├─ chat_msgs   │
   │  ├─ meal_entry  │
   │  └─ ...         │
   └──────────────────┘
        ↕
   External: Google Gemini API
```

## Security Flow

```
User Input (Message)
    ↓
POST /api/meals-ai/chat/send-message
    ↓
Extract JWT Token
    ↓
Verify Token Signature
    ↓
Extract user_id from Token Claims
    ↓
Load ChatSession (verify user_id matches)
    ↓
Get User's Encrypted Gemini Key from DB
    ↓
Decrypt Key (using master encryption key)
    ↓
Initialize GoogleAIService with Key
    ↓
Call Gemini API
    ↓
Destroy Key from Memory (__del__)
    ↓
Save Results to Database
    ↓
Return Response (no keys exposed)
```

## Error Handling Flow

```
User Action
    ↓
Try → Send API Request
    ↓
    ├─→ 400 Bad Request
    │   ├─ Invalid meal_type
    │   ├─ Invalid JSON
    │   └─ Missing required field
    │   ↓
    │   Show validation error to user
    │
    ├─→ 401 Unauthorized
    │   ├─ Invalid/expired token
    │   └─ Token missing
    │   ↓
    │   Redirect to /login
    │
    ├─→ 403 Forbidden
    │   ├─ No API key set
    │   └─ Session not found
    │   ↓
    │   Show "Set API key in settings" or "Session expired"
    │
    ├─→ 500 Server Error
    │   ├─ Gemini API error
    │   ├─ Database error
    │   └─ Unexpected error
    │   ↓
    │   Log error, show generic message, offer retry
    │
    └─→ 200 OK
        ↓
        Update UI with response
```

## Performance Characteristics

```
Operation               Time Range    Bottleneck
────────────────────────────────────────────────────
POST /start             100-300ms     DB insert
POST /send-message      2-5s          Gemini API
GET /messages           50-200ms      DB query
GET /summary            50-100ms      DB query
PUT /meal-items         50-100ms      DB update
POST /save              200-500ms     MealEntry creation
POST /cancel            50-100ms      DB update

Total for typical session:
  3-5 messages × 2-5s each = 6-25 seconds
```

## Scaling Considerations

```
Current Limits:
- SQLite: ~1000s concurrent sessions
- FastAPI: Limited by CPU/memory
- Gemini API: Rate limited by Google quota

Improvement Path:
SQLite → PostgreSQL
  │
  ├─ Connection pooling
  ├─ Better concurrency
  └─ Horizontal scaling

Add Caching Layer
  ├─ Redis for session state
  ├─ Food item caching
  └─ Nutrition calculations

Add Message Queue
  ├─ Async meal processing
  ├─ Batch operations
  └─ Retry logic
```

---

This completes the comprehensive data flow and architectural documentation for the chat system.
