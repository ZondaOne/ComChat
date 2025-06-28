from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
import numpy as np
import logging
from dataclasses import dataclass
from enum import Enum

from app.models import Message, Conversation, Tenant, UsageRecord
from app.services.model_router import ModelRouter
from app.core.config import settings


class ModelType(Enum):
    LOCAL_TEXT = "local_text"
    LOCAL_MULTIMODAL = "local_multimodal"
    OPENAI_TEXT = "openai_text"
    OPENAI_MULTIMODAL = "openai_multimodal"


@dataclass
class ModelPerformance:
    model_name: str
    model_type: ModelType
    avg_response_time: float
    success_rate: float
    cost_per_request: float
    quality_score: float
    usage_count: int
    last_updated: datetime


@dataclass
class OptimizationRecommendation:
    current_model: str
    recommended_model: str
    reason: str
    potential_savings: float
    confidence_score: float
    impact_analysis: Dict[str, Any]


class ModelOptimizerService:
    """Intelligent model routing optimizer that learns from usage patterns"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model_router = ModelRouter()
        
        # Performance thresholds
        self.response_time_threshold = 5000  # 5 seconds
        self.quality_threshold = 0.7  # 70%
        self.cost_efficiency_weight = 0.3
        self.performance_weight = 0.4
        self.quality_weight = 0.3
    
    async def analyze_model_performance(
        self,
        tenant_id: str,
        days: int = 30
    ) -> Dict[str, ModelPerformance]:
        """Analyze performance of all models for a tenant"""
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get message statistics grouped by model
            result = await self.db.execute(
                select(
                    Message.ai_model_used,
                    func.count(Message.id).label("usage_count"),
                    func.avg(Message.processing_time_ms).label("avg_response_time"),
                    func.sum(Message.tokens_used).label("total_tokens"),
                    func.avg(
                        case(
                            (Message.status == "delivered", 1.0),
                            else_=0.0
                        )
                    ).label("success_rate")
                )
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(
                    and_(
                        Conversation.tenant_id == tenant_id,
                        Message.direction == "outbound",
                        Message.ai_model_used.isnot(None),
                        Message.created_at >= start_date
                    )
                )
                .group_by(Message.ai_model_used)
            )
            
            model_stats = result.fetchall()
            performance_data = {}
            
            for stat in model_stats:
                model_name = stat.ai_model_used
                
                # Calculate costs
                cost_per_request = self._calculate_average_cost(
                    model_name, stat.total_tokens or 0, stat.usage_count
                )
                
                # Get quality score (from user feedback, response relevance, etc.)
                quality_score = await self._calculate_quality_score(
                    tenant_id, model_name, start_date
                )
                
                # Determine model type
                model_type = self._classify_model_type(model_name)
                
                performance_data[model_name] = ModelPerformance(
                    model_name=model_name,
                    model_type=model_type,
                    avg_response_time=float(stat.avg_response_time or 0),
                    success_rate=float(stat.success_rate or 0),
                    cost_per_request=cost_per_request,
                    quality_score=quality_score,
                    usage_count=stat.usage_count,
                    last_updated=datetime.utcnow()
                )
            
            return performance_data
            
        except Exception as e:
            logging.error(f"Error analyzing model performance: {e}")
            return {}
    
    async def get_optimization_recommendations(
        self,
        tenant_id: str,
        context: Dict[str, Any] = None
    ) -> List[OptimizationRecommendation]:
        """Get intelligent recommendations for model optimization"""
        
        try:
            # Analyze current performance
            performance_data = await self.analyze_model_performance(tenant_id)
            
            if not performance_data:
                return []
            
            recommendations = []
            
            # Get usage patterns
            usage_patterns = await self._analyze_usage_patterns(tenant_id)
            
            # Check for cost optimization opportunities
            cost_recommendations = self._analyze_cost_optimization(
                performance_data, usage_patterns
            )
            recommendations.extend(cost_recommendations)
            
            # Check for performance optimization opportunities
            performance_recommendations = self._analyze_performance_optimization(
                performance_data, usage_patterns
            )
            recommendations.extend(performance_recommendations)
            
            # Check for quality optimization opportunities
            quality_recommendations = self._analyze_quality_optimization(
                performance_data, usage_patterns
            )
            recommendations.extend(quality_recommendations)
            
            # Sort by confidence score
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            
            return recommendations[:10]  # Top 10 recommendations
            
        except Exception as e:
            logging.error(f"Error getting optimization recommendations: {e}")
            return []
    
    async def optimize_model_routing(
        self,
        tenant_id: str,
        message_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Choose optimal model for a specific request"""
        
        try:
            # Get recent performance data
            performance_data = await self.analyze_model_performance(tenant_id, days=7)
            
            if not performance_data:
                # Fallback to default routing
                return self._get_default_model_choice(message_context)
            
            # Analyze request characteristics
            request_complexity = self._analyze_request_complexity(message_context)
            time_sensitivity = self._analyze_time_sensitivity(message_context)
            cost_sensitivity = self._analyze_cost_sensitivity(tenant_id)
            
            # Score available models
            model_scores = {}
            
            for model_name, perf in performance_data.items():
                score = self._calculate_model_score(
                    perf, request_complexity, time_sensitivity, cost_sensitivity
                )
                model_scores[model_name] = score
            
            # Choose best model
            best_model = max(model_scores.items(), key=lambda x: x[1])
            
            return {
                "recommended_model": best_model[0],
                "confidence_score": best_model[1],
                "reasoning": self._explain_model_choice(
                    best_model[0], performance_data[best_model[0]], message_context
                ),
                "alternatives": [
                    {"model": model, "score": score}
                    for model, score in sorted(model_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
                ]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing model routing: {e}")
            return self._get_default_model_choice(message_context)
    
    async def learn_from_feedback(
        self,
        message_id: str,
        feedback: Dict[str, Any]
    ):
        """Learn from user feedback to improve future recommendations"""
        
        try:
            # Get message details
            message = await self.db.get(Message, message_id)
            if not message:
                return
            
            # Extract feedback metrics
            user_rating = feedback.get("rating")  # 1-5 scale
            response_quality = feedback.get("quality")  # good, bad, excellent
            response_speed = feedback.get("speed")  # fast, slow, acceptable
            
            # Update model quality scores
            await self._update_model_quality_score(
                message.ai_model_used, user_rating, response_quality
            )
            
            # Store feedback for future analysis
            await self._store_feedback_data(message_id, feedback)
            
        except Exception as e:
            logging.error(f"Error learning from feedback: {e}")
    
    async def get_model_efficiency_report(
        self,
        tenant_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive model efficiency report"""
        
        try:
            performance_data = await self.analyze_model_performance(tenant_id, days)
            usage_patterns = await self._analyze_usage_patterns(tenant_id, days)
            
            # Calculate efficiency metrics
            total_cost = sum(p.cost_per_request * p.usage_count for p in performance_data.values())
            total_requests = sum(p.usage_count for p in performance_data.values())
            avg_response_time = np.mean([p.avg_response_time for p in performance_data.values()])
            avg_quality = np.mean([p.quality_score for p in performance_data.values()])
            
            # Identify optimization opportunities
            potential_savings = await self._calculate_potential_savings(
                tenant_id, performance_data
            )
            
            return {
                "summary": {
                    "total_requests": total_requests,
                    "total_cost_cents": int(total_cost * 100),
                    "avg_response_time_ms": avg_response_time,
                    "avg_quality_score": avg_quality,
                    "efficiency_score": self._calculate_efficiency_score(performance_data)
                },
                "model_breakdown": {
                    model: {
                        "usage_count": perf.usage_count,
                        "cost_per_request": perf.cost_per_request,
                        "avg_response_time": perf.avg_response_time,
                        "quality_score": perf.quality_score,
                        "efficiency_rating": self._rate_model_efficiency(perf)
                    }
                    for model, perf in performance_data.items()
                },
                "optimization_opportunities": {
                    "potential_cost_savings_cents": int(potential_savings * 100),
                    "underperforming_models": [
                        model for model, perf in performance_data.items()
                        if perf.quality_score < self.quality_threshold
                    ],
                    "slow_models": [
                        model for model, perf in performance_data.items()
                        if perf.avg_response_time > self.response_time_threshold
                    ]
                },
                "usage_patterns": usage_patterns,
                "recommendations": await self.get_optimization_recommendations(tenant_id)
            }
            
        except Exception as e:
            logging.error(f"Error generating efficiency report: {e}")
            return {"error": str(e)}
    
    def _classify_model_type(self, model_name: str) -> ModelType:
        """Classify model type based on name"""
        
        if "gpt-4o" in model_name:
            return ModelType.OPENAI_MULTIMODAL
        elif "gpt" in model_name:
            return ModelType.OPENAI_TEXT
        elif "llava" in model_name:
            return ModelType.LOCAL_MULTIMODAL
        else:
            return ModelType.LOCAL_TEXT
    
    def _calculate_average_cost(
        self,
        model_name: str,
        total_tokens: int,
        usage_count: int
    ) -> float:
        """Calculate average cost per request for a model"""
        
        if usage_count == 0:
            return 0.0
        
        # Use pricing from chatbot service
        pricing = {
            "gpt-3.5-turbo": 0.0015,  # per 1K tokens
            "gpt-4o": 0.003,
            "mistral:latest": 0.0,
            "llava:latest": 0.0,
            "fallback": 0.0
        }
        
        rate = pricing.get(model_name, 0.0)
        total_cost = (total_tokens / 1000) * rate
        
        return total_cost / usage_count
    
    async def _calculate_quality_score(
        self,
        tenant_id: str,
        model_name: str,
        start_date: datetime
    ) -> float:
        """Calculate quality score for a model based on various metrics"""
        
        try:
            # For now, use success rate as proxy for quality
            # In future, this could include user ratings, conversation resolution rates, etc.
            
            result = await self.db.execute(
                select(
                    func.avg(
                        case(
                            (Message.status == "delivered", 1.0),
                            else_=0.0
                        )
                    ).label("success_rate")
                )
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(
                    and_(
                        Conversation.tenant_id == tenant_id,
                        Message.ai_model_used == model_name,
                        Message.created_at >= start_date
                    )
                )
            )
            
            success_rate = result.scalar() or 0.0
            
            # Adjust based on model type (local models might have different quality expectations)
            model_type = self._classify_model_type(model_name)
            if model_type in [ModelType.LOCAL_TEXT, ModelType.LOCAL_MULTIMODAL]:
                # Local models get slight quality bonus for privacy/speed
                return min(success_rate + 0.1, 1.0)
            
            return success_rate
            
        except Exception as e:
            logging.error(f"Error calculating quality score: {e}")
            return 0.5  # Default neutral score
    
    async def _analyze_usage_patterns(
        self,
        tenant_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze usage patterns to inform optimization"""
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get hourly usage distribution
            hourly_usage = await self._get_hourly_usage_distribution(tenant_id, start_date)
            
            # Get request type distribution
            type_distribution = await self._get_request_type_distribution(tenant_id, start_date)
            
            # Get channel usage
            channel_usage = await self._get_channel_usage_distribution(tenant_id, start_date)
            
            return {
                "hourly_distribution": hourly_usage,
                "request_types": type_distribution,
                "channel_distribution": channel_usage,
                "peak_hours": self._identify_peak_hours(hourly_usage),
                "usage_trends": await self._calculate_usage_trends(tenant_id, days)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing usage patterns: {e}")
            return {}
    
    def _calculate_model_score(
        self,
        performance: ModelPerformance,
        request_complexity: float,
        time_sensitivity: float,
        cost_sensitivity: float
    ) -> float:
        """Calculate overall score for model selection"""
        
        # Normalize metrics
        speed_score = max(0, 1 - (performance.avg_response_time / 10000))  # 10s max
        cost_score = max(0, 1 - (performance.cost_per_request / 0.01))  # $0.01 max
        quality_score = performance.quality_score
        
        # Weight based on context
        weighted_score = (
            speed_score * (1 - time_sensitivity) +
            cost_score * cost_sensitivity +
            quality_score * self.quality_weight
        )
        
        # Adjust for request complexity
        if request_complexity > 0.7 and performance.model_type in [ModelType.OPENAI_TEXT, ModelType.OPENAI_MULTIMODAL]:
            weighted_score += 0.1  # Bonus for complex requests
        
        return min(weighted_score, 1.0)
    
    def _analyze_request_complexity(self, context: Dict[str, Any]) -> float:
        """Analyze complexity of the request (0-1 scale)"""
        
        complexity = 0.0
        
        # Check message length
        message_length = len(context.get("message", ""))
        if message_length > 500:
            complexity += 0.3
        elif message_length > 100:
            complexity += 0.1
        
        # Check for media
        if context.get("media_url"):
            complexity += 0.4
        
        # Check conversation history length
        history_length = len(context.get("conversation_history", []))
        if history_length > 10:
            complexity += 0.2
        elif history_length > 5:
            complexity += 0.1
        
        # Check for technical terms or complexity indicators
        message = context.get("message", "").lower()
        complex_indicators = ["explain", "how to", "step by step", "technical", "problem", "error"]
        if any(indicator in message for indicator in complex_indicators):
            complexity += 0.2
        
        return min(complexity, 1.0)
    
    def _analyze_time_sensitivity(self, context: Dict[str, Any]) -> float:
        """Analyze time sensitivity of request (0-1 scale, 1 = very time sensitive)"""
        
        # Default to moderate sensitivity
        sensitivity = 0.5
        
        # Channel-based sensitivity
        channel = context.get("channel", "")
        if channel == "web":
            sensitivity = 0.8  # Web users expect fast responses
        elif channel == "whatsapp":
            sensitivity = 0.6  # WhatsApp is moderately time-sensitive
        elif channel == "telegram":
            sensitivity = 0.4  # Telegram users more patient
        
        # Urgent keywords
        message = context.get("message", "").lower()
        urgent_words = ["urgent", "emergency", "asap", "immediately", "now", "help"]
        if any(word in message for word in urgent_words):
            sensitivity = min(sensitivity + 0.3, 1.0)
        
        return sensitivity
    
    async def _analyze_cost_sensitivity(self, tenant_id: str) -> float:
        """Analyze cost sensitivity for tenant based on subscription tier"""
        
        try:
            # Get tenant subscription info
            from app.models import Subscription
            
            result = await self.db.execute(
                select(Subscription.plan_name)
                .where(Subscription.tenant_id == tenant_id)
            )
            
            plan = result.scalar()
            
            # Cost sensitivity based on plan
            if plan == "free":
                return 1.0  # Very cost sensitive
            elif plan == "basic":
                return 0.7  # Moderately cost sensitive
            elif plan == "pro":
                return 0.4  # Less cost sensitive
            elif plan == "enterprise":
                return 0.2  # Least cost sensitive
            
            return 0.5  # Default
            
        except Exception:
            return 0.5  # Default moderate sensitivity
    
    def _get_default_model_choice(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get default model choice when optimization data is unavailable"""
        
        has_media = bool(context.get("media_url"))
        
        if has_media:
            model = settings.OPENAI_MODEL_MULTIMODAL if not settings.LOCAL_MODEL_ENABLED else "llava:latest"
        else:
            model = settings.OPENAI_MODEL_TEXT if not settings.LOCAL_MODEL_ENABLED else "mistral:latest"
        
        return {
            "recommended_model": model,
            "confidence_score": 0.5,
            "reasoning": "Default model selection - insufficient data for optimization",
            "alternatives": []
        }
    
    def _explain_model_choice(
        self,
        model_name: str,
        performance: ModelPerformance,
        context: Dict[str, Any]
    ) -> str:
        """Generate explanation for model choice"""
        
        reasons = []
        
        if performance.avg_response_time < 2000:
            reasons.append("fast response time")
        
        if performance.cost_per_request < 0.001:
            reasons.append("cost-effective")
        
        if performance.quality_score > 0.8:
            reasons.append("high quality responses")
        
        if performance.usage_count > 100:
            reasons.append("proven reliability")
        
        if context.get("media_url") and "multimodal" in model_name:
            reasons.append("supports image analysis")
        
        if not reasons:
            reasons = ["balanced performance characteristics"]
        
        return f"Recommended due to: {', '.join(reasons)}"
    
    # Additional helper methods would be implemented here for:
    # - _analyze_cost_optimization
    # - _analyze_performance_optimization  
    # - _analyze_quality_optimization
    # - _calculate_efficiency_score
    # - _rate_model_efficiency
    # - _calculate_potential_savings
    # etc.