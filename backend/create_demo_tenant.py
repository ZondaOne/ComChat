#!/usr/bin/env python3
"""
Create a demo tenant for ComChat
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.tenant import Tenant


async def create_demo_tenant():
    """Create a demo tenant in the database"""
    
    # Create async engine
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(database_url)
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Check if demo tenant already exists
            from sqlalchemy import select
            result = await session.execute(
                select(Tenant).where(Tenant.slug == "demo")
            )
            existing_tenant = result.scalar_one_or_none()
            
            if existing_tenant:
                print("Demo tenant already exists!")
                print(f"ID: {existing_tenant.id}")
                print(f"Name: {existing_tenant.name}")
                print(f"Slug: {existing_tenant.slug}")
                return
            
            # Create new demo tenant
            demo_tenant = Tenant(
                name="Demo Company",
                slug="demo",
                contact_email="demo@example.com",
                contact_phone="+1234567890",
                subscription_tier="free",
                is_active=True,
                web_widget_enabled=True,
                whatsapp_enabled=False,
                telegram_enabled=False,
                monthly_message_limit=1000,
                monthly_message_count=0,
                config={
                    "welcome_message": "Hello! Welcome to our demo chatbot. How can I help you today?",
                    "default_response": "I'm a demo chatbot. I can help answer your questions!",
                    "business_info": {
                        "name": "Demo Company",
                        "industry": "Technology",
                        "description": "A demo company for testing ComChat"
                    }
                }
            )
            
            session.add(demo_tenant)
            await session.commit()
            await session.refresh(demo_tenant)
            
            print("✅ Demo tenant created successfully!")
            print(f"ID: {demo_tenant.id}")
            print(f"Name: {demo_tenant.name}")
            print(f"Slug: {demo_tenant.slug}")
            print(f"Email: {demo_tenant.contact_email}")
            print(f"Active: {demo_tenant.is_active}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating demo tenant: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_demo_tenant())