from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.db import get_db
from app.models import Workflow, WorkflowStep, DomainPromptSet, ClientWorkflowConfig
from app.services.workflow_engine import WorkflowEngine
# TODO: Implement proper authentication
async def get_current_user():
    return {"id": "test-user"}

async def get_current_tenant():
    return {"id": "test-tenant"}


router = APIRouter()


class WorkflowCreateRequest(BaseModel):
    name: str = Field(..., description="Workflow name")
    domain: str = Field(..., description="Domain (healthcare, finance, etc.)")
    description: Optional[str] = None
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict)
    initial_context: Dict[str, Any] = Field(default_factory=dict)
    error_handling: Dict[str, Any] = Field(default_factory=dict)
    is_default_for_domain: bool = False
    priority: int = 0
    max_execution_time_minutes: int = 30
    step_definitions: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowExecuteRequest(BaseModel):
    context: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


class DomainPromptSetCreateRequest(BaseModel):
    domain: str = Field(..., description="Domain name")
    name: str = Field(..., description="Prompt set name")
    subdomain: Optional[str] = None
    description: Optional[str] = None
    language: str = "en"
    region: Optional[str] = None
    compliance_tags: List[str] = Field(default_factory=list)
    prompt_templates: List[Dict[str, Any]] = Field(default_factory=list)
    workflow_templates: List[Dict[str, Any]] = Field(default_factory=list)
    domain_vocabulary: Dict[str, Any] = Field(default_factory=dict)


class ClientConfigRequest(BaseModel):
    domain: str = Field(..., description="Domain to configure")
    config_name: str = Field(..., description="Configuration name")
    custom_workflows: List[Dict[str, Any]] = Field(default_factory=list)
    prompt_customizations: Dict[str, Any] = Field(default_factory=dict)
    domain_context: Dict[str, Any] = Field(default_factory=dict)
    approval_workflows: Dict[str, Any] = Field(default_factory=dict)
    escalation_rules: Dict[str, Any] = Field(default_factory=dict)
    compliance_settings: Dict[str, Any] = Field(default_factory=dict)
    external_apis: Dict[str, Any] = Field(default_factory=dict)
    webhook_endpoints: List[str] = Field(default_factory=list)
    notification_preferences: Dict[str, Any] = Field(default_factory=dict)
    sla_requirements: Dict[str, Any] = Field(default_factory=dict)
    quality_thresholds: Dict[str, Any] = Field(default_factory=dict)


@router.post("/workflows", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    request: WorkflowCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_tenant = Depends(get_current_tenant)
):
    """Create a new workflow"""
    
    workflow_engine = WorkflowEngine(db)
    
    config = {
        "description": request.description,
        "trigger_conditions": request.trigger_conditions,
        "initial_context": request.initial_context,
        "error_handling": request.error_handling,
        "is_default_for_domain": request.is_default_for_domain,
        "priority": request.priority,
        "max_execution_time_minutes": request.max_execution_time_minutes,
        "step_definitions": request.step_definitions
    }
    
    try:
        workflow = await workflow_engine.create_workflow(
            tenant_id=str(current_tenant.id),
            name=request.name,
            domain=request.domain,
            config=config
        )
        
        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "domain": workflow.domain,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    request: WorkflowExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_tenant = Depends(get_current_tenant)
):
    """Execute a workflow"""
    
    workflow_engine = WorkflowEngine(db)
    
    try:
        result = await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            context=request.context,
            tenant_id=str(current_tenant.id),
            conversation_id=request.conversation_id,
            user_id=request.user_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/workflows/domain/{domain}")
async def get_domain_workflows(
    domain: str,
    context: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_tenant = Depends(get_current_tenant)
):
    """Get available workflows for a domain"""
    
    workflow_engine = WorkflowEngine(db)
    
    try:
        import json
        context_dict = json.loads(context) if context else {}
        
        workflows = await workflow_engine.get_domain_workflows(
            tenant_id=str(current_tenant.id),
            domain=domain,
            context=context_dict
        )
        
        return {"workflows": workflows}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/domain-prompt-sets", status_code=status.HTTP_201_CREATED)
