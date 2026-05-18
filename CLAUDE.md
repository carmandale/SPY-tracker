# SPY TA Tracker - Claude Code Instructions

## Project Overview

SPY TA Tracker is a production-ready, mobile-first options trading assistant that helps experienced traders track their SPY predictions and receive AI-powered option strategy suggestions. The application combines React 19 frontend with FastAPI backend, GPT-5 AI predictions, and comprehensive market data integration.

### Current Status
- **Production URL:** https://spy-tracker.onrender.com (**LIVE**)
- **Database:** PostgreSQL on Render (managed service)
- **AI System:** GPT-5 powered predictions with confidence scoring
- **Data Pipeline:** Automated price collection via yfinance
- **Deployment:** Docker-based deployment on Render.com
- **Testing:** Vitest (frontend), pytest (backend), Playwright (E2E)

## Architecture & Tech Stack

### Frontend (React 19 + Vite)
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with hot reload
- **CSS:** Tailwind CSS 4.0.9 with dark mode support
- **UI Components:** shadcn/ui with Framer Motion animations
- **Forms:** React Hook Form with Zod validation
- **Charts:** Recharts for market data visualization
- **Testing:** Vitest 3.2.4 with jsdom environment

### Backend (FastAPI + Python)
- **Framework:** FastAPI 0.111+ with Uvicorn 0.30+
- **Database:** SQLAlchemy 2.0 with PostgreSQL/SQLite support
- **Scheduler:** APScheduler 3.10 for automated market data collection
- **AI Integration:** OpenAI GPT-5 API for price predictions
- **Market Data:** yfinance 0.2.65+ for SPY pricing
- **Environment:** Pydantic Settings with python-dotenv
- **Testing:** pytest with PostgreSQL test containers

### Deployment & DevOps
- **Containerization:** Docker multi-stage build
- **Hosting:** Render.com with PostgreSQL managed database
- **Frontend Build:** Static files served by FastAPI
- **Health Checks:** Comprehensive monitoring at /healthz
- **E2E Testing:** Playwright for production validation

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Available Scripts
- **Frontend:** `yarn dev`, `yarn build`, `yarn test`, `yarn lint`, `yarn format`
- **Backend:** Use `uv` for all Python package management
- **E2E Testing:** `yarn e2e` (Playwright tests)
- **Production:** `./start-production.sh` (with monitoring scripts)

### Database Configuration
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - PostgreSQL migration successful
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Models:** DailyPrediction, AIPrediction, PriceLog with comprehensive schemas
- **Intelligence:** Automatic database detection with fallback capabilities
- **Environment:** Never commit `.env` files; use `.env.example` as template

### Production Status
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Monitoring:** Critical health checks at `/health/critical`
- **AI System:** GPT-5 predictions running daily at 8AM CST
- **Scheduler:** 6 active jobs (pre-market, open, noon, 2PM, close captures)
- **Data Integrity:** Automated validation with weekend/future price checks
- **Performance:** Sub-2s load times with caching and optimization

### Core Features (Production Ready)

#### AI Prediction System
- **GPT-5 Integration:** Advanced price predictions for Open/Noon/2PM/Close
- **Technical Analysis:** RSI, MACD, Bollinger Bands, moving averages
- **Confidence Intervals:** 68% prediction bands with calibrated accuracy
- **Baseline Fallback:** Statistical models when AI unavailable
- **Market Context:** VIX, ES futures, volume analysis integration

#### User Interface
- **Mobile-First Design:** Optimized for one-handed phone operation
- **Prediction Entry:** Sub-60s morning ritual with bias/volatility context
- **Real-time Charts:** Predicted bands vs actual price movement
- **Performance Metrics:** 20-day rolling accuracy with calibration tips
- **Historical Analysis:** Complete prediction history and trends

#### Option Strategy Engine
- **Iron Condor/Butterfly:** Automated structure selection based on bias
- **Multi-Horizon:** 0DTE, 1-week, 1-month recommendations
- **Delta Targeting:** Risk-adjusted strike selection
- **P&L Tracking:** Expected move calculations and profit targets

#### Data Pipeline
- **Automated Collection:** Scheduled price capture at market checkpoints
- **Market Data:** Live SPY pricing via yfinance with error handling
- **Data Validation:** Weekend/future price detection and integrity checks
- **Timezone Handling:** America/Chicago scheduler with ET market times

### Key Project Files

#### Core Application
- **Backend API:** `backend/app/main.py` (40+ endpoints, comprehensive error handling)
- **Database Models:** `backend/app/models.py` (PostgreSQL/SQLite dual support)
- **Frontend App:** `src/App.tsx` (React 19, mobile-optimized)
- **API Configuration:** `backend/app/config.py` (intelligent database detection)

#### AI & Market Data
- **AI Predictions:** `backend/app/ai_predictor.py` (GPT-5 with technical indicators)
- **Market Providers:** `backend/app/providers.py` (yfinance integration)
- **Baseline Models:** `backend/app/baseline_model.py` (statistical fallbacks)
- **Scheduler:** `backend/app/scheduler.py` (APScheduler with timezone handling)

#### Infrastructure
- **Deployment:** `Dockerfile` (multi-stage build), `render.yaml` (Render config)
- **Health Monitoring:** `backend/app/routers/health.py` (critical system checks)
- **Error Handling:** `backend/app/exceptions.py` (comprehensive exception system)
- **Performance Utils:** `src/utils/performance.ts` (caching, debouncing, optimization)

#### Testing & Validation
- **Backend Tests:** `backend/tests/` (pytest with PostgreSQL containers)
- **Frontend Tests:** `src/test/` (Vitest with React Testing Library)
- **E2E Tests:** `tests/*.spec.ts` (Playwright production validation)
- **Integration:** `test-production.spec.ts` (live system verification)

#### Documentation
- **Product Requirements:** `SPY-tracker-PRD.md` (comprehensive specification)
- **Production Status:** `DEPLOYMENT_STATUS.md` (deployment details)
- **README:** `README.md` (quick start and setup instructions)
EOF < /dev/null