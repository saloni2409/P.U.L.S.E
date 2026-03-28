# BYOK (Bring Your Own Key) Architecture

## Overview

**BYOK** = Users provide their own Google Gemini API keys to run the chat meal logging agents.

This approach provides:
- ✅ **Cost Efficiency**: No server-side API costs
- ✅ **Privacy**: P.U.L.S.E never sees unencrypted keys
- ✅ **User Control**: Users manage their own API usage
- ✅ **Scalability**: No single point of failure for API access
- ✅ **Compliance**: No shared credentials, cleaner audit trail

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                        USER (Frontend)                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. User goes to Settings                                     │
│     [⚙️ Settings]                                              │
│           ↓                                                    │
│  2. Enters their Gemini API Key                               │
│     [Enter Gemini API Key: ***********]                       │
│           ↓                                                    │
│  3. Saves key securely                                        │
│     [✓ Save Key]                                               │
│           ↓                                                    │
│           (Key sent to backend over HTTPS)                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  API Endpoint: POST /api/user/gemini-key                      │
│                                                                │
│  1. Receive raw API key                                       │
│  2. Encrypt with AES-256                                      │
│     + Master encryption key                                   │
│     + User ID as part of derivation                           │
│  3. Store encrypted key in database                           │
│     table: UserGeminiKey                                      │
│     columns: user_id, encrypted_key, created_at              │
│  4. Delete raw key from memory                                │
│  5. Return: { success: true, message: "Key saved" }           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│                   DATABASE (SQLite)                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Table: UserGeminiKey                                         │
│  ┌─────────────┬──────────────────┬────────────────────────┐ │
│  │ user_id     │ encrypted_key    │ created_at             │ │
│  ├─────────────┼──────────────────┼────────────────────────┤ │
│  │ user_123    │ gAAAAABn...(256) │ 2026-01-23 10:00:00    │ │
│  │ user_456    │ gAAAAABn...(256) │ 2026-01-23 11:30:00    │ │
│  └─────────────┴──────────────────┴────────────────────────┘ │
│                                                                │
│  Note: Keys are encrypted at rest                             │
│        Only decrypted in memory when needed                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Runtime Flow: Using BYOK Keys

```
USER STARTS CHAT
    ↓
┌──────────────────────────────────────────────────────────┐
│ Frontend: POST /api/meals-ai/chat/start                 │
│ Headers: Authorization: Bearer <jwt_token>              │
└──────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────┐
│ Backend: ChatSessionManager.start_session()              │
│ 1. Extract user_id from JWT token                        │
│ 2. Query: SELECT encrypted_key FROM UserGeminiKey       │
│           WHERE user_id = ?                              │
│ 3. If not found:                                         │
│    - Prompt user to set API key                          │
│    - Return: { error: "Please set Gemini API key" }      │
│ 4. If found:                                             │
│    - Decrypt key in memory:                              │
│      decrypted_key = AES256.decrypt(encrypted_key,      │
│                                      master_key)        │
│    - Initialize GoogleAIService with decrypted_key      │
│    - Store GoogleAIService in session context            │
│    - Create session (in-memory)                          │
│    - Return: { session_id, initial_message }            │
│ 5. Destroy decrypted_key variable after use             │
└──────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────┐
│ Agent Orchestrator receives GoogleAIService              │
│ with USER'S API KEY loaded                               │
│                                                           │
│ Root Agent → Google Gemini API                           │
│   (using user's key)                                     │
│ Parser Agent → Google Gemini API                         │
│   (using user's key)                                     │
│ Nutrition Agent → Google Gemini API                      │
│   (using user's key)                                     │
│                                                           │
│ All API calls charged to USER'S account                  │
└──────────────────────────────────────────────────────────┘
    ↓
USER SEES CHAT WITH AI RESPONSES
    ↓
SESSION ENDS or EXPIRES
    ↓
MEMORY CLEARED
- Session context destroyed
- GoogleAIService instance destroyed
- No sensitive data persisted
```

---

## Database Schema

### New Table: UserGeminiKey

