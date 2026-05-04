# SPY TA Tracker - Claude Code Instructions

## Project Overview
**SPY TA Tracker** is a sophisticated, mobile-first options trading assistant that helps experienced traders systematically track SPY predictions and receive AI-powered iron condor/butterfly suggestions. Built with React 19 and FastAPI, it features GPT-5 powered predictions, real-time market data, and comprehensive performance analytics.

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
- **Active Specs:** None - all core specs completed, including PostgreSQL migration
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

## Technical Stack & Configuration

### Core Technologies
- **Frontend Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with Tailwind CSS 4.0.9
- **Backend Framework:** FastAPI 0.111+ with Python 3.10+
- **Database:** PostgreSQL 16 (production) with SQLite fallback (development)
- **AI/ML:** OpenAI GPT-5 with yfinance market data integration
- **Scheduling:** APScheduler 3.10 for automated market data capture

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers & Commands
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Build:** `yarn build` (creates production static files)
- **Testing:** `yarn test` (Vitest), `yarn test:ui` (UI mode)
- **E2E Testing:** Playwright with `yarn e2e`
- **Linting:** `yarn lint` and `yarn format`

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; no `.env.example` template (check specific router configurations)
- **Docker Development:** Use `docker-compose up db` for local PostgreSQL on port 5433
- **Testing Database:** Separate test database container available via `docker-compose --profile test up`

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)

### Advanced Features & Capabilities

#### Core Trading Features
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, reasoning, and prediction intervals
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance with error handling
- **Option Suggestions:** Intelligent Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Interactive charts showing predicted bands vs actual price movement

#### Advanced AI & Analytics
- **Technical Indicators:** RSI, MACD, Bollinger Bands, Moving Averages, ATR calculations
- **Market Context Analysis:** VIX correlation, ES futures integration, volume analysis
- **Regime Detection:** Trending vs mean-reverting environments, volatility regime shifts
- **Baseline Models:** Statistical fallback predictions with confidence intervals
- **Performance Analytics:** Model accuracy tracking, calibration analysis, error metrics
- **Cross-Asset Analysis:** Multi-ticker support architecture (SPY focused for v1)

#### Infrastructure & Operations
- **Comprehensive Error Handling:** Custom exception system with user-friendly messages
- **Database Intelligence:** Automatic PostgreSQL/SQLite detection and fallback
- **Health Monitoring:** Real-time system health checks and scheduler status
- **Mobile Optimization:** PWA-ready with offline capabilities and touch optimization
- **Performance Optimization:** Caching, debouncing, lazy loading, memory management

### Critical Project Files & Architecture

#### Core Application
- **Main FastAPI App:** `backend/app/main.py` - 40+ endpoints with comprehensive error handling
- **React App:** `src/App.tsx` - Main app component with mobile-first design
- **Database Models:** `backend/app/models.py` - SQLAlchemy models supporting PostgreSQL/SQLite

#### AI & Prediction System
- **AI Predictor:** `backend/app/ai_predictor.py` - GPT-5 integration with technical analysis
- **Baseline Models:** `backend/app/baseline_model.py` - Statistical fallback predictions
- **Market Providers:** `backend/app/providers.py` - yfinance integration and data sourcing
- **Suggestion Engine:** `backend/app/suggestions.py` - Iron Condor/Butterfly algorithms

#### Configuration & Infrastructure
- **App Configuration:** `backend/app/config.py` - Intelligent database detection and settings
- **Database Utils:** `backend/app/database_utils.py` - Connection management and fallback logic
- **Exception Handling:** `backend/app/exceptions.py` - Custom exception system
- **Timezone Utils:** `backend/app/timezone_utils.py` - CST/CDT market hours handling
- **Scheduler:** `backend/app/scheduler.py` - APScheduler for automated data collection

#### Frontend Architecture
- **API Client:** `src/utils/apiClient.ts` - Type-safe API integration with error handling
- **Performance Utils:** `src/utils/performance.ts` - Caching, debouncing, optimization
- **Generated Components:** `src/components/generated/` - Main UI components
- **Mobile Optimization:** `src/components/MobileOptimized.tsx` - Touch and responsive design

#### Documentation & Operations
- **Product Requirements:** `SPY-tracker-PRD.md` - Comprehensive feature specifications
- **Deployment Status:** `DEPLOYMENT_STATUS.md` - Production environment details
- **Database Migration:** `docs/DATABASE_MIGRATION_GUIDE.md` - PostgreSQL setup guide
- **Docker Configuration:** `docker-compose.yml` - Local PostgreSQL setup
- **Production Config:** `render.yaml` - Render.com deployment configuration
## API Structure & Endpoints

