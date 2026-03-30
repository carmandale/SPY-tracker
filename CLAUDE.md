# SPY TA Tracker - Claude Code Instructions

## Project Overview

**SPY TA Tracker** is a mobile-first options trading assistant that helps experienced traders track their SPY predictions and receive data-driven iron condor/butterfly suggestions. The system combines manual technical analysis tracking with AI-powered predictions using GPT-5.

## Agent OS Documentation

### Product Context
- **Mission & Vision:** @.agent-os/product/mission.md
- **Technical Architecture:** @.agent-os/product/tech-stack.md
- **Development Roadmap:** @.agent-os/product/roadmap.md
- **Decision History:** @.agent-os/product/decisions.md

### Development Standards
- **Code Style:** @~/.agent-os/standards/code-style.md
- **Best Practices:** @~/.agent-os/standards/best-practices.md

### Project Management
- **Active Specs:** All core specifications completed through Phase 6
- **Production Status:** ✅ **LIVE** - Deployed on Render.com with PostgreSQL
- **Production URL:** https://spy-tracker.onrender.com (**ACTIVE**)
- **Spec Planning:** Use `@~/.agent-os/instructions/create-spec.md` for new features
- **Tasks Execution:** Use `@~/.agent-os/instructions/execute-tasks.md` for implementation

## Workflow Instructions

When asked to work on this codebase:

1. **First**, check @.agent-os/product/roadmap.md for current priorities
2. **Then**, follow the appropriate instruction file:
   - For product planning: @~/.agent-os/instructions/plan-product.md
   - For new features: @.agent-os/instructions/create-spec.md
   - For tasks execution: @.agent-os/instructions/execute-tasks.md
3. **Always**, adhere to the standards in the files listed above

## Important Notes

- Product-specific files in `.agent-os/product/` override any global standards
- User's specific instructions override (or amend) instructions found in `.agent-os/specs/...`
- Always adhere to established patterns, code style, and best practices documented above.

## Technical Stack

### Core Technologies
- **Frontend:** React 19.0.0 + TypeScript 5.7.2 + Vite 6.2.0
- **Backend:** FastAPI 0.111+ + Python 3.10+ + SQLAlchemy 2.0
- **Database:** PostgreSQL (production) + SQLite (local fallback)
- **AI System:** OpenAI GPT-5 with technical analysis integration
- **Styling:** Tailwind CSS 4.0.9 + shadcn/ui components
- **Charts:** Recharts 2.15.1 for price visualization
- **Testing:** Vitest (frontend) + pytest (backend) + Playwright (E2E)

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

⚠️ **IMPORTANT**: Always use the package managers specified above for dependency management.

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Database:** PostgreSQL on port 5433 (via Docker) or SQLite fallback

### Database Configuration
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Intelligent Detection:** Automatic fallback to SQLite if PostgreSQL unavailable
- **Environment:** Never commit `.env` files; use `.env.example` as template

### AI System Configuration
- **Model:** GPT-5 (gpt-5-turbo-20241121)
- **API:** OpenAI API with structured JSON responses
- **Features:** Price predictions, confidence scoring, technical analysis reasoning
- **Fallback:** Baseline statistical model when AI service unavailable
- **Lookback:** 5-day market analysis window with technical indicators

### Deployment Status
- **Status:** ✅ **LIVE IN PRODUCTION** on Render.com
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Build System:** Docker with Dockerfile + render.yaml
- **Health Monitoring:** `/healthz` endpoint for service monitoring
- **Completed Phases:** 0-6 including full PostgreSQL migration
- **Remaining (Optional):** PWA configuration, backup/restore endpoints
- **Scheduler:** 6 active jobs running in America/Chicago timezone
  - 8:00 AM CDT: AI predictions generation + pre-market capture
  - 8:30 AM CDT: Market open price capture
  - 12:00 PM CDT: Noon price capture
  - 2:00 PM CDT: 2PM price capture
  - 3:00 PM CDT: Market close capture

### Core Features (Production Ready)

#### Prediction System
- **Manual Entry:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions for Open/Noon/2PM/Close with confidence scoring
- **Technical Analysis:** RSI, MACD, Bollinger Bands, moving averages, support/resistance levels
- **Baseline Fallback:** Statistical model when AI service unavailable
- **Real-time Data:** Live SPY pricing via yfinance with market status detection

#### Options Strategy Engine
- **Iron Condor/Butterfly:** Automated recommendations for 0DTE, 1W, 1M horizons
- **Delta Targeting:** Optimal strike selection based on prediction accuracy
- **Structure Selection:** IC vs IB logic based on bias and historical performance
- **Management Notes:** Profit targets and exit strategies for each structure

