# Chat Meal Logging - Data Models & Schemas

## 📊 Backend Data Models

### 1. ChatSession Model (New)

```python
# backend/app/models/__init__.py (add to existing)

class ChatSession(Base):
    """Session for chat-based meal logging"""
    __tablename__ = "chat_sessions"
    
    session_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.user_id"), nullable=False)
    
    # Conversation state
    state = Column(String, default="collecting")  # collecting, parsing, nutrition, complete
    conversation_history = Column(JSON)  # List of messages
    current_step = Column(Integer, default=0)
    
    # Meal being logged
    meal_data = Column(JSON)  # Serialized MealData
    structured_items = Column(JSON)  # Parsed meal items
    nutrition_data = Column(JSON)  # Calculated nutrition
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Auto-cleanup old sessions
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
```

### 2. Updated User Model

```python
# Add to User model
class User(Base):
    # ... existing fields ...
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
```

---

## 🔄 Request/Response Schemas

### Pydantic Schemas

```python
# backend/app/schemas/chat_schemas.py (New file)

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

# ============= Chat Session =============

class ChatStartRequest(BaseModel):
    """Start a new chat session"""
    meal_type: Optional[Literal["BREAKFAST", "LUNCH", "DINNER", "SNACK"]] = None
    meal_date: Optional[str] = None  # YYYY-MM-DD, defaults to today


class ChatStartResponse(BaseModel):
    """Response when starting chat"""
    session_id: str
    initial_message: str
    state: str


# ============= Messages =============

class ChatMessageRequest(BaseModel):
    """Send a message in chat"""
    session_id: str
    user_message: str


class ChatMessage(BaseModel):
    """Single chat message"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    data: Optional[dict] = None  # Additional structured data


class MessageResponse(BaseModel):
    """Response to user message"""
    session_id: str
    agent: Literal["root_agent", "parser_agent", "nutrition_agent"]
    message: str
    state: str
    action_buttons: List[str]  # ["confirm", "edit", "save", "recalculate"]
    
    # Optional structured data based on agent
    structured_data: Optional["StructuredMealData"] = None
    nutrition_data: Optional["NutritionData"] = None


# ============= Meal Data =============

class MealItemData(BaseModel):
    """Structured meal item"""
    food_name: str
    quantity: float
    unit: str
    calories: Optional[float] = None
    description: Optional[str] = None
    ingredients: Optional[dict] = None
    toppings: Optional[List[str]] = None


class StructuredMealData(BaseModel):
    """Structured meal from parser agent"""
    meal_type: str
    meal_description: str
    meal_date: str
    meal_time: Optional[str] = None
    meal_items: List[MealItemData]


class ConfirmItemsRequest(BaseModel):
    """User confirms parsed items"""
    session_id: str
    meal_items: List[MealItemData]


class EditItemsRequest(BaseModel):
    """User edits items"""
    session_id: str
    meal_items: List[MealItemData]


# ============= Nutrition Data =============

class ItemNutrition(BaseModel):
    """Nutrition for single item"""
    food_name: str
    quantity: float
    unit: str
    calories: float
    protein_grams: float
    carbs_grams: float
    fat_grams: float
    fiber_grams: Optional[float] = None
    sugar_grams: Optional[float] = None
    sodium_mg: Optional[float] = None


class NutritionData(BaseModel):
    """Aggregated nutrition data"""
    items: List[ItemNutrition]
    total: ItemNutrition  # Aggregated totals


class SaveMealRequest(BaseModel):
    """Save meal to database"""
    session_id: str
    meal_data: StructuredMealData
    nutrition_data: NutritionData


class SaveMealResponse(BaseModel):
    """Response after saving meal"""
    success: bool
    meal_id: str
    message: str


# ============= Session Management =============

class ChatSessionResponse(BaseModel):
    """Get session state"""
    session_id: str
    user_id: str
    state: str
    conversation_history: List[ChatMessage]
    structured_data: Optional[StructuredMealData] = None
    nutrition_data: Optional[NutritionData] = None
    created_at: datetime
    last_accessed_at: datetime
```

---

## 🤖 Agent Internal Data Structures

### Agent Context

```python
# backend/app/agents/chat_memory.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Message:
    """Single message in conversation"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    agent: Optional[str] = None  # Which agent responded
    data: Optional[Dict] = None


@dataclass
class AgentContext:
    """Context passed between agents"""
    session_id: str
    user_id: str
    state: str  # "collecting", "parsing", "nutrition", "complete"
    conversation_history: List[Message] = field(default_factory=list)
    
    # Parsed meal data
    meal_type: Optional[str] = None
    meal_description: Optional[str] = None
    meal_date: Optional[str] = None
    meal_time: Optional[str] = None
    
    # Structured items (from parser)
    structured_items: Optional[List[Dict]] = None
    
    # Nutrition (from nutrition agent)
    nutrition_data: Optional[Dict] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_message(self, role: str, content: str, agent: Optional[str] = None, data: Optional[Dict] = None):
        """Add message to history"""
        self.conversation_history.append(
            Message(role=role, content=content, agent=agent, data=data)
        )
    
    def get_conversation_string(self) -> str:
        """Get formatted conversation for LLM"""
        output = []
        for msg in self.conversation_history:
            output.append(f"{msg.role.upper()}: {msg.content}")
        return "\n".join(output)
```

