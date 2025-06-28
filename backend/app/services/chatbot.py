from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
import time
import uuid
import logging

from app.models import Tenant, Conversation, Message
from app.services.model_router import ModelRouter
from app.services.decision_tree import DecisionTreeEngine
from app.services.webhook import WebhookService, WebhookEvents
from app.services.billing import BillingService
from app.core.config import settings


class ChatbotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model_router = ModelRouter()
        self.decision_tree = DecisionTreeEngine()
        self.webhook_service = WebhookService(db)
        self.billing_service = BillingService(db)

    async def process_message(
        self,
        tenant_slug: str,
        channel: str,
        channel_user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process an incoming message and generate a response"""
        
        start_time = time.time()
        logging.info(f"🚀 ChatbotService.process_message started for tenant_slug={tenant_slug}")
        
        try:
            # Get tenant
            logging.info(f"🔍 Looking up tenant by slug: {tenant_slug}")
            tenant = await self._get_tenant_by_slug(tenant_slug)
            if not tenant:
                logging.error(f"❌ Tenant not found: {tenant_slug}")
                raise Exception(f"Tenant not found: {tenant_slug}")
            
            logging.info(f"✅ Found tenant: id={tenant.id}, name={tenant.name}, active={tenant.is_active}")
            
            # Check usage limits
            logging.info(f"💳 Checking usage limits for tenant {tenant.id}")
            usage_check = await self.billing_service.check_usage_limits(str(tenant.id))
            logging.info(f"💳 Usage check result: {usage_check}")
            
            if not usage_check["within_limits"]:
                logging.warning(f"⚠️ Usage limits exceeded for tenant {tenant.id}: {usage_check.get('reason', 'Unknown reason')}")
                return {
                    "response": "You have exceeded your usage limits for this billing period. Please upgrade your plan or wait for the next billing cycle.",
                    "conversation_id": conversation_id or "unknown",
                    "message_id": "usage_limit_exceeded",
                    "processing_time_ms": 0,
                    "ai_model_used": "none"
                }
            
            # Get or create conversation
            conversation = await self._get_or_create_conversation(
                tenant, channel, channel_user_id, conversation_id
            )
            
            # Save incoming message
            incoming_message = await self._save_message(
                conversation=conversation,
                content=message,
                direction="inbound",
                sender="user",
                media_url=media_url,
                media_type=media_type
            )
            
            # Generate AI response
            response_content, model_used, tokens_used = await self._generate_response(
                tenant, conversation, message, media_url, media_type
            )
            
            # Process decision tree if configured
            decision_result = await self._process_decision_tree(
                tenant, conversation, message, response_content
            )
            
            # Update response based on decision tree
            if decision_result["action"] != "continue":
                response_content = decision_result.get("response", response_content)
            
            # Save outgoing message
            outgoing_message = await self._save_message(
                conversation=conversation,
                content=response_content,
                direction="outbound",
                sender="bot",
                ai_model_used=model_used,
                tokens_used=tokens_used,
                processed_by_ai=True
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Record usage for billing
            await self.billing_service.record_usage(
                tenant_id=str(tenant.id),
                usage_type="messages",
                quantity=1,
                resource_id=str(incoming_message.id)
            )
            
            await self.billing_service.record_usage(
                tenant_id=str(tenant.id),
                usage_type="ai_requests",
                quantity=1,
                tokens_used=tokens_used,
                cost_cents=self._calculate_ai_cost(model_used, tokens_used),
                resource_id=str(outgoing_message.id),
                metadata={"model": model_used, "processing_time_ms": processing_time}
            )
            
            # Trigger webhooks for message events
            await self.webhook_service.create_webhook_events(
                conversation, incoming_message, WebhookEvents.MESSAGE_RECEIVED
            )
            await self.webhook_service.create_webhook_events(
                conversation, outgoing_message, WebhookEvents.MESSAGE_SENT
            )
            
            response_data = {
                "response": response_content,
                "conversation_id": str(conversation.id),
                "message_id": str(outgoing_message.id),
                "processing_time_ms": processing_time,
                "ai_model_used": model_used
            }
            
            logging.info(f"🎉 ChatbotService.process_message completed successfully: {response_data}")
            return response_data
            
        except Exception as e:
            import traceback
            logging.error(f"❌ Error in ChatbotService.process_message: {str(e)}")
            logging.error(f"❌ Full traceback: {traceback.format_exc()}")
            raise

    async def _get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug"""
        result = await self.db.execute(
            select(Tenant).where(Tenant.slug == slug, Tenant.is_active == True)
        )
        return result.scalar_one_or_none()

    async def _get_or_create_conversation(
        self,
        tenant: Tenant,
        channel: str,
        channel_user_id: str,
        conversation_id: Optional[str] = None
    ) -> Conversation:
        """Get existing conversation or create a new one"""
        
        if conversation_id:
            # Try to get existing conversation
            result = await self.db.execute(
                select(Conversation).where(
                    Conversation.id == uuid.UUID(conversation_id),
                    Conversation.tenant_id == tenant.id
                )
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation
        
        # Create new conversation
        conversation = Conversation(
            tenant_id=tenant.id,
            channel=channel,
            channel_user_id=channel_user_id,
            status="active"
        )
        
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        # Trigger conversation started webhook
        await self.webhook_service.trigger_webhook(
            WebhookEvents.CONVERSATION_STARTED,
            str(tenant.id),
            {
                "conversation_id": str(conversation.id),
                "channel": channel,
                "channel_user_id": channel_user_id,
                "timestamp": conversation.created_at.isoformat()
            }
        )
        
        return conversation

    async def _save_message(
        self,
        conversation: Conversation,
        content: str,
        direction: str,
        sender: str,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None,
        ai_model_used: Optional[str] = None,
        tokens_used: Optional[int] = None,
        processed_by_ai: bool = False
    ) -> Message:
        """Save a message to the database"""
        
        message = Message(
            conversation_id=conversation.id,
            content=content,
            direction=direction,
            sender=sender,
            media_url=media_url,
            media_type=media_type,
            ai_model_used=ai_model_used,
            tokens_used=tokens_used,
            processed_by_ai=processed_by_ai
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        return message

    async def _generate_response(
        self,
        tenant: Tenant,
        conversation: Conversation,
        message: str,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> tuple[str, str, int]:
        """Generate AI response using the model router"""
        
        # Get conversation history for context
        history = await self._get_conversation_history(conversation)
        
        # Determine if we need multimodal processing
        needs_multimodal = media_url is not None and media_type and media_type.startswith('image/')
        
        # Use model router to generate response
        response = await self.model_router.generate_response(
            message=message,
            context=history,
            tenant_config=tenant.config,
            media_url=media_url if needs_multimodal else None,
            use_multimodal=needs_multimodal
        )
        
        return response["content"], response["model"], response["tokens_used"]

    async def _get_conversation_history(
        self,
        conversation: Conversation,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """Get recent conversation history for context"""
        
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        
        messages = result.scalars().all()
        
        # Convert to format expected by model router
        history = []
        for msg in reversed(messages):  # Reverse to get chronological order
            history.append({
                "role": "user" if msg.sender == "user" else "assistant",
                "content": msg.content,
                "media_url": msg.media_url,
                "media_type": msg.media_type
            })
        
        return history

    async def _process_decision_tree(
        self,
        tenant: Tenant,
        conversation: Conversation,
        message: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Process decision tree logic if configured for tenant"""
        
        # Check if tenant has decision trees configured
        decision_trees = tenant.config.get("decision_trees", [])
        if not decision_trees:
            return {"action": "continue", "response": ai_response}
        
        # Get conversation context
        context = {
            "user_id": conversation.channel_user_id,
            "channel": conversation.channel,
            "conversation_id": str(conversation.id),
            "user_name": conversation.user_name,
            "user_phone": conversation.user_phone,
            **conversation.context,
            **conversation.user_metadata
        }
        
        # Process each decision tree until one returns an action
        for tree_config in decision_trees:
            if not tree_config.get("enabled", True):
                continue
                
            result = await self.decision_tree.process_decision_tree(
                tree_config, message, context, ai_response
            )
            
            if result["action"] != "continue":
                # Handle special actions
                await self._handle_decision_tree_action(
                    result, conversation, tenant
                )
                return result
        
        return {"action": "continue", "response": ai_response}

    async def _handle_decision_tree_action(
        self,
        result: Dict[str, Any],
        conversation: Conversation,
        tenant: Tenant
    ):
        """Handle special actions from decision tree processing"""
        
        action = result["action"]
        metadata = result.get("metadata", {})
        
        if action == "handover":
            # Mark conversation for human handover
            conversation.handed_over_to_human = True
            conversation.handover_reason = metadata.get("reason", "Decision tree triggered")
            conversation.status = "handed_over"
            
            # TODO: Trigger webhook for human handover notification
            await self.db.commit()
            
        elif action == "webhook":
            # TODO: Trigger webhook call
            webhook_url = metadata.get("webhook_url")
            if webhook_url:
                logging.info(f"Would trigger webhook: {webhook_url}")
        
        elif action == "message":
            # Custom message handling is already done in the main flow
            pass

    def _calculate_ai_cost(self, model_used: str, tokens_used: int) -> int:
        """Calculate cost in cents for AI usage"""
        
        # Pricing per 1K tokens (in cents)
        pricing = {
            "gpt-3.5-turbo": 0.15,  # $0.0015 per 1K tokens
            "gpt-4o": 0.30,         # $0.003 per 1K tokens
            "mistral:latest": 0.0,  # Local models are free
            "llava:latest": 0.0,
            "fallback": 0.0
        }
        
        rate = pricing.get(model_used, 0.0)
        return int((tokens_used / 1000) * rate * 100)  # Convert to cents