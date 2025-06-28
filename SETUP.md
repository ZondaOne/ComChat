# ComChat Setup Instructions

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Environment Setup

```bash
# Clone and navigate to project
cd comChat

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Required Environment Variables

Add these to your `.env` file:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Database (leave default for Docker setup)
DATABASE_URL=postgresql://comchat_user:comchat_password@localhost:5432/comchat

# Security (change in production)
SECRET_KEY=your_super_secret_key_change_in_production
```

### 3. Start with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Test the Chat

1. Go to http://localhost:3000
2. Type a message in the chat interface
3. The AI should respond using GPT-3.5-turbo

## 🛠 Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Database Setup

```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres

# The database tables will be created automatically
# when the backend starts
```

## 📋 Verification Checklist

- [ ] Docker containers are running
- [ ] Frontend loads at http://localhost:3000
- [ ] Backend API docs accessible at http://localhost:8000/docs
- [ ] Chat interface accepts messages
- [ ] AI responses are generated
- [ ] Database is storing conversations

## 🔧 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure `OPENAI_API_KEY` is set in `.env`
   - Verify the API key is valid

2. **Database Connection Error**
   - Check if PostgreSQL container is running: `docker-compose ps`
   - Verify DATABASE_URL in `.env`

3. **Port Conflicts**
   - Change ports in `docker-compose.yml` if needed
   - Default ports: Frontend (3000), Backend (8000), Database (5432)

4. **Frontend Build Issues**
   - Delete `node_modules` and run `npm install`
   - Check Node.js version (18+)

### Debug Mode

```bash
# Enable debug logging
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run backend with debug
uvicorn app.main:app --reload --log-level debug
```

## 🔄 Next Steps

1. **Configure a Tenant**: Create your first tenant in the database
2. **Channel Integration**: Set up WhatsApp or Telegram (Phase 2)
3. **Customize Responses**: Configure decision trees and prompts
4. **Deploy**: Use Railway, Render, or your preferred platform

## 📚 Architecture

```
┌─────────────────────┐
│   React Frontend    │ ← Chat Interface
│   (Port 3000)       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   FastAPI Backend   │ ← API & AI Logic
│   (Port 8000)       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   PostgreSQL DB     │ ← Data Storage
│   (Port 5432)       │
└─────────────────────┘
```

## 🎯 Current Status

✅ **Phase 1 Complete**
- Core infrastructure
- Basic chat functionality
- GPT-3.5 integration
- Multi-tenant data models

🚧 **Phase 2 In Progress**
- Multimodal support (GPT-4o)
- Channel integrations
- Decision trees
- Enhanced admin UI