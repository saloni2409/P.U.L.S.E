# Chat Meal Logging - Implementation Roadmap

## 📅 Implementation Timeline & Tasks

### ✅ Design Phase: COMPLETE ✅

**Documents Created:**
- ✅ CHAT_MEAL_LOGGING_DESIGN.md - Complete system design
- ✅ CHAT_ARCHITECTURE_DIAGRAMS.md - Visual architecture
- ✅ CHAT_DATA_MODELS.md - Data structures & schemas
- ✅ CHAT_DESIGN_CHECKLIST.md - Quick reference
- ✅ CHAT_UI_DESIGN.md - UI mockups & components
- ✅ CHAT_DESIGN_READY.md - Status overview

**Awaiting:** Your confirmation to proceed

---

## 🚀 Phase 1: Backend Infrastructure (Week 1 - 5 days)

### 1.1 Setup & Dependencies
```bash
# Add to backend/pyproject.toml:
google-generativeai >= 0.3.0
langchain >= 0.1.0 (optional)
redis >= 4.5.0 (optional for session storage)
```

### 1.2 Create Agent Module Structure
```
backend/app/agents/
├── __init__.py              # Export all agents
├── base_agent.py            # Abstract BaseAgent class
├── root_meal_agent.py       # Conversation manager
├── meal_parser_agent.py     # Item structuring
├── nutrition_agent.py       # Nutrition lookup
├── chat_session_manager.py  # Orchestrator
├── chat_memory.py           # Context management
│
├── prompts/
│   ├── __init__.py
│   ├── root_agent_prompt.py     # System prompts
│   ├── parser_agent_prompt.py
│   └── nutrition_agent_prompt.py
│
└── tools/
    ├── __init__.py
    ├── food_lookup.py           # Search FoodDatabase
    ├── nutrition_calculator.py  # Macro calculations
    └── usda_lookup.py           # Optional external API
```

### 1.3 Google Gemini Service
**File:** `backend/app/core/google_ai_service.py`
```python
class GoogleAIService:
    """Wrapper for Google Generative AI (Gemini)"""
    
    async def generate(
        self, 
        prompt: str, 
        conversation_history: List[Message],
        response_format: str = "text"  # "text" or "json"
    ) -> str:
        """Generate response from Gemini"""
    
    async def extract_structured_data(
        self,
        prompt: str,
        json_schema: dict
    ) -> dict:
        """Extract structured JSON from Gemini"""
```

### 1.4 Base Agent Class
**File:** `backend/app/agents/base_agent.py`
```python
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, llm_service: GoogleAIService):
        self.name = name
        self.llm_service = llm_service
    
    @abstractmethod
    async def process(
        self, 
        context: AgentContext
    ) -> dict:
        """Process agent logic and return response"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent"""
        pass
```

### 1.5 Root Agent Implementation
**File:** `backend/app/agents/root_meal_agent.py`
```python
class RootMealAgent(BaseAgent):
    """Manages initial meal information collection"""
    
    async def process(self, context: AgentContext) -> dict:
        """
        Collect meal info through conversation
        Returns: { message, next_step, ready_for_parsing }
        """
        
    def get_system_prompt(self) -> str:
        """Prompt for conversational meal collection"""
```

### 1.6 Parser Agent Implementation
**File:** `backend/app/agents/meal_parser_agent.py`
```python
class MealParserAgent(BaseAgent):
    """Structures meal items from conversation"""
    
    async def process(self, context: AgentContext) -> dict:
        """
        Parse and structure meal items
        Returns: { 
            message, 
            structured_data: MealItemData[],
            next_step
        }
        """
```

### 1.7 Nutrition Agent Implementation
**File:** `backend/app/agents/nutrition_agent.py`
```python
class NutritionAgent(BaseAgent):
    """Calculates nutrition for meal items"""
    
    def __init__(self, llm_service, tools: ToolsRegistry):
        super().__init__("nutrition_agent", llm_service)
        self.tools = tools  # food_lookup, nutrition_calculator
    
    async def process(self, context: AgentContext) -> dict:
        """
        Calculate nutrition for each item
        Returns: { 
            message, 
            nutrition_data: NutritionData,
            next_step
        }
        """
```

