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

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RYC Inmobiliaria WhatsApp Agent")

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

        message_data = provider.parse_webhook(payload)
        if not message_data:
            return JSONResponse({"status": "ignored"}, status_code=200)

        user_id = message_data.get("user_id")
        user_name = message_data.get("user_name", "Cliente")
        user_message = message_data.get("message", "")
        conversation_id = message_data.get("conversation_id")
        account_id = message_data.get("account_id")

        logger.info(f"Processing message from {user_name} (ID: {user_id}): {user_message}")

        conversation = memory.get_conversation(user_id)
        conversation.append({"role": "user", "content": user_message})

        response = await brain.get_response(user_message, conversation, user_name)

        conversation.append({"role": "assistant", "content": response})
        memory.save_conversation(user_id, conversation)

        success = await provider.send_message(conversation_id, account_id, response)

        if
