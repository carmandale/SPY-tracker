# SPY TA Tracker - Claude Code Instructions

## Project Overview

**SPY TA Tracker** is a mobile-first web application for tracking SPY options trading predictions with AI-powered insights. It combines manual predictions with GPT-5 automated analysis, providing iron condor/butterfly suggestions for 0DTE, weekly, and monthly options strategies.

### Key Features
- Morning prediction entry (sub-60 second workflow)
- GPT-5 powered AI predictions with confidence scoring
- Automated price capture at market checkpoints
- Option strategy suggestions (Iron Condor/Butterfly)
- Performance tracking with calibration tips
- Real-time visualization and historical analysis

### Production Status
- **Status:** LIVE IN PRODUCTION ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL on Render (managed service)
- **AI System:** GPT-5 with technical analysis
- **Scheduler:** 6 automated jobs (America/Chicago timezone)

## Technical Architecture

### Tech Stack
- **Frontend:** React 19.0.0, TypeScript 5.7.2, Vite 6.2.0, Tailwind CSS 4.0.9
- **Backend:** FastAPI 0.111+, SQLAlchemy 2.0, Python 3.10+, uvicorn
- **Database:** PostgreSQL (production), SQLite (local fallback)
- **AI/ML:** OpenAI GPT-5, yfinance, pandas, numpy
- **Testing:** Vitest (unit), Playwright (E2E), pytest (backend)
- **Deployment:** Render.com, Docker ready

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Quick Start:** Use `./start.sh` script for both services

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and reasoning
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with full error handling)
- **Database Models:** @backend/app/models.py (DailyPrediction, AIPrediction, PriceLog)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators)
- **API Client:** @src/utils/apiClient.ts (caching, retries, type-safe endpoints)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Schemas:** @backend/app/schemas.py (Pydantic), @src/lib/schemas.ts (Zod validation)

## Architecture Overview

### Backend Structure
```
backend/app/
├── main.py              # FastAPI application & static file serving
├── config.py            # Settings with intelligent DB detection
├── models.py            # SQLAlchemy models (Daily, AI, Price logs)
├── schemas.py           # Pydantic request/response models
├── ai_predictor.py      # GPT-5 prediction system
├── baseline_model.py    # Statistical fallback predictions
├── scheduler.py         # APScheduler for market data automation
├── database.py          # DB connection & session management
├── exceptions.py        # Custom exception handling
├── routers/             # API route modules (predictions, AI, market, etc.)
└── providers.py         # Market data providers (yfinance)
```

### Frontend Structure
```
src/
├── App.tsx                      # Main React app entry point
├── components/
│   ├── generated/              # Generated UI components
│   ├── DashboardWithAI.tsx     # Main dashboard with AI integration
│   ├── PredictionForm.tsx      # Morning prediction form
│   └── LoadingSkeletons.tsx    # Loading states
├── utils/
│   ├── apiClient.ts            # Type-safe API client with caching
│   ├── performance.ts          # Performance optimizations
│   └── errorHandling.ts        # Error handling utilities
├── lib/
│   ├── schemas.ts              # Zod validation schemas
│   └── utils.ts                # General utilities
└── hooks/                      # Custom React hooks
```

### AI Prediction System
- **Primary Model:** GPT-5 with comprehensive market analysis
- **Fallback Model:** Statistical baseline using historical data
- **Technical Indicators:** RSI, MACD, Bollinger Bands, volume analysis
- **Market Context:** VIX, ES futures, support/resistance levels
- **Confidence Scoring:** Calibrated 0.0-1.0 with prediction intervals

### Database Schema
- **DailyPrediction:** Core prediction tracking (manual/AI)
- **AIPrediction:** Detailed AI predictions with confidence & reasoning
- **PriceLog:** Automated price capture at market checkpoints
- **ModelPerformance:** Accuracy tracking and calibration metrics

## Development Commands

