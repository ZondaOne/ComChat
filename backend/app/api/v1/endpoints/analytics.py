from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.db import get_db
from app.models import Conversation, Message, UsageRecord, Tenant

router = APIRouter()


class ConversationStats(BaseModel):
    total_conversations: int
    active_conversations: int
    conversations_today: int
    conversations_this_week: int
    conversations_this_month: int
    avg_messages_per_conversation: float
    avg_response_time_ms: float


class MessageStats(BaseModel):
    total_messages: int
    messages_today: int
    messages_this_week: int
    messages_this_month: int
    user_messages: int
    bot_messages: int
    messages_by_channel: Dict[str, int]


class UsageStats(BaseModel):
    current_period_messages: int
    current_period_ai_requests: int
    total_cost_cents: int
    usage_by_day: List[Dict[str, Any]]
    model_usage: Dict[str, int]


class PopularTopics(BaseModel):
    topics: List[Dict[str, Any]]


@router.get("/overview", response_model=Dict[str, Any])
async def get_analytics_overview(
    tenant_id: str,  # TODO: Get from authentication
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics overview for tenant dashboard"""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get conversation stats
        conversation_stats = await _get_conversation_stats(db, tenant_id, start_date)
        
        # Get message stats
        message_stats = await _get_message_stats(db, tenant_id, start_date)
        
        # Get usage stats
        usage_stats = await _get_usage_stats(db, tenant_id, start_date)
        
        # Get channel performance
        channel_performance = await _get_channel_performance(db, tenant_id, start_date)
        
        # Get response time trends
        response_trends = await _get_response_time_trends(db, tenant_id, start_date)
        
        return {
            "period_days": days,
            "conversations": conversation_stats,
            "messages": message_stats,
            "usage": usage_stats,
            "channel_performance": channel_performance,
            "response_trends": response_trends,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")


@router.get("/conversations/stats", response_model=ConversationStats)
async def get_conversation_stats(
    tenant_id: str,  # TODO: Get from authentication
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed conversation statistics"""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        return await _get_conversation_stats(db, tenant_id, start_date)
        
    except Exception as e:
        logging.error(f"Error getting conversation stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation stats")


@router.get("/messages/stats", response_model=MessageStats)
async def get_message_stats(
    tenant_id: str,  # TODO: Get from authentication
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed message statistics"""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        return await _get_message_stats(db, tenant_id, start_date)
        
    except Exception as e:
        logging.error(f"Error getting message stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get message stats")


@router.get("/usage/stats", response_model=UsageStats)
async def get_usage_stats(
    tenant_id: str,  # TODO: Get from authentication
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed usage statistics"""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        return await _get_usage_stats(db, tenant_id, start_date)
        
    except Exception as e:
        logging.error(f"Error getting usage stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage stats")


@router.get("/conversations/recent")
async def get_recent_conversations(
    tenant_id: str,  # TODO: Get from authentication
    limit: int = Query(10, description="Number of conversations to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get recent conversations with basic info"""
    
    try:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.tenant_id == tenant_id)
            .order_by(desc(Conversation.last_message_at))
            .limit(limit)
        )
        
        conversations = result.scalars().all()
        
        # Get message count for each conversation
        conversation_data = []
        for conv in conversations:
            message_count_result = await db.execute(
                select(func.count(Message.id))
                .where(Message.conversation_id == conv.id)
            )
            message_count = message_count_result.scalar() or 0
            
            conversation_data.append({
                "id": str(conv.id),
                "channel": conv.channel,
                "channel_user_id": conv.channel_user_id,
                "user_name": conv.user_name,
                "status": conv.status,
                "message_count": message_count,
                "created_at": conv.created_at.isoformat(),
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "handed_over_to_human": conv.handed_over_to_human
            })
        
        return {"conversations": conversation_data}
        
    except Exception as e:
        logging.error(f"Error getting recent conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")


async def _get_conversation_stats(db: AsyncSession, tenant_id: str, start_date: datetime) -> ConversationStats:
    """Get conversation statistics"""
    
    # Total conversations
    total_result = await db.execute(
        select(func.count(Conversation.id))
        .where(Conversation.tenant_id == tenant_id)
    )
    total_conversations = total_result.scalar() or 0
    
    # Active conversations
    active_result = await db.execute(
        select(func.count(Conversation.id))
        .where(
            Conversation.tenant_id == tenant_id,
            Conversation.status == "active"
        )
    )
    active_conversations = active_result.scalar() or 0
    
    # Conversations by time period
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    today_result = await db.execute(
        select(func.count(Conversation.id))
        .where(
            Conversation.tenant_id == tenant_id,
            Conversation.created_at >= today
        )
    )
    conversations_today = today_result.scalar() or 0
    
    week_result = await db.execute(
        select(func.count(Conversation.id))
        .where(
            Conversation.tenant_id == tenant_id,
            Conversation.created_at >= week_ago
        )
    )
    conversations_this_week = week_result.scalar() or 0
    
    month_result = await db.execute(
        select(func.count(Conversation.id))
        .where(
            Conversation.tenant_id == tenant_id,
            Conversation.created_at >= month_ago
        )
    )
    conversations_this_month = month_result.scalar() or 0
    
    # Average messages per conversation
    avg_messages_result = await db.execute(
        select(func.avg(func.count(Message.id)))
        .select_from(Conversation)
        .join(Message, Message.conversation_id == Conversation.id)
        .where(Conversation.tenant_id == tenant_id)
        .group_by(Conversation.id)
    )
    avg_messages = float(avg_messages_result.scalar() or 0)
    
    # Average response time
    avg_response_result = await db.execute(
        select(func.avg(Message.processing_time_ms))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.tenant_id == tenant_id,
            Message.direction == "outbound",
            Message.processing_time_ms.isnot(None)
        )
    )
    avg_response_time = float(avg_response_result.scalar() or 0)
    
    return ConversationStats(
        total_conversations=total_conversations,
        active_conversations=active_conversations,
        conversations_today=conversations_today,
        conversations_this_week=conversations_this_week,
        conversations_this_month=conversations_this_month,
        avg_messages_per_conversation=avg_messages,
        avg_response_time_ms=avg_response_time
    )


async def _get_message_stats(db: AsyncSession, tenant_id: str, start_date: datetime) -> MessageStats:
    """Get message statistics"""
    
    # Total messages
    total_result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.tenant_id == tenant_id)
    )
    total_messages = total_result.scalar() or 0
    
    # Messages by time period
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    today_result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.tenant_id == tenant_id,
            Message.created_at >= today
        )
    )
    messages_today = today_result.scalar() or 0
    
    week_result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.tenant_id == tenant_id,
            Message.created_at >= week_ago
        )
    )
    messages_this_week = week_result.scalar() or 0
    
    month_result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.tenant_id == tenant_id,
            Message.created_at >= month_ago
        )
    )
    messages_this_month = month_result.scalar() or 0
    
    # Messages by direction
    user_result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.tenant_id == tenant_id,
            Message.direction == "inbound"
        )
    )
    user_messages = user_result.scalar() or 0
    
    bot_result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.tenant_id == tenant_id,
            Message.direction == "outbound"
        )
    )
    bot_messages = bot_result.scalar() or 0
    
    # Messages by channel
    channel_result = await db.execute(
        select(Conversation.channel, func.count(Message.id))
        .join(Message, Message.conversation_id == Conversation.id)
        .where(Conversation.tenant_id == tenant_id)
        .group_by(Conversation.channel)
    )
    
    messages_by_channel = {row[0]: row[1] for row in channel_result.fetchall()}
    
    return MessageStats(
        total_messages=total_messages,
        messages_today=messages_today,
        messages_this_week=messages_this_week,
        messages_this_month=messages_this_month,
        user_messages=user_messages,
        bot_messages=bot_messages,
        messages_by_channel=messages_by_channel
    )


