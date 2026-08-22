"""Tools and utilities for RYC Inmobiliaria WhatsApp Agent."""
import os
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class PropertyDatabase:
    """Simple in-memory property database for RYC Inmobiliaria."""
    
    def __init__(self):
        """Initialize properties from environment or file."""
        self.properties = self._load_properties()
    
    def _load_properties(self) -> List[Dict[str, Any]]:
        """Load properties from database file or return sample properties."""
        db_path = "config/properties.json"
        
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading properties: {e}")
                return self._sample_properties()
        
        return self._sample_properties()
    
    def _sample_properties(self) -> List[Dict[str, Any]]:
        """Return sample properties for RYC Inmobiliaria."""
        return [
            {
                "id": "P001",
                "location": "Umapalca",
                "size_sqm": 500,
                "price": 45000,
                "description": "Terreno residencial 500m² en zona verde de Umapalca"
            },
            {
                "id": "P002",
                "location": "Sabandía",
                "size_sqm": 800,
                "price": 68000,
                "description": "Terreno grande 800m² ideal para inversión en Sabandía"
            }
        ]
    
    def search_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Search properties by location."""
        return [p for p in self.properties if location.lower() in p.get("location", "").lower()]
