import httpx
import json
import logging
import hashlib
import hmac
import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func

from app.models import Webhook, Tenant, Conversation, Message


class WebhookService:
    """Service for managing and triggering webhooks"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def trigger_webhook(
        self,
        event_type: str,
        tenant_id: str,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ):
        """Trigger webhooks for a specific event"""
        
        try:
            # Get active webhooks for this tenant
            webhooks = await self._get_tenant_webhooks(tenant_id, event_type)
            
            for webhook in webhooks:
                await self._send_webhook(webhook, event_type, payload)
                
        except Exception as e:
            logging.error(f"Error triggering webhooks: {e}")
    
    async def _get_tenant_webhooks(self, tenant_id: str, event_type: str):
        """Get active webhooks for tenant that listen to this event"""
        
        result = await self.db.execute(
            select(Webhook).where(
                Webhook.tenant_id == tenant_id,
                Webhook.is_active == True
            )
        )
        
        webhooks = result.scalars().all()
        
        # Filter by event type
        matching_webhooks = []
        for webhook in webhooks:
            if event_type in webhook.events:
                matching_webhooks.append(webhook)
        
        return matching_webhooks
    
    async def _send_webhook(
        self,
        webhook: Webhook,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Send individual webhook with retry logic"""
        
        webhook_payload = {
            "event": event_type,
            "timestamp": payload.get("timestamp"),
            "data": payload
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ComChat-Webhook/1.0",
            **webhook.headers
        }
        
        # Add webhook signature if secret is configured
        if webhook.secret:
            signature = self._generate_signature(
                webhook.secret,
                json.dumps(webhook_payload, separators=(',', ':'))
            )
            headers["X-ComChat-Signature"] = f"sha256={signature}"
        
        # Add authentication headers
        if webhook.auth_type == "bearer":
            token = webhook.auth_credentials.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        elif webhook.auth_type == "basic":
            username = webhook.auth_credentials.get("username")
            password = webhook.auth_credentials.get("password")
            if username and password:
                auth = httpx.BasicAuth(username, password)
        
        # Send webhook with retries
        success = False
        last_error = None
        
        for attempt in range(webhook.retry_count + 1):
            try:
                response = await self.client.post(
                    webhook.url,
                    json=webhook_payload,
                    headers=headers,
                    timeout=webhook.timeout_seconds
                )
                
                if 200 <= response.status_code < 300:
                    success = True
                    break
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    
            except Exception as e:
                last_error = str(e)
                
            if attempt < webhook.retry_count:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # Update webhook statistics
        webhook.total_calls += 1
        if success:
            webhook.successful_calls += 1
            webhook.last_error = None
        else:
            webhook.failed_calls += 1
            webhook.last_error = last_error
            logging.error(f"Webhook failed after {webhook.retry_count + 1} attempts: {last_error}")
        
        webhook.last_called_at = func.now()
        await self.db.commit()
    
    def _generate_signature(self, secret: str, payload: str) -> str:
        """Generate HMAC SHA256 signature for webhook verification"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def create_webhook_events(
        self,
        conversation: Conversation,
        message: Message,
        event_type: str
    ):
        """Create webhook events for conversation/message events"""
        
        timestamp = message.created_at.isoformat()
        
        base_payload = {
            "timestamp": timestamp,
            "tenant_id": str(conversation.tenant_id),
            "conversation": {
                "id": str(conversation.id),
                "channel": conversation.channel,
                "channel_user_id": conversation.channel_user_id,
                "status": conversation.status,
                "user_name": conversation.user_name,
                "user_phone": conversation.user_phone
            },
            "message": {
                "id": str(message.id),
                "content": message.content,
                "direction": message.direction,
                "sender": message.sender,
                "message_type": message.message_type,
                "media_url": message.media_url,
                "ai_model_used": message.ai_model_used
            }
        }
        
        await self.trigger_webhook(
            event_type,
            str(conversation.tenant_id),
            base_payload,
            str(conversation.id)
        )


# Webhook event types
class WebhookEvents:
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    CONVERSATION_STARTED = "conversation.started"
    CONVERSATION_ENDED = "conversation.ended"
    HANDOVER_REQUESTED = "handover.requested"
    HANDOVER_COMPLETED = "handover.completed"