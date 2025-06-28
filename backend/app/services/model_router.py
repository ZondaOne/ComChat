import openai
import httpx
from typing import Optional, Dict, Any, List
import logging
import asyncio
import base64
import io
from PIL import Image

from app.core.config import settings


class ModelRouter:
    """Routes requests to appropriate AI models based on requirements"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.ollama_client = httpx.AsyncClient(base_url=settings.OLLAMA_BASE_URL, timeout=30.0)
        
    async def generate_response(
        self,
        message: str,
        context: List[Dict[str, Any]],
        tenant_config: Dict[str, Any],
        media_url: Optional[str] = None,
        use_multimodal: bool = False
    ) -> Dict[str, Any]:
        """Generate AI response using the best model for the request"""
        
        try:
            # Determine which model to use based on configuration and availability
            use_local = settings.LOCAL_MODEL_ENABLED and await self.check_ollama_health()
            
            # If no OpenAI client and Ollama is not available, return fallback
            if not self.openai_client and not use_local:
                logging.warning("No AI models available (OpenAI not configured, Ollama not running)")
                return {
                    "content": "Hello! I'm a demo chatbot. I'd be happy to help you, but I need either OpenAI API access or Ollama to be running to provide intelligent responses.",
                    "model": "fallback-demo",
                    "tokens_used": 0
                }
            
            if use_multimodal and media_url:
                if use_local:
                    return await self._generate_local_multimodal_response(
                        message, context, tenant_config, media_url
                    )
                else:
                    return await self._generate_multimodal_response(
                        message, context, tenant_config, media_url
                    )
            else:
                if use_local:
                    return await self._generate_local_text_response(
                        message, context, tenant_config
                    )
                else:
                    return await self._generate_text_response(
                        message, context, tenant_config
                    )
        except Exception as e:
            logging.error(f"Error generating AI response: {e}")
            # Try fallback to local model if OpenAI fails
            if not settings.LOCAL_MODEL_ENABLED:
                try:
                    return await self._generate_local_text_response(
                        message, context, tenant_config
                    )
                except Exception as fallback_error:
                    logging.error(f"Fallback model also failed: {fallback_error}")
            
            # Ultimate fallback response
            return {
                "content": "I apologize, but I'm having trouble processing your request right now. Please try again later.",
                "model": "fallback",
                "tokens_used": 0
            }
    
    async def _generate_text_response(
        self,
        message: str,
        context: List[Dict[str, Any]],
        tenant_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate text-only response using GPT-3.5-turbo"""
        
        # Build conversation messages
        messages = self._build_conversation_messages(context, tenant_config)
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL_TEXT,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": settings.OPENAI_MODEL_TEXT,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_multimodal_response(
        self,
        message: str,
        context: List[Dict[str, Any]],
        tenant_config: Dict[str, Any],
        media_url: str
    ) -> Dict[str, Any]:
        """Generate response for image + text using GPT-4o"""
        
        # Build conversation messages with image support
        messages = self._build_conversation_messages(context, tenant_config, include_media=True)
        
        # Add current message with image
        user_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": message},
                {"type": "image_url", "image_url": {"url": media_url}}
            ]
        }
        messages.append(user_message)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL_MULTIMODAL,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": settings.OPENAI_MODEL_MULTIMODAL,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logging.error(f"OpenAI API error (multimodal): {e}")
            raise
    
    def _build_conversation_messages(
        self,
        context: List[Dict[str, Any]],
        tenant_config: Dict[str, Any],
        include_media: bool = False
    ) -> List[Dict[str, Any]]:
        """Build conversation messages for OpenAI API"""
        
        messages = []
        
        # Add system message with tenant configuration
        system_prompt = self._build_system_prompt(tenant_config)
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        for msg in context:
            if include_media and msg.get("media_url"):
                # Format message with media for multimodal models
                content = [{"type": "text", "text": msg["content"]}]
                if msg.get("media_type", "").startswith("image/"):
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": msg["media_url"]}
                    })
                messages.append({
                    "role": msg["role"],
                    "content": content
                })
            else:
                # Text-only message
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return messages
    
    def _build_system_prompt(self, tenant_config: Dict[str, Any]) -> str:
        """Build system prompt based on tenant configuration"""
        
        base_prompt = """You are a helpful customer service chatbot. Be friendly, professional, and helpful.
        
Guidelines:
- Keep responses concise and relevant
- If you cannot help with something, politely explain and offer alternatives
- Maintain a consistent tone throughout the conversation
- If asked about sensitive information, politely decline and redirect"""
        
        # Add tenant-specific customizations
        custom_prompt = tenant_config.get("system_prompt", "")
        if custom_prompt:
            base_prompt += f"\n\nAdditional instructions:\n{custom_prompt}"
        
        # Add decision tree context if available
        decision_trees = tenant_config.get("decision_trees", [])
        if decision_trees:
            base_prompt += "\n\nAvailable decision paths:\n"
            for tree in decision_trees:
                base_prompt += f"- {tree.get('name', 'Unnamed')}: {tree.get('description', '')}\n"
        
        return base_prompt

    async def _generate_local_text_response(
        self,
        message: str,
        context: List[Dict[str, Any]],
        tenant_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate text response using local Ollama model"""
        
        # Build conversation for Ollama
        conversation = self._build_ollama_conversation(context, tenant_config)
        conversation.append({"role": "user", "content": message})
        
        try:
            response = await self.ollama_client.post(
                "/api/chat",
                json={
                    "model": "llama3.2:3b",
                    "messages": conversation,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": result["message"]["content"],
                    "model": "llama3.2:3b",
                    "tokens_used": result.get("eval_count", 0)
                }
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            logging.error(f"Local model error: {e}")
            raise

    async def _generate_local_multimodal_response(
        self,
        message: str,
        context: List[Dict[str, Any]],
        tenant_config: Dict[str, Any],
        media_url: str
    ) -> Dict[str, Any]:
        """Generate multimodal response using local LLaVA model"""
        
        try:
            # Download and encode image
            image_base64 = await self._encode_image_from_url(media_url)
            
            # Build conversation for LLaVA
            conversation = self._build_ollama_conversation(context, tenant_config, include_system=False)
            
            # LLaVA expects a single message with image
            llava_message = {
                "role": "user",
                "content": message,
                "images": [image_base64]
            }
            
            response = await self.ollama_client.post(
                "/api/chat",
                json={
                    "model": "llava:latest",
                    "messages": [llava_message],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": result["message"]["content"],
                    "model": "llava:latest",
                    "tokens_used": result.get("eval_count", 0)
                }
            else:
                raise Exception(f"LLaVA API error: {response.status_code}")
                
        except Exception as e:
            logging.error(f"Local multimodal model error: {e}")
            raise

    async def _encode_image_from_url(self, image_url: str) -> str:
        """Download image from URL and encode as base64"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                
                # Convert to base64
                image_bytes = response.content
                return base64.b64encode(image_bytes).decode('utf-8')
                
        except Exception as e:
            logging.error(f"Error encoding image: {e}")
            raise

    def _build_ollama_conversation(
        self,
        context: List[Dict[str, Any]],
        tenant_config: Dict[str, Any],
        include_system: bool = True
    ) -> List[Dict[str, Any]]:
        """Build conversation messages for Ollama models"""
        
        messages = []
        
        # Add system message if requested
        if include_system:
            system_prompt = self._build_system_prompt(tenant_config)
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history (text only for now)
        for msg in context:
            if not msg.get("media_url"):  # Skip media messages for text models
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return messages

    async def check_ollama_health(self) -> bool:
        """Check if Ollama is running and responsive"""
        try:
            response = await self.ollama_client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def list_available_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            response = await self.ollama_client.get("/api/tags")
            if response.status_code == 200:
                result = response.json()
                return [model["name"] for model in result.get("models", [])]
            return []
        except Exception as e:
            logging.error(f"Error listing models: {e}")
            return []