### Frontend Commands
```bash
yarn dev              # Start dev server (port 3000)
yarn build           # Production build
yarn test            # Run Vitest unit tests
yarn test:ui         # Vitest UI mode
yarn e2e             # Playwright E2E tests
yarn lint            # ESLint checking
yarn format          # Prettier formatting
```

### Backend Commands
```bash
# Setup
uv venv                          # Create virtual environment
source .venv/bin/activate        # Activate venv
uv pip install -r pyproject.toml # Install dependencies

# Development
uvicorn app.main:app --reload --port 8000  # Start dev server
pytest                                      # Run tests

# Database
# Uses intelligent detection: PostgreSQL (prod) or SQLite (local)
# Set DATABASE_URL environment variable to override
```

### Project Management
```bash
./start.sh              # Start both frontend & backend (development)
./start-production.sh   # Start production server
./monitor.sh            # Monitor production status
./restart.sh            # Restart production server
```

## Environment Configuration

### Required Environment Variables
```bash
# Backend (.env or backend/.env)
OPENAI_API_KEY=sk-...           # Required for AI predictions
DATABASE_URL=postgresql://...   # PostgreSQL connection string
API_PORT=8000                   # Backend port (default: 8000)

# Frontend (.env.local)
PORT=3000                       # Frontend port (default: 3000)
VITE_API_URL=/                  # API base URL (default: same-origin)
```

### Database Configuration
- **Production:** PostgreSQL on Render (managed service)
- **Local Development:** 
  - Docker: `./start.sh` auto-starts PostgreSQL container (port 5433)
  - Fallback: SQLite (`spy_tracker.db`)
- **Intelligent Detection:** Automatically selects best available database

## Testing Strategy

### Unit Tests (Vitest)
- Component testing with React Testing Library
- API client testing with mock responses
- Utility function validation
- Run: `yarn test`

### E2E Tests (Playwright) 
- Full user workflows (prediction entry, data viewing)
- Mobile responsiveness testing
- Data integrity verification
- Run: `yarn e2e`

### Backend Tests (pytest)
- API endpoint testing
- Database operation validation
- AI prediction system testing
- Run: `pytest` in backend directory

## Key APIs & Endpoints

### Core Prediction APIs
- `GET /day/{date}` - Get daily prediction data
- `POST /prediction/{date}` - Create/update prediction
- `POST /capture/{date}` - Log price at checkpoint

### AI Prediction APIs
- `GET /ai/predictions/{date}` - Get AI predictions
- `POST /ai/predict/{date}` - Generate new AI prediction
- `GET /ai/accuracy` - AI performance metrics

### Market Data APIs
- `GET /market-data/{symbol}` - Real-time market data
- `GET /market-status` - Market open/closed status
- `GET /suggestions/{date}` - Option strategy suggestions

### Analytics APIs
- `GET /metrics` - Performance metrics (range hit %, MAE)
- `GET /history` - Historical predictions
- `GET /accuracy` - Accuracy analysis

## Production Deployment

### Render.com Configuration
- **Service Type:** Web service
- **Build Command:** `yarn install && yarn build && cd backend && uv pip install -r requirements.txt`
- **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment:** Set OPENAI_API_KEY, DATABASE_URL

### Health Monitoring
- **Health Check:** `/healthz` endpoint
- **Logs:** Available via Render dashboard
- **Database:** PostgreSQL metrics in Render
- **AI System:** OpenAI API usage tracking

## Development Best Practices

### Code Organization
- Follow existing patterns and file structure
- Use TypeScript for type safety
- Implement proper error handling
- Add loading states for async operations
- Cache API responses appropriately

### AI Integration
- Always provide fallback for AI failures
- Include confidence scores with predictions
- Log AI usage and performance
- Handle OpenAI API rate limits gracefully

### Database Operations
- Use SQLAlchemy ORM for type safety
- Handle both PostgreSQL and SQLite
- Implement proper migrations
- Add database connection retry logic

### Performance
- Use React.memo for expensive components
- Implement proper caching strategies
- Optimize API requests with batching
- Monitor bundle size and loading times