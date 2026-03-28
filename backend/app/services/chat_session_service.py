"""Chat session management service"""

import uuid
import json
import re
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import ChatSession, ChatMessage, User
from app.services.ai_factory import AIFactory
from app.services.base_ai_service import AIChatMessage
from app.services.ai_config_service import AIConfigService


class ChatSessionService:
    """
    Service for managing chat sessions with meal logging agents.
    
    Workflow:
    1. User initiates chat for meal type (BREAKFAST, LUNCH, DINNER, SNACK)
    2. Root Agent converses to collect meal details
    3. Parser Agent structures items into editable table
    4. Nutrition Agent calculates macros/calories
    5. User confirms and saves to meal log
    """
    
    @staticmethod
    async def create_session(
        db: Session,
        user_id: str,
        meal_type: Optional[str] = None
    ) -> dict:
        """
        Create new chat session for meal logging.

        Args:
            db: Database session
            user_id: User ID
            meal_type: Optional - BREAKFAST, LUNCH, DINNER, SNACK. If not provided, will be extracted from conversation
            
        Returns:
            Session info with initial greeting
        """
        # Create session
        session = ChatSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            meal_type=meal_type,  # Can be None - will be inferred
            session_state="COLLECTING"
        )
        db.add(session)
        db.commit()
        
        # Add initial system message - generic greeting if no meal type
        if meal_type:
            greeting = f"Tell me what you ate for {meal_type.lower()}. You can describe it naturally, like 'eggs, toast, and coffee' or 'grilled chicken with rice and broccoli'."
        else:
            greeting = "What did you eat? You can describe it naturally like 'eggs, toast, and coffee' or 'grilled chicken with rice and broccoli'. Also, let me know if this was breakfast, lunch, dinner, or a snack."
        
        system_msg = ChatMessage(
            message_id=str(uuid.uuid4()),
            session_id=session.session_id,
            role="SYSTEM",
            content=greeting
        )
        db.add(system_msg)
        db.commit()
        
        return {
            "session_id": session.session_id,
            "meal_type": meal_type,
            "message": greeting,
            "state": "COLLECTING"
        }
    
    @staticmethod
    async def send_message(
        db: Session,
        user_id: str,
        session_id: str,
        message_text: str
    ) -> dict:
        """
        Send user message and get agent response.
        
        Args:
            db: Database session
            user_id: User ID
            session_id: Chat session ID
            message_text: User's message
            
        Returns:
            Agent response and updated session state
        """
        # Get session
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        if session.session_state == "SAVED":
            raise ValueError("Session already saved")
        
        # Add user message
        user_msg = ChatMessage(
            message_id=str(uuid.uuid4()),
            session_id=session_id,
            role="USER",
            content=message_text
        )
        db.add(user_msg)
        db.commit()
        
        # Get user's active AI configuration
        ai_config = await AIConfigService.get_active_config(db, user_id)
        if not ai_config:
            return {
                "error": "No active AI configuration found. Please configure Gemini or Local AI in settings.",
                "session_id": session_id,
                "state": session.session_state
            }
        
        # Get credential (API Key or Base URL)
        credential = None
        if ai_config.provider_type == "LOCAL":
            credential = ai_config.base_url
        else:
            credential = await AIConfigService.get_decrypted_key(db, ai_config)
            
        if not credential:
            return {
                "error": f"Credential missing for {ai_config.provider_type}. Please update your settings.",
                "session_id": session_id,
                "state": session.session_state
            }
        
        try:
            # Initialize AI Provider via Factory
            ai_service = AIFactory.get_service(
                ai_config.provider_type.lower(), 
                credential, 
                model_name=ai_config.model_name
            )
            
            # Get message history for context and convert to standardized objects
            history = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).all()
            
            messages = [
                AIChatMessage(
                    role=msg.role.lower() if msg.role != "SYSTEM" else "user", 
                    content=msg.content
                )
                for msg in history
            ]
            
            # Determine agent based on session state
            if session.session_state == "COLLECTING":
                response_text = await ChatSessionService._handle_collecting_state(
                    ai_service, messages, message_text, session
                )
            else:
                response_text = "Invalid session state"
            
            # Add assistant response
            assistant_msg = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=session_id,
                role="ASSISTANT",
                content=response_text
            )
            db.add(assistant_msg)
            db.commit()
            
            return {
                "session_id": session_id,
                "message": response_text,
                "state": session.session_state,
                "meal_items": session.parsed_meal_items,
                "nutrition": session.nutrition_data
            }
        
        except Exception as e:
            return {
                "error": f"Failed to get response: {str(e)}",
                "session_id": session_id,
                "state": session.session_state
            }
    
    @staticmethod
    async def _handle_collecting_state(
        ai_service,  # Now accepts any BaseAIService implementation
        messages: List[AIChatMessage],
        user_message: str,
        session: ChatSession
    ) -> str:
        """
        Root Agent: Collect meal information via conversation.
        
        Responsibilities:
        - Extract meal type if not already known
        - Extract meal time from conversation
        - Ask clarifying questions
        - Extract meal items
        - Determine when enough info collected
        """
        
        # Extract meal type and time if not already set
        ChatSessionService._extract_meal_metadata(user_message, session)
        
        meal_type_hint = f" for their {session.meal_type.lower()}" if session.meal_type else ""
        
        system_prompt = f"""You are a friendly meal logging assistant. 
The user is telling you about what they ate{meal_type_hint}.

Your job:
1. Ask about the foods they ate
2. Ask about quantities (e.g., "about how much rice? A cup?")
3. When you have enough info about items, ask to confirm what they said
4. Keep responses concise and friendly
5. After you have 2-3 food items with quantities, ask: "Is that everything? Or did you have anything else?"

Current conversation:"""
        
        # Build system message using standardized schema
        full_messages = [
            AIChatMessage(role="user", content=system_prompt)
        ] + messages
        
        response_text = await ai_service.chat_message(full_messages)
        
        # Check if user is done adding items
        user_lower = user_message.lower()
        if any(word in user_lower for word in ["that's all", "that's it", "nothing else", "i'm done"]):
            # Parse the meal items
            meal_parse_prompt = f"""Extract meal items from this conversation:
{json.dumps(messages[-4:], indent=2)}

Return JSON with food items:
{{"meal_items": [{{"food_name": "", "quantity": 1, "unit": "pieces", "calories": 0}}]}}"""
            
            parsed = await ai_service.parse_meal_description(user_message)
            if parsed.meal_items:
                # Convert Pydantic objects back to dict for JSON database storage
                session.parsed_meal_items = [item.dict() for item in parsed.meal_items]
                session.session_state = "CONFIRMING"
        
        return response_text
    
    @staticmethod
    def _extract_meal_metadata(user_message: str, session: ChatSession) -> None:
        """
        Extract meal type and time from user message.
        
        Updates session.meal_type and session.meal_time if detected.
        """
        message_lower = user_message.lower()
        
        # Extract meal type if not already set
        if not session.meal_type:
            meal_types = {
                'breakfast': ['breakfast', 'bfast', 'morning meal', 'eggs', 'cereal', 'oatmeal'],
                'lunch': ['lunch', 'midday', 'noon', 'sandwich', 'salad'],
                'dinner': ['dinner', 'supper', 'evening meal', 'dinner time'],
                'snack': ['snack', 'snacking', 'chips', 'candy', 'fruit', 'granola', 'bar', 'between meals']
            }
            
            for meal_type, keywords in meal_types.items():
                if any(keyword in message_lower for keyword in keywords):
                    session.meal_type = meal_type.upper()
                    break
        
        # Extract time if present (HH:MM format or time words)
        if not session.meal_time:
            # Look for time patterns like "8am", "12:30pm", "morning", "afternoon", etc.
            time_pattern = r'(\d{1,2}):?(\d{2})?\s*(am|pm)?|(\d{1,2})\s*(am|pm)'
            time_match = re.search(time_pattern, message_lower)
            
            if time_match:
                try:
                    hour = int(time_match.group(1) or time_match.group(4))
                    minute = int(time_match.group(2) or 0)
                    period = time_match.group(3) or time_match.group(5)
                    
                    # Convert to 24-hour format if needed
                    if period and period.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif period and period.lower() == 'am' and hour == 12:
                        hour = 0
                    
                    session.meal_time = f"{hour:02d}:{minute:02d}"
                except (ValueError, TypeError):
                    pass
            
            # Also check for time words
            if not session.meal_time:
                time_words = {
                    'morning': '08:00',
                    'breakfast time': '08:00',
                    'midday': '12:00',
                    'lunch time': '12:00',
                    'afternoon': '14:00',
                    'evening': '18:00',
                    'dinner time': '18:00',
                }
                
                for word, time in time_words.items():
                    if word in message_lower:
                        session.meal_time = time
                        break
    
    @staticmethod
    async def get_meal_summary(
        db: Session,
        user_id: str,
        session_id: str
    ) -> dict:
        """
        Get parsed meal items and nutrition summary for confirmation.
        
        Args:
            db: Database session
            user_id: User ID
            session_id: Chat session ID
            
        Returns:
            Parsed meal items with nutrition data
        """
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        return {
            "session_id": session_id,
            "meal_type": session.meal_type,
            "meal_items": session.parsed_meal_items or [],
            "nutrition": session.nutrition_data or {},
            "state": session.session_state
        }
    
    @staticmethod
    async def update_meal_items(
        db: Session,
        user_id: str,
        session_id: str,
        meal_items: list
    ) -> dict:
        """
        Update meal items (user edited in confirmation UI).
        
        Args:
            db: Database session
            user_id: User ID
            session_id: Chat session ID
            meal_items: List of updated meal items
            
        Returns:
            Updated session info
        """
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        # Update meal items
        session.parsed_meal_items = meal_items
        db.commit()
        
        # Use AI Config Service to get active configuration
        ai_config = await AIConfigService.get_active_config(db, user_id)
        
        if ai_config:
            credential = ai_config.base_url if ai_config.provider_type == "LOCAL" else await AIConfigService.get_decrypted_key(db, ai_config)
            
            if credential:
                ai_service = AIFactory.get_service(
                    ai_config.provider_type.lower(), 
                    credential, 
                    model_name=ai_config.model_name
                )
                nutrition = await ai_service.get_nutrition_estimate(meal_items)
                
                # Store standardized nutrition data
                session.nutrition_data = nutrition.dict()
                db.commit()
        
        return {
            "session_id": session_id,
            "meal_items": session.parsed_meal_items,
            "nutrition": session.nutrition_data
        }
    
    @staticmethod
    async def save_meal_to_log(
        db: Session,
        user_id: str,
        session_id: str
    ) -> dict:
        """
        Save meal from chat session to meal log.
        
        Args:
            db: Database session
            user_id: User ID
            session_id: Chat session ID
            
        Returns:
            Meal entry created
        """
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        if not session.parsed_meal_items:
            raise ValueError("No meal items to save")
        
        # TODO: Save to meal_entries via MealProcessingService
        # For now, mark session as saved
        session.session_state = "SAVED"
        session.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "session_id": session_id,
            "state": "SAVED",
            "message": "Meal saved successfully"
        }
    
    @staticmethod
    async def cancel_session(
        db: Session,
        user_id: str,
        session_id: str
    ) -> dict:
        """
        Cancel chat session without saving.
        
        Args:
            db: Database session
            user_id: User ID
            session_id: Chat session ID
            
        Returns:
            Cancelled session info
        """
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        session.session_state = "CANCELLED"
        session.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "session_id": session_id,
            "state": "CANCELLED",
            "message": "Chat session cancelled"
        }
    
    @staticmethod
    def get_session_messages(
        db: Session,
        user_id: str,
        session_id: str
    ) -> list:
        """
        Get all messages in a chat session.
        
        Args:
            db: Database session
            user_id: User ID
            session_id: Chat session ID
            
        Returns:
            List of messages with role and content
        """
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
        
        return [
            {
                "message_id": msg.message_id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