async def _get_usage_stats(db: AsyncSession, tenant_id: str, start_date: datetime) -> UsageStats:
    """Get usage statistics"""
    
    current_period = datetime.utcnow().strftime("%Y-%m")
    
    # Current period usage
    messages_result = await db.execute(
        select(func.sum(UsageRecord.quantity))
        .where(
            UsageRecord.tenant_id == tenant_id,
            UsageRecord.usage_type == "messages",
            UsageRecord.billing_period == current_period
        )
    )
    current_messages = messages_result.scalar() or 0
    
    ai_result = await db.execute(
        select(func.sum(UsageRecord.quantity))
        .where(
            UsageRecord.tenant_id == tenant_id,
            UsageRecord.usage_type == "ai_requests",
            UsageRecord.billing_period == current_period
        )
    )
    current_ai_requests = ai_result.scalar() or 0
    
    # Total cost
    cost_result = await db.execute(
        select(func.sum(UsageRecord.cost_cents))
        .where(
            UsageRecord.tenant_id == tenant_id,
            UsageRecord.recorded_at >= start_date
        )
    )
    total_cost = cost_result.scalar() or 0
    
    # Usage by day (last 30 days)
    usage_by_day = []
    for i in range(30):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_result = await db.execute(
            select(
                func.sum(UsageRecord.quantity).label("total"),
                UsageRecord.usage_type
            )
            .where(
                UsageRecord.tenant_id == tenant_id,
                UsageRecord.recorded_at >= day_start,
                UsageRecord.recorded_at < day_end
            )
            .group_by(UsageRecord.usage_type)
        )
        
        day_usage = {row[1]: row[0] for row in day_result.fetchall()}
        usage_by_day.append({
            "date": day.strftime("%Y-%m-%d"),
            "messages": day_usage.get("messages", 0),
            "ai_requests": day_usage.get("ai_requests", 0)
        })
    
    # Model usage
    model_result = await db.execute(
        select(Message.ai_model_used, func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.tenant_id == tenant_id,
            Message.ai_model_used.isnot(None),
            Message.created_at >= start_date
        )
        .group_by(Message.ai_model_used)
    )
    
    model_usage = {row[0]: row[1] for row in model_result.fetchall()}
    
    return UsageStats(
        current_period_messages=current_messages,
        current_period_ai_requests=current_ai_requests,
        total_cost_cents=total_cost,
        usage_by_day=usage_by_day,
        model_usage=model_usage
    )


