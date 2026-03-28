# Chat System Developer Guide

Guide for extending and maintaining the P.U.L.S.E chat meal logging system.

## Architecture Overview

```
MVC Pattern:
├─ Models (SQLAlchemy ORM)
│  ├─ ChatSession
│  ├─ ChatMessage
│  └─ Relationships
│
├─ Services (Business Logic)
│  ├─ ChatSessionService
│  ├─ GoogleAIService
│  └─ BYOKService
│
└─ Views (REST API)
   ├─ Routes (FastAPI routers)
   └─ Schemas (Pydantic models)

Frontend:
├─ Pages (Next.js)
│  └─ chat/page.tsx
│
├─ Hooks (React)
│  └─ useChat.ts
│
└─ Components
   └─ UI elements
```

## Adding New Endpoints

### Example: Add "Reset Chat" Endpoint

#### 1. Add to Chat Routes (`app/routes/chat.py`)

```python
@router.post("/api/meals-ai/chat/reset/{session_id}")
async def reset_chat(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Reset chat to COLLECTING state"""
    try:
        result = await ChatSessionService.reset_session(
            db=db,
            user_id=user_id,
            session_id=session_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. Add Service Method (`app/services/chat_session_service.py`)

```python
@staticmethod
async def reset_session(
    db: Session,
    user_id: str,
    session_id: str
) -> Dict[str, Any]:
    """Reset chat to collecting state"""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user_id
    ).first()
    
    if not session:
        raise Exception("Session not found")
    
    # Clear parsed data but keep history
    session.session_state = "COLLECTING"
    session.parsed_meal_items = []
    session.nutrition_data = {}
    db.commit()
    
    # Add system message
    system_msg = ChatMessage(
        message_id=str(uuid.uuid4()),
        session_id=session_id,
        role="SYSTEM",
        content="Chat reset. Let's start fresh!",
        message_data={}
    )
    db.add(system_msg)
    db.commit()
    
    return {
        "session_id": session_id,
        "state": "COLLECTING",
        "message": "Chat reset. Let's start fresh!"
    }
