# SPY TA Tracker - Claude Code Instructions

## Project Overview

**SPY TA Tracker** is a mobile-first web application for options traders to track SPY predictions and receive AI-powered iron condor/butterfly suggestions. The system combines manual prediction entry, automated market data collection, GPT-5 AI predictions, and comprehensive performance analytics.

### Key Product Features
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and detailed reasoning
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons with P&L tracking
- **Performance Analytics:** 20-day rolling metrics, range hit percentage, calibration tips, accuracy tracking
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data, VIX correlation

### Production Status
- **Status:** LIVE IN PRODUCTION
- **Primary Deployment:** Render.com (Docker-based)
- **Alternative Deployment:** Vercel (configured as backup)
- **Database:** PostgreSQL (production) with SQLite fallback
- **Health Monitoring:** Critical health endpoints with scheduler status
- **Active Jobs:** 6 scheduled jobs running in America/Chicago timezone

## Project Documentation

### Core Documentation
- **Product Requirements:** SPY-tracker-PRD.md
- **Deployment Status:** DEPLOYMENT_STATUS.md
- **Migration Guide:** docs/DATABASE_MIGRATION_GUIDE.md
- **Render Deployment:** docs/RENDER_DEPLOYMENT.md
- **Docker Compose:** docs/DOCKER_COMPOSE_REFERENCE.md

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Tech Stack
**Frontend:**
- React 19.0.0 with TypeScript 5.7.2
- Vite 6.2.0 (build tool)
- Tailwind CSS 4.0.9
- shadcn/ui components
- Recharts for data visualization
- React Hook Form + Zod validation
- Framer Motion for animations

**Backend:**
- FastAPI 0.111+ with Python 3.10+
- SQLAlchemy 2.0+ ORM
- Pydantic 2.9+ for validation
- APScheduler 3.10+ for job scheduling
- OpenAI API (GPT-5) for AI predictions
- yfinance for market data
- PostgreSQL/SQLite database support

**Testing & Development:**
- Vitest (frontend testing)
- Playwright (E2E testing)
- pytest (backend testing)
- ESLint + Prettier (linting/formatting)

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Full Stack:** Use separate terminals for concurrent development

### Database Architecture
- **Production:** PostgreSQL (Render managed service)
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Intelligent Detection:** Automatic database type detection with fallback support
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** Complete PostgreSQL migration with historical data preserved
- **Data Models:** 
  - DailyPrediction (manual/AI predictions with locking)
  - AIPrediction (GPT-5 predictions with confidence intervals)
  - PriceLog (automated price capture)
  - ModelPerformance (accuracy tracking)
  - BaselineModel (statistical fallback models)
- **Environment:** Never commit `.env` files; use `.env.example` as template

### Architecture Overview

**API Structure (40+ endpoints across 9 router modules):**
- `predictions.py` - Core prediction CRUD operations
- `ai.py` - GPT-5 AI predictions and accuracy metrics
- `suggestions.py` - Option structure recommendations with P&L
- `market.py` - Real-time market data and status
- `admin.py` - Database management and backfill operations
- `scheduler.py` - Job scheduling and monitoring
- `health.py` - Critical system health monitoring
- `database_fix.py` - Database integrity and repair utilities
- `version.py` - Version info and changelog

**Scheduler Jobs (America/Chicago timezone):**
- 8:00 AM: AI predictions generation + pre-market capture
- 8:30 AM: Market open price capture
- 12:00 PM: Noon price capture
- 2:00 PM: 2PM price capture
- 3:00 PM: Market close capture + accuracy scoring

**AI Prediction System:**
- GPT-5 integration with technical analysis
- Confidence scoring and prediction intervals
- Market context analysis (RSI, MACD, Bollinger Bands)
- VIX correlation and futures analysis
- Baseline statistical models as fallback
- Historical accuracy tracking and calibration

### Performance & Monitoring
- **Error Handling:** Comprehensive exception system with custom SPYTrackerException types
- **Performance Optimization:** 
  - API response caching with TTL
  - Debounced user interactions
  - Lazy loading and skeleton states
  - Request batching and throttling
- **Health Monitoring:** 
  - `/healthz` endpoint for system health
  - `/health/critical` for comprehensive status
  - Scheduler job monitoring
  - Database connection health
- **Development Tools:**
  - Hot reloading (Vite + FastAPI)
  - API proxy configuration
  - Debug endpoints and admin tools
  - Production build optimization

### Key Project Files

**Backend Core:**
- `backend/app/main.py` - FastAPI application with 40+ endpoints and static file serving
- `backend/app/config.py` - Settings with intelligent database detection
- `backend/app/models.py` - SQLAlchemy models (5 main entities)
- `backend/app/database.py` - Database connection and session management
- `backend/app/ai_predictor.py` - GPT-5 prediction engine with technical analysis
- `backend/app/scheduler.py` - APScheduler job management
- `backend/app/exceptions.py` - Custom exception handling system

**Frontend Core:**
- `src/App.tsx` - React 19 main application component
- `src/components/generated/SPYTaTrackerApp.tsx` - Generated main UI component
- `src/utils/apiClient.ts` - API client with error handling
- `src/utils/performance.ts` - Performance optimization utilities
- `vite.config.ts` - Vite configuration with API proxy

**Configuration & Deployment:**
- `package.json` - Frontend dependencies and scripts
- `backend/pyproject.toml` - Backend dependencies (uv package manager)
- `render.yaml` - Render.com deployment configuration
- `vercel.json` - Vercel deployment configuration
- `Dockerfile` - Production container configuration
- `docker-compose.yml` - Local PostgreSQL development setup

**Documentation & Scripts:**
- `SPY-tracker-PRD.md` - Complete product requirements document
- `DEPLOYMENT_STATUS.md` - Production deployment status and procedures
- `docs/` - Comprehensive deployment and setup guides
- `scripts/` - Health checks, database utilities, and automation tools