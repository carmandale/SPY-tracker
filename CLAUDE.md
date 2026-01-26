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
- **Frontend:** Port 3000 - `yarn dev` (Vite 6.2.0 + React 19.0.0)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Tech Stack Versions (Current)
- **Frontend:** React 19.0.0, TypeScript 5.7.2, Vite 6.2.0, Tailwind CSS 4.0.9
- **Backend:** FastAPI 0.111-0.115, SQLAlchemy 2.0, Pydantic 2.9-2.11, Python >=3.10
- **Testing:** Vitest 3.2.4 (frontend), pytest 8.4.1+ (backend), Playwright 1.55.0 (E2E)
- **AI:** OpenAI GPT-5 (gpt-5 model) with enhanced technical analysis

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
- **Completed:** Phases 0-6 including PostgreSQL migration and health monitoring
- **PWA Status:** ✅ Complete manifest.json with icons, shortcuts, and mobile optimization
- **Remaining (Nice-to-have):** Service worker for offline functionality, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)
- **Health Monitoring:** Critical health check endpoint `/health/critical` for system monitoring

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with advanced technical analysis (RSI, MACD, Bollinger Bands)
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance with error handling
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons with delta targeting
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips, accuracy scoring
- **Historical Analysis:** Complete prediction history with accuracy metrics, trends, and model comparison
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement with Recharts 2.15.1
- **Market Data Integration:** Live SPY pricing, market status, volatility data, VIX correlation
- **Health Monitoring:** Comprehensive system health checks with database integrity monitoring
- **Data Integrity:** Weekend data fixes, future price validation, duplicate prevention
- **Mobile PWA:** Complete progressive web app with manifest, icons, and mobile-first design

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (FastAPI app with 40+ endpoints, static file serving)
- **Database Models:** @backend/app/models.py (SQLAlchemy models for PostgreSQL/SQLite)
- **Frontend Root:** @src/App.tsx (React 19, mobile-optimized SPA)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical analysis)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, web vitals tracking)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Health Monitoring:** @backend/app/routers/health.py (critical health check endpoints)
- **Database Utils:** @backend/app/database_utils.py (intelligent database detection)
- **Configuration:** @backend/app/config.py (settings with intelligent database config)
- **PWA Manifest:** @public/manifest.json (complete PWA configuration)

### Available Scripts
- **Frontend:** `yarn dev`, `yarn build`, `yarn test`, `yarn lint`, `yarn format`, `yarn e2e`
- **Backend:** No npm scripts (uv-managed), use direct uvicorn commands
- **Testing:** Vitest (unit), Playwright (E2E), pytest (backend)
- **Development:** Vite dev server with proxy configuration for backend API
EOF < /dev/null