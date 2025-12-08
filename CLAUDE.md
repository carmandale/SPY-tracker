# SPY TA Tracker - Claude Code Instructions

## Project Overview

SPY TA Tracker is a **live production application** - a mobile-first options trading assistant that helps experienced traders track their SPY predictions and receive AI-powered iron condor/butterfly suggestions. The system features GPT-5 powered price predictions, automated data collection, and comprehensive performance tracking.

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
- **Status:** **LIVE IN PRODUCTION** ✅
- **Production URL:** https://spy-tracker.onrender.com (**ACTIVE**)
- **Database:** PostgreSQL on Render (managed service)
- **Scheduler:** 6 active jobs running (AI predictions + price capture)
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
- **Reason:** Historical decision documented in @.agent-os/product/decisions.md

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Development Proxy:** Vite automatically proxies API calls to backend during dev
- **Production Build:** `yarn build` creates static files served by FastAPI

### Database Policy
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - PostgreSQL migration completed
- **Historical Data:** 40+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Intelligent Detection:** App auto-detects available database (PostgreSQL preferred)
- **Models:** Support both SQLite and PostgreSQL via SQLAlchemy

### Technical Stack

#### Frontend Stack
- **Framework:** React 19.0.0
- **Build Tool:** Vite 6.2.0
- **Language:** TypeScript 5.7.2
- **Styling:** Tailwind CSS 4.0.9 with @tailwindcss/vite plugin
- **UI Components:** shadcn/ui with lucide-react icons
- **Forms:** React Hook Form 7.54.2 + Zod 3.24.2 validation
- **Charts:** Recharts 2.15.1
- **Animations:** Framer Motion 12.4.10
- **State Management:** React hooks and context
- **Testing:** Vitest 3.2.4 + Playwright 1.55.0

#### Backend Stack
- **Framework:** FastAPI 0.111-0.116
- **Server:** Uvicorn 0.30-0.32
- **Language:** Python 3.10+
- **Database ORM:** SQLAlchemy 2.0-2.1
- **Validation:** Pydantic 2.9-2.12
- **Scheduler:** APScheduler 3.10-4.0
- **Market Data:** yfinance 0.2.65-0.3
- **AI Integration:** OpenAI 1.46.0-2.0 (GPT-5)
- **Data Processing:** pandas 2.3.1+, numpy 2.2.6+
- **Database:** PostgreSQL (psycopg2-binary 2.9-2.10)
- **Testing:** pytest 8.4.1+

### Production Environment
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Deployment:** Docker-based via Dockerfile + render.yaml
- **Scheduler:** 6 active jobs (America/Chicago timezone)
  - 8:00 AM: AI predictions + pre-market capture
  - 8:30 AM: Market open capture
  - 12:00 PM: Noon price capture
  - 2:00 PM: 2PM price capture
  - 3:00 PM: Market close capture + EOD processing
- **Health Check:** `/healthz` endpoint
- **Static Files:** Served by FastAPI from `/backend/static/`

### Key Features (All Working in Production)

#### Core Prediction System
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions (Open/Noon/2PM/Close) with confidence scoring and detailed reasoning
- **Baseline Model:** Statistical fallback predictions when AI unavailable
- **Prediction Locking:** Prevents modification of finalized predictions
- **Source Tracking:** Distinguishes between AI-generated and manual predictions

#### Data Collection & Processing
- **Automated Price Capture:** Scheduled collection of SPY prices via yfinance
- **Market Status Detection:** Holiday and half-day handling
- **Real-time Data:** Pre-market, open, noon, 2PM, and close price logging
- **Technical Indicators:** RSI, MACD, Bollinger Bands, moving averages, volume analysis
- **VIX & Futures:** Cross-asset analysis for market context

#### Options Strategy Engine
- **Iron Condor/Butterfly:** Automated structure recommendations
- **Multi-horizon Analysis:** 0DTE, 1W, 1M strategies
- **Delta Targeting:** Intelligent strike selection based on bias and accuracy
- **Risk Management:** IVR filters and position sizing
- **Management Notes:** Profit targets and exit strategies

#### Performance Analytics
- **20-day Rolling Metrics:** Range hit percentage, median absolute error
- **Calibration System:** Data-driven accuracy improvement suggestions
- **Historical Analysis:** Complete prediction history with searchable interface
- **Model Performance:** AI vs baseline comparison and tracking
- **Accuracy Scoring:** Automatic prediction vs actual outcome analysis

