from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
import asyncio
import json
import logging
from enum import Enum

from app.models import Workflow, WorkflowStep, WorkflowExecution, DomainPromptSet, ClientWorkflowConfig
from app.models.workflow import WorkflowStatus, WorkflowStepType
from app.services.prompt_management import PromptManagementService
from app.services.model_router import ModelRouter


class ExecutionStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowEngine:
    """Service for executing and managing workflows"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.prompt_service = PromptManagementService(db)
        self.model_router = ModelRouter()
    
    async def create_workflow(
        self,
        tenant_id: str,
        name: str,
        domain: str,
        config: Dict[str, Any]
    ) -> Workflow:
        """Create a new workflow"""
        
        try:
            workflow = Workflow(
                tenant_id=tenant_id,
                name=name,
                domain=domain,
                description=config.get("description", ""),
                trigger_conditions=config.get("trigger_conditions", {}),
                initial_context=config.get("initial_context", {}),
                steps=config.get("steps", []),
                error_handling=config.get("error_handling", {}),
                status=WorkflowStatus(config.get("status", "draft")),
                is_default_for_domain=config.get("is_default_for_domain", False),
                priority=config.get("priority", 0),
                max_execution_time_minutes=config.get("max_execution_time_minutes", 30),
                version=config.get("version", "1.0")
            )
            
            self.db.add(workflow)
            await self.db.commit()
            await self.db.refresh(workflow)
            
            # Create workflow steps
            if "step_definitions" in config:
                await self._create_workflow_steps(workflow.id, config["step_definitions"])
            
            return workflow
            
        except Exception as e:
            logging.error(f"Error creating workflow: {e}")
            raise
    
    async def execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any],
        tenant_id: str,
        conversation_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Execute a workflow with given context"""
        
        start_time = datetime.utcnow()
        
        try:
            # Get workflow and validate
            workflow = await self.db.get(Workflow, workflow_id)
            if not workflow or workflow.status != WorkflowStatus.ACTIVE:
                raise ValueError("Workflow not found or not active")
            
            # Create execution record
            execution = WorkflowExecution(
                workflow_id=workflow.id,
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                user_id=user_id,
                status=ExecutionStatus.RUNNING.value,
                context_variables={**workflow.initial_context, **context},
                execution_log=[]
            )
            
            self.db.add(execution)
            await self.db.commit()
            await self.db.refresh(execution)
            
            # Get workflow steps
            steps = await self._get_workflow_steps(workflow.id)
            
            # Execute workflow
            result = await self._execute_workflow_steps(execution, steps, workflow)
            
            # Update execution record
            execution.status = ExecutionStatus.COMPLETED.value if result["success"] else ExecutionStatus.FAILED.value
            execution.completed_at = func.now()
            execution.total_execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            execution.final_output = result["output"]
            
            if not result["success"]:
                execution.error_details = result.get("error")
            
            # Update workflow stats
            await self._update_workflow_stats(workflow.id, result["success"])
            
            await self.db.commit()
            
            return {
                "execution_id": str(execution.id),
                "success": result["success"],
                "output": result["output"],
                "execution_time_ms": execution.total_execution_time_ms,
                "steps_executed": len(result.get("steps_log", [])),
                "error": result.get("error")
            }
            
        except Exception as e:
            logging.error(f"Error executing workflow: {e}")
            raise
    
    async def get_domain_workflows(
        self,
        tenant_id: str,
        domain: str,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Get available workflows for a domain with relevance scoring"""
        
        try:
            # Get client-specific configuration
            client_config = await self._get_client_config(tenant_id, domain)
            
            # Get base workflows for domain
            result = await self.db.execute(
                select(Workflow)
                .where(
                    and_(
                        Workflow.tenant_id == tenant_id,
                        Workflow.domain == domain,
                        Workflow.status == WorkflowStatus.ACTIVE
                    )
                )
                .order_by(Workflow.priority.desc(), Workflow.execution_count.desc())
            )
            
            workflows = result.scalars().all()
            workflow_suggestions = []
            
            for workflow in workflows:
                # Calculate relevance score
                score = self._calculate_workflow_relevance(workflow, context, client_config)
                
                if score > 0.3:  # Minimum relevance threshold
                    workflow_suggestions.append({
                        "workflow_id": str(workflow.id),
                        "name": workflow.name,
                        "description": workflow.description,
                        "domain": workflow.domain,
                        "relevance_score": score,
                        "execution_count": workflow.execution_count,
                        "success_rate": workflow.success_rate,
                        "estimated_duration_minutes": self._estimate_duration(workflow),
                        "required_context": self._get_required_context(workflow)
                    })
            
            # Sort by relevance score
            workflow_suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return workflow_suggestions[:5]  # Top 5 suggestions
            
        except Exception as e:
            logging.error(f"Error getting domain workflows: {e}")
            return []
    
    async def create_domain_prompt_set(
        self,
        domain: str,
        name: str,
        config: Dict[str, Any]
    ) -> DomainPromptSet:
        """Create a domain-specific prompt set"""
        
        try:
            prompt_set = DomainPromptSet(
                domain=domain,
                subdomain=config.get("subdomain"),
                name=name,
                description=config.get("description", ""),
                version=config.get("version", "1.0"),
                language=config.get("language", "en"),
                region=config.get("region"),
                compliance_tags=config.get("compliance_tags", []),
                prompt_templates=config.get("prompt_templates", []),
                workflow_templates=config.get("workflow_templates", []),
                domain_vocabulary=config.get("domain_vocabulary", {})
            )
            
            self.db.add(prompt_set)
            await self.db.commit()
            await self.db.refresh(prompt_set)
            
            # Auto-create prompt templates and workflows
            await self._deploy_domain_templates(prompt_set)
            
            return prompt_set
            
        except Exception as e:
            logging.error(f"Error creating domain prompt set: {e}")
            raise
    
    async def configure_client_domain(
        self,
        tenant_id: str,
        domain: str,
        config: Dict[str, Any]
    ) -> ClientWorkflowConfig:
        """Configure domain-specific settings for a client"""
        
        try:
            # Check if config already exists
            result = await self.db.execute(
                select(ClientWorkflowConfig)
                .where(
                    and_(
                        ClientWorkflowConfig.tenant_id == tenant_id,
                        ClientWorkflowConfig.domain == domain
                    )
                )
            )
            
            client_config = result.scalar()
            
            if client_config:
                # Update existing configuration
                for key, value in config.items():
                    if hasattr(client_config, key):
                        setattr(client_config, key, value)
                client_config.updated_at = func.now()
            else:
                # Create new configuration
                client_config = ClientWorkflowConfig(
                    tenant_id=tenant_id,
                    domain=domain,
                    config_name=config.get("config_name", f"{domain}_config"),
                    custom_workflows=config.get("custom_workflows", []),
                    prompt_customizations=config.get("prompt_customizations", {}),
                    domain_context=config.get("domain_context", {}),
                    approval_workflows=config.get("approval_workflows", {}),
                    escalation_rules=config.get("escalation_rules", {}),
                    compliance_settings=config.get("compliance_settings", {}),
                    external_apis=config.get("external_apis", {}),
                    webhook_endpoints=config.get("webhook_endpoints", []),
                    notification_preferences=config.get("notification_preferences", {}),
                    sla_requirements=config.get("sla_requirements", {}),
                    quality_thresholds=config.get("quality_thresholds", {})
                )
                
                self.db.add(client_config)
            
            await self.db.commit()
            await self.db.refresh(client_config)
            
            return client_config
            
        except Exception as e:
            logging.error(f"Error configuring client domain: {e}")
            raise
    
    async def _execute_workflow_steps(
        self,
        execution: WorkflowExecution,
        steps: List[WorkflowStep],
        workflow: Workflow
    ) -> Dict[str, Any]:
        """Execute all steps in a workflow"""
        
        context = execution.context_variables.copy()
        steps_log = []
        
        try:
            for step in steps:
                step_start = datetime.utcnow()
                
                # Update current step
                execution.current_step_id = step.id
                await self.db.commit()
                
                # Execute step
                step_result = await self._execute_step(step, context, execution)
                
                step_duration = int((datetime.utcnow() - step_start).total_seconds() * 1000)
                
                # Log step execution
                step_log = {
                    "step_id": str(step.id),
                    "step_name": step.name,
                    "step_type": step.step_type.value,
                    "success": step_result["success"],
                    "duration_ms": step_duration,
                    "output": step_result.get("output"),
                    "error": step_result.get("error")
                }
                
                steps_log.append(step_log)
                execution.execution_log = steps_log
                
                if not step_result["success"]:
                    # Handle step failure
                    if step.retry_config.get("max_retries", 0) > 0:
                        # Implement retry logic
                        retry_result = await self._retry_step(step, context, execution)
                        if retry_result["success"]:
                            step_result = retry_result
                        else:
                            return {
                                "success": False,
                                "output": {},
                                "error": step_result.get("error"),
                                "steps_log": steps_log
                            }
                    else:
                        return {
                            "success": False,
                            "output": {},
                            "error": step_result.get("error"),
                            "steps_log": steps_log
                        }
                
                # Update context with step output
                if "output" in step_result:
                    context.update(step_result["output"])
                
                # Check for conditional next steps
                next_step = self._determine_next_step(step, step_result, steps)
                if next_step and next_step != steps[steps.index(step) + 1] if steps.index(step) + 1 < len(steps) else None:
                    # Jump to different step
                    next_index = next((i for i, s in enumerate(steps) if s.id == next_step.id), None)
                    if next_index:
                        steps = steps[next_index:]
                        continue
            
            return {
                "success": True,
                "output": context,
                "steps_log": steps_log
            }
            
        except Exception as e:
            logging.error(f"Error executing workflow steps: {e}")
            return {
                "success": False,
                "output": {},
                "error": str(e),
                "steps_log": steps_log
            }
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        try:
            if step.step_type == WorkflowStepType.PROMPT:
                return await self._execute_prompt_step(step, context, execution)
            elif step.step_type == WorkflowStepType.CONDITION:
                return await self._execute_condition_step(step, context)
            elif step.step_type == WorkflowStepType.ACTION:
                return await self._execute_action_step(step, context)
            elif step.step_type == WorkflowStepType.DELAY:
                return await self._execute_delay_step(step, context)
            elif step.step_type == WorkflowStepType.WEBHOOK:
                return await self._execute_webhook_step(step, context)
            else:
                return {"success": False, "error": f"Unknown step type: {step.step_type}"}
                
        except Exception as e:
            logging.error(f"Error executing step {step.name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_prompt_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute a prompt-based step"""
        
        try:
            if not step.prompt_template_id:
                return {"success": False, "error": "No prompt template specified"}
            
            # Map inputs
            input_variables = {}
            for var_name, mapping in step.input_mapping.items():
                if mapping.startswith("context."):
                    context_key = mapping.replace("context.", "")
                    input_variables[var_name] = context.get(context_key)
                else:
                    input_variables[var_name] = mapping
            
            # Execute prompt template
            prompt_result = await self.prompt_service.execute_prompt_template(
                template_id=str(step.prompt_template_id),
                variables=input_variables,
                context={
                    "conversation_id": execution.conversation_id,
                    "user_id": execution.user_id,
                    "workflow_execution_id": str(execution.id)
                }
            )
            
            # Map outputs
            output = {}
            for output_key, mapping in step.output_mapping.items():
                if mapping == "response":
                    output[output_key] = prompt_result["response"]
                elif mapping == "model_used":
                    output[output_key] = prompt_result["model_used"]
                else:
                    output[output_key] = prompt_result.get(mapping)
            
            return {
                "success": True,
                "output": output,
                "prompt_execution_id": prompt_result["execution_id"]
            }
            
        except Exception as e:
            logging.error(f"Error executing prompt step: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_condition_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a conditional logic step"""
        
        try:
            conditions = step.config.get("conditions", [])
            
            for condition in conditions:
                operator = condition.get("operator")
                left_value = self._get_context_value(condition.get("left"), context)
                right_value = condition.get("right")
                
                result = self._evaluate_condition(left_value, operator, right_value)
                
                if result:
                    return {
                        "success": True,
                        "output": {"condition_result": True, "matched_condition": condition}
                    }
            
            return {
                "success": True,
                "output": {"condition_result": False}
            }
            
        except Exception as e:
            logging.error(f"Error executing condition step: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_action_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an action step"""
        
        try:
            action_type = step.config.get("action_type")
            
            if action_type == "set_variable":
                variable_name = step.config.get("variable_name")
                variable_value = self._get_context_value(step.config.get("variable_value"), context)
                
                return {
                    "success": True,
                    "output": {variable_name: variable_value}
                }
            
            elif action_type == "api_call":
                # Implement API call logic
                return await self._execute_api_call(step.config, context)
            
            else:
                return {"success": False, "error": f"Unknown action type: {action_type}"}
                
        except Exception as e:
            logging.error(f"Error executing action step: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_delay_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a delay step"""
        
        try:
            delay_seconds = step.config.get("delay_seconds", 1)
            await asyncio.sleep(delay_seconds)
            
            return {
                "success": True,
                "output": {"delayed_seconds": delay_seconds}
            }
            
        except Exception as e:
            logging.error(f"Error executing delay step: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_webhook_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a webhook step"""
        
        try:
            import aiohttp
            
            webhook_url = step.config.get("webhook_url")
            payload = step.config.get("payload", {})
            
            # Replace context variables in payload
            processed_payload = self._process_payload_variables(payload, context)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=processed_payload) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return {
                            "success": True,
                            "output": {"webhook_response": response_data}
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Webhook returned status {response.status}"
                        }
                        
        except Exception as e:
            logging.error(f"Error executing webhook step: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_workflow_relevance(
        self,
        workflow: Workflow,
        context: Dict[str, Any],
        client_config: Optional[ClientWorkflowConfig]
    ) -> float:
        """Calculate relevance score for workflow suggestion"""
        
        score = 0.0
        
        # Base score from usage and success rate
        usage_score = min(workflow.execution_count / 100, 1.0) * 0.3
        success_score = workflow.success_rate * 0.3
        
        score += usage_score + success_score
        
        # Trigger condition matching
        if workflow.trigger_conditions and context:
            conditions = workflow.trigger_conditions
            matches = 0
            total_conditions = len(conditions)
            
            for condition_key, condition_value in conditions.items():
                if context.get(condition_key) == condition_value:
                    matches += 1
            
            if total_conditions > 0:
                score += (matches / total_conditions) * 0.4
        
        # Client customization bonus
        if client_config and workflow.name in client_config.custom_workflows:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _get_workflow_steps(self, workflow_id: str) -> List[WorkflowStep]:
        """Get workflow steps in order"""
        
        result = await self.db.execute(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == workflow_id)
            .order_by(WorkflowStep.order_index)
        )
        
        return result.scalars().all()
    
    async def _get_client_config(self, tenant_id: str, domain: str) -> Optional[ClientWorkflowConfig]:
        """Get client-specific configuration for domain"""
        
        result = await self.db.execute(
            select(ClientWorkflowConfig)
            .where(
                and_(
                    ClientWorkflowConfig.tenant_id == tenant_id,
                    ClientWorkflowConfig.domain == domain,
                    ClientWorkflowConfig.is_active == True
                )
            )
        )
        
        return result.scalar()
    
    def _get_context_value(self, expression: str, context: Dict[str, Any]) -> Any:
        """Get value from context using dot notation"""
        
        if not expression.startswith("context."):
            return expression
        
        keys = expression.replace("context.", "").split(".")
        value = context
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _evaluate_condition(self, left: Any, operator: str, right: Any) -> bool:
        """Evaluate a condition"""
        
        if operator == "equals":
            return left == right
        elif operator == "not_equals":
            return left != right
        elif operator == "greater_than":
            return left > right
        elif operator == "less_than":
            return left < right
        elif operator == "contains":
            return right in str(left)
        elif operator == "starts_with":
            return str(left).startswith(str(right))
        elif operator == "ends_with":
            return str(left).endswith(str(right))
        else:
            return False
    
    async def _update_workflow_stats(self, workflow_id: str, success: bool):
        """Update workflow usage statistics"""
        
        await self.db.execute(
            update(Workflow)
            .where(Workflow.id == workflow_id)
            .values(
                execution_count=Workflow.execution_count + 1,
                last_executed_at=func.now()
            )
        )