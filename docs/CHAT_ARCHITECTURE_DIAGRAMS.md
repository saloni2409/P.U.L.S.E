# Chat-Based Meal Logging - Architecture Diagram

## System Architecture Visualization

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    MealChatWindow Component                       │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │  ChatMessages                                           │    │   │
│  │  │  - Display bot & user messages                          │    │   │
│  │  │  - Inline MealItemsTable (when parser agent responds)   │    │   │
│  │  │  - Inline NutritionTable (when nutrition agent responds)│    │   │
│  │  │  - Display action buttons                               │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  │                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │  MealItemsTable                                         │    │   │
│  │  │  - Editable table for meal items                        │    │   │
│  │  │  - Inline edit on double-click                          │    │   │
│  │  │  - Add/remove rows                                      │    │   │
│  │  │  - [✓ Confirm] [✎ Edit] buttons                        │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  │                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │  UserInputField                                         │    │   │
│  │  │  - Text input for user messages                         │    │   │
│  │  │  - Send button                                          │    │   │
│  │  │  - Disabled during agent processing                     │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  useMealChat() Hook                                                       │
│  - Manages chat state                                                     │
│  - Handles API calls                                                      │
│  - Manages session_id                                                     │
└──────────────────────────────────────────────────────────────────────────┘
                                  ↑
                                  ↓ HTTP/JSON
┌──────────────────────────────────────────────────────────────────────────┐
│                    BACKEND API LAYER (FastAPI)                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Routes: /api/meals-ai/chat/                                    │   │
│  │  - POST /start         → Initialize session                     │   │
│  │  - POST /message       → Send message to agents                 │   │
│  │  - PUT  /confirm-items → User confirms parsed items             │   │
│  │  - PUT  /edit-items    → User edits items                       │   │
│  │  - POST /save          → Save meal to database                  │   │
│  │  - GET  /session/{id}  → Get session state                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  Dependency Injection:                                                    │
│  - get_current_user_id (JWT)                                             │
│  - get_db (Database Session)                                             │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
                                  ↑
                                  ↓
┌──────────────────────────────────────────────────────────────────────────┐
│              AGENT ORCHESTRATOR (Conversation Manager)                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                   ChatSessionManager                            │    │
│  │  - Maintains session state                                      │    │
│  │  - Routes messages to appropriate agent                         │    │
│  │  - Manages conversation history                                 │    │
│  │  - Decides next agent in pipeline                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Root Agent      │  │  Parser Agent    │  │  Nutrition Agent │      │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤      │
│  │ • Greet user     │  │ • Parse items    │  │ • Lookup nutrition│     │
│  │ • Collect meal   │  │ • Structure data │  │ • Calculate macros│     │
│  │ • Ask questions  │  │ • Validate qty   │  │ • Show nutrition  │     │
│  │ • Suggest help   │  │ • Format table   │  │ • Suggest edits   │     │
│  │ • Transition     │  │ • Ask confirm    │  │ • Prepare for save│     │
│  │                  │  │                  │  │                   │     │
│  │ State:           │  │ State:           │  │ State:            │     │
│  │ collecting       │  │ parsing          │  │ nutrition         │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│         ↓                      ↓                      ↓                   │
│    "What did you        "Structured meal      "Nutrition data"           │
│     eat today?"         items confirmed"       calculated"              │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
                                  ↑
                                  ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                    GOOGLE GENERATIVE AI (Gemini)                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  • Multi-turn conversations                                              │
│  • Context-aware responses                                               │
│  • Structured data extraction                                            │
│  • Validation & error handling                                           │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
                                  ↑
                                  ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                      TOOLS & DATA SOURCES                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────┐  ┌──────────────────────┐                     │
│  │  Food Lookup Tool    │  │ Nutrition Calculator │                     │
│  ├──────────────────────┤  ├──────────────────────┤                     │
│  │ • Search FoodDB      │  │ • Calculate macros   │                     │
│  │ • Get serving sizes  │  │ • Handle units       │                     │
│  │ • Match food names   │  │ • Aggregate totals   │                     │
│  └──────────────────────┘  └──────────────────────┘                     │
│         ↓                            ↓                                    │
│     ┌────────────────────────────────────────┐                           │
│     │    SQLite Database                     │                           │
│     ├────────────────────────────────────────┤                           │
│     │ • FoodDatabase (calories, macros)      │                           │
│     │ • MealEntry & MealItem (save)          │                           │
│     │ • Macronutrients (store details)       │                           │
│     │ • DailyNutritionSummary (update)       │                           │
│     └────────────────────────────────────────┘                           │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

## State Flow Diagram

