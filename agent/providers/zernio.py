"""Zernio WhatsApp provider integration."""
import os
import logging
import httpx
from typing import Dict, Any, Optional
from .base import BaseProvider

logger = logging.getLogger(__name__)

class ZernioProvider(BaseProvider):
    """Integration with Zernio WhatsApp messaging service."""
    
    def __init__(self):
        """Initialize Zernio provider."""
        self.api_key = os.getenv("ZERNIO_API_KEY")
        if not self.api_key:
            raise ValueError("ZERNIO_API_KEY environment variable not set")
        
        self.base_url = "https://api.zernio.com"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Zernio webhook payload."""
        try:
            if payload.get("type") != "message":
                logger.debug(f"Ignoring webhook type: {payload.get('type')}")
                return None
            
            message = payload.get("message", {})
            text = message.get("text", "").strip()
            
            if not text:
                logger.debug("Ignoring empty message")
                return None
            
            return {
                "user_id": message.get("from", "unknown"),
                "user_name": message.get("name", "Cliente"),
                "message": text
            }
        except Exception as e:
            logger.error(f"Error parsing Zernio webhook: {e}")
            return None
    
    async def send_message(self, user_id: str, message: str) -> bool:
        """Send a message via Zernio API."""
        try:
            payload = {
                "to": user_id,
                "text": message,
                "type": "text"
            }
            
            response = await self.client.post(
                f"{self.base_url}/send-message",
                json=payload,
                timeout=10.0
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Message sent to {user_id} via Zernio")
                return True
            else:
                logger.error(f"Zernio API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message via Zernio: {e}")
            return False
