from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from app.core.db import get_db
from app.services.model_router import ModelRouter

router = APIRouter()


class ModelInfo(BaseModel):
    name: str
    type: str  # local, openai
    status: str  # available, unavailable
    size: str = None
    description: str = None


class ModelHealthResponse(BaseModel):
    ollama_available: bool
    openai_available: bool
    available_models: List[ModelInfo]


@router.get("/health", response_model=ModelHealthResponse)
async def get_model_health(db: AsyncSession = Depends(get_db)):
    """Get the health status of all AI models"""
    
    model_router = ModelRouter()
    
    try:
        # Check Ollama health
        ollama_healthy = await model_router.check_ollama_health()
        
        # Check OpenAI availability (basic check)
        openai_available = model_router.openai_client is not None
        
        # Get available models
        available_models = []
        
        if ollama_healthy:
            ollama_models = await model_router.list_available_models()
            for model_name in ollama_models:
                available_models.append(ModelInfo(
                    name=model_name,
                    type="local",
                    status="available",
                    description=f"Local Ollama model: {model_name}"
                ))
        
        if openai_available:
            available_models.extend([
                ModelInfo(
                    name="gpt-3.5-turbo",
                    type="openai",
                    status="available",
                    description="OpenAI GPT-3.5 Turbo for text generation"
                ),
                ModelInfo(
                    name="gpt-4o",
                    type="openai", 
                    status="available",
                    description="OpenAI GPT-4o for multimodal (text + image) processing"
                )
            ])
        
        return ModelHealthResponse(
            ollama_available=ollama_healthy,
            openai_available=openai_available,
            available_models=available_models
        )
        
    except Exception as e:
        logging.error(f"Error checking model health: {e}")
        raise HTTPException(status_code=500, detail="Failed to check model health")


@router.post("/ollama/pull")
async def pull_ollama_model(
    model_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Pull a model in Ollama"""
    
    model_router = ModelRouter()
    
    try:
        # Check if Ollama is running
        if not await model_router.check_ollama_health():
            raise HTTPException(status_code=503, detail="Ollama is not available")
        
        # Trigger model pull
        response = await model_router.ollama_client.post(
            "/api/pull",
            json={"name": model_name}
        )
        
        if response.status_code == 200:
            return {"message": f"Started pulling model: {model_name}"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to pull model: {model_name}")
            
    except Exception as e:
        logging.error(f"Error pulling model: {e}")
        raise HTTPException(status_code=500, detail="Failed to pull model")


@router.get("/ollama/models")
async def list_ollama_models(db: AsyncSession = Depends(get_db)):
    """List all available Ollama models"""
    
    model_router = ModelRouter()
    
    try:
        if not await model_router.check_ollama_health():
            raise HTTPException(status_code=503, detail="Ollama is not available")
        
        models = await model_router.list_available_models()
        return {"models": models}
        
    except Exception as e:
        logging.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail="Failed to list models")


@router.post("/test")
async def test_model(
    model_name: str,
    test_message: str = "Hello, how are you?",
    db: AsyncSession = Depends(get_db)
):
    """Test a specific model with a sample message"""
    
    model_router = ModelRouter()
    
    try:
        if model_name.startswith("gpt-"):
            # Test OpenAI model
            if not model_router.openai_client:
                raise HTTPException(status_code=503, detail="OpenAI client not available")
            
            response = await model_router.openai_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": test_message}],
                max_tokens=100
            )
            
            return {
                "model": model_name,
                "response": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens
            }
        else:
            # Test Ollama model
            if not await model_router.check_ollama_health():
                raise HTTPException(status_code=503, detail="Ollama is not available")
            
            response = await model_router.ollama_client.post(
                "/api/chat",
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": test_message}],
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "model": model_name,
                    "response": result["message"]["content"],
                    "tokens_used": result.get("eval_count", 0)
                }
            else:
                raise HTTPException(status_code=400, detail=f"Model test failed: {response.status_code}")
                
    except Exception as e:
        logging.error(f"Error testing model: {e}")
        raise HTTPException(status_code=500, detail="Failed to test model")