"""
Claude AI brain for RYC Inmobiliaria WhatsApp Agent.
Handles conversation logic and integrates with Anthropic API.
"""
import os
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class AgentBrain:
    """Manages interaction with Claude for real estate conversations."""
    
    def __init__(self):
        """Initialize Anthropic client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = Anthropic()
        self.model = "claude-sonnet-5"
        
        # Get system prompt from environment or use default
        self.system_prompt = os.getenv("SYSTEM_PROMPT", self._default_system_prompt())
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for RYC Inmobiliaria if not configured."""
        return """Eres un agente de ventas para RYC Inmobiliaria, empresa especializada en venta de terrenos en Umapalca y Sabandía.

Tu objetivo es ayudar a clientes potenciales a:
1. Conocer las propiedades disponibles
2. Responder preguntas sobre ubicación, tamaño y precio
3. Agendar citas para visitas
4. Proporcionar información sobre el proceso de compra

Sé amable, profesional y conciso. Responde en español. Si el cliente pregunta algo fuera de tu alcance, ofrece transferirlo a un representante humano.

Información clave:
- Ubicaciones: Umapalca y Sabandía (zonas residenciales de calidad)
- Especializamos en terrenos para vivienda y desarrollo inmobiliario
- Proceso de compra transparente y asesoría legal incluida
- Horario: Lunes a viernes 8am-6pm, Sábados 10am-2pm

Siempre sé honesto sobre disponibilidad y detalles de propiedades."""
    
    async def get_response(self, user_message: str, conversation_history: list, user_name: str = "Cliente") -> str:
        """
        Get Claude's response for a user message.
        """
        try:
            messages = conversation_history[-20:]
            
            logger.info(f"Calling Claude for user {user_name}")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=messages
            )
            
            assistant_message = None for block in response.content: if getattr(block, "type", None) == "text": assistant_message = block.text break if not assistant_message: assistant_message = "Disculpa, no pude generar una respuesta clara. ¿Podrías reformular tu pregunta?" logger.info(f"Claude response: {assistant_message[:100]}...")
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error calling Claude: {str(e)}", exc_info=True)
            return "Disculpa, tengo un problema técnico. Por favor intenta de nuevo en unos momentos."
