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
- **Lock Files Verified:** ✅ yarn.lock (204KB), ✅ backend/uv.lock (306KB)

### Development Servers
- **Frontend:** Port 3000 (configurable via PORT env) - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Proxy Configuration:** Vite dev server proxies API routes (/day, /ai, /metrics, /suggestions, /market-status, /accuracy) to backend

### Tech Stack Versions (Verified)
#### Frontend Dependencies
- **React:** 19.0.0 with React DOM 19.0.0
- **TypeScript:** 5.7.2
- **Vite:** 6.2.0 with @vitejs/plugin-react 4.3.4
- **Tailwind CSS:** 4.0.9 with @tailwindcss/vite plugin
- **Testing:** Vitest 3.2.4 with @testing-library/react 16.3.0
- **E2E:** Playwright 1.55.0
- **Charts:** Recharts 2.15.1
- **Forms:** React Hook Form 7.54.2 with Zod 3.24.2
- **UI Components:** shadcn/ui components (lucide-react 0.477.0)
- **Animations:** Framer Motion 12.4.10

#### Backend Dependencies  
- **FastAPI:** 0.111+ to <0.116 with Uvicorn 0.30+ to <0.32
- **Database:** SQLAlchemy 2.0+ to <2.1 with psycopg2-binary 2.9+ to <2.10
- **Validation:** Pydantic 2.9+ to <2.12
- **Scheduling:** APScheduler 3.10+ to <4.0
- **Market Data:** yfinance 0.2.65+ to <0.3
- **AI:** OpenAI 1.46.0+ to <2.0
- **Data Analysis:** pandas 2.3.1+, numpy 2.2.6+
- **HTTP Client:** httpx 0.27+ to <0.28
- **Testing:** pytest 8.4.1+ (dev dependency)

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment Files:** 
  - `.env.example` - Template with PostgreSQL defaults
  - `.env.postgres.example` - PostgreSQL-specific template
  - `.env.production` - Production environment settings
  - **Never commit actual `.env` files** - Use templates as reference
- **Intelligent Database Detection:** Automatic PostgreSQL/SQLite detection with fallback support

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, technical analysis reasoning, and sentiment detection
- **Baseline Model:** Statistical fallback predictions using ATR, seasonality patterns, and mean reversion
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance with market holiday handling
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons with delta targeting
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips, and model accuracy comparison
- **Historical Analysis:** Complete prediction history with accuracy metrics, trends, and prediction intervals
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement with mobile optimization
- **Market Data Integration:** Live SPY pricing, VIX data, ES futures, market status, and volatility analysis
- **Comprehensive Testing:** Vitest (frontend), pytest (backend), Playwright (E2E) with 26+ test files
- **Production Deployment:** Live on Render.com with PostgreSQL, scheduled jobs, and health monitoring

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (10 router modules with comprehensive error handling)
- **Database Models:** @backend/app/models.py (DailyPrediction, PriceLog, AIPrediction, BaselineModel, ModelPerformance)
- **Frontend App:** @src/App.tsx (React 19, mobile-first with generated UI components)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators and baseline fallback)
- **Baseline Model:** @backend/app/baseline_model.py (statistical fallback predictions)
- **Option Suggestions:** @backend/app/suggestions.py (Iron Condor/Butterfly algorithm)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading, web vitals)
- **Error Handling:** @backend/app/exceptions.py (custom exceptions with structured responses)
- **Database Utils:** @backend/app/database_utils.py (intelligent connection management)
- **Configuration:** @backend/app/config.py (Pydantic settings with env detection)

### API Router Structure (10 modules)
- **Predictions:** @backend/app/routers/predictions.py
- **AI Predictions:** @backend/app/routers/ai.py  
- **Market Data:** @backend/app/routers/market.py
- **Option Suggestions:** @backend/app/routers/suggestions.py
- **Admin Tools:** @backend/app/routers/admin.py
- **Scheduler Management:** @backend/app/routers/scheduler.py
- **Database Fixes:** @backend/app/routers/database_fix.py
- **Health Checks:** @backend/app/routers/health.py
- **Version Info:** @backend/app/routers/version.py

### AI Prediction System Details
- **Primary Model:** GPT-5 with reasoning effort configuration
- **Technical Analysis:** RSI, MACD, Bollinger Bands, Moving Averages, Volume Analysis
- **Market Data Sources:** SPY, VIX, ES Futures via yfinance
- **Prediction Checkpoints:** Open, Noon, 2PM, Close with confidence intervals
- **Fallback System:** Statistical baseline model using ATR and seasonality
- **Prompt Version Tracking:** v3.0.0 with comprehensive expert analysis
- **Model Performance:** Tracks MAE, RMSE, hit rates, and interval coverage

### Testing Framework Configuration
- **Frontend Testing:** Vitest 3.2.4 with jsdom environment and @testing-library/react
- **Backend Testing:** pytest 8.4.1+ with comprehensive test coverage
- **E2E Testing:** Playwright 1.55.0 with data integrity tests
- **Test Files:** 26+ test files across frontend/backend/e2e
- **Coverage:** API endpoints, database integrity, market data, AI predictions
EOF < /dev/null