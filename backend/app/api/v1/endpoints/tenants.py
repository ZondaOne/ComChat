from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from app.core.db import get_db

router = APIRouter()


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    subscription_tier: str
    is_active: bool


@router.get("/", response_model=List[TenantResponse])
async def get_tenants(db: AsyncSession = Depends(get_db)):
    """Get all tenants (admin only)"""
    # TODO: Implement with proper authentication
    return []


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Get tenant details"""
    # TODO: Implement
    return TenantResponse(
        id=tenant_id,
        name="Sample Tenant",
        slug="sample",
        subscription_tier="free",
        is_active=True
    )