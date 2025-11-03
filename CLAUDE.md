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

### Tech Stack Versions (Verified)
- **Frontend Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with @vitejs/plugin-react 4.3.4
- **CSS Framework:** Tailwind CSS 4.0.9 (@tailwindcss/vite)
- **Backend Framework:** FastAPI 0.111+ with Uvicorn 0.30+
- **Database ORM:** SQLAlchemy 2.0+ with Pydantic 2.9+
- **AI Integration:** OpenAI 1.46.0+ (GPT-5 support)
- **Market Data:** yfinance 0.2.65+ with pandas 2.3.1+
- **Scheduler:** APScheduler 3.10+ for automated jobs
- **Testing:** Vitest 3.2.4 (frontend), pytest 8.4.1+ (backend), Playwright 1.55.0 (E2E)

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev` (Vite dev server with proxy to backend)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; intelligent database detection enabled
- **Database Models:** 5 models (DailyPrediction, PriceLog, AIPrediction, BaselineModel, ModelPerformance)

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)
- **Note:** DEPLOYMENT_STATUS.md shows localhost deployment; Render deployment via render.yaml

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and reasoning
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data
- **Advanced AI System:** 5 database models, baseline model fallback, comprehensive technical analysis
- **Production Health Monitoring:** Health checks, exception handling, scheduler monitoring

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (9 routers, comprehensive static file serving)
- **Database Models:** @backend/app/models.py (5 models: DailyPrediction, PriceLog, AIPrediction, BaselineModel, ModelPerformance)
- **Frontend:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators, prompt v3.0.0)
- **Performance:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **API Schemas:** @backend/app/schemas.py (Pydantic models for API validation)
- **Configuration:** @backend/app/config.py (intelligent database detection, environment management)

### Architecture Overview
- **Project Type:** Monorepo with frontend and backend
- **Frontend Structure:** React SPA with mobile-first design, component-based architecture
- **Backend Structure:** FastAPI with modular routers (9 routers), comprehensive API
- **Database Architecture:** 5 models supporting both SQLite and PostgreSQL
- **AI Pipeline:** GPT-5 predictions with baseline model fallback, technical indicator analysis
- **Scheduler:** 6 automated jobs for market data collection and AI predictions
- **Error Handling:** Custom exception hierarchy with comprehensive error responses
- **Performance:** Caching, debouncing, lazy loading, web vitals tracking

### Development Commands
- **Frontend Development:** `yarn dev` (starts Vite dev server on port 3000)
- **Backend Development:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Frontend Build:** `yarn build` (creates production build in dist/)
- **Frontend Test:** `yarn test` (Vitest), `yarn test:coverage` (with coverage)
- **Backend Test:** `cd backend && pytest` (requires .venv activation)
- **E2E Test:** `yarn e2e` (Playwright tests)
- **Linting:** `yarn lint` (ESLint), `yarn format` (Prettier)

### Environment Configuration
- **Root .env:** Primary environment file (never commit)
- **Backend .env:** Optional backend-specific overrides
- **Intelligent Detection:** Automatic PostgreSQL/SQLite fallback
- **Required Variables:** DATABASE_URL, OPENAI_API_KEY
- **Timezone:** America/Chicago (CST/CDT) for all operations
EOF < /dev/null