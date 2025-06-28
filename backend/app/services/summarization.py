from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import json
import logging
import re

from app.models import Conversation, ConversationSummary, SummaryTemplate, Message, Tenant
from app.services.model_router import ModelRouter
from app.core.config import settings


class SummarizationService:
    """Service for automatically summarizing conversations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model_router = ModelRouter()
    
    async def auto_summarize_conversation(
        self,
        conversation: Conversation,
        force_regenerate: bool = False
    ) -> Optional[ConversationSummary]:
        """Automatically summarize a conversation when appropriate"""
        
        try:
            # Check if conversation should be summarized
            if not await self._should_summarize_conversation(conversation, force_regenerate):
                return None
            
            # Get or create summary
            existing_summary = await self._get_existing_summary(conversation.id)
            if existing_summary and not force_regenerate:
                return existing_summary
            
            # Get conversation messages
            messages = await self._get_conversation_messages(conversation.id)
            if len(messages) < 2:  # Need at least user message + bot response
                return None
            
            # Get summarization template
            template = await self._get_summarization_template(conversation.tenant_id)
            
            # Generate summary
            summary_data = await self._generate_summary(
                conversation, messages, template
            )
            
            # Save or update summary
            if existing_summary:
                summary = await self._update_summary(existing_summary, summary_data)
            else:
                summary = await self._create_summary(conversation, summary_data)
            
            return summary
            
        except Exception as e:
            logging.error(f"Error auto-summarizing conversation {conversation.id}: {e}")
            return None
    
    async def summarize_batch_conversations(
        self,
        tenant_id: str,
        batch_size: int = 10,
        max_age_hours: int = 24
    ) -> List[ConversationSummary]:
        """Summarize multiple conversations in batch"""
        
        try:
            # Get conversations that need summarization
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            result = await self.db.execute(
                select(Conversation)
                .where(
                    and_(
                        Conversation.tenant_id == tenant_id,
                        Conversation.status.in_(["closed", "handed_over"]),
                        Conversation.updated_at >= cutoff_time
                    )
                )
                .limit(batch_size)
            )
            
            conversations = result.scalars().all()
            summaries = []
            
            for conversation in conversations:
                summary = await self.auto_summarize_conversation(conversation)
                if summary:
                    summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logging.error(f"Error in batch summarization: {e}")
            return []
    
    async def create_custom_summary_template(
        self,
        tenant_id: str,
        name: str,
        prompt_template: str,
        config: Dict[str, Any]
    ) -> SummaryTemplate:
        """Create a custom summarization template for a tenant"""
        
        template = SummaryTemplate(
            tenant_id=tenant_id,
            name=name,
            prompt_template=prompt_template,
            description=config.get("description", ""),
            trigger_conditions=config.get("trigger_conditions", {}),
            is_active=config.get("is_active", True),
            is_default=config.get("is_default", False),
            priority=config.get("priority", 0),
            preferred_model=config.get("preferred_model"),
            max_tokens=config.get("max_tokens", 500),
            temperature=config.get("temperature", 0.3),
            include_sentiment=config.get("include_sentiment", True),
            include_topics=config.get("include_topics", True),
            include_intent=config.get("include_intent", True),
            include_resolution=config.get("include_resolution", True)
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        return template
    
    async def get_conversation_insights(
        self,
        tenant_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get insights from conversation summaries"""
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get summaries for analysis
            result = await self.db.execute(
                select(ConversationSummary)
                .join(Conversation, ConversationSummary.conversation_id == Conversation.id)
                .where(
                    and_(
                        Conversation.tenant_id == tenant_id,
                        ConversationSummary.created_at >= start_date
                    )
                )
            )
            
            summaries = result.scalars().all()
            
            if not summaries:
                return {"total_summaries": 0}
            
            # Analyze summaries
            insights = {
                "total_summaries": len(summaries),
                "sentiment_distribution": self._analyze_sentiment_distribution(summaries),
                "top_topics": self._extract_top_topics(summaries),
                "resolution_rates": self._analyze_resolution_rates(summaries),
                "common_intents": self._analyze_common_intents(summaries),
                "average_satisfaction": self._calculate_average_satisfaction(summaries),
                "language_distribution": self._analyze_language_distribution(summaries)
            }
            
            return insights
            
        except Exception as e:
            logging.error(f"Error getting conversation insights: {e}")
            return {"error": str(e)}
    
    async def _should_summarize_conversation(
        self,
        conversation: Conversation,
        force_regenerate: bool = False
    ) -> bool:
        """Determine if a conversation should be summarized"""
        
        if force_regenerate:
            return True
        
        # Check if conversation is in a summarizable state
        if conversation.status not in ["closed", "handed_over"]:
            return False
        
        # Check minimum message count
        message_count_result = await self.db.execute(
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation.id)
        )
        message_count = message_count_result.scalar() or 0
        
        if message_count < 3:  # Need meaningful conversation
            return False
        
        # Check if summary already exists
        existing_summary = await self._get_existing_summary(conversation.id)
        if existing_summary and not existing_summary.manual_override:
            return False
        
        return True
    
    async def _get_existing_summary(
        self,
        conversation_id: str
    ) -> Optional[ConversationSummary]:
        """Get existing summary for conversation"""
        
        result = await self.db.execute(
            select(ConversationSummary)
            .where(ConversationSummary.conversation_id == conversation_id)
        )
        
        return result.scalar_one_or_none()
    
    async def _get_conversation_messages(
        self,
        conversation_id: str
    ) -> List[Message]:
        """Get all messages for a conversation"""
        
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        
        return result.scalars().all()
    
    async def _get_summarization_template(
        self,
        tenant_id: str
    ) -> SummaryTemplate:
        """Get the best summarization template for a tenant"""
        
        # Try to get tenant-specific template
        result = await self.db.execute(
            select(SummaryTemplate)
            .where(
                and_(
                    SummaryTemplate.tenant_id == tenant_id,
                    SummaryTemplate.is_active == True
                )
            )
            .order_by(SummaryTemplate.priority.desc(), SummaryTemplate.is_default.desc())
        )
        
        template = result.scalar_one_or_none()
        
        if template:
            return template
        
        # Create default template if none exists
        return await self._create_default_template(tenant_id)
    
    async def _create_default_template(self, tenant_id: str) -> SummaryTemplate:
        """Create a default summarization template"""
        
        default_prompt = """
        Analyze this customer service conversation and provide a structured summary:

        CONVERSATION:
        {conversation_text}

        Please provide:
        1. SUMMARY: A concise 2-3 sentence summary of the conversation
        2. TOPICS: Main topics discussed (max 5)
        3. INTENT: Primary customer intent
        4. RESOLUTION: Was the issue resolved? (resolved/unresolved/escalated)
        5. SENTIMENT: Overall customer sentiment (positive/negative/neutral)
        6. SATISFACTION: Customer satisfaction level (satisfied/dissatisfied/neutral)

        Format as JSON:
        {
            "summary": "...",
            "topics": ["topic1", "topic2"],
            "intent": "...",
            "resolution": "...",
            "sentiment": "...",
            "satisfaction": "..."
        }
        """
        
        template = SummaryTemplate(
            tenant_id=tenant_id,
            name="Default Template",
            description="Default conversation summarization template",
            prompt_template=default_prompt,
            is_active=True,
            is_default=True,
            priority=0
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        return template
    
    async def _generate_summary(
        self,
        conversation: Conversation,
        messages: List[Message],
        template: SummaryTemplate
    ) -> Dict[str, Any]:
        """Generate summary using AI model"""
        
        try:
            # Build conversation text
            conversation_text = self._build_conversation_text(messages)
            
            # Format prompt
            prompt = template.prompt_template.format(
                conversation_text=conversation_text,
                user_name=conversation.user_name or "User",
                channel=conversation.channel
            )
            
            # Generate summary using AI
            response = await self.model_router.generate_response(
                message=prompt,
                context=[],
                tenant_config={},
                use_multimodal=False
            )
            
            # Parse AI response
            summary_data = self._parse_ai_summary_response(
                response["content"],
                len(messages),
                conversation
            )
            
            summary_data["summarized_by_model"] = response["model"]
            summary_data["processing_time_ms"] = response.get("processing_time_ms", 0)
            
            return summary_data
            
        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            # Return fallback summary
            return self._create_fallback_summary(messages, conversation)
    
    def _build_conversation_text(self, messages: List[Message]) -> str:
        """Build formatted conversation text for AI analysis"""
        
        conversation_lines = []
        
        for message in messages:
            sender = "Customer" if message.sender == "user" else "Agent"
            timestamp = message.created_at.strftime("%H:%M")
            
            line = f"[{timestamp}] {sender}: {message.content}"
            
            if message.media_url:
                media_type = message.media_type or "media"
                line += f" [Shared {media_type}]"
            
            conversation_lines.append(line)
        
        return "\n".join(conversation_lines)
    
    def _parse_ai_summary_response(
        self,
        ai_response: str,
        message_count: int,
        conversation: Conversation
    ) -> Dict[str, Any]:
        """Parse AI response into structured summary data"""
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                summary_json = json.loads(json_match.group())
                
                return {
                    "summary": summary_json.get("summary", "")[:1000],  # Limit length
                    "key_topics": summary_json.get("topics", [])[:5],  # Max 5 topics
                    "user_intent": summary_json.get("intent", "")[:255],
                    "resolution_status": summary_json.get("resolution", "unresolved"),
                    "overall_sentiment": summary_json.get("sentiment", "neutral"),
                    "user_satisfaction": summary_json.get("satisfaction", "neutral"),
                    "message_count": message_count,
                    "duration_minutes": self._calculate_conversation_duration(conversation),
                    "summary_confidence": 0.8,  # High confidence for structured response
                    "auto_generated": True
                }
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"Failed to parse AI summary JSON: {e}")
        
        # Fallback: extract information from free text
        return self._extract_summary_from_text(ai_response, message_count, conversation)
    
    def _extract_summary_from_text(
        self,
        text: str,
        message_count: int,
        conversation: Conversation
    ) -> Dict[str, Any]:
        """Extract summary information from free text response"""
        
        # Simple text extraction (could be enhanced with NLP)
        summary = text[:500] if text else "Conversation summary unavailable"
        
        # Basic sentiment detection
        sentiment = "neutral"
        if any(word in text.lower() for word in ["happy", "satisfied", "good", "great"]):
            sentiment = "positive"
        elif any(word in text.lower() for word in ["angry", "frustrated", "bad", "terrible"]):
            sentiment = "negative"
        
        return {
            "summary": summary,
            "key_topics": [],
            "user_intent": "general_inquiry",
            "resolution_status": "unresolved",
            "overall_sentiment": sentiment,
            "user_satisfaction": "neutral",
            "message_count": message_count,
            "duration_minutes": self._calculate_conversation_duration(conversation),
            "summary_confidence": 0.4,  # Lower confidence for unstructured response
            "auto_generated": True
        }
    
    def _create_fallback_summary(
        self,
        messages: List[Message],
        conversation: Conversation
    ) -> Dict[str, Any]:
        """Create a basic fallback summary when AI fails"""
        
        return {
            "summary": f"Conversation with {len(messages)} messages via {conversation.channel}",
            "key_topics": [],
            "user_intent": "general_inquiry",
            "resolution_status": "unresolved",
            "overall_sentiment": "neutral",
            "user_satisfaction": "neutral",
            "message_count": len(messages),
            "duration_minutes": self._calculate_conversation_duration(conversation),
            "summary_confidence": 0.2,  # Low confidence for fallback
            "auto_generated": True
        }
    
    def _calculate_conversation_duration(self, conversation: Conversation) -> Optional[int]:
        """Calculate conversation duration in minutes"""
        
        if conversation.last_message_at and conversation.created_at:
            duration = conversation.last_message_at - conversation.created_at
            return int(duration.total_seconds() / 60)
        
        return None
    
    async def _create_summary(
        self,
        conversation: Conversation,
        summary_data: Dict[str, Any]
    ) -> ConversationSummary:
        """Create new conversation summary"""
        
        summary = ConversationSummary(
            conversation_id=conversation.id,
            **summary_data
        )
        
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)
        
        return summary
    
    async def _update_summary(
        self,
        existing_summary: ConversationSummary,
        summary_data: Dict[str, Any]
    ) -> ConversationSummary:
        """Update existing conversation summary"""
        
        for key, value in summary_data.items():
            setattr(existing_summary, key, value)
        
        existing_summary.updated_at = func.now()
        await self.db.commit()
        await self.db.refresh(existing_summary)
        
        return existing_summary
    
    # Insight analysis methods
    def _analyze_sentiment_distribution(self, summaries: List[ConversationSummary]) -> Dict[str, int]:
        """Analyze sentiment distribution"""
        sentiments = {}
        for summary in summaries:
            sentiment = summary.overall_sentiment or "neutral"
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        return sentiments
    
    def _extract_top_topics(self, summaries: List[ConversationSummary]) -> List[Dict[str, Any]]:
        """Extract top topics from summaries"""
        topic_counts = {}
        for summary in summaries:
            for topic in summary.key_topics or []:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return [
            {"topic": topic, "count": count}
            for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _analyze_resolution_rates(self, summaries: List[ConversationSummary]) -> Dict[str, Any]:
        """Analyze resolution rates"""
        resolutions = {}
        for summary in summaries:
            status = summary.resolution_status or "unresolved"
            resolutions[status] = resolutions.get(status, 0) + 1
        
        total = len(summaries)
        resolved = resolutions.get("resolved", 0)
        resolution_rate = (resolved / total * 100) if total > 0 else 0
        
        return {
            "resolution_rate_percent": round(resolution_rate, 1),
            "breakdown": resolutions
        }
    
    def _analyze_common_intents(self, summaries: List[ConversationSummary]) -> List[Dict[str, Any]]:
        """Analyze common user intents"""
        intents = {}
        for summary in summaries:
            intent = summary.user_intent or "unknown"
            intents[intent] = intents.get(intent, 0) + 1
        
        return [
            {"intent": intent, "count": count}
            for intent, count in sorted(intents.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _calculate_average_satisfaction(self, summaries: List[ConversationSummary]) -> Dict[str, Any]:
        """Calculate average satisfaction metrics"""
        satisfactions = {}
        for summary in summaries:
            satisfaction = summary.user_satisfaction or "neutral"
            satisfactions[satisfaction] = satisfactions.get(satisfaction, 0) + 1
        
        total = len(summaries)
        satisfied = satisfactions.get("satisfied", 0)
        satisfaction_rate = (satisfied / total * 100) if total > 0 else 0
        
        return {
            "satisfaction_rate_percent": round(satisfaction_rate, 1),
            "breakdown": satisfactions
        }
    
    def _analyze_language_distribution(self, summaries: List[ConversationSummary]) -> Dict[str, int]:
        """Analyze language distribution"""
        languages = {}
        for summary in summaries:
            for lang in summary.languages_detected or ["en"]:
                languages[lang] = languages.get(lang, 0) + 1
        return languages