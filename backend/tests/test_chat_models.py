"""Test chat functionality"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.models import User, ChatSession, ChatMessage
from app.core.security import get_password_hash
from datetime import datetime
import uuid


def test_chat_models():
    """Test that chat models work correctly"""
    print("🧪 Testing Chat Models...")
    
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    try:
        # Create test user
        user_id = str(uuid.uuid4())
        test_user = User(
            user_id=user_id,
            username="chattest",
            email="chattest@example.com",
            password_hash=get_password_hash("password123")
        )
        db.add(test_user)
        db.commit()
        print("✅ User created")
        
        # Create chat session
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            meal_type="BREAKFAST",
            session_state="COLLECTING",
            parsed_meal_items=[],
            nutrition_data={}
        )
        db.add(chat_session)
        db.commit()
        print("✅ Chat session created")
        
        # Create chat messages
        user_msg = ChatMessage(
            message_id=str(uuid.uuid4()),
            session_id=session_id,
            role="USER",
            content="I had 2 eggs and oatmeal",
            message_data={}
        )
        db.add(user_msg)
        db.commit()
        print("✅ User message created")
        
        assistant_msg = ChatMessage(
            message_id=str(uuid.uuid4()),
            session_id=session_id,
            role="ASSISTANT",
            content="Great! I logged your breakfast. That's approximately 400 calories.",
            message_data={"parsed": True}
        )
        db.add(assistant_msg)
        db.commit()
        print("✅ Assistant message created")
        
        # Query and verify
        retrieved_session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        assert retrieved_session is not None, "Session not found"
        assert len(retrieved_session.messages) == 2, "Messages not linked"
        print("✅ Chat session retrieved with messages")
        
        # Verify cascade
        db.delete(retrieved_session)
        db.commit()
        
        orphaned_msg = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).first()
        
        assert orphaned_msg is None, "Messages not deleted with session"
        print("✅ Cascade delete works")
        
        print("\n✅ All chat model tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_chat_models()
