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
- **Frontend:** Port 3000 - `yarn dev` (Vite 6.2.0)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Testing Framework
- **Frontend Testing:** Vitest 3.2.4 with React Testing Library
- **E2E Testing:** Playwright 1.55.0 for end-to-end tests
- **Backend Testing:** pytest (configured in pyproject.toml)
- **Test Commands:** `yarn test` (frontend), `yarn e2e` (E2E), `uv run pytest` (backend)

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Driver:** psycopg2-binary for PostgreSQL connections

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Version:** 2.1.0 (as of latest changelog)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **PWA Status:** Manifest.json configured, service worker not yet implemented
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)
- **Health Monitoring:** Available at `/healthz` endpoint

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, reasoning, and technical analysis
- **Automated Data Collection:** Scheduled capture of Pre-market/Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons with P&L calculations
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips, MAE tracking
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement using Recharts
- **Market Data Integration:** Live SPY pricing, VIX data, ES futures, market status, volatility data
- **Mobile Optimization:** Responsive design with touch-optimized UI, loading skeletons
- **Version Tracking:** Next prediction countdown, deployment version display, changelog API
- **Error Handling:** Comprehensive exception system with structured error responses

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Project Status:** @PROJECT_REALITY_CHECK.md (current operational status)
- **Changelog:** @CHANGELOG.md (version history and feature releases)
- **Backend API:** @backend/app/main.py (40+ endpoints across 10 router modules)
- **Database Models:** @backend/app/models.py (PostgreSQL-optimized with SQLAlchemy 2.0)
- **Frontend App:** @src/App.tsx (React 19.0.0, mobile-first design)
- **Main Component:** @src/components/generated/SPYTaTrackerApp.tsx (core application)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical analysis)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Configuration:** @backend/app/config.py (Pydantic settings management)
- **PWA Manifest:** @public/manifest.json (Progressive Web App configuration)

### Tech Stack Details
- **Frontend Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with hot module replacement
- **CSS Framework:** Tailwind CSS 4.0.9 with custom design tokens
- **UI Components:** shadcn/ui components with Radix UI primitives
- **Charts:** Recharts 2.15.1 for data visualization
- **Animation:** Framer Motion 12.4.10 for smooth transitions
- **Backend Framework:** FastAPI 0.111+ with Uvicorn ASGI server
- **Database ORM:** SQLAlchemy 2.0 with Pydantic 2.9+ for validation
- **Task Scheduling:** APScheduler 3.10 for market data collection
- **AI Integration:** OpenAI Python client 1.46+ for GPT-5 predictions
- **Market Data:** yfinance 0.2.65+ for SPY pricing and technical indicators
- **HTTP Client:** httpx 0.27 for async requests

### API Endpoints Structure
The FastAPI application provides 40+ endpoints across 10 router modules:
- **Predictions Router** (`/prediction`, `/day/{date}`): Core prediction CRUD operations
- **AI Router** (`/ai/*`): AI prediction generation and simulation endpoints  
- **Market Router** (`/market/*`): Market data, status, and pricing endpoints
- **Suggestions Router** (`/suggestions/*`): Option strategy recommendations and P&L
- **Admin Router** (`/admin/*`): Database management and maintenance operations
- **Health Router** (`/healthz`, `/health/*`): System health and monitoring
- **Scheduler Router** (`/scheduler/*`): Job status and next prediction timing
- **Version Router** (`/api/version`): Deployment and build information
- **Database Fix Router** (`/database-fix/*`): Weekend data repair utilities

### Scheduler Jobs (America/Chicago timezone)
Six automated jobs run daily during market hours:
- **8:00 AM CST:** AI prediction generation + pre-market price capture
- **8:30 AM CST:** Market open price capture
- **12:00 PM CST:** Noon price checkpoint
- **2:00 PM CST:** Afternoon price checkpoint  
- **3:00 PM CST:** Market close price capture + daily calculations
- **Weekend/Holiday Detection:** Smart scheduling with market calendar integration

### AI System Architecture
- **Primary Model:** GPT-5 (`gpt-5-turbo-20241121`) with reasoning effort configuration
- **Fallback System:** Statistical baseline model for service continuity
- **Technical Indicators:** RSI, MACD, Bollinger Bands, volume analysis, support/resistance
- **Market Context:** VIX data, ES futures, cross-asset analysis for regime detection
- **Confidence Intervals:** 68% prediction bands with dynamic width based on volatility
- **Performance Tracking:** Real-time accuracy metrics and model comparison

### Production Deployment Notes
- **Platform:** Render.com with Docker containers
- **Static Assets:** Served by FastAPI backend (791KB production bundle)
- **Database Connection:** PostgreSQL with connection pooling via SQLAlchemy
- **Environment Variables:** OPENAI_API_KEY, DATABASE_URL managed via Render dashboard
- **Health Checks:** Automatic monitoring via `/healthz` endpoint
- **Process Management:** Single worker deployment suitable for current load

### Development Workflow
1. **Frontend Development:** `yarn dev` starts Vite dev server with API proxy to localhost:8000
2. **Backend Development:** Virtual environment activation required: `cd backend && source .venv/bin/activate`
3. **Database Setup:** Docker Compose provides PostgreSQL container on port 5433
4. **Testing:** Run `yarn test` for frontend, `yarn e2e` for Playwright tests
5. **Building:** `yarn build` creates production static assets in `backend/static/`
6. **Linting:** `yarn lint` and `yarn format` for code quality