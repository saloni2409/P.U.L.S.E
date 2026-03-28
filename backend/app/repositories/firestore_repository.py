"""Firestore Implementation of Repositories"""

import uuid
from datetime import datetime, date
from typing import List, Optional, Any, Dict
from google.cloud import firestore

from app.repositories.base_repository import (
    IUserRepository, IMealEntryRepository, 
    IAIConfigRepository, IChatSessionRepository
)


class FirestoreUserRepository(IUserRepository):
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = self.db.collection("users")

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = self.collection.document(user_id).get()
        return doc.to_dict() if doc.exists else None
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        docs = self.collection.where("username", "==", username).limit(1).get()
        return docs[0].to_dict() if docs else None

    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = user_data.get("user_id") or str(uuid.uuid4())
        user_data["user_id"] = user_id
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        self.collection.document(user_id).set(user_data)
        return user_data


class FirestoreMealEntryRepository(IMealEntryRepository):
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = self.db.collection("meal_entries")

    def get_meal_by_id(self, meal_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        doc = self.collection.document(meal_id).get()
        if doc.exists:
            data = doc.to_dict()
            if data["user_id"] == user_id:
                return data
        return None
        
    def get_user_meals(self, user_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        # Firestore offset is expensive, usually we use cursors but for simplicity we'll use limit
        docs = self.collection.where("user_id", "==", user_id).order_by("meal_date", direction=firestore.Query.DESCENDING).limit(limit).get()
        return [doc.to_dict() for doc in docs]

    def get_user_meals_by_date(self, user_id: str, meal_date: date) -> List[Dict[str, Any]]:
        # Firestore stores dates as timestamps. We need to handle the conversion.
        # For simplicity, we assume meal_date is stored as ISO string or timestamp
        date_str = meal_date.isoformat()
        docs = self.collection.where("user_id", "==", user_id).where("meal_date", "==", date_str).order_by("meal_time").get()
        return [doc.to_dict() for doc in docs]
    
    def create_meal(self, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        meal_id = meal_data.get("meal_id") or str(uuid.uuid4())
        meal_data["meal_id"] = meal_id
        # Convert date/time to strings for Firestore
        if isinstance(meal_data.get("meal_date"), date):
            meal_data["meal_date"] = meal_data["meal_date"].isoformat()
        
        meal_data["created_at"] = datetime.utcnow()
        meal_data["updated_at"] = datetime.utcnow()
        self.collection.document(meal_id).set(meal_data)
        return meal_data
        
    def update_meal(self, meal_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        doc_ref = self.collection.document(meal_id)
        update_data["updated_at"] = datetime.utcnow()
        doc_ref.update(update_data)
        return doc_ref.get().to_dict()
        
    def delete_meal(self, meal_id: str, user_id: str) -> bool:
        doc_ref = self.collection.document(meal_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict()["user_id"] == user_id:
            doc_ref.delete()
            return True
        return False
        
    def add_meal_item(self, meal_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        item_id = str(uuid.uuid4())
        item_data["item_id"] = item_id
        item_data["meal_id"] = meal_id
        item_data["created_at"] = datetime.utcnow()
        
        self.collection.document(meal_id).collection("items").document(item_id).set(item_data)
        return item_data
        
    def get_meal_items(self, meal_id: str) -> List[Dict[str, Any]]:
        docs = self.collection.document(meal_id).collection("items").get()
        return [doc.to_dict() for doc in docs]


class FirestoreAIConfigRepository(IAIConfigRepository):
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = self.db.collection("ai_configs")

    def get_active_config(self, user_id: str) -> Optional[Dict[str, Any]]:
        docs = self.collection.where("user_id", "==", user_id).where("is_active", "==", True).limit(1).get()
        return docs[0].to_dict() if docs else None

    def get_config_by_provider(self, user_id: str, provider: str) -> Optional[Dict[str, Any]]:
        docs = self.collection.where("user_id", "==", user_id).where("provider_type", "==", provider.upper()).limit(1).get()
        return docs[0].to_dict() if docs else None

    def deactivate_other_configs(self, user_id: str, active_provider: str):
        docs = self.collection.where("user_id", "==", user_id).where("provider_type", "!=", active_provider.upper()).get()
        for doc in docs:
            doc.reference.update({"is_active": False})

    def upsert_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = config_data.get("user_id")
        provider = config_data.get("provider_type")
        
        docs = self.collection.where("user_id", "==", user_id).where("provider_type", "==", provider).limit(1).get()
        
        if docs:
            doc_ref = docs[0].reference
            config_data["updated_at"] = datetime.utcnow()
            doc_ref.update(config_data)
        else:
            config_id = config_data.get("config_id") or str(uuid.uuid4())
            config_data["config_id"] = config_id
            config_data["created_at"] = datetime.utcnow()
            config_data["updated_at"] = datetime.utcnow()
            self.collection.document(config_id).set(config_data)
            
        return config_data


class FirestoreChatSessionRepository(IChatSessionRepository):
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = self.db.collection("chat_sessions")

    def get_session(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        doc = self.collection.document(session_id).get()
        if doc.exists:
            data = doc.to_dict()
            if data["user_id"] == user_id:
                return data
        return None

    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        session_id = session_data.get("session_id") or str(uuid.uuid4())
        session_data["session_id"] = session_id
        session_data["created_at"] = datetime.utcnow()
        session_data["updated_at"] = datetime.utcnow()
        self.collection.document(session_id).set(session_data)
        return session_data

    def update_session(self, session_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        doc_ref = self.collection.document(session_id)
        update_data["updated_at"] = datetime.utcnow()
        doc_ref.update(update_data)
        return doc_ref.get().to_dict()

    def add_message(self, session_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        message_id = str(uuid.uuid4())
        message_data["message_id"] = message_id
        message_data["created_at"] = datetime.utcnow()
        
        self.collection.document(session_id).collection("messages").document(message_id).set(message_data)
        return message_data

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        docs = self.collection.document(session_id).collection("messages").order_by("created_at").get()
        return [doc.to_dict() for doc in docs]
