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
- **AI Model:** Currently using GPT-5 (gpt-5) with minimal reasoning effort for cost optimization
- **Timezone:** All operations in America/Chicago (CST/CDT) for market hours
- **Docker Support:** Multi-stage Dockerfile with Node 20 (frontend) and Python 3.11 (backend)

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev` (Vite 6.2.0 with React 19.0.0)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

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
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, reasoning, and technical analysis (v3.0.0 prompt)
- **Advanced AI Analysis:** RSI, MACD, Bollinger Bands, volume analysis, support/resistance levels, VIX correlation
- **Baseline Model:** Statistical fallback predictor for when AI service is unavailable
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance (6 scheduled jobs)
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips, interval coverage
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends (41+ historical predictions)
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement (Recharts)
- **Market Data Integration:** Live SPY pricing, market status, volatility data, ES futures, VIX integration
- **Health Monitoring:** Comprehensive health checks with data integrity validation
- **Error Handling:** Robust exception system with custom SPY Tracker exceptions

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (FastAPI 0.111+ with 40+ endpoints and comprehensive error handling)
- **Database Models:** @backend/app/models.py (SQLAlchemy 2.0, PostgreSQL/SQLite support, AI prediction tracking)
- **AI Prediction System:** @backend/app/ai_predictor.py (GPT-5 with advanced technical analysis and regime detection)
- **Baseline Predictor:** @backend/app/baseline_model.py (statistical fallback model)
- **Router Structure:** @backend/app/routers/ (modular API endpoints: admin, ai, health, predictions, etc.)
- **Frontend App:** @src/App.tsx (React 19.0.0, mobile-first, Tailwind CSS 4.0.9)
- **Frontend Components:** @src/components/generated/ (SPYTaTrackerApp, dashboard screens)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading, web vitals)
- **Error Handling:** @backend/app/exceptions.py (custom SPY Tracker exception hierarchy)
- **Configuration:** @backend/app/config.py (intelligent database detection, environment handling)
- **Testing:** Vitest (frontend), pytest (backend), Playwright (E2E)

## Tech Stack Details

### Frontend Stack (React 19)
- **Build Tool:** Vite 6.2.0 (replaces Create React App)
- **TypeScript:** 5.7.2 with strict configuration
- **Styling:** Tailwind CSS 4.0.9 with @tailwindcss/vite plugin
- **UI Components:** shadcn/ui with Radix UI primitives
- **Forms:** React Hook Form 7.54.2 with Zod 3.24.2 validation
- **Charts:** Recharts 2.15.1 for market data visualization
- **Icons:** Lucide React 0.477.0
- **Animations:** Framer Motion 12.4.10
- **Theme:** next-themes 0.4.6 for dark/light mode

### Backend Stack (FastAPI)
- **Framework:** FastAPI 0.111+ with Uvicorn ASGI server
- **Python:** 3.11+ (required minimum version)
- **ORM:** SQLAlchemy 2.0 with Alembic migrations
- **Validation:** Pydantic 2.9+ for request/response schemas
- **Scheduling:** APScheduler 3.11.0 for market data collection
- **Market Data:** yfinance 0.2.65+ for live SPY prices
- **AI Integration:** OpenAI 1.46.0+ for GPT-5 predictions
- **Database:** PostgreSQL (production) / SQLite (fallback)
- **HTTP Client:** httpx 0.27 for external API calls

### Testing & Quality
- **Frontend Testing:** Vitest 3.2.4 with jsdom environment
- **Backend Testing:** pytest 8.4.1 (configured in uv dev dependencies)
- **E2E Testing:** Playwright 1.55.0 for integration tests
- **Linting:** ESLint 9.21.0 with React hooks plugin
- **Formatting:** Prettier 3.5.3 for code formatting
- **Type Checking:** TypeScript with strict mode enabled

### Deployment & DevOps
- **Container:** Multi-stage Docker build (Node 20 + Python 3.11)
- **Production:** Render.com with PostgreSQL managed database
- **CI/CD:** GitHub Actions with automated health checks
- **Health Monitoring:** Comprehensive endpoints at /health/critical and /healthz
- **Static Assets:** FastAPI serves built frontend from /static directory

## Environment Configuration

### Required Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@host:port/dbname
OPENAI_API_KEY=sk-...your-api-key...
TIMEZONE=America/Chicago
SYMBOL=SPY

# Optional Configuration
OPENAI_MODEL=gpt-5
OPENAI_REASONING_EFFORT=minimal
OPENAI_MAX_COMPLETION_TOKENS=600
USE_INTELLIGENT_DATABASE_DETECTION=true
FALLBACK_TO_SQLITE=true
```

### Development Setup Commands
```bash
# Frontend development
yarn install
yarn dev  # Starts Vite dev server on port 3000

# Backend development  
cd backend
uv sync  # Install dependencies
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Full stack development
# Terminal 1: yarn dev
# Terminal 2: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000
```

## Database Schema

### Core Tables
- **daily_predictions:** User and AI predictions with bias, volatility context
- **price_logs:** Historical price capture at market checkpoints  
- **ai_predictions:** GPT-5 predictions with confidence and reasoning
- **baseline_models:** Statistical model configurations
- **model_performance:** Daily performance metrics for all models

### Key Features
- **Timezone Support:** All timestamps in America/Chicago
- **Data Integrity:** Unique constraints and foreign keys
- **Audit Trail:** created_at/updated_at for all records
- **Migration Support:** Alembic migrations for schema changes
- **Dual Database:** PostgreSQL (production) + SQLite (local/fallback)

## AI Prediction System

### GPT-5 Integration
- **Model:** gpt-5 (latest) with minimal reasoning effort for cost optimization
- **Prompt Version:** v3.0.0 with enhanced technical analysis
- **Technical Indicators:** RSI, MACD, Bollinger Bands, Moving Averages
- **Market Context:** VIX correlation, ES futures, volume analysis
- **Confidence Scoring:** 0.0-1.0 scale with prediction intervals
- **Fallback System:** Baseline statistical model when AI unavailable

### Prediction Workflow
1. **8:00 AM CST:** AI generates predictions for Open/Noon/2PM/Close
2. **Market Hours:** Automated price capture at checkpoints
3. **End of Day:** Accuracy scoring and model performance tracking
4. **Historical Analysis:** 41+ predictions with rolling 20-day metrics

## Scheduler System

### Active Jobs (6 total)
- **8:00 AM:** AI predictions + pre-market capture
- **8:30 AM:** Market open capture
- **12:00 PM:** Noon price capture  
- **2:00 PM:** 2PM price capture
- **3:00 PM:** Market close capture + EOD processing
- **Health Monitoring:** Periodic data integrity checks

### Timezone Handling
- **Primary:** America/Chicago (handles CST/CDT transitions automatically)
- **Market Hours:** Converted to Eastern Time for NYSE schedule
- **Holiday Support:** Market holiday detection and skip logic
EOF < /dev/null