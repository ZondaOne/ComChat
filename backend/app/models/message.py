from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Conversation relationship
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    conversation = relationship("Conversation", back_populates="messages")
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, image, audio, video, document
    
    # Direction and source
    direction = Column(String(20), nullable=False)  # inbound, outbound
    sender = Column(String(50), nullable=False)  # user, bot, agent
    
    # Channel-specific data
    channel_message_id = Column(String(255), nullable=True)  # Message ID from the channel
    channel_data = Column(JSON, default=dict)  # Channel-specific metadata
    
    # AI/Bot processing
    processed_by_ai = Column(Boolean, default=False)
    ai_model_used = Column(String(100), nullable=True)  # gpt-3.5-turbo, gpt-4o, etc.
    ai_confidence = Column(Integer, nullable=True)  # 0-100
    ai_intent = Column(String(255), nullable=True)  # Detected intent
    
    # Media handling
    media_url = Column(Text, nullable=True)
    media_type = Column(String(50), nullable=True)  # image/jpeg, audio/mpeg, etc.
    media_size = Column(Integer, nullable=True)  # File size in bytes
    
    # Processing metadata
    processing_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_cents = Column(Integer, nullable=True)  # Cost in cents
    
    # Status
    status = Column(String(50), default="delivered")  # pending, delivered, failed, read
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Message {self.id} ({self.direction})>"