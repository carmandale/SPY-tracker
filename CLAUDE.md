# SPY TA Tracker - Claude Code Instructions

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
- **Active Specs:** None - all specs completed, including PostgreSQL migration
- **Production URL:** https://spy-tracker.onrender.com (**LIVE**)
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

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Unified Start:** `./start.sh` (recommended - starts both services with proper environment setup)

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **Production URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback with intelligent detection
- **Completed:** Phases 0-6 including PostgreSQL migration, health monitoring, data integrity fixes
- **Recent Updates:** Health monitoring endpoint (#38), data integrity fixes for weekend/future prices
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)
- **Testing:** Vitest (frontend), Playwright (E2E), pytest (backend)

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with comprehensive technical analysis, confidence scoring, and reasoning
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance with CST/CDT timezone handling
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons with delta targeting
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips, accuracy trend analysis
- **Historical Analysis:** Complete prediction history with accuracy metrics, trends, and AI vs human comparison
- **Real-time Visualization:** Interactive charts with Recharts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, VIX data, ES futures, technical indicators (RSI, MACD, Bollinger Bands)
- **Health Monitoring:** Comprehensive health checks, scheduler status, database connectivity monitoring
- **Data Integrity:** Automated fixes for weekend data, future price handling, duplicate prevention

### Key Project Files

#### Architecture & Configuration
- **Product Requirements:** @SPY-tracker-PRD.md (comprehensive product specification)
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Tech Stack:** @.agent-os/product/tech-stack.md (React 19, FastAPI 0.111+, SQLAlchemy 2.0)
- **Roadmap:** @.agent-os/product/roadmap.md (development phases, completed features)
- **Environment Setup:** @.env.example, @backend/.env.example (configuration templates)

#### Backend Core
- **Main API:** @backend/app/main.py (40+ endpoints, static file serving, health checks)
- **Database Models:** @backend/app/models.py (DailyPrediction, AIPrediction, PriceLog with PostgreSQL/SQLite support)
- **Configuration:** @backend/app/config.py (intelligent database detection, environment loading)
- **Database Layer:** @backend/app/database.py (connection management, fallback logic)
- **AI Predictor:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical analysis)
- **Baseline Model:** @backend/app/baseline_model.py (statistical fallback predictions)
- **Scheduler:** @backend/app/scheduler.py (APScheduler with 6 jobs, CST timezone)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)

#### API Routers (backend/app/routers/)
- **Predictions:** predictions.py (daily prediction CRUD)
- **AI:** ai.py (AI prediction endpoints)
- **Market:** market.py (SPY price data, market status)
- **Suggestions:** suggestions.py (iron condor/butterfly recommendations)
- **Health:** health.py (comprehensive health monitoring)
- **Admin:** admin.py (data recovery, analytics)
- **Scheduler:** scheduler.py (job management)
- **Database Fix:** database_fix.py (data integrity endpoints)

#### Frontend Core
- **Main App:** @src/App.tsx (React 19 with theme management)
- **Main Component:** @src/components/generated/SPYTaTrackerApp.tsx (primary UI)
- **Dashboard:** @src/components/generated/DashboardScreen.tsx (today's data)
- **Prediction Form:** @src/components/PredictionForm.tsx (morning entry)
- **AI Integration:** @src/components/DashboardWithAI.tsx (AI prediction display)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **API Client:** @src/utils/apiClient.ts (centralized API communication)
- **Error Handling:** @src/utils/errorHandling.ts (user-friendly error display)

#### Testing & Scripts
- **Vitest Config:** @vitest.config.ts (frontend testing)
- **E2E Tests:** @tests/ (Playwright data integrity tests)
- **Backend Tests:** @backend/tests/ (pytest suite)
- **Scripts:** @scripts/ (health checks, database queries, icon generation)
EOF < /dev/null