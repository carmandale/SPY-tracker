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

## Code Quality & Testing

### Frontend Testing
- **Unit Tests:** Vitest 3.2.4 with React Testing Library 16.3.0
- **E2E Tests:** Playwright 1.55.0 with comprehensive page coverage
- **Linting:** ESLint 9.21 with TypeScript ESLint 8.24.1
- **Formatting:** Prettier 3.5.3 with consistent code style

### Backend Testing
- **Test Framework:** pytest 8.4.1 with comprehensive test coverage
- **Database Tests:** PostgreSQL integration and SQLite fallback testing
- **API Tests:** Full endpoint testing with mocked dependencies
- **Scheduler Tests:** APScheduler job testing and timezone handling

### Performance Optimizations
- **Frontend:** Lazy loading, code splitting, Web Vitals tracking
- **Backend:** Connection pooling, intelligent caching, request debouncing
- **Database:** Optimized queries, proper indexing, connection management

## Deployment Architecture

### Production (Render.com)
- **Platform:** Docker-based deployment on Render
- **Configuration:** `render.yaml`, `Dockerfile`, and `nixpacks.toml`
- **Health Checks:** `/healthz` endpoint with scheduler status
- **Environment:** Managed PostgreSQL with automatic SSL
- **Auto-deploy:** GitHub integration with main branch

### Alternative Platforms
- **Vercel:** Frontend-ready with `vercel.json`
- **Docker:** Full-stack with `docker-compose.yml`
- **Local:** Development scripts (`start.sh`, `monitor.sh`, `restart.sh`)

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Key Commands
- **Frontend Build:** `yarn build` (production static files)
- **Frontend Lint:** `yarn lint` (ESLint 9.21)
- **Frontend Format:** `yarn format` (Prettier 3.5.3)
- **Frontend Test:** `yarn test` (Vitest 3.2.4)
- **E2E Tests:** `yarn e2e` (Playwright 1.55)
- **Backend Test:** `cd backend && uv run pytest`

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment Files:** 
  - Root: `.env.example` (comprehensive template with quick start examples)
  - Backend: `backend/.env.example` (backend-specific configuration)
  - Production: `.env.production` (production overrides)
  - PostgreSQL: `backend/.env.postgres.example` (PostgreSQL-specific)
  - **NEVER** commit actual `.env` files with credentials
- **Intelligent Database Detection:** Automatic fallback from PostgreSQL to SQLite if needed

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and comprehensive reasoning
  - Technical indicators: RSI, MACD, Bollinger Bands, Moving Averages
  - Market microstructure analysis: VWAP, volume patterns, support/resistance
  - Cross-asset analysis: VIX correlation, ES futures, sector rotation signals
  - Behavioral factors: Options expiry effects, sentiment extremes
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement (Recharts)
- **Market Data Integration:** Live SPY pricing, market status, volatility data
- **Baseline Models:** Statistical fallback predictions when AI is unavailable
- **Model Performance:** Comparative accuracy tracking between AI and baseline models
- **Data Integrity:** Automatic duplicate detection and cleanup endpoints
- **Health Monitoring:** Comprehensive system health checks and scheduler status

### Tech Stack Versions (Current)
- **Frontend Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with @vitejs/plugin-react 4.3.4
- **CSS Framework:** Tailwind CSS 4.0.9 with @tailwindcss/vite
- **Backend Framework:** FastAPI 0.111+ with Uvicorn 0.30+
- **Database ORM:** SQLAlchemy 2.0+ with Pydantic 2.9+
- **Scheduler:** APScheduler 3.10+ for market data automation
- **Market Data:** yfinance 0.2.65+ for SPY price feeds
- **AI Integration:** OpenAI 1.46+ for GPT-5 predictions
- **Database:** PostgreSQL (production) + SQLite (fallback)

### API Architecture (50+ Endpoints)
- **Router Files:** 9 specialized routers in `backend/app/routers/`
  - `predictions.py`: Core prediction CRUD operations
  - `ai.py`: GPT-5 prediction system and accuracy metrics
  - `market.py`: Real-time SPY data and market status
  - `suggestions.py`: Iron Condor/Butterfly recommendations
  - `admin.py`: Database management and cleanup
  - `scheduler.py`: Job monitoring and control
  - `health.py`: System health checks
  - `version.py`: Version and system status
  - `database_fix.py`: Data integrity maintenance

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (159 lines, modular router system)
- **Database Models:** @backend/app/models.py (5 models: DailyPrediction, PriceLog, AIPrediction, BaselineModel, ModelPerformance)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical indicators)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading, Web Vitals)
- **Error Handling:** @backend/app/exceptions.py (6 custom exception types with handlers)
- **Configuration:** @backend/app/config.py (intelligent database detection with fallback)
- **Environment Templates:** @.env.example and @backend/.env.example (comprehensive config guides)
EOF < /dev/null