"""
Conversation memory management for RYC Inmobiliaria WhatsApp Agent.
Stores and retrieves conversation history for each user.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Manages conversation history for each user."""
    
    def __init__(self, storage_dir: str = "agent_memory"):
        """Initialize memory storage."""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def _get_file_path(self, user_id: str) -> str:
        """Get the file path for a user's conversation history."""
        return os.path.join(self.storage_dir, f"{user_id}.json")
    
    def get_conversation(self, user_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a user."""
        if user_id in self.conversations:
            return self.conversations[user_id]
        
        file_path = self._get_file_path(user_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    self.conversations[user_id] = json.load(f)
                    logger.info(f"Loaded conversation for user {user_id}")
                    return self.conversations[user_id]
            except Exception as e:
                logger.error(f"Error loading conversation for {user_id}: {e}")
                return []
        
        logger.info(f"Starting new conversation with user {user_id}")
        return []
    
    def save_conversation(self, user_id: str, conversation: List[Dict[str, str]]) -> bool:
        """Save conversation history for a user."""
        try:
            self.conversations[user_id] = conversation
            file_path = self._get_file_path(user_id)
            with open(file_path, 'w') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved conversation for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving conversation for {user_id}: {e}")
            return False
    
    def clear_conversation(self, user_id: str) -> bool:
        """Clear conversation history for a user."""
        try:
            if user_id in self.conversations:
                del self.conversations[user_id]
            
            file_path = self._get_file_path(user_id)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            logger.info(f"Cleared conversation for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing conversation for {user_id}: {e}")
            return False