### 1.8 Chat Session Manager
**File:** `backend/app/agents/chat_session_manager.py`
```python
class ChatSessionManager:
    """Orchestrates agent flow"""
    
    async def start_session(self, user_id: str, meal_date: str) -> str:
        """Initialize new session, return session_id"""
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str
    ) -> dict:
        """Route message to appropriate agent"""
    
    async def confirm_items(
        self, 
        session_id: str, 
        meal_items: List[MealItemData]
    ) -> dict:
        """User confirmed items, proceed to nutrition"""
    
    async def save_meal(
        self, 
        session_id: str, 
        meal_data: StructuredMealData
    ) -> str:
        """Save meal to database, return meal_id"""
```

### 1.9 Tools Implementation
**File:** `backend/app/agents/tools/food_lookup.py`
```python
class FoodLookupTool:
    """Search FoodDatabase for food items"""
    
    @staticmethod
    async def search(
        food_name: str, 
        db: Session
    ) -> List[FoodDatabaseResponse]:
        """Search for food in database"""
    
    @staticmethod
    async def get_best_match(
        food_name: str, 
        db: Session
    ) -> Optional[FoodDatabaseResponse]:
        """Find best matching food"""
```

**File:** `backend/app/agents/tools/nutrition_calculator.py`
```python
class NutritionCalculatorTool:
    """Calculate nutrition based on quantity"""
    
    @staticmethod
    async def calculate_nutrition(
        food: FoodDatabase,
        quantity: float,
        unit: str
    ) -> ItemNutrition:
        """Calculate nutrition for given quantity"""
    
    @staticmethod
    async def aggregate_nutrition(
        items: List[ItemNutrition]
    ) -> ItemNutrition:
        """Sum nutrition for multiple items"""
```

### 1.10 Database Models Update
**File:** `backend/app/models/__init__.py`
```python
# Add ChatSession model:
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    session_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.user_id"))
    state = Column(String, default="collecting")
    conversation_history = Column(JSON)
    meal_data = Column(JSON)
    nutrition_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
```

### 1.11 Chat API Endpoints
**File:** `backend/app/routes/meals_ai_chat.py` (new file)
```python
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.core.security import get_current_user_id

router = APIRouter(prefix="/api/meals-ai/chat", tags=["chat"])

@router.post("/start")
async def start_chat_session(...):
    """POST /api/meals-ai/chat/start"""

@router.post("/message")
async def send_message(...):
    """POST /api/meals-ai/chat/message"""

@router.put("/confirm-items")
async def confirm_items(...):
    """PUT /api/meals-ai/chat/confirm-items"""

@router.put("/edit-items")
async def edit_items(...):
    """PUT /api/meals-ai/chat/edit-items"""

@router.post("/save")
async def save_meal(...):
    """POST /api/meals-ai/chat/save"""

@router.get("/session/{session_id}")
async def get_session(...):
    """GET /api/meals-ai/chat/session/{session_id}"""
```

### 1.12 Settings & Configuration
**File:** `backend/app/core/settings.py` (update)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Google API
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-pro"
    
    # Chat settings
    CHAT_SESSION_TIMEOUT: int = 3600  # 1 hour
    CHAT_MAX_HISTORY: int = 50
    CHAT_SESSION_STORAGE: str = "memory"  # "memory" or "redis"
    
    class Config:
        env_file = ".env"
```

### 1.13 Update main.py
**File:** `backend/main.py` (update)
```python
# Add new router:
from app.routes.meals_ai_chat import router as meals_ai_chat_router

