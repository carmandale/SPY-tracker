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

## Current Tech Stack & Versions

### Frontend Stack
- **React:** 19.0.0 (latest with concurrent features)
- **TypeScript:** 5.7.2 (strict mode enabled)
- **Vite:** 6.2.0 (build tool and dev server)
- **Tailwind CSS:** 4.0.9 (utility-first styling)
- **UI Library:** shadcn/ui components with Radix primitives
- **Charts:** Recharts 2.15.1 (React chart library)
- **Forms:** React Hook Form 7.54.2 + Zod 3.24.2 validation
- **Icons:** Lucide React 0.477.0
- **Animations:** Framer Motion 12.4.10

### Backend Stack  
- **FastAPI:** 0.111-0.116 (modern Python API framework)
- **Python:** ≥3.10 (required minimum version)
- **SQLAlchemy:** 2.0+ (async ORM with PostgreSQL/SQLite support)
- **Pydantic:** 2.9-2.12 (data validation and settings)
- **OpenAI:** 1.46.0+ (GPT-5 AI predictions)
- **APScheduler:** 3.10+ (automated market data collection)
- **yfinance:** 0.2.65+ (Yahoo Finance market data)
- **PostgreSQL:** psycopg2-binary 2.9+ (production database)

### Development & Testing
- **Package Managers:** yarn (frontend), uv (backend) - CRITICAL
- **Testing:** Vitest 3.2.4 (unit tests), Playwright 1.55.0 (E2E)
- **Linting:** ESLint 9.21.0, Prettier 3.5.3
- **Type Checking:** TypeScript strict mode

### Deployment & Production
- **Platform:** Render.com (Docker deployment)
- **Database:** PostgreSQL managed service on Render
- **Containerization:** Docker with multi-stage build
- **Static Assets:** Served by FastAPI StaticFiles
- **Health Monitoring:** /healthz endpoint with scheduler status

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev` (with Vite proxy to backend)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Production:** Served via Docker on Render.com with static frontend bundled

### Available Scripts & Commands

#### Frontend (yarn)
- `yarn dev` - Start development server with hot reload
- `yarn build` - Build production bundle (outputs to backend/static/)
- `yarn test` - Run Vitest unit tests
- `yarn test:ui` - Run Vitest with UI
- `yarn e2e` - Run Playwright E2E tests
- `yarn lint` - ESLint code checking
- `yarn format` - Prettier code formatting

#### Backend (uv)
- `uv sync` - Install/sync dependencies from uv.lock
- `uv run pytest` - Run Python tests
- `uv run uvicorn app.main:app --reload` - Start development server

#### Production Management
- `./start-production.sh` - Start production server with nohup
- `./monitor.sh` - Check server and scheduler status
- `./restart.sh` - Restart production server
- `docker-compose up postgres` - Start local PostgreSQL container

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
- **Remaining (Nice-to-have):** Service worker registration, backup/restore endpoints
- **PWA Status:** Manifest.json configured with icons, shortcuts, and metadata
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, reasoning, and technical analysis
- **Baseline Models:** Statistical fallback predictions when AI service is unavailable
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance (6 scheduled jobs)
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement (Recharts)
- **Market Data Integration:** Live SPY pricing, market status, volatility data, VIX integration
- **Comprehensive Error Handling:** Custom exception system with user-friendly error messages
- **Health Monitoring:** Health check endpoints for production monitoring
- **Database Flexibility:** Intelligent database detection (PostgreSQL preferred, SQLite fallback)

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (159 lines, modular router system with 10 router modules)
- **API Routers:** @backend/app/routers/ (ai, predictions, market, suggestions, admin, health, etc.)
- **Database:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Frontend:** @src/App.tsx (React 19, mobile-first SPA with 4 main screens)
- **Main Component:** @src/components/generated/SPYTaTrackerApp.tsx (Dashboard, Predict, History, Metrics)
- **UI Components:** @src/components/ (optimized loading skeletons, mobile navigation, version footer)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with RSI, MACD, Bollinger Bands, volume analysis)
- **AI Configuration:** GPT-5 model with reasoning effort, 600 max tokens, 0.2 temperature
- **Baseline Model:** @backend/app/baseline_model.py (statistical fallback predictions)
- **Performance:** @src/utils/performance.ts (memory caching, debouncing, lazy loading, Web Vitals tracking)
- **API Client:** @src/utils/apiClient.ts (centralized API communication with error handling)
- **Test Configuration:** Vitest + Playwright E2E testing setup
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
EOF < /dev/null