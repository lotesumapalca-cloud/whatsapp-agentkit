"""
FastAPI server for RYC Inmobiliaria WhatsApp Agent.
Receives webhooks from Zernio and processes messages with Claude AI.
"""
import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .brain import AgentBrain
from .memory import ConversationMemory
from .providers import get_provider

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="RYC Inmobiliaria WhatsApp Agent")

# Initialize agent components
brain = AgentBrain()
memory = ConversationMemory()
provider = get_provider()

@app.get("/health")
async def health():
    """Health check endpoint for Railway."""
    return {"status": "ok", "service": "ryc-inmobiliaria-agent"}

@app.post("/webhook")
async def webhook(request: Request):
    """
    Webhook endpoint that receives messages from Zernio (WhatsApp provider).
    Processes the message and sends a response via the provider.
    """
    try:
        payload = await request.json()
        logger.info(f"Received webhook: {json.dumps(payload, indent=2)}")
        
        # Extract message data from Zernio webhook
        message_data = provider.parse_webhook(payload)
        if not message_data:
            return JSONResponse({"status": "ignored"}, status_code=200)
        
        user_id = message_data.get("user_id")
        user_name = message_data.get("user_name", "Cliente")
        user_message = message_data.get("message", "")
        
        logger.info(f"Processing message from {user_name} (ID: {user_id}): {user_message}")
        
        # Get conversation history for this user
        conversation = memory.get_conversation(user_id)
        conversation.append({"role": "user", "content": user_message})
        
        # Get Claude's response
        response = await brain.get_response(user_message, conversation, user_name)
        
        # Add to memory
        conversation.append({"role": "assistant", "content": response})
        memory.save_conversation(user_id, conversation)
        
        # Send response via Zernio
        success = await provider.send_message(user_id, response)
        
        if success:
            logger.info(f"Response sent to {user_name}")
            return JSONResponse({"status": "success"}, status_code=200)
        else:
            logger.error(f"Failed to send response to {user_name}")
            return JSONResponse({"status": "error"}, status_code=500)
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/webhook/status")
async def webhook_status(request: Request):
    """Optional: webhook for message delivery status updates from Zernio."""
    try:
        payload = await request.json()
        logger.info(f"Status update: {json.dumps(payload, indent=2)}")
        return JSONResponse({"status": "acknowledged"}, status_code=200)
    except Exception as e:
        logger.error(f"Error processing status webhook: {str(e)}")
        return JSONResponse({"status": "error"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