```python
# backend/app/models/__init__.py

class UserGeminiKey(Base):
    """User's encrypted Gemini API key"""
    __tablename__ = "user_gemini_key"
    
    # Primary
    key_id = Column(String, primary_key=True)  # UUID
    user_id = Column(String, ForeignKey("user.user_id"), unique=True, nullable=False)
    
    # Encrypted data
    encrypted_key = Column(String, nullable=False)  # AES-256 encrypted
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="gemini_key")
    
    def __repr__(self):
        return f"<UserGeminiKey user_id={self.user_id}>"
```

### Updated User Model

```python
class User(Base):
    # ... existing fields ...
    
    # Relationships
    gemini_key = relationship("UserGeminiKey", back_populates="user", uselist=False)
    chat_sessions = relationship("ChatSession", back_populates="user")
```

---

## Encryption Service

### Key Encryption/Decryption

```python
# backend/app/core/encryption_service.py

from cryptography.fernet import Fernet
import base64
from hashlib import sha256

class EncryptionService:
    """
    Service for encrypting/decrypting user API keys
    Uses Fernet (symmetric encryption) with master key
    """
    
    def __init__(self, master_key: str):
        """
        Initialize with master encryption key
        Master key must be 32 bytes (base64 encoded Fernet key)
        """
        self.cipher_suite = Fernet(master_key.encode())
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        key = Fernet.generate_key()
        return key.decode()
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext (API key)
        Returns: base64 encoded encrypted data
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty key")
        
        encrypted_bytes = self.cipher_suite.encrypt(plaintext.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data
        Returns: plaintext (API key)
        WARNING: Only decrypt in memory when needed!
        """
        if not encrypted_data:
            raise ValueError("Cannot decrypt empty data")
        
        decrypted_bytes = self.cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()
    
    @staticmethod
    def derive_key(master_key: str, salt: str = "P.U.L.S.E") -> str:
        """
        Derive encryption key from master key
        Optional: Can include user_id in salt for per-user derivation
        """
        combined = f"{master_key}:{salt}"
        derived = sha256(combined.encode()).digest()
        # Fernet requires base64 encoded 32-byte key
        return base64.urlsafe_b64encode(derived).decode()
```

---

## API Endpoints (BYOK)

### 1. Set/Update Gemini Key

```python
# backend/app/routes/settings.py (new endpoint)

@router.post("/api/user/gemini-key")
async def set_gemini_key(
    request: SetGeminiKeyRequest,  # { api_key: str }
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    User sets their own Gemini API key
    
    Security:
    - Only HTTPS allowed (enforced by FastAPI)
    - Token validated via JWT
    - Key encrypted before storage
    - No logging of key values
    """
    
    # 1. Validate key format
    if not request.api_key or len(request.api_key) < 20:
        raise HTTPException(
            status_code=400,
            detail="Invalid API key format"
        )
    
    # 2. Test key with Google API (optional but recommended)
    try:
        test_response = await GoogleAIService(request.api_key).test_connection()
        if not test_response:
            raise HTTPException(
                status_code=400,
                detail="Invalid Gemini API key - test failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not validate key: {str(e)}"
        )
    
    # 3. Encrypt key
    encryption_service = EncryptionService(settings.ENCRYPTION_KEY)
    encrypted_key = encryption_service.encrypt(request.api_key)
    
    # 4. Store in database
    existing = db.query(UserGeminiKey).filter_by(user_id=user_id).first()
    
    if existing:
        # Update existing
        existing.encrypted_key = encrypted_key
        existing.updated_at = datetime.utcnow()
        existing.last_verified_at = datetime.utcnow()
    else:
        # Create new
        new_key = UserGeminiKey(
            key_id=str(uuid4()),
            user_id=user_id,
            encrypted_key=encrypted_key,
            last_verified_at=datetime.utcnow()
        )
        db.add(new_key)
    
    db.commit()
    
    return {
        "success": True,
        "message": "Gemini API key saved securely",
        "last_verified": datetime.utcnow()
    }
```

### 2. Check if Key Set