```

#### 3. Update Frontend Hook (`hooks/useChat.ts`)

```typescript
const resetSession = useCallback(
    async (token: string) => {
        if (!sessionId) return null;
        
        try {
            setLoading(true);
            const res = await fetch(`/api/meals-ai/chat/reset/${sessionId}`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` }
            });
            
            if (!res.ok) throw new Error('Reset failed');
            
            setState('COLLECTING');
            setMealItems([]);
            setNutrition({});
            return await res.json();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Reset failed');
            return null;
        } finally {
            setLoading(false);
        }
    },
    [sessionId]
);

// Return from hook
return {
    // ... existing returns
    resetSession
};
```

#### 4. Use in UI

```tsx
<button
    onClick={() => resetSession(token)}
    className="px-4 py-2 bg-gray-600 text-white rounded"
>
    Reset Chat
</button>
```

## Extending AI Capabilities

### Adding New Agent Phase

Current flow: COLLECTING → CONFIRMING → SAVED

To add a REFINING phase:

#### 1. Update State in Service

```python
# In _handle_collecting_state()
if needs_refinement:
    session.session_state = "REFINING"
    return {
        "state": "REFINING",
        "message": "Let me refine these estimates based on typical portions..."
    }
```

#### 2. Add Handler Method

```python
@staticmethod
async def _handle_refining_state(
    db: Session,
    session: ChatSession,
    message: str,
    google_service: GoogleAIService
) -> Dict[str, Any]:
    """Handle REFINING state - ask user for validation"""
    # Use specialized prompt for refinement
    response = await google_service.chat_message([
        {"role": "user", "content": message}
    ])
    
    # Analyze response
    if "correct" in response.lower():
        session.session_state = "CONFIRMING"
    
    return {"state": session.session_state}
```

#### 3. Add to send_message Flow

```python
if session.session_state == "REFINING":
    return await ChatSessionService._handle_refining_state(...)
```

## Database Operations

### Adding New Field to ChatSession

```python
# 1. Update Model
class ChatSession(Base):
    # ... existing fields
    confidence_score = Column(Float, default=0.5)  # Add this

# 2. Migration (SQLite auto-updates, but be careful)
# For production: use Alembic migrations

# 3. Update Service
session.confidence_score = computed_confidence

# 4. Update Pydantic Schema if exposed via API
class ChatSessionResponse(BaseModel):
    # ... existing
    confidence_score: float
```

### Querying Examples

```python
# Get user's recent sessions
recent = db.query(ChatSession)\
    .filter(ChatSession.user_id == user_id)\
    .order_by(ChatSession.created_at.desc())\
    .limit(10)\
    .all()

# Find incomplete sessions
incomplete = db.query(ChatSession)\
    .filter(
        ChatSession.user_id == user_id,
        ChatSession.session_state == "COLLECTING"
    )\
    .all()

# Get conversation history
messages = db.query(ChatMessage)\
    .filter(ChatMessage.session_id == session_id)\
    .order_by(ChatMessage.created_at)\
    .all()
```

## Frontend Component Development

### Creating Editable Meal Item Row

```tsx
// components/MealItemRow.tsx
interface MealItemRowProps {
  item: MealItem;
  index: number;
  editable: boolean;
  onUpdate: (index: number, field: string, value: any) => void;
  onDelete: (index: number) => void;
}

export function MealItemRow({
  item,
  index,
  editable,
  onUpdate,
  onDelete
}: MealItemRowProps) {
  return (
    <tr className="border-b">
      <td className="px-4 py-2">
        <input
          type="text"
          value={item.food_name}
          onChange={(e) => onUpdate(index, 'food_name', e.target.value)}
          disabled={!editable}
          className="w-full px-2 py-1 border rounded disabled:bg-gray-100"
        />
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          value={item.quantity}
          onChange={(e) => onUpdate(index, 'quantity', parseFloat(e.target.value))}
          disabled={!editable}
          className="w-20 px-2 py-1 border rounded disabled:bg-gray-100"
        />
      </td>
      <td className="px-4 py-2">
        <select
          value={item.unit}
          onChange={(e) => onUpdate(index, 'unit', e.target.value)}
          disabled={!editable}
          className="px-2 py-1 border rounded disabled:bg-gray-100"
        >
          <option>pieces</option>
          <option>grams</option>
          <option>cups</option>
        </select>
      </td>
      <td className="px-4 py-2">{item.calories}</td>
      {editable && (
        <td className="px-4 py-2">
          <button
            onClick={() => onDelete(index)}
            className="text-red-600 hover:text-red-700"
          >
            Delete
          </button>
        </td>
      )}
    </tr>
  );
}
```

### Using in Chat Page

```tsx
<tbody>
  {mealItems.map((item, idx) => (
    <MealItemRow
      key={idx}
      item={item}
      index={idx}
      editable={editMode}
      onUpdate={handleUpdateMealItem}
      onDelete={handleRemoveItem}
    />
  ))}
</tbody>
```

## Testing New Features

### Unit Test Template

```python
# backend/tests/test_chat_new_feature.py

def test_new_feature():
    """Test new chat feature"""
    db = SessionLocal()
    
    try:
        # Setup
        user = create_test_user(db)
        session = create_test_session(db, user.user_id)
        
        # Test action
        result = some_new_function(db, session.session_id)
        
        # Assertions
        assert result is not None
        assert result.state == "EXPECTED_STATE"
        assert result.message is not None
        
    finally:
        db.close()
```

### Integration Test Template

```typescript
// Frontend test
test('new feature works', async () => {
  const { result } = renderHook(() => useChat());
  
  await act(async () => {
    await result.current.startSession('BREAKFAST', token);
    await result.current.someNewMethod(token);
  });
  
  expect(result.current.state).toBe('EXPECTED');
});
```

## Performance Optimization

### Caching Meal Parsing Results

```python
# In GoogleAIService
class GoogleAIService:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        self.cache = {}  # Add cache
    
    async def parse_meal_description(self, description: str):
        # Check cache first
        cache_key = hash(description)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Call API
        result = await self._call_gemini(...)
        
        # Store in cache
        self.cache[cache_key] = result
        return result
```

### Database Query Optimization

```python
# Before: Lazy loads messages
session = db.query(ChatSession).first()  # 1 query
messages = session.messages  # N queries

# After: Join eagerly
session = db.query(ChatSession)\
    .options(joinedload(ChatSession.messages))\
    .first()  # 1 query with JOIN
```

## Security Best Practices

### API Key Handling

```python
# ✅ CORRECT: Key only in memory
api_key = decrypt_key(user.encrypted_key)
service = GoogleAIService(api_key)
# api_key goes out of scope, garbage collected

# ❌ WRONG: Storing key in session/cache
session['api_key'] = decrypt_key(...)  # Never do this
```

### Input Validation

```python
# ✅ CORRECT: Validate before use
def send_message(message: str):
    # Pydantic validates automatically
    if len(message) > 1000:
        raise ValueError("Message too long")
```

### Error Messages

```python
# ✅ CORRECT: Generic error to user
HTTPException(status_code=500, detail="Something went wrong")

# ❌ WRONG: Exposing internal details
HTTPException(status_code=500, detail=f"API key {api_key} failed")
```

## Debugging Tips

### Enable Detailed Logging

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# In services
logger = logging.getLogger(__name__)
logger.debug(f"Processing message: {message}")
```

### Database Inspection

```python
# Query database directly
db = SessionLocal()
sessions = db.query(ChatSession).all()
for s in sessions:
    print(f"Session {s.session_id}: {s.session_state}")
    for m in s.messages:
        print(f"  {m.role}: {m.content[:50]}...")
```

### Frontend Debugging

```tsx
// In useChat hook
const sendMessage = useCallback(async (message: string, token: string) => {
  console.log('Sending:', message);
  
  const response = await fetch(...);
  const data = await response.json();
  
  console.log('Response:', data);
  console.log('State changed to:', data.state);
  
  // ... rest of method
}, []);
```

## Code Style Guidelines

### Python
```python
# Use type hints
async def process_message(
    db: Session,
    user_id: str,
    message: str
) -> Dict[str, Any]:
    """Process message with full docstring.
    
    Args:
        db: Database session
        user_id: User identifier
        message: User message text
    
    Returns:
        Response dictionary with state and message
    """
    pass

# Follow PEP 8
# - 4 spaces indentation
# - Max 88 characters per line
# - Docstrings for all functions
```

### TypeScript/React
```typescript
// Use type definitions
interface ChatMessage {
  message_id: string;
  role: 'USER' | 'ASSISTANT' | 'SYSTEM';
  content: string;
  created_at: string;
}

// Clear component structure
export function ChatComponent({ sessionId }: { sessionId: string }) {
  const [state, setState] = useState<ChatState>('COLLECTING');
  
  useEffect(() => {
    // Load data
  }, [sessionId]);
  
  return (
    // JSX
  );
}
```

## Common Pitfalls & Solutions

| Issue | Solution |
|-------|----------|
| State not updating | Check if modifying state directly instead of via setState |
| API timeout | Add timeout parameter to fetch calls |
| Session not found | Always validate session belongs to user |
| Memory leak | Cleanup subscriptions/timeouts in useEffect cleanup |
| DB locked (SQLite) | Ensure connections closed, use connection pool |
| API key exposed in logs | Never log API key, use sanitized messages |

## Release Checklist

Before deploying new features:

- [ ] Code review completed
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No console errors or warnings
- [ ] Performance tested
- [ ] Security review done
- [ ] Database migrations planned
- [ ] Backward compatibility checked
- [ ] Error messages user-friendly
- [ ] API contract documented

---

**Happy Coding! 🚀**
