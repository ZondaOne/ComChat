from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.db import Base


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Conversation relationship
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, unique=True)
    conversation = relationship("Conversation", back_populates="summary")
    
    # Summary content
    summary = Column(Text, nullable=False)
    key_topics = Column(JSON, default=list)  # List of main topics discussed
    user_intent = Column(String(255), nullable=True)  # Primary user intent
    resolution_status = Column(String(50), nullable=True)  # resolved, unresolved, escalated
    
    # Sentiment analysis
    overall_sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    user_satisfaction = Column(String(20), nullable=True)  # satisfied, dissatisfied, neutral
    
    # Metadata
    message_count = Column(Integer, default=0)
    duration_minutes = Column(Integer, nullable=True)
    languages_detected = Column(JSON, default=list)
    
    # AI processing info
    summarized_by_model = Column(String(100), nullable=True)
    summary_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    processing_time_ms = Column(Integer, nullable=True)
    
    # Auto-summarization settings
    auto_generated = Column(Boolean, default=True)
    manual_override = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ConversationSummary {self.conversation_id}>"


class SummaryTemplate(Base):
    __tablename__ = "summary_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")
    
    # Template details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template configuration
    prompt_template = Column(Text, nullable=False)
    trigger_conditions = Column(JSON, default=dict)  # When to apply this template
    
    # Template settings
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    priority = Column(Integer, default=0)  # Higher priority templates used first
    
    # AI model preferences
    preferred_model = Column(String(100), nullable=True)
    max_tokens = Column(Integer, default=500)
    temperature = Column(Float, default=0.3)
    
    # Output format
    include_sentiment = Column(Boolean, default=True)
    include_topics = Column(Boolean, default=True)
    include_intent = Column(Boolean, default=True)
    include_resolution = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SummaryTemplate {self.name}>"