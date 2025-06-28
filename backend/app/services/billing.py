import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging

from app.models import Tenant, Subscription, UsageRecord, Invoice, PaymentMethod
from app.core.config import settings

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class BillingService:
    """Service for managing billing, subscriptions, and usage tracking"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_subscription(
        self,
        tenant: Tenant,
        plan_name: str,
        billing_cycle: str = "monthly",
        trial_days: Optional[int] = None
    ) -> Subscription:
        """Create a new subscription for a tenant"""
        
        try:
            # Create Stripe customer if not exists
            if not tenant.contact_email:
                raise ValueError("Tenant email is required for billing")
            
            stripe_customer = stripe.Customer.create(
                email=tenant.contact_email,
                name=tenant.name,
                metadata={
                    "tenant_id": str(tenant.id),
                    "tenant_slug": tenant.slug
                }
            )
            
            # Get plan configuration
            plan_config = self._get_plan_config(plan_name)
            
            # Calculate trial end
            trial_end = None
            if trial_days:
                trial_end = datetime.utcnow() + timedelta(days=trial_days)
            
            # Create subscription record
            subscription = Subscription(
                tenant_id=tenant.id,
                stripe_customer_id=stripe_customer.id,
                plan_name=plan_name,
                billing_cycle=billing_cycle,
                monthly_price_cents=plan_config["monthly_price_cents"],
                yearly_price_cents=plan_config["yearly_price_cents"],
                monthly_message_limit=plan_config["monthly_message_limit"],
                monthly_ai_request_limit=plan_config["monthly_ai_request_limit"],
                max_channels=plan_config["max_channels"],
                max_users=plan_config["max_users"],
                features_enabled=plan_config["features"],
                trial_end=trial_end,
                is_trial=trial_days is not None
            )
            
            # Create Stripe subscription if not free plan
            if plan_name != "free":
                price_id = plan_config[f"{billing_cycle}_stripe_price_id"]
                
                stripe_subscription = stripe.Subscription.create(
                    customer=stripe_customer.id,
                    items=[{"price": price_id}],
                    trial_end=int(trial_end.timestamp()) if trial_end else None,
                    metadata={
                        "tenant_id": str(tenant.id),
                        "plan_name": plan_name
                    }
                )
                
                subscription.stripe_subscription_id = stripe_subscription.id
                subscription.stripe_price_id = price_id
                subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
                subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
            
            self.db.add(subscription)
            await self.db.commit()
            await self.db.refresh(subscription)
            
            return subscription
            
        except Exception as e:
            logging.error(f"Error creating subscription: {e}")
            raise
    
    async def record_usage(
        self,
        tenant_id: str,
        usage_type: str,
        quantity: int = 1,
        cost_cents: int = 0,
        tokens_used: Optional[int] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UsageRecord:
        """Record usage for billing purposes"""
        
        billing_period = datetime.utcnow().strftime("%Y-%m")
        
        usage_record = UsageRecord(
            tenant_id=tenant_id,
            usage_type=usage_type,
            quantity=quantity,
            cost_cents=cost_cents,
            tokens_used=tokens_used,
            resource_id=resource_id,
            metadata=metadata or {},
            billing_period=billing_period
        )
        
        self.db.add(usage_record)
        await self.db.commit()
        await self.db.refresh(usage_record)
        
        return usage_record
    
    async def check_usage_limits(self, tenant_id: str) -> Dict[str, Any]:
        """Check if tenant is within usage limits"""
        
        logging.info(f"💳 BillingService.check_usage_limits called for tenant_id={tenant_id}")
        
        # Get tenant subscription
        logging.info(f"💳 Looking up subscription for tenant {tenant_id}")
        subscription = await self._get_tenant_subscription(tenant_id)
        if not subscription:
            logging.warning(f"💳 No subscription found for tenant {tenant_id}")
            return {"within_limits": False, "reason": "No subscription found"}
        
        logging.info(f"💳 Found subscription: plan={subscription.plan_name}, status={subscription.status}, message_limit={subscription.monthly_message_limit}, ai_limit={subscription.monthly_ai_request_limit}")
        
        current_period = datetime.utcnow().strftime("%Y-%m")
        logging.info(f"💳 Checking usage for billing period: {current_period}")
        
        # Get current usage
        logging.info(f"💳 Querying message usage for tenant {tenant_id}")
        result = await self.db.execute(
            select(func.sum(UsageRecord.quantity))
            .where(
                UsageRecord.tenant_id == tenant_id,
                UsageRecord.usage_type == "messages",
                UsageRecord.billing_period == current_period
            )
        )
        
        current_messages = result.scalar() or 0
        logging.info(f"💳 Current message usage: {current_messages}")
        
        logging.info(f"💳 Querying AI request usage for tenant {tenant_id}")
        result = await self.db.execute(
            select(func.sum(UsageRecord.quantity))
            .where(
                UsageRecord.tenant_id == tenant_id,
                UsageRecord.usage_type == "ai_requests",
                UsageRecord.billing_period == current_period
            )
        )
        
        current_ai_requests = result.scalar() or 0
        logging.info(f"💳 Current AI request usage: {current_ai_requests}")
        
        # Check limits
        within_message_limit = current_messages < subscription.monthly_message_limit
        within_ai_limit = current_ai_requests < subscription.monthly_ai_request_limit
        
        logging.info(f"💳 Limit checks: messages={current_messages}/{subscription.monthly_message_limit} (within: {within_message_limit}), ai_requests={current_ai_requests}/{subscription.monthly_ai_request_limit} (within: {within_ai_limit})")
        
        result = {
            "within_limits": within_message_limit and within_ai_limit,
            "current_messages": current_messages,
            "message_limit": subscription.monthly_message_limit,
            "current_ai_requests": current_ai_requests,
            "ai_request_limit": subscription.monthly_ai_request_limit,
            "plan_name": subscription.plan_name
        }
        
        logging.info(f"💳 Usage check result: {result}")
        return result
    
    async def handle_stripe_webhook(self, event: Dict[str, Any]) -> bool:
        """Handle Stripe webhook events"""
        
        try:
            event_type = event["type"]
            data = event["data"]["object"]
            
            if event_type == "customer.subscription.updated":
                await self._handle_subscription_updated(data)
            elif event_type == "customer.subscription.deleted":
                await self._handle_subscription_canceled(data)
            elif event_type == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(data)
            elif event_type == "invoice.payment_failed":
                await self._handle_payment_failed(data)
            
            return True
            
        except Exception as e:
            logging.error(f"Error handling Stripe webhook: {e}")
            return False
    
    async def _handle_subscription_updated(self, stripe_subscription: Dict[str, Any]):
        """Handle subscription update from Stripe"""
        
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription["id"]
            )
        )
        
        subscription = result.scalar_one_or_none()
        if subscription:
            subscription.status = stripe_subscription["status"]
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_subscription["current_period_start"]
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_subscription["current_period_end"]
            )
            await self.db.commit()
    
    async def _handle_subscription_canceled(self, stripe_subscription: Dict[str, Any]):
        """Handle subscription cancellation"""
        
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription["id"]
            )
        )
        
        subscription = result.scalar_one_or_none()
        if subscription:
            subscription.status = "canceled"
            subscription.canceled_at = datetime.utcnow()
            await self.db.commit()
    
    async def _handle_payment_succeeded(self, stripe_invoice: Dict[str, Any]):
        """Handle successful payment"""
        
        # Update invoice status
        result = await self.db.execute(
            select(Invoice).where(
                Invoice.stripe_invoice_id == stripe_invoice["id"]
            )
        )
        
        invoice = result.scalar_one_or_none()
        if invoice:
            invoice.status = "paid"
            invoice.paid_at = datetime.utcnow()
            await self.db.commit()
    
    async def _handle_payment_failed(self, stripe_invoice: Dict[str, Any]):
        """Handle failed payment"""
        
        # Update invoice status and possibly suspend service
        result = await self.db.execute(
            select(Invoice).where(
                Invoice.stripe_invoice_id == stripe_invoice["id"]
            )
        )
        
        invoice = result.scalar_one_or_none()
        if invoice:
            invoice.status = "failed"
            await self.db.commit()
            
            # TODO: Send notification to tenant
            # TODO: Implement grace period before service suspension
    
    async def _get_tenant_subscription(self, tenant_id: str) -> Optional[Subscription]:
        """Get active subscription for tenant"""
        
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.tenant_id == tenant_id,
                Subscription.status.in_(["active", "trialing"])
            )
        )
        
        return result.scalar_one_or_none()
    
    def _get_plan_config(self, plan_name: str) -> Dict[str, Any]:
        """Get configuration for a billing plan"""
        
        plans = {
            "free": {
                "monthly_price_cents": 0,
                "yearly_price_cents": 0,
                "monthly_message_limit": 1000,
                "monthly_ai_request_limit": 500,
                "max_channels": 1,
                "max_users": 1,
                "features": {
                    "web_chat": True,
                    "telegram": False,
                    "whatsapp": False,
                    "analytics": False,
                    "webhooks": False,
                    "decision_trees": False
                }
            },
            "basic": {
                "monthly_price_cents": 2900,  # $29
                "yearly_price_cents": 29000,  # $290 (17% discount)
                "monthly_stripe_price_id": "price_basic_monthly",
                "yearly_stripe_price_id": "price_basic_yearly",
                "monthly_message_limit": 5000,
                "monthly_ai_request_limit": 2500,
                "max_channels": 2,
                "max_users": 3,
                "features": {
                    "web_chat": True,
                    "telegram": True,
                    "whatsapp": False,
                    "analytics": True,
                    "webhooks": True,
                    "decision_trees": True
                }
            },
            "pro": {
                "monthly_price_cents": 9900,  # $99
                "yearly_price_cents": 99000,  # $990
                "monthly_stripe_price_id": "price_pro_monthly",
                "yearly_stripe_price_id": "price_pro_yearly",
                "monthly_message_limit": 25000,
                "monthly_ai_request_limit": 12500,
                "max_channels": 3,
                "max_users": 10,
                "features": {
                    "web_chat": True,
                    "telegram": True,
                    "whatsapp": True,
                    "analytics": True,
                    "webhooks": True,
                    "decision_trees": True,
                    "custom_branding": True,
                    "priority_support": True
                }
            },
            "enterprise": {
                "monthly_price_cents": 29900,  # $299
                "yearly_price_cents": 299000,  # $2990
                "monthly_stripe_price_id": "price_enterprise_monthly",
                "yearly_stripe_price_id": "price_enterprise_yearly",
                "monthly_message_limit": 100000,
                "monthly_ai_request_limit": 50000,
                "max_channels": 10,
                "max_users": 50,
                "features": {
                    "web_chat": True,
                    "telegram": True,
                    "whatsapp": True,
                    "analytics": True,
                    "webhooks": True,
                    "decision_trees": True,
                    "custom_branding": True,
                    "priority_support": True,
                    "custom_integration": True,
                    "sso": True,
                    "dedicated_support": True
                }
            }
        }
        
        if plan_name not in plans:
            raise ValueError(f"Unknown plan: {plan_name}")
        
        return plans[plan_name]