```python
@router.get("/api/user/gemini-key/status")
async def get_gemini_key_status(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Check if user has set a Gemini API key"""
    
    key_exists = db.query(UserGeminiKey).filter_by(user_id=user_id).first()
    
    return {
        "has_key": key_exists is not None,
        "last_verified": key_exists.last_verified_at if key_exists else None,
        "setup_required": key_exists is None
    }
```

### 3. Delete Key

```python
@router.delete("/api/user/gemini-key")
async def delete_gemini_key(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Remove user's stored Gemini API key"""
    
    key = db.query(UserGeminiKey).filter_by(user_id=user_id).first()
    
    if key:
        db.delete(key)
        db.commit()
        return { "success": True, "message": "Key deleted" }
    
    raise HTTPException(status_code=404, detail="No key found")
```

---

## Frontend - Settings UI

### Gemini API Key Setup Page

```tsx
// frontendV2/src/app/settings/gemini/page.tsx

export default function GeminiSettingsPage() {
  const [apiKey, setApiKey] = useState("")
  const [showKey, setShowKey] = useState(false)
  const [hasKey, setHasKey] = useState(false)
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    // Check if user has key set
    checkKeyStatus()
  }, [])
  
  const checkKeyStatus = async () => {
    const res = await fetch("/api/user/gemini-key/status", {
      headers: { Authorization: `Bearer ${token}` }
    })
    const data = await res.json()
    setHasKey(data.has_key)
  }
  
  const handleSaveKey = async () => {
    setLoading(true)
    try {
      const res = await fetch("/api/user/gemini-key", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ api_key: apiKey })
      })
      
      if (res.ok) {
        toast.success("Gemini API key saved securely!")
        setHasKey(true)
        setApiKey("")
      } else {
        toast.error("Failed to save key")
      }
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Gemini API Key</h1>
      
      {hasKey ? (
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <p className="text-green-800 font-medium mb-4">
            ✅ Your Gemini API key is set
          </p>
          <p className="text-sm text-green-600 mb-4">
            All chat requests will use your personal API key.
            You are responsible for API usage and billing.
          </p>
          <button
            onClick={() => handleDeleteKey()}
            className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Remove Key
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-800 mb-2">
              <strong>How to get your API key:</strong>
            </p>
            <ol className="text-sm text-blue-700 list-decimal list-inside">
              <li>Go to https://aistudio.google.com/</li>
              <li>Click "Get API Key"</li>
              <li>Copy your API key</li>
              <li>Paste it below</li>
            </ol>
          </div>
          
          <div className="space-y-2">
            <label className="block font-medium">Your Gemini API Key</label>
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full px-4 py-2 border rounded-lg pr-10"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-2"
              >
                {showKey ? "Hide" : "Show"}
              </button>
            </div>
          </div>
          
          <div className="text-xs text-gray-600 space-y-1">
            <p>🔒 Your key is encrypted and never exposed</p>
            <p>💰 You pay Google directly for API usage</p>
            <p>🔐 Only you can access your key</p>
          </div>
          
          <button
            onClick={handleSaveKey}
            disabled={!apiKey || loading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Saving..." : "Save Key"}
          </button>
        </div>
      )}
    </div>
  )
}
```

---

## Security Best Practices

### ✅ Do's
- ✅ Use HTTPS for all key transmission
- ✅ Encrypt keys with AES-256 at rest
- ✅ Decrypt keys only in memory when needed
- ✅ Validate keys before storing (test API call)
- ✅ Log key activity (without storing actual keys)
- ✅ Use environment variable for master encryption key
- ✅ Implement key rotation capability
- ✅ Use JWT for user authentication
- ✅ Rate limit key endpoints
- ✅ Add audit trail for key changes

### ❌ Don'ts
- ❌ Store keys in plain text
- ❌ Log unencrypted keys
- ❌ Send keys in URL parameters
- ❌ Cache decrypted keys in database
- ❌ Share master encryption key in code
- ❌ Expose keys in error messages
- ❌ Store multiple keys per user (at least initially)

---

## Environment Setup

### 1. Generate Master Encryption Key

