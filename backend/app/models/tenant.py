from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.db import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Contact info
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=True)
    
    # Subscription info
    subscription_tier = Column(String(50), default="free")  # free, basic, pro, enterprise
    is_active = Column(Boolean, default=True)
    
    # Configuration
    config = Column(JSON, default=dict)  # Chatbot configuration, decision trees, etc.
    
    # Channel settings
    whatsapp_enabled = Column(Boolean, default=False)
    telegram_enabled = Column(Boolean, default=False)
    web_widget_enabled = Column(Boolean, default=True)
    
    # API keys and tokens
    whatsapp_access_token = Column(Text, nullable=True)
    telegram_bot_token = Column(Text, nullable=True)
    
    # Human handover settings
    human_handover_enabled = Column(Boolean, default=False)
    handover_webhook_url = Column(Text, nullable=True)
    
    # Usage limits
    monthly_message_limit = Column(Integer, default=1000)
    monthly_message_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="tenant", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="tenant", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant {self.name} ({self.slug})>"