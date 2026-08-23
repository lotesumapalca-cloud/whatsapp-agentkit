"""
Claude AI brain for RYC Inmobiliaria WhatsApp Agent.
Handles conversation logic and integrates with Anthropic API.
"""
import os
import yaml
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
        
        # Get system prompt from config file, environment, or hardcoded default
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from config/prompts.yaml, env, or use default."""
        # Try config file first
        config_path = "config/prompts.yaml"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and 'system_prompt' in config:
                        logger.info("Loaded system_prompt from config/prompts.yaml")
                        return config['system_prompt']
            except Exception as e:
                logger.warning(f"Error loading config file: {e}, falling back to env")
        
        # Try environment variable
        env_prompt = os.getenv("SYSTEM_PROMPT")
        if env_prompt:
            logger.info("Loaded system_prompt from SYSTEM_PROMPT env var")
            return env_prompt
        
        # Use hardcoded default
        logger.info("Using default system_prompt")
        return self._default_system_prompt()
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for RYC Inmobiliaria if not configured."""
        return """Te llamas Julio, eres el Asesor Virtual de RYC Inmobiliaria."""
    
    async def get_response(self, user_message: str, conversation_history: list, user_name: str = "Cliente") -> str:
        """
        Get Claude's response for a user message.
        """
        try:
            messages = conversation_history[-20:]
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"Calling Claude for user {user_name}")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=messages
            )
            
            assistant_message = next((block.text for block in response.content if block.type == "text"), None)
            logger.info(f"Claude response: {assistant_message[:100]}...")
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error calling Claude: {str(e)}", exc_info=True)
            return "Disculpa, tengo un problema técnico. Por favor intenta de nuevo en unos momentos."