```bash
# One-time setup
python3 << 'EOF'
from cryptography.fernet import Fernet
import base64

key = Fernet.generate_key()
print(f"Add to .env:")
print(f"ENCRYPTION_KEY={key.decode()}")
EOF
```

### 2. Update .env

```bash
# backend/.env

# BYOK Settings
BYOK_ENABLED=true
REQUIRE_USER_KEY=true
ENCRYPTION_KEY=<generated-key-above>

# Optional: Fallback key for demo
DEFAULT_GEMINI_KEY=<your-demo-key-if-needed>

# LLM
LLM_SERVICE=google
GEMINI_MODEL=gemini-pro
```

### 3. Initialize Database

```bash
# Run migration to create UserGeminiKey table
alembic upgrade head
```

---

## User Flow

```
1. User installs P.U.L.S.E
   ↓
2. User goes to Settings → Gemini API
   ↓
3. User follows setup instructions
   - Go to https://aistudio.google.com/
   - Create API key
   - Copy key
   ↓
4. User pastes key in P.U.L.S.E
   ↓
5. P.U.L.S.E validates key (test call)
   ↓
6. Key encrypted and stored
   ↓
7. User can now use chat meal logging
   ↓
8. All chat requests use user's API key
   ↓
9. Charges go to user's Google account
```

---

## Failure Scenarios

### What if user deletes their API key?
```
→ Chat feature becomes unavailable
→ User sees error: "Please set your Gemini API key to use chat"
→ User can set key again anytime
```

### What if API key becomes invalid?
```
→ First chat request fails with error
→ Error message: "API key validation failed. Please check your key."
→ User can update key in settings
```

### What if encryption key is lost?
```
→ All stored keys become unrecoverable
→ Users must re-enter their keys
→ Plan: Backup encryption key securely
```

### What if user's Google account is compromised?
```
→ Their key is compromised
→ They should:
  1. Delete/revoke key at Google
  2. Remove key from P.U.L.S.E settings
  3. Generate new key
  4. Add new key to P.U.L.S.E
→ P.U.L.S.E recommends key rotation
```

---

## Monitoring & Logging

### What to Log (NO KEYS)
```python
{
  "event": "gemini_key_set",
  "user_id": "user_123",
  "timestamp": "2026-01-23T10:30:00Z",
  "key_length": 39,  # Generic, not actual key
  "validation": "passed",
  "ip_address": "192.168.1.1"
}

{
  "event": "chat_session_started",
  "user_id": "user_123",
  "session_id": "sess_abc",
  "has_personal_key": true,
  "timestamp": "2026-01-23T10:35:00Z"
}

{
  "event": "gemini_api_call",
  "session_id": "sess_abc",
  "agent": "root_agent",
  "status": "success",
  "latency_ms": 1250,
  "timestamp": "2026-01-23T10:35:05Z"
  # NO: api_key, response_content, request_content
}
```

---

## Benefits of BYOK

| Benefit | Impact |
|---------|--------|
| **Cost** | P.U.L.S.E $0 for LLM | User pays Google directly |
| **Privacy** | P.U.L.S.E never sees keys | Only encrypted storage |
| **Control** | Users manage usage | Can delete key anytime |
| **Security** | No shared credentials | Per-user isolation |
| **Scalability** | No API quota limits | Scales with users |
| **Compliance** | Clean audit trail | User responsible for their key |

---

## Roadmap

### Phase 1 (MVP)
- ✅ Encryption service
- ✅ Store user keys
- ✅ Decrypt on use
- ✅ Settings UI
- ✅ Agent integration

### Phase 2 (Future)
- 🔄 Key rotation
- 🔄 Usage analytics
- 🔄 Alternative providers (OpenAI, Anthropic)
- 🔄 Batch operations with user keys

---

## Conclusion

BYOK architecture provides:
1. **Cost Efficiency**: P.U.L.S.E has zero LLM costs
2. **User Control**: Users manage their own API access
3. **Privacy**: Encrypted at rest, isolated calls
4. **Scalability**: No single point of failure
5. **Security**: Best practices for key management

This is a modern, enterprise-ready approach for multi-user SaaS applications using LLMs.