### Core Trading APIs
- **Predictions:** `/prediction/{date}` - CRUD operations for daily predictions
- **AI Predictions:** `/ai/predictions/{date}` - GPT-5 powered predictions with confidence intervals
- **Market Data:** `/day/{date}` - Daily market data aggregation
- **Price Capture:** `/capture/{date}` - Manual/automated price logging
- **Suggestions:** `/suggestions/{date}` - Iron Condor/Butterfly recommendations
- **Historical Data:** `/history` - Prediction history with performance metrics
- **Performance Metrics:** `/metrics` - Rolling accuracy and calibration statistics

### System & Administration
- **Health Check:** `/healthz` - System health and scheduler status
- **Version Info:** `/version` - Application version and build information
- **Database Admin:** `/admin/` - Database management and diagnostics
- **Database Fixes:** `/database-fix/` - Data integrity and repair endpoints
- **Market Status:** `/market/status` - Current market hours and trading status
- **Scheduler Status:** `/scheduler/status` - APScheduler job monitoring

## Testing Configuration

### Frontend Testing
- **Framework:** Vitest with jsdom environment
- **Component Testing:** React Testing Library integration
- **E2E Testing:** Playwright for full user journey testing
- **UI Testing:** Dedicated test UI mode with `yarn test:ui`

### Backend Testing
- **Framework:** pytest with comprehensive test coverage
- **Database Testing:** Separate test database with PostgreSQL/SQLite support
- **Integration Testing:** Full API endpoint testing with real database
- **Scheduler Testing:** APScheduler job testing and timezone validation

### Test Commands
```bash
# Frontend
yarn test              # Run Vitest tests
yarn test:ui          # Interactive test UI
yarn test:coverage    # Coverage reports

# Backend (from backend directory)
python -m pytest     # Run all backend tests
python -m pytest -v  # Verbose test output
```

## Development Workflow

### Daily Development
1. **Start Local Database:** `docker-compose up db` (PostgreSQL on port 5433)
2. **Start Backend:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
3. **Start Frontend:** `yarn dev` (serves on port 3000)
4. **Run Tests:** `yarn test` and `python -m pytest` in backend

### Code Quality
- **Linting:** ESLint 9.21 with TypeScript support
- **Formatting:** Prettier 3.5.3 with automatic formatting
- **Type Checking:** TypeScript strict mode with path aliases

### Production Deployment
- **Platform:** Render.com with Docker deployment
- **Database:** Managed PostgreSQL service
- **Static Assets:** Served by FastAPI from `backend/static/`
- **Health Monitoring:** `/healthz` endpoint for service monitoring

## Important Development Notes

### Database Intelligence
The application features intelligent database detection that automatically:
- Attempts PostgreSQL connection first (production preference)
- Falls back to SQLite for development if PostgreSQL unavailable
- Logs database status and configuration at startup
- Supports both connection methods seamlessly

### Scheduler System
- **Timezone:** Operates in America/Chicago (handles CST/CDT transitions)
- **Jobs:** 6 scheduled jobs for market data collection
- **Monitoring:** Real-time job status and health checking
- **Error Handling:** Robust error handling with automatic retries

### AI Prediction System
- **Primary Model:** GPT-5 with sophisticated market analysis prompts
- **Fallback Model:** Statistical baseline with technical indicators
- **Performance Tracking:** Model accuracy comparison and calibration
- **Prompt Versioning:** Tracked for reproducibility and optimization

### Mobile-First Design
- **Touch Optimization:** All interactions optimized for mobile usage
- **PWA Ready:** Service worker and manifest configuration
- **Responsive:** Tailwind CSS with mobile-first breakpoints
- **Performance:** Lazy loading, caching, and optimization utilities

## Key Dependencies

### Frontend Core
- **React:** 19.0.0 (latest with performance improvements)
- **Vite:** 6.2.0 (fast build tool and dev server)
- **Tailwind CSS:** 4.0.9 (utility-first styling)
- **Recharts:** 2.15.1 (trading charts and visualization)
- **Zod:** 3.24.2 (runtime type validation)

### Backend Core
- **FastAPI:** 0.111+ (high-performance Python API framework)
- **SQLAlchemy:** 2.0+ (modern ORM with async support)
- **APScheduler:** 3.10+ (background job scheduling)
- **yfinance:** 0.2.65+ (real-time market data)
- **OpenAI:** 1.46+ (GPT-5 API integration)

### Database & Infrastructure
- **PostgreSQL:** 16 (primary production database)
- **psycopg2-binary:** 2.9+ (PostgreSQL adapter)
- **uvicorn:** 0.30+ (ASGI server with hot reload)