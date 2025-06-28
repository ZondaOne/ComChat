from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.db import Base


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant", back_populates="webhooks")
    
    # Webhook configuration
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    secret = Column(String(255), nullable=True)  # For webhook verification
    
    # Events to listen for
    events = Column(JSON, default=list)  # ['message.received', 'conversation.started', etc.]
    
    # Settings
    is_active = Column(Boolean, default=True)
    retry_count = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=30)
    
    # Headers and authentication
    headers = Column(JSON, default=dict)
    auth_type = Column(String(50), nullable=True)  # bearer, basic, custom
    auth_credentials = Column(JSON, default=dict)
    
    # Statistics
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    failed_calls = Column(Integer, default=0)
    last_called_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Webhook {self.name} ({self.url})>"