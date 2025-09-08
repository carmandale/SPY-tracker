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

## Architecture Overview

### API Structure
- **Health & Monitoring:** `/health/critical`, `/health/status`, `/healthz`
- **Predictions:** `/day/{date}`, `/prediction/{date}`, `/capture/{date}`
- **AI Predictions:** `/ai/predictions/{date}`, `/ai/accuracy`
- **Market Data:** `/market-status`, `/suggestions/{date}`
- **Admin & Database:** `/admin/`, `/database-fix/`
- **System Info:** `/version`, `/scheduler/status`

### Database Schema
- **DailyPrediction:** User predictions with price data and accuracy metrics
- **AIPrediction:** AI predictions with confidence intervals and error tracking
- **PriceLog:** Historical price capture logs
- **ModelPerformance:** AI model accuracy tracking over time

### AI Prediction System
- **Model:** GPT-5 (gpt-5) with minimal reasoning effort for speed
- **Analysis:** 50+ technical indicators, market regime detection, cross-asset signals
- **Confidence:** Calibrated confidence scores with 68% prediction intervals
- **Fallback:** Statistical baseline model for AI service failures

### Environment Configuration
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Production:** PostgreSQL on Render with intelligent database detection
- **Environment Variables:** DATABASE_URL, OPENAI_API_KEY (never commit .env files)
- **Timezone Handling:** America/Chicago for scheduler, America/New_York for market data

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Tech Stack (Current Versions)
- **Frontend:** React 19.0.0, Vite 6.2.0, TypeScript 5.7.2, Tailwind CSS 4.0.9
- **Backend:** FastAPI 0.111+, Python >=3.10, SQLAlchemy 2.0, Pydantic 2.9+
- **AI/ML:** OpenAI GPT-5 (gpt-5), yfinance 0.2.65+, pandas 2.3.1+
- **Database:** PostgreSQL 16 (production), SQLite (local fallback)
- **Testing:** Vitest 3.2.4, Playwright 1.55.0, pytest 8.4.1+

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Available Scripts
- **Frontend:** `yarn dev`, `yarn build`, `yarn test`, `yarn lint`, `yarn format`, `yarn e2e`
- **Backend:** `uv run pytest`, `uv run uvicorn app.main:app --reload --port 8000`
- **Docker:** `docker-compose up db` (PostgreSQL), `docker-compose --profile test up` (test DB)

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
- **Docker Support:** Full containerization with docker-compose.yml
- **Health Monitoring:** `/health/critical`, `/health/status`, `/healthz` endpoints
- **Completed:** Phases 0-6 including PostgreSQL migration (Issue #13 closed)
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)
- **AI System:** GPT-5 powered predictions with technical indicators and market analysis

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and comprehensive market analysis
  - Technical indicators: RSI, MACD, Bollinger Bands, Moving averages
  - Market regime detection (trending, range-bound, volatile, breakout)
  - Cross-asset analysis (VIX, ES futures integration)
  - Prediction intervals with 68% confidence bounds
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data
- **Health Monitoring:** Critical system health checks with data integrity validation
- **Error Handling:** Comprehensive exception system with user-friendly error responses

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (complete FastAPI app with 40+ endpoints)
- **Database Models:** @backend/app/models.py (SQLAlchemy models for PostgreSQL/SQLite)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized UI)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with advanced technical analysis)
- **Health Monitoring:** @backend/app/routers/health.py (comprehensive system health checks)
- **Configuration:** @backend/app/config.py (intelligent database detection and settings)
- **Exception Handling:** @backend/app/exceptions.py (structured error responses)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Testing Config:** @vitest.config.ts, @backend/tests/ (Vitest + pytest + Playwright)
- **Docker Config:** @docker-compose.yml (PostgreSQL 16 + adminer + test containers)
- **Deployment:** @render.yaml, @Dockerfile, @nixpacks.toml (multi-platform deployment)
EOF < /dev/null