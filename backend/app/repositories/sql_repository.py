"""SQL Implementation of Repositories using SQLAlchemy"""

import uuid
from datetime import datetime, date
from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models import User, MealEntry, MealItem, ChatSession, ChatMessage, UserAIConfig, Macronutrients
from app.repositories.base_repository import (
    IUserRepository, IMealEntryRepository, 
    IAIConfigRepository, IChatSessionRepository
)


class SQLUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        user = self.db.query(User).filter(User.user_id == user_id).first()
        return self._to_dict(user) if user else None
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        user = self.db.query(User).filter(User.username == username).first()
        return self._to_dict(user) if user else None

    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._to_dict(user)

    def _to_dict(self, user: User) -> Dict[str, Any]:
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "dietary_preferences": user.dietary_preferences,
            "daily_calorie_goal": user.daily_calorie_goal,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }


class SQLMealEntryRepository(IMealEntryRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_meal_by_id(self, meal_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        meal = self.db.query(MealEntry).filter(
            and_(MealEntry.meal_id == meal_id, MealEntry.user_id == user_id)
        ).first()
        return self._to_dict(meal) if meal else None
        
    def get_user_meals(self, user_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        meals = self.db.query(MealEntry).filter(
            MealEntry.user_id == user_id
        ).order_by(MealEntry.meal_date.desc()).limit(limit).offset(offset).all()
        return [self._to_dict(m) for m in meals]

    def get_user_meals_by_date(self, user_id: str, meal_date: date) -> List[Dict[str, Any]]:
        meals = self.db.query(MealEntry).filter(
            and_(MealEntry.user_id == user_id, MealEntry.meal_date == meal_date)
        ).order_by(MealEntry.meal_time).all()
        return [self._to_dict(m) for m in meals]
    
    def create_meal(self, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        meal = MealEntry(**meal_data)
        self.db.add(meal)
        self.db.commit()
        self.db.refresh(meal)
        return self._to_dict(meal)
        
    def update_meal(self, meal_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        meal = self.db.query(MealEntry).filter(
            and_(MealEntry.meal_id == meal_id, MealEntry.user_id == user_id)
        ).first()
        if meal:
            for key, value in update_data.items():
                setattr(meal, key, value)
            meal.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(meal)
            return self._to_dict(meal)
        return None
        
    def delete_meal(self, meal_id: str, user_id: str) -> bool:
        meal = self.db.query(MealEntry).filter(
            and_(MealEntry.meal_id == meal_id, MealEntry.user_id == user_id)
        ).first()
        if not meal:
            return False
        self.db.delete(meal)
        self.db.commit()
        return True
        
    def add_meal_item(self, meal_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        macro_data = item_data.pop("macronutrients", None)
        item = MealItem(meal_id=meal_id, **item_data)
        self.db.add(item)
        self.db.flush()
        
        if macro_data:
            macro = Macronutrients(item_id=item.item_id, **macro_data)
            self.db.add(macro)
            
        self.db.commit()
        self.db.refresh(item)
        return self._item_to_dict(item)
        
    def get_meal_items(self, meal_id: str) -> List[Dict[str, Any]]:
        items = self.db.query(MealItem).filter(MealItem.meal_id == meal_id).all()
        return [self._item_to_dict(i) for i in items]

    def _to_dict(self, meal: MealEntry) -> Dict[str, Any]:
        return {
            "meal_id": meal.meal_id,
            "user_id": meal.user_id,
            "meal_type": meal.meal_type,
            "meal_description": meal.meal_description,
            "meal_date": meal.meal_date,
            "meal_time": meal.meal_time,
            "is_processed": meal.is_processed,
            "created_at": meal.created_at,
            "updated_at": meal.updated_at
        }
        
    def _item_to_dict(self, item: MealItem) -> Dict[str, Any]:
        return {
            "item_id": item.item_id,
            "meal_id": item.meal_id,
            "food_name": item.food_name,
            "quantity": item.quantity,
            "unit": item.unit,
            "calories": item.calories,
            "is_verified": item.is_verified,
            "created_at": item.created_at
        }


class SQLAIConfigRepository(IAIConfigRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_active_config(self, user_id: str) -> Optional[Dict[str, Any]]:
        config = self.db.query(UserAIConfig).filter(
            UserAIConfig.user_id == user_id,
            UserAIConfig.is_active == True
        ).first()
        return self._to_dict(config) if config else None

    def get_config_by_provider(self, user_id: str, provider: str) -> Optional[Dict[str, Any]]:
        config = self.db.query(UserAIConfig).filter(
            UserAIConfig.user_id == user_id,
            UserAIConfig.provider_type == provider.upper()
        ).first()
        return self._to_dict(config) if config else None

    def deactivate_other_configs(self, user_id: str, active_provider: str):
        self.db.query(UserAIConfig).filter(
            UserAIConfig.user_id == user_id,
            UserAIConfig.provider_type != active_provider.upper()
        ).update({"is_active": False})
        self.db.commit()

    def upsert_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = config_data.get("user_id")
        provider = config_data.get("provider_type")
        
        existing = self.db.query(UserAIConfig).filter(
            UserAIConfig.user_id == user_id,
            UserAIConfig.provider_type == provider
        ).first()
        
        if existing:
            for key, value in config_data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            config = existing
        else:
            config = UserAIConfig(**config_data)
            self.db.add(config)
            
        self.db.commit()
        self.db.refresh(config)
        return self._to_dict(config)

    def _to_dict(self, config: UserAIConfig) -> Dict[str, Any]:
        return {
            "config_id": config.config_id,
            "user_id": config.user_id,
            "provider_type": config.provider_type,
            "model_name": config.model_name,
            "base_url": config.base_url,
            "encrypted_key": config.encrypted_key,
            "is_active": config.is_active,
            "created_at": config.created_at,
            "updated_at": config.updated_at
        }


class SQLChatSessionRepository(IChatSessionRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_session(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        session = self.db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        ).first()
        return self._to_dict(session) if session else None

    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        session = ChatSession(**session_data)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return self._to_dict(session)

    def update_session(self, session_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        session = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            for key, value in update_data.items():
                setattr(session, key, value)
            session.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
            return self._to_dict(session)
        return None

    def add_message(self, session_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        msg = ChatMessage(session_id=session_id, **message_data)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return {
            "message_id": msg.message_id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at
        }

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
        return [
            {
                "message_id": msg.message_id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]

    def _to_dict(self, session: ChatSession) -> Dict[str, Any]:
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "meal_type": session.meal_type,
            "meal_time": session.meal_time,
            "session_state": session.session_state,
            "parsed_meal_items": session.parsed_meal_items,
            "nutrition_data": session.nutrition_data,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "completed_at": session.completed_at
        }