---

## 🗄️ Database Relationships

```
User (1) ──── (N) ChatSession
             │
             ├── conversation_history (JSON)
             ├── meal_data (JSON)
             ├── structured_items (JSON)
             └── nutrition_data (JSON)

(When saved)
            │
            ├── MealEntry (1)
            │    └── (N) MealItem
            │         └── (1) Macronutrients
            │
            └── DailyNutritionSummary (updated)
```

---

## 🔐 API Request/Response Examples

### Example 1: Start Chat

**Request:**
```json
POST /api/meals-ai/chat/start
{
  "meal_type": null,
  "meal_date": "2025-01-23"
}
```

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "initial_message": "Hi! I'd love to help you log your meal. What did you eat today?",
  "state": "collecting"
}
```

### Example 2: Send Message

**Request:**
```json
POST /api/meals-ai/chat/message
{
  "session_id": "sess_abc123def456",
  "user_message": "I had chicken biryani with raita, about 1.5 cups"
}
```

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "agent": "root_agent",
  "message": "Nice! How much raita did you have? And was there any ghee or oil used in the biryani?",
  "state": "collecting",
  "action_buttons": [],
  "structured_data": null,
  "nutrition_data": null
}
```

### Example 3: Confirm Items

**Request:**
```json
PUT /api/meals-ai/chat/confirm-items
{
  "session_id": "sess_abc123def456",
  "meal_items": [
    {
      "food_name": "Biryani, chicken",
      "quantity": 1.5,
      "unit": "CUPS",
      "calories": 450
    },
    {
      "food_name": "Raita",
      "quantity": 1,
      "unit": "CUPS",
      "calories": 80
    },
    {
      "food_name": "Ghee",
      "quantity": 1,
      "unit": "TABLESPOONS",
      "calories": 216
    }
  ]
}
```

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "agent": "nutrition_agent",
  "message": "Here's the nutrition breakdown for your meal:",
  "state": "nutrition",
  "action_buttons": ["save", "edit_items", "recalculate"],
  "structured_data": null,
  "nutrition_data": {
    "items": [
      {
        "food_name": "Biryani, chicken",
        "quantity": 1.5,
        "unit": "CUPS",
        "calories": 450,
        "protein_grams": 20,
        "carbs_grams": 55,
        "fat_grams": 15
      },
      {
        "food_name": "Raita",
        "quantity": 1,
        "unit": "CUPS",
        "calories": 80,
        "protein_grams": 5,
        "carbs_grams": 6,
        "fat_grams": 4
      },
      {
        "food_name": "Ghee",
        "quantity": 1,
        "unit": "TABLESPOONS",
        "calories": 216,
        "protein_grams": 0,
        "carbs_grams": 0,
        "fat_grams": 24
      }
    ],
    "total": {
      "food_name": "Total",
      "quantity": 0,
      "unit": "",
      "calories": 746,
      "protein_grams": 25,
      "carbs_grams": 61,
      "fat_grams": 43
    }
  }
}
```

### Example 4: Save Meal

**Request:**
```json
POST /api/meals-ai/chat/save
{
  "session_id": "sess_abc123def456",
  "meal_data": {
    "meal_type": "LUNCH",
    "meal_description": "Chicken biryani with raita and ghee",
    "meal_date": "2025-01-23",
    "meal_time": "13:30",
    "meal_items": [...]
  },
  "nutrition_data": {...}
}
```

**Response:**
```json
{
  "success": true,
  "meal_id": "meal_xyz789",
  "message": "✅ Meal saved successfully! Your lunch has been logged."
}
```

---

## 🔄 State Transitions

```
State Diagram:
┌─────────────┐
│  collecting │  (Root Agent active)
│             │  - Gathering meal info
└──────┬──────┘
       │ [Enough info collected]
       ↓
┌─────────────┐
│  parsing    │  (Parser Agent active)
│             │  - Structuring items
└──────┬──────┘
       │ [User confirms]
       ↓
┌─────────────┐
│  nutrition  │  (Nutrition Agent active)
│             │  - Calculating macros
└──────┬──────┘
       │ [User saves]
       ↓
┌─────────────┐
│  complete   │  (Chat ends)
│             │  - Meal saved to DB
└─────────────┘
```

---

## 🔑 Key Design Decisions

| Aspect | Design | Reason |
|--------|--------|--------|
| Session Storage | In-Memory dict | Simple for MVP, can migrate to Redis |
| Conversation History | JSON in DB | Persists for audit, can review later |
| Meal Data Storage | JSON during chat | Flexible for structured data |
| State Management | Explicit state field | Clear transitions, easier debugging |
| Nutrition Precision | Float values | Flexibility for fractional amounts |
| Meal Save | Converts to MealEntry | Consistent with existing schema |

---

**Ready to start implementation?**
