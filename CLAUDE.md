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
- **Frontend:** Port 3000 - `yarn dev` (Vite 6.2.0 dev server)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Tech Stack Details
#### Frontend Stack
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with @vitejs/plugin-react 4.3.4
- **Styling:** Tailwind CSS 4.0.9 with @tailwindcss/vite plugin
- **UI Components:** shadcn/ui components with Lucide icons
- **Forms:** React Hook Form 7.54.2 with Zod 3.24.2 validation
- **Charts:** Recharts 2.15.1 for data visualization
- **State Management:** React 19 hooks and context
- **Animations:** Framer Motion 12.4.10
- **Testing:** Vitest 3.2.4, Playwright 1.55.0, React Testing Library 16.3.0
- **Linting:** ESLint 9.21.0, Prettier 3.5.3

#### Backend Stack
- **Framework:** FastAPI 0.111-0.115 with Uvicorn 0.30-0.31
- **Database:** SQLAlchemy 2.0+ with psycopg2-binary 2.9+ (PostgreSQL)
- **Validation:** Pydantic 2.9-2.11 with pydantic-settings 2.3-2.5
- **Task Scheduler:** APScheduler 3.10+ for automated jobs
- **Market Data:** yfinance 0.2.65+ for SPY price feeds
- **AI Integration:** OpenAI API 1.46+ (GPT-5 model)
- **Data Processing:** pandas 2.3.1+, numpy 2.2.6+
- **HTTP Client:** httpx 0.27+ for external API calls
- **Testing:** pytest 8.4.1+
- **Environment:** python-dotenv for configuration

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
- **Deployment:** Docker-based deployment via render.yaml configuration
- **Health Monitoring:** /healthz endpoint for uptime monitoring

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and comprehensive reasoning
  - Technical analysis with RSI, MACD, Bollinger Bands, moving averages
  - Market microstructure analysis with VIX correlation and ES futures
  - Regime detection (trending, mean-reverting, volatile) with behavioral factors
  - 68% confidence intervals and calibrated confidence scoring
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement with Recharts
- **Market Data Integration:** Live SPY pricing, market status, volatility data
- **Comprehensive API:** 40+ REST endpoints with full exception handling and validation
- **Database Intelligence:** Automatic PostgreSQL/SQLite detection with fallback mechanisms
- **Mobile-First Design:** React 19 PWA-ready interface optimized for mobile trading

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md (complete PRD with technical specifications)
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with full error handling)
- **Database Models:** @backend/app/models.py (SQLAlchemy 2.0+ with PostgreSQL/SQLite support)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized with loading states)
- **Main Component:** @src/components/generated/SPYTaTrackerApp.tsx (4-screen navigation)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical analysis)
- **Configuration:** @backend/app/config.py (intelligent database detection)
- **API Routes:** @backend/app/routers/ (modular router architecture)
  - predictions.py (core prediction CRUD)
  - ai.py (AI prediction endpoints)
  - suggestions.py (option strategy recommendations)
  - market.py (market data and status)
  - scheduler.py (job management)
  - admin.py (admin operations)
  - health.py (health checks)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Database Utils:** @backend/app/database_utils.py (intelligent DB config resolution)
- **Market Integration:** @backend/app/providers.py (yfinance wrapper with fallbacks)
- **Scheduling:** @backend/app/scheduler.py (APScheduler with America/Chicago timezone)
- **Environment Config:** @.env.example (comprehensive configuration template)
## API Architecture

### Core Endpoints
- **GET /day/{date}** - Retrieve daily prediction and price data
- **POST /prediction/{date}** - Create/update daily predictions
- **POST /capture/{date}** - Manual price capture
- **GET /ai/predictions/{date}** - Generate/retrieve AI predictions
- **GET /suggestions/{date}** - Get option strategy recommendations
- **GET /metrics** - Performance metrics and calibration data
- **GET /history** - Historical predictions with pagination
- **GET /market-status** - Current market status and trading hours
- **GET /scheduler/status** - Active job status and next runs
- **GET /healthz** - Health check endpoint

### Database Schema
- **DailyPrediction:** Manual predictions with performance scoring
- **AIPrediction:** GPT-5 predictions with confidence and intervals
- **PriceLog:** Intraday price captures at key checkpoints
- **ModelPerformance:** Daily accuracy metrics by model type
- **BaselineModel:** Statistical model configurations

## AI Prediction System

### GPT-5 Integration
- **Model:** gpt-5 with reasoning_effort=minimal for cost optimization
- **Context Window:** Comprehensive market analysis including:
  - 5-day price history with technical indicators
  - RSI, MACD, Bollinger Bands, moving averages
  - VIX volatility index and ES futures correlation
  - Support/resistance levels and volume analysis
- **Output:** Structured JSON with:
  - Price predictions for Open/Noon/2PM/Close
  - Confidence scores (0.0-1.0)
  - 68% confidence intervals
  - Expert reasoning (max 100 chars per prediction)
  - Market regime analysis and sentiment

### Fallback System
- **Baseline Model:** Statistical predictions when AI unavailable
- **Emergency Mode:** Simple volatility-based predictions as last resort
- **Error Recovery:** Comprehensive exception handling with graceful degradation

## Deployment Configuration

### Production (Render.com)
- **Service:** Docker-based web service on Render starter plan
- **Region:** Oregon (oregon)
- **Health Check:** /healthz endpoint for uptime monitoring
- **Auto Deploy:** Enabled via render.yaml
- **Environment Variables:** OPENAI_API_KEY, DATABASE_URL (managed secrets)
- **Database:** Managed PostgreSQL service on Render

### Local Development
- **Frontend:** `yarn dev` on port 3000 with Vite proxy to backend
- **Backend:** uvicorn on port 8000 with hot reload
- **Database:** Docker PostgreSQL (port 5433) or SQLite fallback
- **AI:** Requires OPENAI_API_KEY in .env file

### Testing Strategy
- **Frontend:** Vitest unit tests, Playwright E2E tests
- **Backend:** pytest with fixtures for database testing
- **Integration:** Production health checks and data integrity tests
- **Performance:** Load testing with performance monitoring

## Development Workflow

### Environment Setup
1. Copy `.env.example` to `.env` and configure
2. Install dependencies: `yarn install` and `cd backend && uv sync`
3. Start services: `yarn dev` and backend uvicorn command
4. Verify setup: Check localhost:3000 and API health

### Code Quality
- **Frontend:** ESLint + Prettier for consistent formatting
- **Backend:** Python type hints with Pydantic validation
- **Git Hooks:** Pre-commit formatting and linting
- **Documentation:** Comprehensive docstrings and inline comments

### Production Monitoring
- **Health Checks:** Automated uptime monitoring via /healthz
- **Scheduler Status:** Job monitoring via /scheduler/status
- **Error Tracking:** Comprehensive logging with exception details
- **Performance Metrics:** API response times and database query performance

---

**Last Updated:** 2025-01-22 (Comprehensive tech stack audit)
**Version:** 2.1.0 (Live production with full feature set)