#### Performance Analytics
- **Rolling Metrics:** 20-day range hit percentage and median absolute error
- **Accuracy Tracking:** AI vs manual prediction performance comparison
- **Calibration System:** Data-driven suggestions to improve prediction accuracy
- **Historical Analysis:** Complete prediction history with trend analysis

#### User Interface
- **Mobile-First Design:** Optimized for one-handed trading during market hours
- **Real-time Charts:** Predicted bands vs actual price movement visualization
- **Loading States:** Comprehensive skeleton UI with shimmer animations
- **Error Handling:** Graceful degradation with user-friendly error messages

### Project Architecture

#### Key Backend Files
- **Main Application:** `backend/app/main.py` - FastAPI app with 40+ endpoints
- **Database Models:** `backend/app/models.py` - SQLAlchemy models (DailyPrediction, AIPrediction, PriceLog)
- **AI System:** `backend/app/ai_predictor.py` - GPT-5 integration with technical analysis
- **API Routers:** `backend/app/routers/` - Modular endpoint organization
  - `predictions.py` - Manual prediction CRUD
  - `ai.py` - AI prediction endpoints
  - `suggestions.py` - Options strategy recommendations
  - `market.py` - Market data and status
  - `admin.py` - Administrative endpoints
  - `health.py` - Health monitoring
- **Configuration:** `backend/app/config.py` - Environment-based settings
- **Exception Handling:** `backend/app/exceptions.py` - Comprehensive error system
- **Scheduler:** `backend/app/scheduler.py` - APScheduler for market data collection

#### Key Frontend Files
- **Main App:** `src/App.tsx` - React 19 root component
- **Generated Components:** `src/components/generated/` - Core UI screens
  - `SPYTaTrackerApp.tsx` - Main application shell
  - `DashboardScreen.tsx` - Today's predictions and data
  - `PredictScreen.tsx` - Prediction entry form
  - `HistoryScreen.tsx` - Historical predictions
  - `MetricsScreen.tsx` - Performance analytics
- **API Client:** `src/utils/apiClient.ts` - Centralized API communication
- **Performance Utils:** `src/utils/performance.ts` - Caching, debouncing, lazy loading
- **Error Handling:** `src/utils/errorHandling.ts` - Frontend error management

#### Configuration Files
- **Product Requirements:** `SPY-tracker-PRD.md` - Complete product specification
- **Deployment Status:** `DEPLOYMENT_STATUS.md` - Production environment details
- **Dependencies:** `package.json` (frontend), `pyproject.toml` (backend)
- **Build Config:** `vite.config.ts`, `vitest.config.ts`, `Dockerfile`
- **Deployment:** `render.yaml` - Render.com service configuration
### Development Workflow

#### Available Scripts
- **Frontend:**
  - `yarn dev` - Development server with HMR
  - `yarn build` - Production build
  - `yarn test` - Run Vitest unit tests
  - `yarn e2e` - Run Playwright E2E tests
  - `yarn lint` - ESLint code quality checks
  - `yarn format` - Prettier code formatting

- **Backend:**
  - `uv run uvicorn app.main:app --reload --port 8000` - Development server
  - `uv run pytest` - Run backend tests
  - `uv sync` - Sync dependencies

#### Testing Strategy
- **Unit Tests:** Vitest for frontend components and utilities
- **E2E Tests:** Playwright for full user workflow testing
- **Backend Tests:** pytest for API endpoints and business logic
- **Database Tests:** PostgreSQL integration tests with Docker
- **AI Tests:** Mock and integration tests for GPT-5 predictions

#### Environment Setup
1. **Frontend:** `yarn install` to install dependencies
2. **Backend:** `cd backend && uv sync` to set up Python environment
3. **Database:** Docker Compose for PostgreSQL or automatic SQLite fallback
4. **Environment:** Copy `.env.example` to `.env` and configure API keys

#### API Endpoints Overview
The backend exposes 40+ endpoints across multiple routers:
- `/prediction/` - Daily prediction CRUD operations
- `/ai/` - AI prediction generation and retrieval
- `/suggestions/` - Options strategy recommendations
- `/market/` - Market data and status
- `/admin/` - Administrative functions
- `/healthz` - Health monitoring for deployment

#### Key Dependencies
- **Frontend:** React 19, TypeScript 5.7, Vite 6, Tailwind 4, Recharts, Zod
- **Backend:** FastAPI 0.111+, SQLAlchemy 2.0, OpenAI 1.46+, yfinance 0.2.65+
- **Database:** PostgreSQL with psycopg2-binary driver
- **Deployment:** Docker, Render.com with managed PostgreSQL

---

**Last Updated:** March 30, 2026  
**Version:** 2.0.0 - Production deployment with AI predictions
**Status:** ✅ Live and actively trading