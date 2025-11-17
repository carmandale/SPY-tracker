# SPY TA Tracker - Claude Code Instructions

> **Project Status:** LIVE IN PRODUCTION on Render.com with PostgreSQL
> **Last Updated:** November 17, 2025 (Automated)
> **Version:** v2.0.0 with AI-powered predictions and comprehensive health monitoring

## Project Overview

SPY TA Tracker is a **mobile-first options trading assistant** that helps experienced traders:
- Track SPY predictions with AI-powered price forecasting using GPT-5
- Receive data-driven iron condor/butterfly suggestions for 0DTE, weekly, and monthly options
- Monitor real-time performance with 20-day rolling metrics and calibration tips
- Visualize predicted bands vs actual price movement with comprehensive charts

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
- **Active Specs:** None - all core specs completed through Phase 6
- **Production URL:** https://spy-tracker.onrender.com (**LIVE & MONITORED**)
- **Health Monitoring:** /health/critical endpoint with comprehensive data integrity checks
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
- Always adhere to established patterns, code style, and best practices documented above
- The application uses **America/Chicago** timezone for scheduling and **America/New_York** for market data
- All predictions and price data are automatically validated for data integrity

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed in backend/

### Development Servers
- **Frontend:** Port 3000 - `yarn dev` (Vite 6.2.0 with React 19.0.0)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Technology Stack (Current)
- **Frontend:** React 19.0.0, TypeScript 5.7.2, Vite 6.2.0, Tailwind CSS 4.0.9
- **Backend:** FastAPI 0.111+, SQLAlchemy 2.0, Pydantic 2.9+, APScheduler 3.10, OpenAI 1.46+
- **Database:** PostgreSQL (production) / SQLite (local fallback)
- **Testing:** Vitest (frontend), pytest (backend), Playwright (E2E)
- **Icons & UI:** lucide-react, shadcn/ui components, Framer Motion 12.4.10
- **Charts:** Recharts 2.15.1 for prediction visualization
- **Market Data:** yfinance 0.2.65+ for real-time SPY pricing

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE & MONITORED**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking with data integrity validation
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Data Integrity:** Automated validation prevents weekend data and future prices

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com (Docker-based deployment)
- **Database:** PostgreSQL (Render managed service) with intelligent connection fallback
- **Completed:** Phases 0-6 including PostgreSQL migration and health monitoring (Issue #38)
- **Recent Additions:** Critical health monitoring endpoint, data integrity validation, weekend data cleanup
- **Remaining (Nice-to-have):** PWA service worker, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions with GPT-5 verified)
- **Health Monitoring:** /health/critical endpoint provides comprehensive system status

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions (Open/Noon/2PM/Close) with confidence intervals and technical analysis
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance with market holiday detection
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons based on prediction accuracy
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips with accuracy trend analysis
- **Historical Analysis:** Complete prediction history with accuracy metrics, trends, and AI vs manual comparison
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement with Recharts
- **Market Data Integration:** Live SPY pricing, VIX data, ES futures, technical indicators (RSI, MACD, Bollinger Bands)
- **Health Monitoring:** Comprehensive health checks with data integrity validation and alert system
- **Data Integrity:** Automated prevention of weekend data and future price entries
- **Technical Indicators:** RSI, MACD, Bollinger Bands, volume analysis, moving averages for AI predictions

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md (comprehensive feature specifications)
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (50+ endpoints with comprehensive error handling and static file serving)
- **Database Models:** @backend/app/models.py (SQLAlchemy 2.0 with PostgreSQL/SQLite support, AI predictions table)
- **Frontend App:** @src/App.tsx (React 19.0.0, mobile-optimized with loading states)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical indicators and confidence intervals)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading, web vitals tracking)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system with user-friendly messages)
- **Health Monitoring:** @backend/app/routers/health.py (critical health checks and data integrity validation)
- **Configuration:** @backend/app/config.py (intelligent database detection with PostgreSQL/SQLite fallback)
- **Frontend Components:** @src/components/generated/ (SPYTaTrackerApp, Dashboard, History, Metrics, Predict screens)
- **API Client:** @src/utils/apiClient.ts (typed API client with error handling and fallback data)
- **Testing Setup:** @src/test/setup.ts (Vitest configuration with mocks for animations and timezones)

### API Structure (9 Routers)
- **Predictions:** `/prediction/` - Daily prediction CRUD operations
- **AI:** `/ai/` - GPT-5 powered predictions with technical analysis
- **Market:** `/market/` - SPY pricing, VIX, ES futures, market status
- **Suggestions:** `/suggestions/` - Iron condor/butterfly recommendations
- **Admin:** `/admin/` - Administrative operations and data management
- **Scheduler:** `/scheduler/` - Job status and scheduling information
- **Health:** `/health/` - Critical health monitoring and data integrity checks
- **Database Fix:** `/database-fix/` - Data integrity maintenance endpoints
- **Version:** `/version/` - Application version and system information

### Development Commands
- **Frontend Start:** `yarn dev` (Vite development server on port 3000)
- **Frontend Build:** `yarn build` (Production build with asset optimization)
- **Frontend Test:** `yarn test` (Vitest unit tests), `yarn test:ui` (test UI), `yarn e2e` (Playwright E2E)
- **Backend Start:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Backend Test:** `cd backend && pytest` (Python unit tests)
- **Code Quality:** `yarn lint` (ESLint), `yarn format` (Prettier), `yarn format:check`

### PWA Configuration (Partial)
- **Manifest:** @public/manifest.json (PWA manifest with icons and shortcuts)
- **Icons:** @public/icons/ (192x192, 512x512, maskable variants)
- **Missing:** Service worker for offline functionality (nice-to-have feature)

### Environment Configuration
- **Root Directory:** `.env` (primary configuration, never commit)
- **Backend Directory:** `backend/.env` (backend-specific overrides)
- **Frontend:** `PORT=3000` (Vite development server)
- **Database:** `DATABASE_URL` (PostgreSQL connection string or SQLite path)
- **AI Service:** `OPENAI_API_KEY` (GPT-5 API access)
- **Intelligent Detection:** Automatic PostgreSQL/SQLite fallback based on availability
EOF < /dev/null