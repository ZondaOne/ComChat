from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
import uuid
import logging
import traceback

from app.core.db import get_db
from app.services.chatbot import ChatbotService
from app.models import Conversation, Message, Tenant

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    channel: str = "web"
    channel_user_id: str
    tenant_slug: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str
    processing_time_ms: int
    ai_model_used: str


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Send a message to the chatbot and get a response"""
    logger.info(f"🔥 Received chat request: tenant={request.tenant_slug}, channel={request.channel}, user={request.channel_user_id}, message_length={len(request.message)}")
    
    try:
        logger.info(f"🤖 Creating ChatbotService instance...")
        chatbot_service = ChatbotService(db)
        
        logger.info(f"📨 Processing message with ChatbotService...")
        response = await chatbot_service.process_message(
            tenant_slug=request.tenant_slug,
            channel=request.channel,
            channel_user_id=request.channel_user_id,
            message=request.message,
            conversation_id=request.conversation_id,
            media_url=request.media_url,
            media_type=request.media_type
        )
        
        logger.info(f"✅ ChatbotService returned response: conversation_id={response.get('conversation_id')}, message_id={response.get('message_id')}, processing_time={response.get('processing_time_ms')}ms")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in send_message endpoint: {str(e)}")
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a conversation"""
    # TODO: Add authentication and tenant validation
    try:
        conversation_uuid = uuid.UUID(conversation_id)
        # Query messages for the conversation
        # This would be implemented with proper database queries
        return {"messages": [], "conversation_id": conversation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/{channel}")
async def handle_channel_webhook(
    channel: str,
    request: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Handle incoming webhooks from messaging channels"""
    if channel == "whatsapp":
        # Handle WhatsApp webhook
        return await handle_whatsapp_webhook(request, background_tasks, db)
    elif channel == "telegram":
        # Handle Telegram webhook
        return await handle_telegram_webhook(request, background_tasks, db)
    else:
        raise HTTPException(status_code=400, detail="Unsupported channel")


async def handle_whatsapp_webhook(request: dict, background_tasks: BackgroundTasks, db: AsyncSession):
    """Handle WhatsApp Business API webhook"""
    # TODO: Implement WhatsApp webhook processing
    return {"status": "received"}


async def handle_telegram_webhook(request: dict, background_tasks: BackgroundTasks, db: AsyncSession):
    """Handle Telegram Bot API webhook"""
    # TODO: Implement Telegram webhook processing
    return {"status": "received"}