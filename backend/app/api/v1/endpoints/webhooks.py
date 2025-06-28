from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db

router = APIRouter()


@router.get("/")
async def get_webhooks(db: AsyncSession = Depends(get_db)):
    """Get webhooks for current tenant"""
    return []