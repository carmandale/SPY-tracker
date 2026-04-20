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

### Database Configuration

#### Intelligent Database Detection
The application uses intelligent database detection (configurable via environment):
- **Production:** PostgreSQL automatically detected and used
- **Local Development:** PostgreSQL via Docker (port 5433) preferred, SQLite fallback
- **Configuration:** `DATABASE_URL` environment variable
- **Detection Logic:** @backend/app/database_utils.py
- **Flags:** `use_intelligent_database_detection`, `fallback_to_sqlite`

#### Database Models
- `DailyPrediction` - User and AI predictions with bias, volatility context
- `PriceLog` - Intraday price captures (open, noon, 2PM, close)
- `AIPrediction` - AI-generated predictions with confidence intervals
- `BaselineModel` - Statistical model configurations
- `ModelPerformance` - Daily performance metrics tracking

## Important Notes

- Product-specific files in `.agent-os/product/` override any global standards
- User's specific instructions override (or amend) instructions found in `.agent-os/specs/...`
- Always adhere to established patterns, code style, and best practices documented above.
- **Never commit `.env` files** - use `.env.example` as template
- **Package managers are enforced** - yarn for frontend, uv for backend (do not change)
- **Testing is automated** - Playwright E2E tests run against production API

## Tech Stack Details

### Frontend Stack
- **React:** 19.0.0 (latest with new features)
- **TypeScript:** 5.7.2 
- **Vite:** 6.2.0 (build tool and dev server)
- **Tailwind CSS:** 4.0.9 (@tailwindcss/vite plugin)
- **UI Components:** shadcn/ui with Radix primitives
- **Charts:** Recharts 2.15.1
- **Forms:** React Hook Form 7.54.2 with Zod 3.24.2 validation
- **Animation:** Framer Motion 12.4.10
- **Icons:** Lucide React 0.477.0
- **Testing:** Vitest 3.2.4 with jsdom environment

### Backend Stack  
- **FastAPI:** 0.111-0.116 (async web framework)
- **Uvicorn:** 0.30-0.32 (ASGI server)
- **SQLAlchemy:** 2.0+ (ORM with PostgreSQL/SQLite support)
- **Pydantic:** 2.9-2.12 (data validation)
- **APScheduler:** 3.10+ (job scheduling for market hours)
- **OpenAI:** 1.46.0+ (GPT-5 API integration)
- **yfinance:** 0.2.65+ (market data)
- **pandas/numpy:** Data analysis for technical indicators
- **psycopg2-binary:** PostgreSQL adapter
- **Testing:** pytest 8.4.1+