#### User Interface
- **Mobile-first Design:** Optimized for trading on-the-go
- **Real-time Charts:** Predicted bands vs actual price movement
- **Loading States:** Comprehensive skeleton UI with shimmer animations
- **Error Handling:** User-friendly error messages and fallback states
- **Performance Optimization:** Caching, debouncing, lazy loading
- **PWA Ready:** Manifest and icons configured (service worker pending)

### Key Project Files & Architecture

#### Core Application Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Main Backend:** @backend/app/main.py (FastAPI app with 40+ endpoints)
- **Database Models:** @backend/app/models.py (SQLAlchemy models for SQLite/PostgreSQL)
- **Frontend App:** @src/App.tsx (React 19, dark theme, mobile-optimized)
- **Main Component:** @src/components/generated/SPYTaTrackerApp.tsx

#### Backend API Structure
- **Configuration:** @backend/app/config.py (settings with intelligent DB detection)
- **Database:** @backend/app/database.py (connection handling + migrations)
- **Models:** @backend/app/models.py (DailyPrediction, PriceLog, AIPrediction, ModelPerformance)
- **Routers:** @backend/app/routers/ (modular API endpoints)
  - `predictions.py` - Core prediction CRUD
  - `ai.py` - AI prediction endpoints
  - `market.py` - Market data and status
  - `suggestions.py` - Options strategy recommendations
  - `admin.py` - Admin utilities
  - `health.py` - Health checks
  - `scheduler.py` - Job management
  - `database_fix.py` - Data integrity tools
  - `version.py` - System information
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical analysis)
- **Scheduler:** @backend/app/scheduler.py (APScheduler with timezone handling)
- **Exception Handling:** @backend/app/exceptions.py (comprehensive error system)
- **Market Data:** @backend/app/providers.py (yfinance integration)
- **Baseline Model:** @backend/app/baseline_model.py (statistical fallback)

#### Frontend Structure
- **Main App:** @src/components/generated/SPYTaTrackerApp.tsx
- **Screens:** @src/components/generated/ (Dashboard, Predict, History, Metrics, PLChart)
- **Components:** @src/components/ (reusable UI components)
- **API Client:** @src/utils/apiClient.ts (HTTP client with error handling)
- **Performance:** @src/utils/performance.ts (optimization utilities)
- **Schemas:** @src/lib/schemas.ts (Zod validation schemas)
- **Utils:** @src/lib/utils.ts (shared utilities)

#### Configuration & Deployment
- **Frontend Build:** @vite.config.ts (Vite + Tailwind CSS 4)
- **Backend Deps:** @backend/pyproject.toml (uv package management)
- **Frontend Deps:** @package.json (yarn package management)
- **Docker:** @Dockerfile (production container)
- **Render:** @render.yaml (cloud deployment config)
- **Database:** @docker-compose.yml (local PostgreSQL setup)

#### Testing
- **Frontend Tests:** @vitest.config.ts (Vitest + jsdom)
- **E2E Tests:** @test-*.spec.ts (Playwright)
- **Backend Tests:** @backend/tests/ (pytest)

#### Scripts & Tools
- **Production:** @start-production.sh, @monitor.sh, @restart.sh
- **Development:** @start.sh
- **Health Checks:** @scripts/health-check.sh
- **Database Tools:** @scripts/verify-*.sh, @fix_*.py

---

## Development Workflow

### Starting Development
1. **Backend:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
2. **Frontend:** `yarn dev` (runs on port 3000 with API proxy)
3. **Database:** Use Docker Compose for PostgreSQL or fallback to SQLite

### Building for Production
1. **Frontend:** `yarn build` (creates static files)
2. **Backend:** Serves static files + API endpoints
3. **Deploy:** Push to trigger Render deployment

### Package Management Commands
- **Frontend:** `yarn install`, `yarn add <package>`, `yarn dev`, `yarn build`
- **Backend:** `uv add <package>`, `uv sync`, `uv run <command>`

### Testing
- **Frontend Unit:** `yarn test` (Vitest)
- **E2E:** `yarn e2e` (Playwright)
- **Backend:** `cd backend && uv run pytest`

### Environment Variables
- **Required:** `OPENAI_API_KEY`, `DATABASE_URL`
- **Optional:** See @backend/app/config.py for all settings
- **Never commit .env files** - use templates in documentation

---

**⚠️ CRITICAL:** This is a live production application with real trading data. Always test changes thoroughly and follow the established patterns for database operations, API endpoints, and user interface components.