async def _get_channel_performance(db: AsyncSession, tenant_id: str, start_date: datetime) -> Dict[str, Any]:
    """Get channel performance metrics"""
    
    result = await db.execute(
        select(
            Conversation.channel,
            func.count(Conversation.id).label("conversations"),
            func.count(Message.id).label("messages"),
            func.avg(Message.processing_time_ms).label("avg_response_time")
        )
        .join(Message, Message.conversation_id == Conversation.id, isouter=True)
        .where(
            Conversation.tenant_id == tenant_id,
            Conversation.created_at >= start_date
        )
        .group_by(Conversation.channel)
    )
    
    channels = []
    for row in result.fetchall():
        channels.append({
            "channel": row[0],
            "conversations": row[1],
            "messages": row[2] or 0,
            "avg_response_time_ms": float(row[3] or 0)
        })
    
    return {"channels": channels}


async def _get_response_time_trends(db: AsyncSession, tenant_id: str, start_date: datetime) -> Dict[str, Any]:
    """Get response time trends over time"""
    
    # Get daily average response times
    trends = []
    for i in range(30):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        result = await db.execute(
            select(func.avg(Message.processing_time_ms))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.tenant_id == tenant_id,
                Message.direction == "outbound",
                Message.processing_time_ms.isnot(None),
                Message.created_at >= day_start,
                Message.created_at < day_end
            )
        )
        
        avg_time = result.scalar()
        trends.append({
            "date": day.strftime("%Y-%m-%d"),
            "avg_response_time_ms": float(avg_time or 0)
        })
    
    return {"trends": trends}