### Testing Infrastructure
- **Unit Tests:** Vitest (frontend), pytest (backend)
- **E2E Tests:** Playwright with production API tests
- **Data Integrity:** Automated tests for weekend data validation
- **API Testing:** HTTP endpoint validation
- **Test Files:** `/tests/*.spec.ts`, `/backend/tests/test_*.py`

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev` (with API proxy to backend)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Production:** Single FastAPI server serves both API and static frontend files
- **Proxy Routes:** Frontend dev server proxies `/day`, `/ai`, `/metrics`, `/suggestions`, `/market-status`, `/accuracy` to backend

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable  
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Docker Compose:** Includes PostgreSQL setup for local development
- **Port:** PostgreSQL runs on 5433 to avoid conflicts with system PostgreSQL

### Project Directory Structure

```
SPY-tracker/
├── backend/                    # FastAPI backend application
│   ├── app/                    # Main application package
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Settings and environment variables
│   │   ├── models.py           # SQLAlchemy database models
│   │   ├── ai_predictor.py     # GPT-5 prediction engine
│   │   ├── baseline_model.py   # Statistical fallback predictions
│   │   ├── scheduler.py        # APScheduler job definitions
│   │   ├── database_utils.py   # Smart database detection
│   │   ├── exceptions.py       # Custom exception handlers
│   │   ├── providers.py        # Market data providers (yfinance)
│   │   └── routers/            # FastAPI route modules
│   │       ├── predictions.py   # Prediction CRUD endpoints
│   │       ├── ai.py            # AI prediction endpoints
│   │       ├── market.py        # Market data endpoints
│   │       ├── suggestions.py   # Option strategy suggestions
│   │       ├── admin.py         # Admin/debug endpoints
│   │       ├── health.py        # Health check endpoints
│   │       └── scheduler.py     # Scheduler status endpoints
│   ├── static/                 # Production frontend build
│   ├── tests/                  # Backend test suite (pytest)
│   ├── pyproject.toml          # Python dependencies (uv)
│   └── uv.lock                 # Locked dependency versions
├── src/                        # React frontend source
│   ├── components/             # React components
│   │   └── generated/          # Generated UI components
│   │       ├── SPYTaTrackerApp.tsx # Main app component
│   │       ├── DashboardScreen.tsx # Dashboard view
│   │       ├── PredictScreen.tsx   # Prediction entry
│   │       ├── HistoryScreen.tsx   # Historical data
│   │       └── MetricsScreen.tsx   # Performance metrics
│   ├── utils/                  # Frontend utilities
│   │   ├── apiClient.ts        # API client with error handling
│   │   └── performance.ts      # Performance optimization utils
│   └── App.tsx                 # Root React component
├── tests/                      # E2E test suite (Playwright)
│   ├── test-data-integrity.spec.ts
│   └── verify-other-dates.spec.ts
├── .agent-os/                  # Agent OS documentation
│   └── product/                # Product specifications
├── docs/                       # Additional documentation
├── scripts/                    # Utility scripts
├── package.json                # Frontend dependencies (yarn)
├── yarn.lock                   # Locked frontend dependencies
├── vite.config.ts              # Vite configuration
├── vitest.config.ts            # Vitest test configuration
├── docker-compose.yml          # PostgreSQL for local dev
└── CLAUDE.md                   # This file
```

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **Production URL:** https://spy-tracker.onrender.com
- **Local Development URL:** http://localhost:8000 (serves both API and frontend)
- **Database:** PostgreSQL (Render managed service for production)
- **Completed:** Phases 0-6 including PostgreSQL migration (Issue #13 closed)
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)
- **AI Model:** GPT-5 (gpt-5-turbo-20241121) with baseline fallback

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 (gpt-5-turbo-20241121) powered price predictions with confidence scoring, reasoning, and statistical baseline fallback
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance with timezone handling
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons with delta targeting
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips, accuracy trends
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data, VIX tracking
- **Technical Analysis:** RSI, MACD, Bollinger Bands, Moving Averages, ATR, Volume analysis
- **Baseline Models:** Statistical fallback predictions when AI is unavailable
- **Error Handling:** Comprehensive exception system with user-friendly error messages
- **Mobile Optimization:** Touch-friendly interface optimized for one-handed use
- **PWA Ready:** Service worker and manifest.json configured (icons in place)
- **Health Monitoring:** Automated health checks and system status endpoints

### Development Commands

#### Frontend (yarn)
- `yarn dev` - Start development server (port 3000)
- `yarn build` - Production build
- `yarn preview` - Preview production build
- `yarn test` - Run Vitest unit tests
- `yarn test:ui` - Run tests with UI
- `yarn lint` - ESLint code checking
- `yarn format` - Prettier code formatting
- `yarn e2e` - Run Playwright E2E tests

#### Backend (uv)
- `cd backend && source .venv/bin/activate` - Activate virtual environment
- `uvicorn app.main:app --reload --port 8000` - Start development server
- `uv sync` - Install/update dependencies
- `pytest` - Run backend tests
- `python -m app.scheduler` - Test scheduler jobs

#### Production
- `./start-production.sh` - Start production server
- `./monitor.sh` - Monitor server status  
- `./restart.sh` - Restart server

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with full error handling)
- **Database Models:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Database Utils:** @backend/app/database_utils.py (intelligent database detection)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **Main Dashboard:** @src/components/generated/SPYTaTrackerApp.tsx
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical indicators)
- **Baseline Model:** @backend/app/baseline_model.py (statistical fallback predictions)
- **Test Suite:** @tests/ (Playwright E2E tests for data integrity)
- **Frontend Config:** @vite.config.ts (dev proxy, build settings, path aliases)
- **Backend Config:** @backend/app/config.py (environment variables, database detection)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Market Data:** @backend/app/providers.py (yfinance integration with caching)
- **Scheduler:** @backend/app/scheduler.py (timezone-aware job scheduling)
EOF < /dev/null