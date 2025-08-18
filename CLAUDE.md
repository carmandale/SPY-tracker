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

## Tech Stack Details

### Frontend Technologies
- **React:** 19.0.0 (latest with new features)
- **TypeScript:** 5.7.2
- **Vite:** 6.2.0 (build tool and dev server)
- **Tailwind CSS:** 4.0.9 (styling framework)
- **UI Components:** Custom components with shadcn/ui patterns
- **Icons:** Lucide React 0.477.0
- **Charts:** Recharts 2.15.1
- **Forms:** React Hook Form 7.54.2 with Zod validation
- **Animations:** Framer Motion 12.4.10
- **State Management:** React hooks and context
- **Testing:** Vitest 3.2.4 with Testing Library

### Backend Technologies
- **FastAPI:** 0.111+ (async web framework)
- **Python:** 3.10+ (required version)
- **Database:** SQLAlchemy 2.0 ORM with PostgreSQL/SQLite support
- **Validation:** Pydantic 2.9+ for data validation
- **Scheduler:** APScheduler 3.10+ for automated jobs
- **Market Data:** yfinance 0.2.65+ for SPY price feeds
- **AI Integration:** OpenAI 1.46+ for GPT-5 predictions
- **HTTP Client:** httpx 0.27 for external API calls
- **Environment:** python-dotenv for configuration
- **Analysis:** pandas 2.3.1+ and numpy 2.2.6+ for data processing

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 (configurable via PORT env var) - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Full Stack:** Use `yarn dev` (with proxy config) for integrated development

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
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and detailed market analysis
  - Technical indicators: RSI, MACD, Bollinger Bands, moving averages
  - Market regime detection (trending, range-bound, volatile, breakout)
  - Cross-asset analysis (VIX correlation, ES futures, volume analysis)
  - Confidence intervals and prediction accuracy tracking
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Sophisticated Iron Condor/Butterfly algorithms for 0DTE, 1W, 1M horizons
  - Delta-based strike selection with simplified Black-Scholes approximation
  - Expected move calculations and volatility-based positioning
  - Risk management with profit targets and stop losses
  - Intelligent IC vs IB selection based on bias and historical accuracy
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data
- **Database Intelligence:** Automatic PostgreSQL/SQLite detection with fallback handling
- **Mobile-First Design:** Touch-optimized interface with bottom navigation
- **Error Handling:** Comprehensive exception system with user-friendly messages

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with full error handling)
- **Database Models:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **Main UI Component:** @src/components/generated/SPYTaTrackerApp.tsx
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators and comprehensive market analysis)
- **Option Suggestions:** @backend/app/suggestions.py (Iron Condor/Butterfly algorithms)
- **Configuration:** @backend/app/config.py (environment-based settings with intelligent database detection)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **API Client:** @src/utils/apiClient.ts (frontend API communication)
- **Database Utils:** @backend/app/database_utils.py (intelligent PostgreSQL/SQLite detection)
## Development Workflow

### Starting Development
1. **Frontend Only:** `yarn dev` (starts Vite dev server on port 3000)
2. **Backend Only:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
3. **Full Stack:** `yarn dev` uses proxy config to route API calls to backend

### Code Quality Tools
- **Linting:** `yarn lint` (ESLint 9.21)
- **Formatting:** `yarn format` (Prettier 3.5.3) or `yarn format:check`
- **Testing:** `yarn test` (Vitest), `yarn test:ui`, `yarn test:coverage`
- **Build:** `yarn build` (generates static files in `dist/`)
- **Preview:** `yarn preview` (preview production build)

### API Proxy Configuration
Vite dev server proxies these API routes to backend:
- `/day/*` - Daily prediction endpoints
- `/ai/*` - AI prediction endpoints  
- `/metrics/*` - Performance metrics
- `/suggestions/*` - Option suggestion endpoints
- `/market-status/*` - Market data endpoints
- `/accuracy/*` - Accuracy tracking

### Database Configuration
- **Intelligent Detection:** Automatically detects PostgreSQL availability and falls back to SQLite
- **Environment Variables:**
  - `DATABASE_URL` - Direct database connection string
  - `USE_INTELLIGENT_DATABASE_DETECTION=true` - Enable auto-detection (default)
  - `FALLBACK_TO_SQLITE=true` - Allow SQLite fallback (default)
- **Local PostgreSQL:** Uses Docker container on port 5433
- **Production:** PostgreSQL on Render managed service

### AI Configuration
- **OpenAI API:** Set `OPENAI_API_KEY` in environment
- **Model:** GPT-5 (configurable via `OPENAI_MODEL`)
- **Reasoning Effort:** Minimal (configurable via `OPENAI_REASONING_EFFORT`)
- **Fallback:** Baseline statistical model when AI unavailable

### Scheduler Jobs (America/Chicago Timezone)
- **8:00 AM:** AI predictions generation + pre-market capture
- **8:30 AM:** Market open price capture
- **12:00 PM:** Noon price capture
- **2:00 PM:** 2PM price capture
- **3:00 PM:** Market close price capture + daily scoring

EOF < /dev/null