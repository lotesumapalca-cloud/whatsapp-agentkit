"""Base class for WhatsApp providers."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseProvider(ABC):
    """Abstract base class for WhatsApp providers."""
    
    @abstractmethod
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse incoming webhook from the provider."""
        pass
    
    @abstractmethod
    async def send_message(self, conversation_id: str, account_id: str, message: str) -> bool:
        """Send a message to the user via the provider."""
        pass