async def create_domain_prompt_set(
    request: DomainPromptSetCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a domain-specific prompt set"""
    
    workflow_engine = WorkflowEngine(db)
    
    config = {
        "subdomain": request.subdomain,
        "description": request.description,
        "language": request.language,
        "region": request.region,
        "compliance_tags": request.compliance_tags,
        "prompt_templates": request.prompt_templates,
        "workflow_templates": request.workflow_templates,
        "domain_vocabulary": request.domain_vocabulary
    }
    
    try:
        prompt_set = await workflow_engine.create_domain_prompt_set(
            domain=request.domain,
            name=request.name,
            config=config
        )
        
        return {
            "id": str(prompt_set.id),
            "domain": prompt_set.domain,
            "name": prompt_set.name,
            "version": prompt_set.version,
            "created_at": prompt_set.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/client-config", status_code=status.HTTP_201_CREATED)
async def configure_client_domain(
    request: ClientConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_tenant = Depends(get_current_tenant)
):
    """Configure domain-specific settings for current tenant"""
    
    workflow_engine = WorkflowEngine(db)
    
    config = {
        "config_name": request.config_name,
        "custom_workflows": request.custom_workflows,
        "prompt_customizations": request.prompt_customizations,
        "domain_context": request.domain_context,
        "approval_workflows": request.approval_workflows,
        "escalation_rules": request.escalation_rules,
        "compliance_settings": request.compliance_settings,
        "external_apis": request.external_apis,
        "webhook_endpoints": request.webhook_endpoints,
        "notification_preferences": request.notification_preferences,
        "sla_requirements": request.sla_requirements,
        "quality_thresholds": request.quality_thresholds
    }
    
    try:
        client_config = await workflow_engine.configure_client_domain(
            tenant_id=str(current_tenant.id),
            domain=request.domain,
            config=config
        )
        
        return {
            "id": str(client_config.id),
            "domain": client_config.domain,
            "config_name": client_config.config_name,
            "created_at": client_config.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/client-config/{domain}")
async def get_client_config(
    domain: str,
    db: AsyncSession = Depends(get_db),
    current_tenant = Depends(get_current_tenant)
):
    """Get client configuration for a domain"""
    
    from sqlalchemy import select, and_
    
    try:
        result = await db.execute(
            select(ClientWorkflowConfig)
            .where(
                and_(
                    ClientWorkflowConfig.tenant_id == current_tenant.id,
                    ClientWorkflowConfig.domain == domain,
                    ClientWorkflowConfig.is_active == True
                )
            )
        )
        
        config = result.scalar()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )
        
        return {
            "id": str(config.id),
            "domain": config.domain,
            "config_name": config.config_name,
            "custom_workflows": config.custom_workflows,
            "prompt_customizations": config.prompt_customizations,
            "domain_context": config.domain_context,
            "approval_workflows": config.approval_workflows,
            "escalation_rules": config.escalation_rules,
            "compliance_settings": config.compliance_settings,
            "external_apis": config.external_apis,
            "webhook_endpoints": config.webhook_endpoints,
            "notification_preferences": config.notification_preferences,
            "sla_requirements": config.sla_requirements,
            "quality_thresholds": config.quality_thresholds,
            "created_at": config.created_at.isoformat(),
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_tenant = Depends(get_current_tenant)
):
    """Get workflow details"""
    
    try:
        workflow = await db.get(Workflow, workflow_id)
        
        if not workflow or workflow.tenant_id != current_tenant.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Get workflow steps
        from sqlalchemy import select
        result = await db.execute(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == workflow.id)
            .order_by(WorkflowStep.order_index)
        )
        
        steps = result.scalars().all()
        
        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "domain": workflow.domain,
            "description": workflow.description,
            "status": workflow.status.value,
            "trigger_conditions": workflow.trigger_conditions,
            "initial_context": workflow.initial_context,
            "error_handling": workflow.error_handling,
            "execution_count": workflow.execution_count,
            "success_rate": workflow.success_rate,
            "steps": [
                {
                    "id": str(step.id),
                    "name": step.name,
                    "step_type": step.step_type.value,
                    "order_index": step.order_index,
                    "config": step.config,
                    "input_mapping": step.input_mapping,
                    "output_mapping": step.output_mapping
                }
                for step in steps
            ],
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/domain-prompt-sets")
async def list_domain_prompt_sets(
    domain: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List available domain prompt sets"""
    
    try:
        from sqlalchemy import select
        
        query = select(DomainPromptSet).where(DomainPromptSet.is_active == True)
        
        if domain:
            query = query.where(DomainPromptSet.domain == domain)
        
        result = await db.execute(query.order_by(DomainPromptSet.usage_count.desc()))
        prompt_sets = result.scalars().all()
        
        return {
            "prompt_sets": [
                {
                    "id": str(ps.id),
                    "domain": ps.domain,
                    "subdomain": ps.subdomain,
                    "name": ps.name,
                    "description": ps.description,
                    "version": ps.version,
                    "language": ps.language,
                    "region": ps.region,
                    "compliance_tags": ps.compliance_tags,
                    "usage_count": ps.usage_count,
                    "created_at": ps.created_at.isoformat()
                }
                for ps in prompt_sets
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )