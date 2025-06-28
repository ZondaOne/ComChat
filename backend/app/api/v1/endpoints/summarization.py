from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.core.db import get_db
from app.services.summarization import SummarizationService
from app.models import Conversation, ConversationSummary, SummaryTemplate

router = APIRouter()


class SummaryResponse(BaseModel):
    id: str
    conversation_id: str
    summary: str
    key_topics: List[str]
    user_intent: Optional[str]
    resolution_status: Optional[str]
    overall_sentiment: Optional[str]
    user_satisfaction: Optional[str]
    message_count: int
    duration_minutes: Optional[int]
    summarized_by_model: Optional[str]
    summary_confidence: Optional[float]
    auto_generated: bool
    created_at: str


class CreateTemplateRequest(BaseModel):
    name: str
    prompt_template: str
    description: Optional[str] = ""
    trigger_conditions: Dict[str, Any] = {}
    is_active: bool = True
    is_default: bool = False
    priority: int = 0
    preferred_model: Optional[str] = None
    max_tokens: int = 500
    temperature: float = 0.3
    include_sentiment: bool = True
    include_topics: bool = True
    include_intent: bool = True
    include_resolution: bool = True


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_active: bool
    is_default: bool
    priority: int
    created_at: str


class InsightsResponse(BaseModel):
    total_summaries: int
    sentiment_distribution: Dict[str, int]
    top_topics: List[Dict[str, Any]]
    resolution_rates: Dict[str, Any]
    common_intents: List[Dict[str, Any]]
    average_satisfaction: Dict[str, Any]
    language_distribution: Dict[str, int]


@router.post("/conversations/{conversation_id}/summarize", response_model=SummaryResponse)
async def summarize_conversation(
    conversation_id: str,
    background_tasks: BackgroundTasks,
    force_regenerate: bool = Query(False, description="Force regenerate summary if exists"),
    tenant_id: str = Query(..., description="Tenant ID"),  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Generate or update summary for a specific conversation"""
    
    try:
        # Get conversation
        conversation = await db.get(Conversation, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Verify tenant ownership
        if str(conversation.tenant_id) != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        summarization_service = SummarizationService(db)
        
        # Generate summary
        summary = await summarization_service.auto_summarize_conversation(
            conversation, force_regenerate=force_regenerate
        )
        
        if not summary:
            raise HTTPException(status_code=400, detail="Conversation cannot be summarized")
        
        return SummaryResponse(
            id=str(summary.id),
            conversation_id=str(summary.conversation_id),
            summary=summary.summary,
            key_topics=summary.key_topics or [],
            user_intent=summary.user_intent,
            resolution_status=summary.resolution_status,
            overall_sentiment=summary.overall_sentiment,
            user_satisfaction=summary.user_satisfaction,
            message_count=summary.message_count,
            duration_minutes=summary.duration_minutes,
            summarized_by_model=summary.summarized_by_model,
            summary_confidence=summary.summary_confidence,
            auto_generated=summary.auto_generated,
            created_at=summary.created_at.isoformat()
        )
        
    except Exception as e:
        logging.error(f"Error summarizing conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to summarize conversation")


@router.post("/batch-summarize")
async def batch_summarize_conversations(
    background_tasks: BackgroundTasks,
    tenant_id: str = Query(..., description="Tenant ID"),  # TODO: Get from auth
    batch_size: int = Query(10, description="Number of conversations to process"),
    max_age_hours: int = Query(24, description="Maximum age of conversations to process"),
    db: AsyncSession = Depends(get_db)
):
    """Batch summarize multiple conversations"""
    
    try:
        summarization_service = SummarizationService(db)
        
        # Run batch summarization in background
        background_tasks.add_task(
            summarization_service.summarize_batch_conversations,
            tenant_id, batch_size, max_age_hours
        )
        
        return {
            "message": f"Started batch summarization for up to {batch_size} conversations",
            "batch_size": batch_size,
            "max_age_hours": max_age_hours
        }
        
    except Exception as e:
        logging.error(f"Error starting batch summarization: {e}")
        raise HTTPException(status_code=500, detail="Failed to start batch summarization")


@router.get("/conversations/{conversation_id}/summary", response_model=SummaryResponse)
async def get_conversation_summary(
    conversation_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Get existing summary for a conversation"""
    
    try:
        # Get conversation and verify ownership
        conversation = await db.get(Conversation, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if str(conversation.tenant_id) != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get summary
        summary = conversation.summary
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return SummaryResponse(
            id=str(summary.id),
            conversation_id=str(summary.conversation_id),
            summary=summary.summary,
            key_topics=summary.key_topics or [],
            user_intent=summary.user_intent,
            resolution_status=summary.resolution_status,
            overall_sentiment=summary.overall_sentiment,
            user_satisfaction=summary.user_satisfaction,
            message_count=summary.message_count,
            duration_minutes=summary.duration_minutes,
            summarized_by_model=summary.summarized_by_model,
            summary_confidence=summary.summary_confidence,
            auto_generated=summary.auto_generated,
            created_at=summary.created_at.isoformat()
        )
        
    except Exception as e:
        logging.error(f"Error getting conversation summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get summary")


@router.post("/templates", response_model=TemplateResponse)
async def create_summary_template(
    request: CreateTemplateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Create a custom summarization template"""
    
    try:
        summarization_service = SummarizationService(db)
        
        template = await summarization_service.create_custom_summary_template(
            tenant_id=tenant_id,
            name=request.name,
            prompt_template=request.prompt_template,
            config={
                "description": request.description,
                "trigger_conditions": request.trigger_conditions,
                "is_active": request.is_active,
                "is_default": request.is_default,
                "priority": request.priority,
                "preferred_model": request.preferred_model,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "include_sentiment": request.include_sentiment,
                "include_topics": request.include_topics,
                "include_intent": request.include_intent,
                "include_resolution": request.include_resolution
            }
        )
        
        return TemplateResponse(
            id=str(template.id),
            name=template.name,
            description=template.description,
            is_active=template.is_active,
            is_default=template.is_default,
            priority=template.priority,
            created_at=template.created_at.isoformat()
        )
        
    except Exception as e:
        logging.error(f"Error creating summary template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")


@router.get("/templates", response_model=List[TemplateResponse])
async def get_summary_templates(
    tenant_id: str = Query(..., description="Tenant ID"),  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Get all summary templates for a tenant"""
    
    try:
        from sqlalchemy import select
        
        result = await db.execute(
            select(SummaryTemplate)
            .where(SummaryTemplate.tenant_id == tenant_id)
            .order_by(SummaryTemplate.priority.desc(), SummaryTemplate.created_at.desc())
        )
        
        templates = result.scalars().all()
        
        return [
            TemplateResponse(
                id=str(template.id),
                name=template.name,
                description=template.description,
                is_active=template.is_active,
                is_default=template.is_default,
                priority=template.priority,
                created_at=template.created_at.isoformat()
            )
            for template in templates
        ]
        
    except Exception as e:
        logging.error(f"Error getting summary templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")


@router.get("/insights", response_model=InsightsResponse)
async def get_conversation_insights(
    tenant_id: str = Query(..., description="Tenant ID"),  # TODO: Get from auth
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get insights from conversation summaries"""
    
    try:
        summarization_service = SummarizationService(db)
        
        insights = await summarization_service.get_conversation_insights(
            tenant_id=tenant_id,
            days=days
        )
        
        if "error" in insights:
            raise HTTPException(status_code=500, detail=insights["error"])
        
        return InsightsResponse(**insights)
        
    except Exception as e:
        logging.error(f"Error getting conversation insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")


@router.get("/summaries")
async def get_recent_summaries(
    tenant_id: str = Query(..., description="Tenant ID"),  # TODO: Get from auth
    limit: int = Query(20, description="Number of summaries to return"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    resolution_status: Optional[str] = Query(None, description="Filter by resolution status"),
    db: AsyncSession = Depends(get_db)
):
    """Get recent conversation summaries with optional filters"""
    
    try:
        from sqlalchemy import select, and_
        
        # Build query with filters
        query = (
            select(ConversationSummary)
            .join(Conversation, ConversationSummary.conversation_id == Conversation.id)
            .where(Conversation.tenant_id == tenant_id)
        )
        
        if sentiment:
            query = query.where(ConversationSummary.overall_sentiment == sentiment)
        
        if resolution_status:
            query = query.where(ConversationSummary.resolution_status == resolution_status)
        
        query = query.order_by(ConversationSummary.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        summaries = result.scalars().all()
        
        return {
            "summaries": [
                {
                    "id": str(summary.id),
                    "conversation_id": str(summary.conversation_id),
                    "summary": summary.summary,
                    "key_topics": summary.key_topics or [],
                    "user_intent": summary.user_intent,
                    "resolution_status": summary.resolution_status,
                    "overall_sentiment": summary.overall_sentiment,
                    "user_satisfaction": summary.user_satisfaction,
                    "message_count": summary.message_count,
                    "duration_minutes": summary.duration_minutes,
                    "created_at": summary.created_at.isoformat()
                }
                for summary in summaries
            ],
            "total": len(summaries),
            "filters_applied": {
                "sentiment": sentiment,
                "resolution_status": resolution_status
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting recent summaries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get summaries")