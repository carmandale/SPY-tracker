# SPY TA Tracker - Claude Code Instructions

## Agent OS Documentation

### Product Context
- **Mission & Vision:** @.agent-os/product/mission.md
- **Technical Architecture:** @.agent-os/product/tech-stack.md
- **Development Roadmap:** @.agent-os/product/roadmap.md
- **Decision History:** @.agent-os/product/decisions.md

### Development Standards
- Follow established patterns in the codebase
- Mobile-first design principles
- Error handling with comprehensive exception system
- Performance optimization (caching, debouncing, lazy loading)

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
- **Status:** ✅ Both lock files verified and present

### Development Servers
- **Frontend:** Port 3000 - `yarn dev` (Vite 6.2.0 dev server)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Proxy:** Frontend proxies API calls to backend automatically

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
- **Advanced Analytics:** RSI, MACD, Bollinger Bands, volume analysis
- **Health Monitoring:** Comprehensive health checks and error handling

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (150+ endpoints across 9 routers with full error handling)
- **Database Models:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Frontend:** @src/App.tsx (React 19.0.0, mobile-optimized, loading states)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators)
- **Performance:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **API Routers:** @backend/app/routers/ (9 router files: admin, ai, database_fix, health, market, predictions, scheduler, suggestions, version)

## Technical Stack Details

### Frontend Technologies
- **React:** 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0
- **Styling:** Tailwind CSS 4.0.9 with animations
- **UI Components:** shadcn/ui components, Lucide React icons
- **Charts:** Recharts 2.15.1
- **Forms:** React Hook Form 7.54.2 with Zod 3.24.2 validation
- **Animation:** Framer Motion 12.4.10
- **State Management:** React hooks and context

### Backend Technologies
- **Framework:** FastAPI 0.111+
- **Server:** Uvicorn with standard extras
- **Database:** SQLAlchemy 2.0+ with PostgreSQL/SQLite support
- **Scheduler:** APScheduler 3.10+ for market hours automation
- **Market Data:** yfinance 0.2.65+ for live SPY data
- **AI Integration:** OpenAI API 1.46+ with GPT-5
- **Data Analysis:** pandas 2.3.1+, numpy 2.2.6+
- **Database Driver:** psycopg2-binary for PostgreSQL

### Testing & Quality
- **Frontend Testing:** Vitest 3.2.4 with @testing-library/react 16.3.0
- **E2E Testing:** Playwright 1.55.0 with comprehensive test suites
- **Backend Testing:** pytest 8.4.1+ with comprehensive test coverage
- **Code Quality:** ESLint 9.21.0, Prettier 3.5.3
- **Type Checking:** TypeScript strict mode

### Development Tools
- **Package Managers:** yarn (frontend), uv (backend)
- **Environment:** Docker Compose for PostgreSQL development
- **CI/CD:** GitHub Actions with automated testing
- **Monitoring:** Health check endpoints and error tracking
EOF < /dev/null