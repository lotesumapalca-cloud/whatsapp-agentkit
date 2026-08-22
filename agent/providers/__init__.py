"""WhatsApp provider integrations."""
import os
import logging
from .base import BaseProvider
from .zernio import ZernioProvider

logger = logging.getLogger(__name__)

__all__ = ["get_provider", "BaseProvider", "ZernioProvider"]

def get_provider() -> BaseProvider:
    """Factory function to get the configured WhatsApp provider."""
    provider_name = os.getenv("PROVIDER", "zernio").lower()
    
    if provider_name == "zernio":
        logger.info("Initializing Zernio provider")
        return ZernioProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
