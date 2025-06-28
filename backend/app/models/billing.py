from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.db import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, unique=True)
    tenant = relationship("Tenant", back_populates="subscription")
    
    # Stripe integration
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    stripe_price_id = Column(String(255), nullable=True)
    
    # Subscription details
    plan_name = Column(String(100), nullable=False)  # free, basic, pro, enterprise
    status = Column(String(50), default="active")  # active, canceled, past_due, unpaid
    
    # Billing cycle
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Pricing
    monthly_price_cents = Column(Integer, default=0)  # Price in cents
    yearly_price_cents = Column(Integer, default=0)
    
    # Usage limits
    monthly_message_limit = Column(Integer, default=1000)
    monthly_ai_request_limit = Column(Integer, default=500)
    max_channels = Column(Integer, default=1)
    max_users = Column(Integer, default=1)
    
    # Features
    features_enabled = Column(JSON, default=dict)
    
    # Trial
    trial_end = Column(DateTime(timezone=True), nullable=True)
    is_trial = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Subscription {self.plan_name} for {self.tenant_id}>"


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")
    
    # Usage tracking
    usage_type = Column(String(50), nullable=False)  # messages, ai_requests, storage, etc.
    quantity = Column(Integer, default=1)
    
    # Cost tracking
    cost_cents = Column(Integer, default=0)  # Cost in cents
    tokens_used = Column(Integer, nullable=True)  # For AI requests
    
    # Context
    resource_id = Column(String(255), nullable=True)  # message_id, conversation_id, etc.
    usage_metadata = Column(JSON, default=dict)
    
    # Time tracking
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    billing_period = Column(String(20), nullable=False)  # YYYY-MM format

    def __repr__(self):
        return f"<UsageRecord {self.usage_type}: {self.quantity}>"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")
    
    # Stripe integration
    stripe_invoice_id = Column(String(255), nullable=True, unique=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    
    # Invoice details
    invoice_number = Column(String(100), nullable=False, unique=True)
    status = Column(String(50), default="draft")  # draft, sent, paid, failed, canceled
    
    # Amounts
    subtotal_cents = Column(Integer, default=0)
    tax_cents = Column(Integer, default=0)
    total_cents = Column(Integer, default=0)
    
    # Billing period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Payment
    due_date = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Invoice data
    line_items = Column(JSON, default=list)  # Detailed breakdown
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant")
    
    # Stripe integration
    stripe_payment_method_id = Column(String(255), nullable=False, unique=True)
    
    # Payment method details
    type = Column(String(50), nullable=False)  # card, bank_account, etc.
    
    # Card details (if applicable)
    card_brand = Column(String(20), nullable=True)  # visa, mastercard, etc.
    card_last4 = Column(String(4), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<PaymentMethod {self.type} ending in {self.card_last4}>"