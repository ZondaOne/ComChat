#!/usr/bin/env python3
"""
Create a demo subscription for the demo tenant
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.tenant import Tenant
from app.models.billing import Subscription


async def create_demo_subscription():
    """Create a demo subscription for the demo tenant"""
    
    # Create async engine
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(database_url)
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Find the demo tenant
            result = await session.execute(
                select(Tenant).where(Tenant.slug == "demo")
            )
            demo_tenant = result.scalar_one_or_none()
            
            if not demo_tenant:
                print("❌ Demo tenant not found! Run create_demo_tenant.py first.")
                return
            
            # Check if subscription already exists
            result = await session.execute(
                select(Subscription).where(Subscription.tenant_id == demo_tenant.id)
            )
            existing_subscription = result.scalar_one_or_none()
            
            if existing_subscription:
                print("Demo subscription already exists!")
                print(f"Plan: {existing_subscription.plan_name}")
                print(f"Status: {existing_subscription.status}")
                return
            
            # Create new demo subscription
            demo_subscription = Subscription(
                tenant_id=demo_tenant.id,
                plan_name="free",
                status="active",
                billing_cycle="monthly",
                monthly_price_cents=0,  # Free plan
                yearly_price_cents=0,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                monthly_message_limit=1000,
                monthly_ai_request_limit=1000,
                max_channels=3,
                max_users=1,
                features_enabled={
                    "web_widget": True,
                    "whatsapp": False,
                    "telegram": False,
                    "analytics": True,
                    "custom_branding": False,
                    "priority_support": False
                }
            )
            
            session.add(demo_subscription)
            await session.commit()
            await session.refresh(demo_subscription)
            
            print("✅ Demo subscription created successfully!")
            print(f"Tenant ID: {demo_subscription.tenant_id}")
            print(f"Plan: {demo_subscription.plan_name}")
            print(f"Status: {demo_subscription.status}")
            print(f"Message Limit: {demo_subscription.monthly_message_limit}")
            print(f"AI Request Limit: {demo_subscription.monthly_ai_request_limit}")
            print(f"Current Period: {demo_subscription.current_period_start} to {demo_subscription.current_period_end}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating demo subscription: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_demo_subscription())