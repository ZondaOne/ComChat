from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import logging

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,  # Disable SQL logging to reduce noise
    poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
    connect_args={
        "ssl": "require",
        "server_settings": {
            "application_name": "ComChat",
        }
    }
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Import all models here to ensure they're registered
        from app.models import tenant, user, conversation, message, webhook, workflow
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Database tables created successfully")


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()