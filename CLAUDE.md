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
- **Frontend:** Port 3000 - `yarn dev` (Vite development server)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Quick Start:** Use `bash start.sh` to run both servers simultaneously

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

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and reasoning
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data

### Tech Stack Details
- **Frontend:** React 19.0.0 + TypeScript 5.7.2 + Vite 6.2.0 + Tailwind CSS 4.0.9
- **Backend:** FastAPI 0.111+ + SQLAlchemy 2.0+ + Pydantic 2.9+ + Python 3.10+
- **Database:** PostgreSQL (production) / SQLite (local fallback)
- **AI/ML:** OpenAI GPT-5 + yfinance 0.2.65+ for market data
- **Scheduling:** APScheduler 3.10+ for automated price capture
- **Testing:** Vitest (frontend) + pytest (backend) + Playwright (E2E)
- **UI Components:** shadcn/ui + Recharts + Framer Motion + lucide-react

### Architecture Overview
- **API Routers:** 10 modular routers handling 45+ endpoints
- **Database Models:** DailyPrediction, PriceLog, AIPrediction, BaselineModel, ModelPerformance
- **Scheduler Jobs:** 6 automated jobs (8AM AI predictions, market price captures)
- **Mobile-First:** PWA-ready with responsive design and touch optimization

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (45+ endpoints with comprehensive error handling)
- **Database Models:** @backend/app/models.py (PostgreSQL + SQLite dual support)
- **Frontend App:** @src/App.tsx + @src/components/generated/SPYTaTrackerApp.tsx
- **AI Prediction System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators)
- **Performance Utilities:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Configuration:** @backend/app/config.py (intelligent database detection)
- **Startup Logic:** @backend/app/startup.py (database init, scheduler, AI warmup)
EOF < /dev/null