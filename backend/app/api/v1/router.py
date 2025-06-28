from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, tenants, users, conversations, webhooks, models, billing, analytics, summarization, workflows

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Chat and messaging routes
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Tenant management routes
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])

# User management routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Conversation routes
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])

# Webhook routes
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

# Model management routes
api_router.include_router(models.router, prefix="/models", tags=["Models"])

# Billing routes
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])

# Analytics routes
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Summarization routes
api_router.include_router(summarization.router, prefix="/summarization", tags=["Summarization"])

# Workflow routes
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])