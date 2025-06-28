from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.db import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Channel information
    channel = Column(String(50), nullable=False)  # web, whatsapp, telegram
    channel_user_id = Column(String(255), nullable=False)  # user ID from the channel
    channel_conversation_id = Column(String(255), nullable=True)  # conversation/chat ID from channel
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant", back_populates="conversations")
    
    # Conversation state
    status = Column(String(50), default="active")  # active, handed_over, closed
    context = Column(JSON, default=dict)  # Store conversation context
    
    # Human handover
    handed_over_to_human = Column(Boolean, default=False)
    handover_reason = Column(Text, nullable=True)
    human_agent_id = Column(String(255), nullable=True)
    
    # Metadata
    user_name = Column(String(255), nullable=True)
    user_phone = Column(String(20), nullable=True)
    user_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    summary = relationship("ConversationSummary", back_populates="conversation", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation {self.id} ({self.channel})>"