from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.db import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")
    
    # Template details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # system, conversation, summarization, etc.
    
    # Template content
    template_content = Column(Text, nullable=False)
    variables = Column(JSON, default=list)  # List of available variables
    
    # Usage context
    use_cases = Column(JSON, default=list)  # Where this template can be used
    trigger_conditions = Column(JSON, default=dict)  # When to use this template
    
    # Template settings
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    
    # AI model preferences
    preferred_model = Column(String(100), nullable=True)
    model_parameters = Column(JSON, default=dict)  # temperature, max_tokens, etc.
    
    # Performance tracking
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # Based on user feedback
    average_response_time = Column(Float, default=0.0)
    
    # Version control
    version = Column(String(20), default="1.0")
    parent_template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<PromptTemplate {self.name} ({self.category})>"


class PromptVariable(Base):
    __tablename__ = "prompt_variables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template relationship
    template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=False)
    template = relationship("PromptTemplate")
    
    # Variable definition
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    variable_type = Column(String(50), nullable=False)  # string, number, boolean, array, object
    
    # Validation
    is_required = Column(Boolean, default=False)
    default_value = Column(Text, nullable=True)
    validation_rules = Column(JSON, default=dict)  # regex, min/max length, etc.
    
    # Examples and help
    example_values = Column(JSON, default=list)
    help_text = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<PromptVariable {self.name}>"


class PromptExecution(Base):
    __tablename__ = "prompt_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template relationship
    template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=False)
    template = relationship("PromptTemplate")
    
    # Execution context
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Input and output
    input_variables = Column(JSON, default=dict)
    rendered_prompt = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    
    # Execution metadata
    model_used = Column(String(100), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_cents = Column(Integer, nullable=True)
    
    # Quality metrics
    success = Column(Boolean, default=True)
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    user_feedback = Column(Text, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PromptExecution {self.template_id}>"