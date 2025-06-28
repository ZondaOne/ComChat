from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON, Integer, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.db import Base


class WorkflowStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class WorkflowStepType(enum.Enum):
    PROMPT = "prompt"
    CONDITION = "condition"
    ACTION = "action"
    DELAY = "delay"
    WEBHOOK = "webhook"


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")
    
    # Workflow details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=False)  # healthcare, finance, education, etc.
    
    # Workflow configuration
    trigger_conditions = Column(JSON, default=dict)  # When to start this workflow
    initial_context = Column(JSON, default=dict)  # Default context variables
    
    # Flow control
    steps = Column(JSON, default=list)  # Ordered list of workflow steps
    error_handling = Column(JSON, default=dict)  # Error recovery strategies
    
    # Settings
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    is_default_for_domain = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    max_execution_time_minutes = Column(Integer, default=30)
    
    # Performance tracking
    execution_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_completion_time = Column(Float, default=0.0)
    
    # Version control
    version = Column(String(20), default="1.0")
    parent_workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_executed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Workflow {self.name} ({self.domain})>"


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Workflow relationship
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    workflow = relationship("Workflow")
    
    # Step details
    name = Column(String(255), nullable=False)
    step_type = Column(Enum(WorkflowStepType), nullable=False)
    order_index = Column(Integer, nullable=False)
    
    # Step configuration
    config = Column(JSON, default=dict)  # Step-specific configuration
    input_mapping = Column(JSON, default=dict)  # How to map inputs
    output_mapping = Column(JSON, default=dict)  # How to map outputs
    
    # Flow control
    next_step_conditions = Column(JSON, default=list)  # Conditional next steps
    timeout_seconds = Column(Integer, default=300)
    retry_config = Column(JSON, default=dict)
    
    # Template reference (for prompt steps)
    prompt_template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=True)
    prompt_template = relationship("PromptTemplate")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<WorkflowStep {self.name} ({self.step_type})>"


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Workflow relationship
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    workflow = relationship("Workflow")
    
    # Execution context
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Execution state
    status = Column(String(50), nullable=False)  # running, completed, failed, cancelled
    current_step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id"), nullable=True)
    context_variables = Column(JSON, default=dict)
    
    # Results
    execution_log = Column(JSON, default=list)  # Step-by-step execution log
    final_output = Column(JSON, default=dict)
    error_details = Column(JSON, nullable=True)
    
    # Performance
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_execution_time_ms = Column(Integer, nullable=True)
    
    # Quality metrics
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    user_feedback = Column(Text, nullable=True)

    def __repr__(self):
        return f"<WorkflowExecution {self.workflow_id}>"


class DomainPromptSet(Base):
    __tablename__ = "domain_prompt_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Domain details
    domain = Column(String(100), nullable=False)  # healthcare, finance, education, etc.
    subdomain = Column(String(100), nullable=True)  # cardiology, investment, k12, etc.
    
    # Set details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0")
    
    # Localization and compliance
    language = Column(String(10), default="en")
    region = Column(String(50), nullable=True)  # us, eu, asia-pacific, etc.
    compliance_tags = Column(JSON, default=list)  # HIPAA, GDPR, SOX, etc.
    
    # Content
    prompt_templates = Column(JSON, default=list)  # List of template configurations
    workflow_templates = Column(JSON, default=list)  # List of workflow configurations
    domain_vocabulary = Column(JSON, default=dict)  # Domain-specific terms and definitions
    
    # Usage
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<DomainPromptSet {self.domain}/{self.name}>"


class ClientWorkflowConfig(Base):
    __tablename__ = "client_workflow_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")
    
    # Configuration details
    domain = Column(String(100), nullable=False)
    config_name = Column(String(255), nullable=False)
    
    # Client customizations
    custom_workflows = Column(JSON, default=list)  # Client-specific workflow overrides
    prompt_customizations = Column(JSON, default=dict)  # Template modifications
    domain_context = Column(JSON, default=dict)  # Client-specific domain knowledge
    
    # Business rules
    approval_workflows = Column(JSON, default=dict)  # When human approval is needed
    escalation_rules = Column(JSON, default=dict)  # When to escalate to human agents
    compliance_settings = Column(JSON, default=dict)  # Compliance requirements
    
    # Integration settings
    external_apis = Column(JSON, default=dict)  # External system integrations
    webhook_endpoints = Column(JSON, default=list)  # Client webhook URLs
    notification_preferences = Column(JSON, default=dict)
    
    # Performance settings
    sla_requirements = Column(JSON, default=dict)  # Response time requirements
    quality_thresholds = Column(JSON, default=dict)  # Quality metrics
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ClientWorkflowConfig {self.tenant_id}/{self.domain}>"