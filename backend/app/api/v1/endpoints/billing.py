from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import stripe
import logging

from app.core.db import get_db
from app.core.config import settings
from app.services.billing import BillingService
from app.models import Tenant, Subscription

router = APIRouter()


class SubscriptionRequest(BaseModel):
    plan_name: str
    billing_cycle: str = "monthly"
    trial_days: Optional[int] = None


class SubscriptionResponse(BaseModel):
    id: str
    plan_name: str
    status: str
    billing_cycle: str
    monthly_price_cents: int
    current_period_end: Optional[str]
    trial_end: Optional[str]
    features_enabled: Dict[str, Any]


class UsageResponse(BaseModel):
    within_limits: bool
    current_messages: int
    message_limit: int
    current_ai_requests: int
    ai_request_limit: int
    plan_name: str


class PaymentMethodRequest(BaseModel):
    stripe_payment_method_id: str
    is_default: bool = False


@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionRequest,
    tenant_id: str,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription for a tenant"""
    
    try:
        billing_service = BillingService(db)
        
        # Get tenant
        tenant = await db.get(Tenant, tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Check if tenant already has a subscription
        existing_subscription = await db.execute(
            select(Subscription).where(Subscription.tenant_id == tenant.id)
        )
        if existing_subscription.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Tenant already has a subscription")
        
        subscription = await billing_service.create_subscription(
            tenant=tenant,
            plan_name=request.plan_name,
            billing_cycle=request.billing_cycle,
            trial_days=request.trial_days
        )
        
        return SubscriptionResponse(
            id=str(subscription.id),
            plan_name=subscription.plan_name,
            status=subscription.status,
            billing_cycle=subscription.billing_cycle,
            monthly_price_cents=subscription.monthly_price_cents,
            current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            trial_end=subscription.trial_end.isoformat() if subscription.trial_end else None,
            features_enabled=subscription.features_enabled
        )
        
    except Exception as e:
        logging.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")


@router.get("/subscriptions/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    tenant_id: str,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db)
):
    """Get current subscription for tenant"""
    
    try:
        result = await db.execute(
            select(Subscription).where(Subscription.tenant_id == tenant_id)
        )
        
        subscription = result.scalar_one_or_none()
        if not subscription:
            raise HTTPException(status_code=404, detail="No subscription found")
        
        return SubscriptionResponse(
            id=str(subscription.id),
            plan_name=subscription.plan_name,
            status=subscription.status,
            billing_cycle=subscription.billing_cycle,
            monthly_price_cents=subscription.monthly_price_cents,
            current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            trial_end=subscription.trial_end.isoformat() if subscription.trial_end else None,
            features_enabled=subscription.features_enabled
        )
        
    except Exception as e:
        logging.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subscription")


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    tenant_id: str,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db)
):
    """Get current usage for tenant"""
    
    try:
        billing_service = BillingService(db)
        usage_info = await billing_service.check_usage_limits(tenant_id)
        
        return UsageResponse(**usage_info)
        
    except Exception as e:
        logging.error(f"Error getting usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage")


@router.post("/payment-methods")
async def add_payment_method(
    request: PaymentMethodRequest,
    tenant_id: str,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db)
):
    """Add a payment method for tenant"""
    
    try:
        # Get tenant subscription
        result = await db.execute(
            select(Subscription).where(Subscription.tenant_id == tenant_id)
        )
        
        subscription = result.scalar_one_or_none()
        if not subscription or not subscription.stripe_customer_id:
            raise HTTPException(status_code=400, detail="No Stripe customer found")
        
        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            request.stripe_payment_method_id,
            customer=subscription.stripe_customer_id
        )
        
        # Set as default if requested
        if request.is_default:
            stripe.Customer.modify(
                subscription.stripe_customer_id,
                invoice_settings={
                    "default_payment_method": request.stripe_payment_method_id
                }
            )
        
        return {"success": True, "message": "Payment method added successfully"}
        
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error adding payment method: {e}")
        raise HTTPException(status_code=500, detail="Failed to add payment method")


@router.post("/create-setup-intent")
async def create_setup_intent(
    tenant_id: str,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db)
):
    """Create a setup intent for adding payment methods"""
    
    try:
        # Get tenant subscription
        result = await db.execute(
            select(Subscription).where(Subscription.tenant_id == tenant_id)
        )
        
        subscription = result.scalar_one_or_none()
        if not subscription or not subscription.stripe_customer_id:
            raise HTTPException(status_code=400, detail="No Stripe customer found")
        
        # Create setup intent
        setup_intent = stripe.SetupIntent.create(
            customer=subscription.stripe_customer_id,
            usage="off_session"
        )
        
        return {
            "client_secret": setup_intent.client_secret,
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY
        }
        
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error creating setup intent: {e}")
        raise HTTPException(status_code=500, detail="Failed to create setup intent")


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events"""
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logging.error("Invalid payload in Stripe webhook")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logging.error("Invalid signature in Stripe webhook")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    billing_service = BillingService(db)
    success = await billing_service.handle_stripe_webhook(event)
    
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/plans")
async def get_billing_plans():
    """Get available billing plans"""
    
    plans = [
        {
            "name": "free",
            "display_name": "Free",
            "price_monthly": 0,
            "price_yearly": 0,
            "features": {
                "messages_per_month": 1000,
                "ai_requests_per_month": 500,
                "channels": ["Web"],
                "users": 1,
                "support": "Community"
            }
        },
        {
            "name": "basic",
            "display_name": "Basic",
            "price_monthly": 29,
            "price_yearly": 290,
            "features": {
                "messages_per_month": 5000,
                "ai_requests_per_month": 2500,
                "channels": ["Web", "Telegram"],
                "users": 3,
                "analytics": True,
                "webhooks": True,
                "decision_trees": True,
                "support": "Email"
            }
        },
        {
            "name": "pro",
            "display_name": "Pro",
            "price_monthly": 99,
            "price_yearly": 990,
            "features": {
                "messages_per_month": 25000,
                "ai_requests_per_month": 12500,
                "channels": ["Web", "Telegram", "WhatsApp"],
                "users": 10,
                "analytics": True,
                "webhooks": True,
                "decision_trees": True,
                "custom_branding": True,
                "support": "Priority"
            }
        },
        {
            "name": "enterprise",
            "display_name": "Enterprise",
            "price_monthly": 299,
            "price_yearly": 2990,
            "features": {
                "messages_per_month": 100000,
                "ai_requests_per_month": 50000,
                "channels": ["Web", "Telegram", "WhatsApp", "Custom"],
                "users": 50,
                "analytics": True,
                "webhooks": True,
                "decision_trees": True,
                "custom_branding": True,
                "sso": True,
                "dedicated_support": True,
                "support": "Phone + Dedicated"
            }
        }
    ]
    
    return {"plans": plans}