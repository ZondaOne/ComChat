# ComChat - Multi-tenant Chatbot SaaS Platform

A modular, multi-tenant SaaS chatbot platform with multimodal interaction capabilities (text, image, decision-tree logic), deployable across web, WhatsApp, and Telegram.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │ Messaging       │
│   (React)       │◄──►│   (FastAPI)     │◄──►│ Adapters        │
│                 │    │                 │    │ (Node.js)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Database      │
                    │   (PostgreSQL)  │
                    └─────────────────┘
```

## Features

- **Multimodal AI**: GPT-4o for image analysis, GPT-3.5-turbo for text
- **Multi-channel**: Web widget, WhatsApp, Telegram
- **Multi-tenant**: Complete data isolation per client
- **Decision Trees**: Visual workflow builder
- **Human Handover**: Configurable fallback policies
- **Developer API**: Webhooks and REST API access

## Quick Start

### Development Setup

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Database Setup**
   ```bash
   docker-compose up -d postgres
   alembic upgrade head
   ```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/comchat

# OpenAI
OPENAI_API_KEY=your_openai_key

# Auth
SECRET_KEY=your_secret_key
ALGORITHM=HS256

# Channels
TELEGRAM_BOT_TOKEN=your_telegram_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
```

## Development Phases

### Phase 1 - Core Infrastructure ✅
- [x] Project structure
- [ ] FastAPI backend with PostgreSQL
- [ ] Basic authentication and tenancy
- [ ] GPT-3.5 text-only pipeline
- [ ] Admin UI for client onboarding

### Phase 2 - Multimodal & Logic
- [ ] GPT-4o integration
- [ ] Image upload and analysis
- [ ] Decision tree engine
- [ ] Webhook configuration

### Phase 3 - Channel Expansion
- [ ] WhatsApp integration
- [ ] Billing pipeline (Stripe)
- [ ] Client dashboard
- [ ] Human handover routing

### Phase 4 - Optimization
- [ ] Auto-summarization
- [ ] Custom prompt editing
- [ ] On-prem deployment
- [ ] Model router optimization

## Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL + Alembic
- **Auth**: Supabase/Firebase Auth
- **Vector DB**: Qdrant for image context
- **Messaging**: Node.js microservices
- **Deployment**: Docker + Railway/Render

## API Documentation

Once running, visit:
- Backend API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details