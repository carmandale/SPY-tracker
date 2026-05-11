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
- **Frontend:** Port 3000 - `yarn dev` (configured in vite.config.ts)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Tech Stack (Verified)
- **Frontend:** React 19.0.0, TypeScript 5.7.2, Vite 6.2.0, TailwindCSS 4.0.9
- **Backend:** FastAPI 0.111+, Python 3.10+, SQLAlchemy 2.0, Pydantic 2.9+
- **Database:** PostgreSQL (production) / SQLite (development fallback)
- **AI System:** OpenAI GPT-5 with baseline statistical fallback
- **Testing:** Vitest (frontend), pytest (backend), Playwright (E2E)
- **Deployment:** Render.com with Docker, health checks via /healthz endpoint

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Intelligent Detection:** Backend auto-detects PostgreSQL vs SQLite based on environment
- **Connection Pooling:** SQLAlchemy engine with connection pooling for production reliability

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Version:** FastAPI 2.0.0 (backend), React 19.0.0 (frontend)
- **Completed:** Phases 0-6 including PostgreSQL migration (#13 closed)
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Active Jobs:** 6 scheduled jobs running (8AM AI predictions, hourly price captures)
- **Health Monitoring:** /healthz endpoint with scheduler status checks
- **Docker Deployment:** Single container with static file serving via FastAPI
- **Environment:** Production secrets managed via Render dashboard
- **Static Assets:** Frontend built into backend/static/ and served by FastAPI
- **API Proxy:** Vite dev server proxies API calls to localhost:8000 during development

### Testing Configuration
- **Frontend Tests:** Vitest with jsdom environment, React Testing Library
- **Backend Tests:** pytest with fixtures, database test isolation  
- **E2E Tests:** Playwright with production environment verification
- **Test Scripts:** `yarn test` (frontend), `cd backend && pytest` (backend), `yarn e2e` (E2E)
- **Coverage:** Vitest coverage reporting configured

### Development Workflow
1. **Setup:** `yarn install` (frontend), `cd backend && uv venv && uv pip sync requirements.txt` (backend)
2. **Dev Servers:** `yarn dev` (port 3000) + `uvicorn app.main:app --reload --port 8000` (backend)
3. **Database:** Auto-detects PostgreSQL container or falls back to SQLite
4. **Testing:** Run tests with `yarn test` (frontend) and `pytest` (backend)
5. **Linting:** `yarn lint` (ESLint) and `yarn format` (Prettier)
6. **Building:** `yarn build` creates production assets in backend/static/

### AI Prediction System Details
- **Primary Model:** OpenAI GPT-5 with technical analysis prompts (v3.0.0)
- **Fallback System:** Statistical baseline model using moving averages and volatility
- **Technical Indicators:** RSI, MACD, Bollinger Bands, SMA/EMA, volume analysis
- **Market Data:** SPY, VIX, ES futures integration via yfinance
- **Confidence Intervals:** 68% prediction intervals with regime-aware scaling
- **Performance Tracking:** Model accuracy comparison and calibration metrics

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, reasoning, and technical analysis
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance with America/Chicago timezone
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons with delta targeting
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips, accuracy scoring
- **Historical Analysis:** Complete prediction history with accuracy metrics, trends, and model performance comparison
- **Real-time Visualization:** Interactive charts showing predicted bands vs actual price movement with Recharts
- **Market Data Integration:** Live SPY pricing, market status, volatility data, VIX correlation, ES futures tracking
- **Comprehensive Error Handling:** Custom exception system with detailed error responses and logging
- **Advanced Scheduler:** APScheduler with 6 automated jobs running in production (8AM AI predictions, price captures)
- **Mobile-First Design:** React 19 components optimized for mobile trading workflows

### Key Project Files & Architecture
- **Product Requirements:** @SPY-tracker-PRD.md (comprehensive feature specifications)
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (FastAPI app with 40+ endpoints, full error handling)
- **Database Models:** @backend/app/models.py (SQLAlchemy models supporting SQLite/PostgreSQL)
- **Frontend Root:** @src/App.tsx (React 19 app with dark theme, mobile-optimized)
- **AI Prediction System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical analysis)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading, web vitals)
- **Exception System:** @backend/app/exceptions.py (custom exceptions with structured error responses)
- **Configuration:** @backend/app/config.py (intelligent database detection, OpenAI settings)
- **Scheduler:** @backend/app/scheduler.py (APScheduler with market hours automation)
- **API Client:** @src/utils/apiClient.ts (typed API interactions with error handling)
- **Database Utils:** @backend/app/database_utils.py (intelligent PostgreSQL/SQLite switching)
- **Market Data:** @backend/app/providers.py (yfinance integration with caching)
- **Option Suggestions:** @backend/app/suggestions.py (IC/IB algorithm with delta targeting)
- **Component Library:** @src/components/generated/ (auto-generated UI components)
### Important Development Notes

#### Package Manager Enforcement
- **NEVER use npm** - this project uses yarn exclusively due to dependency compatibility
- **NEVER use pip** - this project uses uv for faster, more reliable Python package management
- Lock files (yarn.lock, uv.lock) are committed and must be respected

#### Database Switching Logic
- Backend intelligently detects available databases (PostgreSQL preferred, SQLite fallback)
- Set `DATABASE_URL` environment variable to override detection
- Docker Compose provides local PostgreSQL on port 5433 for development

#### Scheduler Requirements
- All times use America/Chicago timezone (CST/CDT with automatic DST handling)
- 6 scheduled jobs: AI predictions (8AM), price captures (8:30AM, 12PM, 2PM, 3PM), market data refresh
- APScheduler configured with timezone awareness and job persistence

#### Production Deployment
- Render.com deployment via Docker with health checks
- Static files served by FastAPI (not separate CDN)
- OpenAI API key and DATABASE_URL configured as Render secrets
- Auto-deploy enabled from main branch

#### Code Quality Standards
- TypeScript strict mode enabled
- ESLint + Prettier formatting enforced
- React 19 with latest patterns (no legacy class components)
- FastAPI with Pydantic 2.9+ validation
- SQLAlchemy 2.0+ with async patterns where applicable

#### Mobile-First Design
- All components optimized for mobile viewport
- Touch-friendly interfaces with 44px minimum touch targets
- Dark theme default with system preference detection
- Performance optimized for mobile networks (< 200KB initial bundle)

EOF < /dev/null