app.include_router(meals_ai_chat_router)
```

### 1.14 Prompts Folder
**File:** `backend/app/agents/prompts/root_agent_prompt.py`
```python
SYSTEM_PROMPT = """
You are a friendly meal logging assistant. Your goal is to gather detailed 
information about what the user ate, including:
- Main dish description
- Quantity/portion size
- Cooking method
- Ingredients and toppings
- Any sauces or additions

Ask clarifying questions one at a time to get complete information.
Be conversational and helpful.
"""
```

---

## 🧪 Phase 1 Testing Checklist

- [ ] Base agent class instantiates correctly
- [ ] Root agent asks clarifying questions
- [ ] Parser agent structures meal items correctly
- [ ] Nutrition agent calculates macros accurately
- [ ] Chat session manager routes between agents
- [ ] Food lookup tool finds foods in database
- [ ] All API endpoints respond correctly
- [ ] Error handling works for missing foods
- [ ] Session timeout works
- [ ] Database inserts meal correctly

---

## 🎨 Phase 2: Frontend Components (Week 1-2 - 5-6 days)

### 2.1 Chat Window Component
**File:** `frontendV2/src/components/meal-chat/MealChatWindow.tsx`
```tsx
export default function MealChatWindow({
  isOpen: boolean,
  onClose: () => void
}) {
  const { session_id, messages, loading } = useMealChat()
  
  return (
    <div className="fixed bottom-4 right-4 w-96 h-96 bg-white rounded-lg shadow-lg">
      {/* Implementation */}
    </div>
  )
}
```

### 2.2 Chat Messages Component
**File:** `frontendV2/src/components/meal-chat/ChatMessages.tsx`
```tsx
export default function ChatMessages({
  messages: ChatMessage[],
  loading: boolean
}) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {/* Message rendering */}
    </div>
  )
}
```

### 2.3 Meal Items Table Component
**File:** `frontendV2/src/components/meal-chat/MealItemsTable.tsx`
```tsx
export default function MealItemsTable({
  items: MealItemData[],
  editable: boolean,
  onConfirm: (items) => void,
  onEdit: (items) => void
}) {
  return (
    <table className="w-full">
      {/* Table rendering */}
    </table>
  )
}
```

### 2.4 Nutrition Table Component
**File:** `frontendV2/src/components/meal-chat/NutritionTable.tsx`
```tsx
export default function NutritionTable({
  nutrition: NutritionData,
  onSave: () => void,
  onEdit: () => void
}) {
  return (
    <table className="w-full">
      {/* Table rendering */}
    </table>
  )
}
```

### 2.5 User Input Component
**File:** `frontendV2/src/components/meal-chat/UserInputField.tsx`
```tsx
export default function UserInputField({
  onSend: (message: string) => void,
  disabled: boolean
}) {
  return (
    <div className="flex gap-2">
      {/* Input field and send button */}
    </div>
  )
}
```

### 2.6 Chat Hook
**File:** `frontendV2/src/hooks/useMealChat.ts`
```typescript
export function useMealChat() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  
  const startChat = async () => {
    // POST /api/meals-ai/chat/start
  }
  
  const sendMessage = async (message: string) => {
    // POST /api/meals-ai/chat/message
  }
  
  const confirmItems = async (items: MealItemData[]) => {
    // PUT /api/meals-ai/chat/confirm-items
  }
  
  const saveMeal = async (mealData: StructuredMealData) => {
    // POST /api/meals-ai/chat/save
  }
  
  return { sessionId, messages, loading, startChat, sendMessage, confirmItems, saveMeal }
}
```

### 2.7 Chat Modal/Layout
**File:** `frontendV2/src/app/meals/chat/page.tsx`
```tsx
export default function MealChatPage() {
  const [isOpen, setIsOpen] = useState(true)
  
  return (
    <AuthLayout>
      <MealChatWindow isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </AuthLayout>
  )
}
```

### 2.8 Styling with Tailwind
All components use consistent Tailwind classes:
- Primary colors: primary-500, primary-600
- Success: success-500, success-600
- Danger: danger-500, danger-600
- Spacing: p-4, gap-4, etc.

---

## ✨ Phase 3: Integration & Testing (Week 2-3 - 3-4 days)

### 3.1 Backend Integration Tests
```python
# tests/test_chat_agents.py
- Test root agent message generation
- Test parser agent item extraction
- Test nutrition agent calculations
- Test chat session lifecycle
- Test all API endpoints
- Test error scenarios
```

### 3.2 Frontend Integration Tests
```typescript
// frontendV2/tests/chat.test.tsx
- Test MealChatWindow renders
- Test message sending
- Test table display
- Test save functionality
```

### 3.3 End-to-End Test
```
1. User opens chat
2. Bot greets user
3. User describes meal
4. Bot asks questions
5. User provides details
6. Bot shows structured items
7. User confirms
8. Bot shows nutrition
9. User saves
10. Meal appears in meals list
```

---

## 🚀 Phase 4: Polish & Deployment (Week 3 - 2-3 days)

### 4.1 Error Handling
- [ ] Handle food not found in database
- [ ] Handle invalid quantities
- [ ] Handle API failures
- [ ] Handle session timeouts
- [ ] Show user-friendly error messages

### 4.2 Performance
- [ ] Optimize table rendering (virtualization)
- [ ] Cache nutrition calculations
- [ ] Debounce edits
- [ ] Lazy load chat component

### 4.3 Polish
- [ ] Loading animations
- [ ] Toast notifications
- [ ] Success/error messages
- [ ] Mobile responsiveness
- [ ] Accessibility

### 4.4 Documentation
- [ ] Update API documentation
- [ ] Create user guide
- [ ] Document agent prompts
- [ ] Create troubleshooting guide

---

## 📊 Development Estimates

| Phase | Task | Days | Notes |
|-------|------|------|-------|
| 1 | Backend Infrastructure | 5 | Agents, endpoints, database |
| 1 | Testing | 2 | Unit & integration tests |
| 2 | Frontend Components | 5 | Chat UI, tables, forms |
| 2 | Integration | 2 | Connect frontend/backend |
| 3 | End-to-End Testing | 2 | Full user flows |
| 4 | Polish & Deploy | 3 | Errors, performance, UX |
| | **TOTAL** | **19 days** | ~4 weeks with buffer |

---

## 🔑 Key Success Criteria

✅ **Functional Requirements:**
- [ ] Multi-turn conversation works
- [ ] Meal items parsed correctly
- [ ] Nutrition calculated accurately
- [ ] Items can be edited in chat
- [ ] Meals save to database
- [ ] Full workflow end-to-end

✅ **Performance:**
- [ ] Chat responds in < 3 seconds
- [ ] Tables render smoothly
- [ ] No lag with 50+ messages
- [ ] Mobile loads in < 2 seconds

✅ **Quality:**
- [ ] 90%+ test coverage
- [ ] Zero critical bugs
- [ ] Graceful error handling
- [ ] Works on Chrome, Safari, Firefox

✅ **UX:**
- [ ] Intuitive conversation flow
- [ ] Clear action buttons
- [ ] Mobile responsive
- [ ] Accessible (WCAG AA)

---

## 📝 Pre-Implementation Checklist

Before starting Phase 1, confirm:

- [ ] Google Gemini API key obtained
- [ ] Team review design complete
- [ ] Database setup ready
- [ ] Backend environment configured
- [ ] Frontend environment ready
- [ ] Testing framework setup
- [ ] Deployment target identified

---

## 🎬 Getting Started

### To Begin Phase 1:

1. **Install dependencies:**
   ```bash
   cd backend
   pip install google-generativeai langchain redis
   ```

2. **Set environment variables:**
   ```bash
   GOOGLE_API_KEY=<your-gemini-api-key>
   GEMINI_MODEL=gemini-pro
   CHAT_SESSION_TIMEOUT=3600
   ```

3. **Create agent module:**
   ```bash
   mkdir -p backend/app/agents/tools
   mkdir -p backend/app/agents/prompts
   touch backend/app/agents/__init__.py
   ```

4. **Start with BaseAgent class**
   Then implement RootMealAgent
   Then Parser Agent
   Then Nutrition Agent
   Then Chat Session Manager
   Then API endpoints

5. **Test as you go**
   Unit test each agent
   Integration test full flow

---

## 🎯 Success Metrics

After implementation:

1. **Adoption**: Users prefer chat vs manual logging
2. **Accuracy**: Nutrition data 95%+ accurate
3. **Speed**: Logging takes < 2 minutes
4. **Satisfaction**: User NPS > 7/10
5. **Completeness**: Captures all meal details

---

**Ready to proceed with implementation? Confirm and I'll start Phase 1!** 🚀
