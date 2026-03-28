"""Abstract repository interfaces for storage decoupling"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from datetime import date

class BaseRepository(ABC):
    """Base generic repository interface"""
    pass

class IUserRepository(BaseRepository):
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class IMealEntryRepository(BaseRepository):
    @abstractmethod
    def get_meal_by_id(self, meal_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def get_user_meals(self, user_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_user_meals_by_date(self, user_id: str, meal_date: date) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def create_meal(self, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def update_meal(self, meal_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def delete_meal(self, meal_id: str, user_id: str) -> bool:
        pass
        
    @abstractmethod
    def add_meal_item(self, meal_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def get_meal_items(self, meal_id: str) -> List[Dict[str, Any]]:
        pass

class IAIConfigRepository(BaseRepository):
    @abstractmethod
    def get_active_config(self, user_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_config_by_provider(self, user_id: str, provider: str) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def upsert_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def deactivate_other_configs(self, user_id: str, active_provider: str):
        pass

class IChatSessionRepository(BaseRepository):
    @abstractmethod
    def get_session(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def update_session(self, session_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def add_message(self, session_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        pass
