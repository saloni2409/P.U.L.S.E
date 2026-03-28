"""Factory for resolving repository implementations"""

from typing import Union
from sqlalchemy.orm import Session
from google.cloud import firestore

from app.core.settings import settings
from app.repositories.sql_repository import (
    SQLUserRepository, SQLAIConfigRepository, SQLChatSessionRepository, SQLMealEntryRepository
)
from app.repositories.firestore_repository import (
    FirestoreUserRepository, FirestoreAIConfigRepository, FirestoreChatSessionRepository, FirestoreMealEntryRepository
)

# Get Firestore client only if needed
_firestore_client = None

def get_firestore_client():
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client(project=settings.firestore_project_id)
    return _firestore_client

class RepositoryFactory:
    """Factory to resolve repositories based on settings"""

    @staticmethod
    def get_user_repository(db: Union[Session, firestore.Client]):
        if settings.db_type == "FIRESTORE":
            return FirestoreUserRepository(db)
        return SQLUserRepository(db)

    @staticmethod
    def get_ai_config_repository(db: Union[Session, firestore.Client]):
        if settings.db_type == "FIRESTORE":
            return FirestoreAIConfigRepository(db)
        return SQLAIConfigRepository(db)

    @staticmethod
    def get_chat_session_repository(db: Union[Session, firestore.Client]):
        if settings.db_type == "FIRESTORE":
            return FirestoreChatSessionRepository(db)
        return SQLChatSessionRepository(db)

    @staticmethod
    def get_meal_repository(db: Union[Session, firestore.Client]):
        if settings.db_type == "FIRESTORE":
            return FirestoreMealEntryRepository(db)
        return SQLMealEntryRepository(db)
