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
        
        self.base_url = "https://zernio.com/api/v1"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Zernio webhook payload."""
        try:
            if payload.get("event") != "message.received":
                logger.debug(f"Ignoring webhook event: {payload.get('event')}")
                return None
            
            message = payload.get("message", {})
            
            if message.get("direction") != "incoming":
                logger.debug("Ignoring non-incoming message")
                return None
            
            text = message.get("text", "").strip()
            if not text:
                logger.debug("Ignoring empty message")
                return None
            
            sender = message.get("sender", {})
            account = payload.get("account", {})
            
            return {
                "user_id": sender.get("id") or sender.get("phoneNumber", "unknown"),
                "user_name": sender.get("name", "Cliente"),
                "message": text,
                "conversation_id": message.get("conversationId"),
                "account_id": account.get("id")
            }
        except Exception as e:
            logger.error(f"Error parsing Zernio webhook: {e}")
            return None
    
    async def send_message(self, conversation_id: str, account_id: str, message: str) -> bool:
        """Send a message via Zernio API (unified inbox endpoint)."""
        try:
            payload = {
                "accountId": account_id,
                "message": message
            }
            
            response = await self.client.post(
                f"{self.base_url}/inbox/conversations/{conversation_id}/messages",
                json=payload,
                timeout=10.0
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Message sent to conversation {conversation_id} via Zernio")
                return True
            else:
                logger.error(f"Zernio API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message via Zernio: {e}")
            return False
