from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
import re
import json
import logging

from app.models import PromptTemplate, PromptVariable, PromptExecution, Tenant, Conversation
from app.services.model_router import ModelRouter


class PromptManagementService:
    """Service for managing and executing custom prompt templates"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model_router = ModelRouter()
    
    async def create_prompt_template(
        self,
        tenant_id: str,
        name: str,
        template_content: str,
        category: str,
        config: Dict[str, Any]
    ) -> PromptTemplate:
        """Create a new prompt template"""
        
        try:
            # Extract variables from template
            variables = self._extract_variables_from_template(template_content)
            
            template = PromptTemplate(
                tenant_id=tenant_id,
                name=name,
                description=config.get("description", ""),
                category=category,
                template_content=template_content,
                variables=variables,
                use_cases=config.get("use_cases", []),
                trigger_conditions=config.get("trigger_conditions", {}),
                is_active=config.get("is_active", True),
                is_default=config.get("is_default", False),
                priority=config.get("priority", 0),
                preferred_model=config.get("preferred_model"),
                model_parameters=config.get("model_parameters", {}),
                version=config.get("version", "1.0")
            )
            
            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)
            
            # Create variable definitions if provided
            if "variable_definitions" in config:
                await self._create_variable_definitions(
                    template.id, config["variable_definitions"]
                )
            
            return template
            
        except Exception as e:
            logging.error(f"Error creating prompt template: {e}")
            raise
    
    async def update_prompt_template(
        self,
        template_id: str,
        updates: Dict[str, Any]
    ) -> PromptTemplate:
        """Update an existing prompt template"""
        
        try:
            template = await self.db.get(PromptTemplate, template_id)
            if not template:
                raise ValueError("Template not found")
            
            # Update template content and re-extract variables if needed
            if "template_content" in updates:
                updates["variables"] = self._extract_variables_from_template(
                    updates["template_content"]
                )
            
            # Update fields
            for key, value in updates.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            template.updated_at = func.now()
            await self.db.commit()
            await self.db.refresh(template)
            
            return template
            
        except Exception as e:
            logging.error(f"Error updating prompt template: {e}")
            raise
    
    async def execute_prompt_template(
        self,
        template_id: str,
        variables: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a prompt template with given variables"""
        
        start_time = datetime.utcnow()
        
        try:
            # Get template
            template = await self.db.get(PromptTemplate, template_id)
            if not template or not template.is_active:
                raise ValueError("Template not found or inactive")
            
            # Validate variables
            validation_errors = await self._validate_template_variables(
                template, variables
            )
            if validation_errors:
                raise ValueError(f"Variable validation errors: {validation_errors}")
            
            # Render template
            rendered_prompt = self._render_template(
                template.template_content, variables
            )
            
            # Execute with AI model
            model_params = template.model_parameters or {}
            ai_response = await self.model_router.generate_response(
                message=rendered_prompt,
                context=context.get("conversation_history", []) if context else [],
                tenant_config=context.get("tenant_config", {}) if context else {},
                use_multimodal=model_params.get("use_multimodal", False)
            )
            
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Record execution
            execution = PromptExecution(
                template_id=template.id,
                tenant_id=template.tenant_id,
                conversation_id=context.get("conversation_id") if context else None,
                user_id=context.get("user_id") if context else None,
                input_variables=variables,
                rendered_prompt=rendered_prompt,
                ai_response=ai_response["content"],
                model_used=ai_response["model"],
                execution_time_ms=execution_time,
                tokens_used=ai_response.get("tokens_used", 0),
                success=True
            )
            
            self.db.add(execution)
            
            # Update template usage stats
            await self._update_template_stats(template.id, execution_time, True)
            
            await self.db.commit()
            
            return {
                "execution_id": str(execution.id),
                "response": ai_response["content"],
                "model_used": ai_response["model"],
                "execution_time_ms": execution_time,
                "tokens_used": ai_response.get("tokens_used", 0),
                "rendered_prompt": rendered_prompt,
                "success": True
            }
            
        except Exception as e:
            logging.error(f"Error executing prompt template: {e}")
            
            # Record failed execution
            execution = PromptExecution(
                template_id=template_id,
                tenant_id=template.tenant_id if 'template' in locals() else None,
                input_variables=variables,
                rendered_prompt=rendered_prompt if 'rendered_prompt' in locals() else "",
                success=False,
                error_message=str(e)
            )
            
            self.db.add(execution)
            await self.db.commit()
            
            raise
    
    async def get_template_suggestions(
        self,
        tenant_id: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get template suggestions based on context"""
        
        try:
            # Get all active templates for tenant
            result = await self.db.execute(
                select(PromptTemplate)
                .where(
                    and_(
                        PromptTemplate.tenant_id == tenant_id,
                        PromptTemplate.is_active == True
                    )
                )
                .order_by(PromptTemplate.priority.desc(), PromptTemplate.usage_count.desc())
            )
            
            templates = result.scalars().all()
            suggestions = []
            
            for template in templates:
                score = self._calculate_relevance_score(template, context)
                if score > 0.3:  # Minimum relevance threshold
                    suggestions.append({
                        "template_id": str(template.id),
                        "name": template.name,
                        "description": template.description,
                        "category": template.category,
                        "relevance_score": score,
                        "usage_count": template.usage_count,
                        "success_rate": template.success_rate
                    })
            
            # Sort by relevance score
            suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return suggestions[:10]  # Top 10 suggestions
            
        except Exception as e:
            logging.error(f"Error getting template suggestions: {e}")
            return []
    
    async def analyze_template_performance(
        self,
        template_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze performance metrics for a template"""
        
        try:
            from datetime import timedelta
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get execution statistics
            result = await self.db.execute(
                select(
                    func.count(PromptExecution.id).label("total_executions"),
                    func.sum(case((PromptExecution.success == True, 1), else_=0)).label("successful_executions"),
                    func.avg(PromptExecution.execution_time_ms).label("avg_execution_time"),
                    func.sum(PromptExecution.tokens_used).label("total_tokens"),
                    func.avg(PromptExecution.user_rating).label("avg_rating")
                )
                .where(
                    and_(
                        PromptExecution.template_id == template_id,
                        PromptExecution.created_at >= start_date
                    )
                )
            )
            
            stats = result.first()
            
            # Get usage trends (daily)
            daily_usage = await self._get_daily_usage_trend(template_id, days)
            
            # Get common failure reasons
            failure_reasons = await self._get_failure_reasons(template_id, days)
            
            return {
                "period_days": days,
                "total_executions": stats.total_executions or 0,
                "successful_executions": stats.successful_executions or 0,
                "success_rate": (stats.successful_executions / stats.total_executions * 100) if stats.total_executions else 0,
                "avg_execution_time_ms": float(stats.avg_execution_time or 0),
                "total_tokens_used": stats.total_tokens or 0,
                "avg_user_rating": float(stats.avg_rating or 0),
                "daily_usage": daily_usage,
                "common_failures": failure_reasons
            }
            
        except Exception as e:
            logging.error(f"Error analyzing template performance: {e}")
            return {"error": str(e)}
    
    def _extract_variables_from_template(self, template_content: str) -> List[str]:
        """Extract variable names from template content"""
        
        # Find all {{variable}} patterns
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, template_content)
        
        # Clean up variable names (remove whitespace)
        variables = [match.strip() for match in matches]
        
        # Remove duplicates while preserving order
        unique_variables = []
        for var in variables:
            if var not in unique_variables:
                unique_variables.append(var)
        
        return unique_variables
    
    def _render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """Render template with provided variables"""
        
        rendered = template_content
        
        for var_name, value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    async def _validate_template_variables(
        self,
        template: PromptTemplate,
        variables: Dict[str, Any]
    ) -> List[str]:
        """Validate provided variables against template requirements"""
        
        errors = []
        
        # Get variable definitions
        result = await self.db.execute(
            select(PromptVariable)
            .where(PromptVariable.template_id == template.id)
        )
        
        variable_definitions = {var.name: var for var in result.scalars().all()}
        
        # Check required variables
        for var_name in template.variables:
            var_def = variable_definitions.get(var_name)
            
            if var_def and var_def.is_required and var_name not in variables:
                errors.append(f"Required variable '{var_name}' is missing")
            
            if var_name in variables and var_def:
                # Validate type and rules
                value = variables[var_name]
                validation_error = self._validate_variable_value(var_def, value)
                if validation_error:
                    errors.append(f"Variable '{var_name}': {validation_error}")
        
        return errors
    
    def _validate_variable_value(self, var_def: PromptVariable, value: Any) -> Optional[str]:
        """Validate a single variable value"""
        
        # Type validation
        expected_type = var_def.variable_type
        
        if expected_type == "string" and not isinstance(value, str):
            return f"Expected string, got {type(value).__name__}"
        elif expected_type == "number" and not isinstance(value, (int, float)):
            return f"Expected number, got {type(value).__name__}"
        elif expected_type == "boolean" and not isinstance(value, bool):
            return f"Expected boolean, got {type(value).__name__}"
        elif expected_type == "array" and not isinstance(value, list):
            return f"Expected array, got {type(value).__name__}"
        
        # Validation rules
        rules = var_def.validation_rules or {}
        
        if "min_length" in rules and len(str(value)) < rules["min_length"]:
            return f"Minimum length is {rules['min_length']}"
        
        if "max_length" in rules and len(str(value)) > rules["max_length"]:
            return f"Maximum length is {rules['max_length']}"
        
        if "regex" in rules:
            pattern = rules["regex"]
            if not re.match(pattern, str(value)):
                return f"Value does not match required pattern"
        
        return None
    
    def _calculate_relevance_score(
        self,
        template: PromptTemplate,
        context: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for template suggestion"""
        
        score = 0.0
        
        # Base score from usage and success rate
        usage_score = min(template.usage_count / 100, 1.0) * 0.3
        success_score = template.success_rate * 0.3
        
        score += usage_score + success_score
        
        # Context matching
        if template.trigger_conditions:
            conditions = template.trigger_conditions
            
            # Match channel
            if "channels" in conditions and context.get("channel") in conditions["channels"]:
                score += 0.2
            
            # Match intent
            if "intents" in conditions and context.get("intent") in conditions["intents"]:
                score += 0.3
            
            # Match sentiment
            if "sentiments" in conditions and context.get("sentiment") in conditions["sentiments"]:
                score += 0.1
        
        # Category bonus
        if template.category == context.get("preferred_category"):
            score += 0.2
        
        return min(score, 1.0)
    
    async def _update_template_stats(
        self,
        template_id: str,
        execution_time_ms: int,
        success: bool
    ):
        """Update template usage statistics"""
        
        await self.db.execute(
            update(PromptTemplate)
            .where(PromptTemplate.id == template_id)
            .values(
                usage_count=PromptTemplate.usage_count + 1,
                last_used_at=func.now()
            )
        )
    
    async def _create_variable_definitions(
        self,
        template_id: str,
        variable_definitions: List[Dict[str, Any]]
    ):
        """Create variable definitions for a template"""
        
        for var_def in variable_definitions:
            variable = PromptVariable(
                template_id=template_id,
                name=var_def["name"],
                description=var_def.get("description"),
                variable_type=var_def["type"],
                is_required=var_def.get("is_required", False),
                default_value=var_def.get("default_value"),
                validation_rules=var_def.get("validation_rules", {}),
                example_values=var_def.get("example_values", []),
                help_text=var_def.get("help_text")
            )
            
            self.db.add(variable)
    
    async def _get_daily_usage_trend(self, template_id: str, days: int) -> List[Dict[str, Any]]:
        """Get daily usage trend for template"""
        
        from datetime import timedelta
        
        trends = []
        
        for i in range(days):
            day = datetime.utcnow() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            result = await self.db.execute(
                select(func.count(PromptExecution.id))
                .where(
                    and_(
                        PromptExecution.template_id == template_id,
                        PromptExecution.created_at >= day_start,
                        PromptExecution.created_at < day_end
                    )
                )
            )
            
            count = result.scalar() or 0
            trends.append({
                "date": day.strftime("%Y-%m-%d"),
                "executions": count
            })
        
        return trends
    
    async def _get_failure_reasons(self, template_id: str, days: int) -> List[Dict[str, Any]]:
        """Get common failure reasons for template"""
        
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                PromptExecution.error_message,
                func.count(PromptExecution.id).label("count")
            )
            .where(
                and_(
                    PromptExecution.template_id == template_id,
                    PromptExecution.success == False,
                    PromptExecution.created_at >= start_date,
                    PromptExecution.error_message.isnot(None)
                )
            )
            .group_by(PromptExecution.error_message)
            .order_by(func.count(PromptExecution.id).desc())
            .limit(5)
        )
        
        return [
            {"error": row.error_message, "count": row.count}
            for row in result.fetchall()
        ]