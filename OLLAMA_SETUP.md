# Ollama Integration Setup Guide

This guide shows how to set up local AI models using Ollama for development and testing.

## 🎯 Overview

Ollama integration provides:
- **Local AI Models**: Run Mistral, LLaVA, and other models locally
- **Cost Savings**: No API costs during development
- **Privacy**: All processing happens locally
- **Offline Support**: Works without internet connection
- **Fallback**: Automatic fallback if OpenAI is unavailable

## 🚀 Quick Start with Docker

### 1. Start Ollama with Docker Compose

```bash
# Start all services including Ollama
docker-compose up -d

# Check if Ollama is running
docker ps | grep ollama
```

### 2. Pull Required Models

```bash
# Pull Mistral for text generation (4GB)
docker exec comchat_ollama ollama pull mistral:latest

# Pull LLaVA for image analysis (4.5GB)
docker exec comchat_ollama ollama pull llava:latest

# Optional: Pull smaller models for testing
docker exec comchat_ollama ollama pull llama3.2:1b
```

### 3. Enable Local Models

Update your `.env` file:

```env
# Enable local models as primary
LOCAL_MODEL_ENABLED=true

# Ollama configuration  
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Disable OpenAI for local-only testing
# OPENAI_API_KEY=
```

### 4. Test the Integration

```bash
# Check model health via API
curl http://localhost:8000/api/v1/models/health

# Test a model directly
curl -X POST "http://localhost:8000/api/v1/models/test?model_name=mistral:latest" \
  -H "Content-Type: application/json" \
  -d '{"test_message": "Hello! How are you?"}'
```

## 🔧 Manual Ollama Installation

### Option 1: Native Installation

```bash
# macOS
brew install ollama

# Linux  
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

### Option 2: Docker Only

```bash
# Run Ollama in Docker
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama:latest

# Pull models
docker exec ollama ollama pull mistral:latest
docker exec ollama ollama pull llava:latest
```

## 📊 Model Comparison

| Model | Size | Use Case | Speed | Quality |
|-------|------|----------|--------|---------|
| **mistral:latest** | ~4GB | General text generation | Fast | High |
| **llava:latest** | ~4.5GB | Image + text analysis | Medium | High |
| **llama3.2:1b** | ~1GB | Testing, fast responses | Very Fast | Good |
| **codellama:7b** | ~4GB | Code generation | Fast | High |

## 🔄 Automatic Fallback System

The system automatically handles model availability:

```python
# Model routing logic
if LOCAL_MODEL_ENABLED or not openai_available:
    use_local_model()
else:
    use_openai_model()
```

**Fallback Order:**
1. Local models (if enabled)
2. OpenAI models (if API key available)
3. Error response

## 🌐 API Endpoints

### Model Health Check
```bash
GET /api/v1/models/health
```

### List Available Models
```bash
GET /api/v1/models/ollama/models
```

### Pull New Model
```bash
POST /api/v1/models/ollama/pull?model_name=mistral:latest
```

### Test Model
```bash
POST /api/v1/models/test?model_name=mistral:latest
```

## 💻 Frontend Integration

The frontend automatically detects available models:

```typescript
// Check model availability
const modelHealth = await fetch('/api/v1/models/health');
const { ollama_available, openai_available } = await modelHealth.json();

if (ollama_available) {
  console.log('Local models available! 🎉');
}
```

## 🔧 Configuration Options

### Environment Variables

```env
# Local Models
LOCAL_MODEL_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434

# Model Selection
OLLAMA_TEXT_MODEL=mistral:latest
OLLAMA_MULTIMODAL_MODEL=llava:latest

# Performance
OLLAMA_TIMEOUT=30
OLLAMA_KEEP_ALIVE=5m
```

### Docker Compose Overrides

For GPU support:

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  ollama:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama not starting**
   ```bash
   # Check logs
   docker logs comchat_ollama
   
   # Restart service
   docker-compose restart ollama
   ```

2. **Model download fails**
   ```bash
   # Check disk space (models are large!)
   df -h
   
   # Check internet connection
   docker exec comchat_ollama ollama list
   ```

3. **Slow model responses**
   ```bash
   # Check system resources
   docker stats comchat_ollama
   
   # Use smaller models for testing
   docker exec comchat_ollama ollama pull llama3.2:1b
   ```

4. **API errors**
   ```bash
   # Test Ollama directly
   curl http://localhost:11434/api/tags
   
   # Check backend logs
   docker logs comchat_backend
   ```

### Performance Tips

1. **GPU Acceleration**: Enable NVIDIA runtime for GPU support
2. **Model Size**: Use smaller models (1B-3B params) for development
3. **Memory**: Ensure 8GB+ RAM for larger models
4. **Storage**: Allow 10GB+ for model storage

## 📱 Testing Different Scenarios

### Text-Only Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "channel": "web",
    "channel_user_id": "test-user",
    "tenant_slug": "demo"
  }'
```

### Image Analysis (LLaVA)
```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do you see in this image?",
    "channel": "web", 
    "channel_user_id": "test-user",
    "tenant_slug": "demo",
    "media_url": "https://example.com/image.jpg",
    "media_type": "image/jpeg"
  }'
```

## 🎯 Production Considerations

### Resource Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB+ for multiple models
- **Storage**: 20GB+ for model storage
- **GPU**: Optional but significantly improves performance

### Scaling
- Use model-specific containers for high loads
- Implement model loading/unloading for memory management
- Consider model quantization for reduced resource usage

### Security
- Run Ollama in isolated containers
- Restrict network access to internal services only
- Monitor resource usage and implement limits

## 📚 Next Steps

1. **Custom Models**: Train custom models for your specific use case
2. **Model Fine-tuning**: Fine-tune existing models with your data  
3. **Performance Optimization**: Implement model caching and load balancing
4. **Monitoring**: Set up model performance and usage monitoring

---

**Need help?** Check the [main setup guide](SETUP.md) or open an issue in the repository.