```
┌─────────────────┐
│   START         │
└────────┬────────┘
         │
         ↓
┌──────────────────────────────┐
│  SESSION INITIALIZED         │
│  - session_id created        │
│  - Empty conversation        │
│  - state = "collecting"      │
└────────┬─────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│  ROOT AGENT ACTIVE           │
│  - Greet user                │
│  - Ask meal type             │
│  - Ask meal description      │
│  - Ask detailed questions    │
│  - Parse responses           │
└────────┬─────────────────────┘
         │ User provides all info
         ↓
┌──────────────────────────────┐
│  TRANSITION TO PARSER        │
│  - state = "parsing"         │
│  - Extract meal items        │
│  - Structure & validate      │
│  - Create items table        │
└────────┬─────────────────────┘
         │
         ├─────────────────────────────┐
         │                             │
         ↓                             ↓
    [User Confirms]            [User Edits]
         │                             │
         ↓                             ↓
┌──────────────────────────────┐   Edit Mode
│  TRANSITION TO NUTRITION     │   (inline edit)
│  - state = "nutrition"       │       │
│  - Lookup food nutrition     │       │
│  - Calculate macros          │       │
│  - Aggregate totals          │       │
└────────┬─────────────────────┘       │
         │                             │
         ↑─────────────────────────────┘
         │
         ├─────────────────────────────┐
         │                             │
         ↓                             ↓
    [User Saves]              [User Recalculates]
         │                             │
         ↓                             ↓
┌──────────────────────────────┐   Recalc
│  SAVE TO DATABASE            │   Nutrition
│  - Create MealEntry          │       │
│  - Create MealItems          │       │
│  - Create Macronutrients     │       │
│  - Update DailySummary       │       │
│  - state = "complete"        │       │
└────────┬─────────────────────┘       │
         │                             │
         ↓                             ↓
┌──────────────────────────────┐   Return to
│  SUCCESS / SHOW CONFIRMATION │   Nutrition
│  - Close chat window         │   Display
│  - Show saved meal summary   │       │
│  - Redirect to meals page    │       │
└──────────────────────────────┘       │
                                       ↑
                                       │
                                   Loop back

```

## Message Flow Example

```
Timeline: User logs "Chicken Biryani with raita"

1. Frontend → Backend: POST /api/meals-ai/chat/start
   Response: { session_id: "sess_123", initial_message: "Hi! What did you eat?" }

2. Frontend → Backend: POST /api/meals-ai/chat/message
   { session_id: "sess_123", user_message: "Chicken biryani with raita" }
   Response: {
     agent: "root_agent",
     message: "Great! How much biryani did you have? And was it with ghee?",
     next_agent: "root_agent"
   }

3. Frontend → Backend: POST /api/meals-ai/chat/message
   { session_id: "sess_123", user_message: "1.5 cups biryani, with ghee, and a cup of raita" }
   Response: {
     agent: "root_agent",
     message: "Perfect! Any specific meat or protein? Any side dishes?",
     next_agent: "root_agent"
   }

4. Frontend → Backend: POST /api/meals-ai/chat/message
   { session_id: "sess_123", user_message: "It's with chicken, no sides" }
   Response: {
     agent: "parser_agent",
     message: "Let me organize what you told me...",
     structured_data: {
       meal_type: "LUNCH",
       meal_description: "Chicken biryani with ghee and raita",
       meal_items: [
         { food_name: "Biryani, chicken", qty: 1.5, unit: "CUPS" },
         { food_name: "Raita", qty: 1, unit: "CUPS" },
         { food_name: "Ghee", qty: 1, unit: "TABLESPOONS" }
       ]
     },
     action_buttons: ["confirm", "edit"]
   }

5. Frontend displays table, user clicks "Confirm"
   Frontend → Backend: PUT /api/meals-ai/chat/confirm-items
   { session_id: "sess_123", meal_items: [...] }
   Response: {
     agent: "nutrition_agent",
     message: "Here's the nutrition breakdown...",
     nutrition_data: {
       items: [
         { food_name: "Biryani", cals: 450, protein: 25, carbs: 55, fat: 15 },
         { food_name: "Raita", cals: 80, protein: 5, carbs: 6, fat: 4 },
         { food_name: "Ghee", cals: 216, protein: 0, carbs: 0, fat: 24 }
       ],
       total: { cals: 746, protein: 30, carbs: 61, fat: 43 }
     },
     action_buttons: ["save", "edit_items", "recalculate"]
   }

6. User clicks "Save"
   Frontend → Backend: POST /api/meals-ai/chat/save
   { session_id: "sess_123", meal_data: {...} }
   Response: {
     success: true,
     meal_id: "meal_456",
     message: "Meal saved successfully!"
   }

7. Frontend closes chat, redirects to meals page with saved meal visible
```

## Backend Module Structure

```
backend/app/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py              # Abstract base class
│   ├── root_meal_agent.py          # Conversation manager
│   ├── meal_parser_agent.py        # Structure & tabulate
│   ├── nutrition_agent.py          # Macro/calorie lookup
│   ├── chat_session_manager.py     # Session orchestration
│   ├── chat_memory.py              # Memory management
│   ├── prompts/
│   │   ├── root_agent_prompt.py
│   │   ├── parser_agent_prompt.py
│   │   └── nutrition_agent_prompt.py
│   └── tools/
│       ├── __init__.py
│       ├── food_lookup.py          # Search & match foods
│       ├── nutrition_calculator.py # Macro calculations
│       └── usda_lookup.py          # Optional external API
│
├── routes/
│   ├── meals_ai_chat.py            # New chat endpoints
│   └── meals_ai.py                 # Existing AI endpoints
│
├── core/
│   └── google_ai_service.py        # Google Gemini wrapper
│
└── schemas/
    └── chat_schemas.py             # Chat request/response DTOs
```

---

**Ready for implementation confirmation?**
