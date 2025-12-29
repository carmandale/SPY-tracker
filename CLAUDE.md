# SPY TA Tracker - Claude Code Instructions

## Overview

SPY TA Tracker is a live, production-ready mobile-first options trading assistant that helps traders track SPY predictions and receive AI-powered iron condor/butterfly suggestions. The application combines manual technical analysis predictions with GPT-5 powered AI predictions, automated market data collection, and sophisticated option strategy recommendations.

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
- **Production Status:** ✅ **LIVE IN PRODUCTION** on Render.com
- **Production URL:** https://spy-tracker.onrender.com
- **Active Specs:** See @.agent-os/specs/ directory for feature specifications
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

## Development Workflow

### Quick Start Commands
```bash
# Frontend development
yarn dev                    # Start Vite dev server (port 3000)
yarn build                 # Production build
yarn test                  # Run Vitest tests
yarn lint                  # ESLint check
yarn format                # Prettier format

# Backend development  
cd backend
source .venv/bin/activate   # Activate Python environment
uvicorn app.main:app --reload --port 8000   # Start FastAPI server
uv pip sync pyproject.toml  # Install/update dependencies
pytest                     # Run backend tests

# Full application
./start.sh                 # Start both frontend and backend
./start-production.sh      # Start production mode
./monitor.sh              # Monitor production status
```

### Environment Configuration
- **Frontend:** Uses `.env.local` for local overrides
- **Backend:** Uses `.env` with fallback to `backend/.env`
- **Required Variables:** DATABASE_URL, OPENAI_API_KEY, API_PORT, PORT
- **Optional Variables:** See @backend/app/config.py for full list

### Database Management
- **Local Development:** Automatic PostgreSQL container or SQLite fallback
- **Migrations:** Manual SQL migrations in @backend/app/migrations/
- **Data Recovery:** @backend/app/database_recovery.py for data fixes
- **Health Checks:** Built-in database connection validation

### Testing Strategy
- **Unit Tests:** Vitest (frontend), pytest (backend)
- **E2E Tests:** Playwright for critical user flows
- **API Tests:** FastAPI TestClient for endpoint validation
- **Data Integrity:** Specialized Playwright tests for database consistency

### Deployment Process
- **Production Platform:** Render.com with Docker
- **Database:** Managed PostgreSQL on Render
- **CI/CD:** Automatic deployment from main branch
- **Health Monitoring:** /healthz endpoint with scheduler status
- **Static Serving:** FastAPI serves built React app

### AI System Configuration
- **Model:** GPT-5 (gpt-5) with minimal reasoning effort
- **Prompts:** Versioned prompts (currently v3.0.0) with technical indicators
- **Fallback:** Statistical baseline model for reliability
- **Rate Limits:** Configured for production workloads

## Important Notes

- Product-specific files in `.agent-os/product/` override any global standards
- User's specific instructions override (or amend) instructions found in `.agent-os/specs/...`
- Always adhere to established patterns, code style, and best practices documented above
- **CRITICAL:** Always use `yarn` for frontend and `uv` for backend package management
- **Database:** Uses intelligent detection - prefers PostgreSQL, falls back to SQLite
- **Timezone:** All operations in America/Chicago for market synchronization
- **Mobile-First:** UI designed for one-handed mobile trading workflows

## Technical Stack (Verified)

### Frontend
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with React plugin
- **Styling:** Tailwind CSS 4.0.9 with CSS-in-JS
- **UI Components:** Custom components with shadcn/ui patterns
- **Charts:** Recharts 2.15.1 for price visualization
- **Forms:** React Hook Form 7.54.2 with Zod validation
- **Animations:** Framer Motion 12.4.10
- **Icons:** Lucide React 0.477.0
- **Testing:** Vitest 3.2.4 + Testing Library + Playwright 1.55.0

### Backend
- **Framework:** FastAPI 0.111+ with Uvicorn
- **Database:** SQLAlchemy 2.0 with PostgreSQL (production) / SQLite (development)
- **AI System:** OpenAI GPT-5 with comprehensive market analysis
- **Task Scheduler:** APScheduler 3.10 for automated data collection
- **Market Data:** yfinance 0.2.65+ with real-time SPY data
- **HTTP Client:** httpx 0.27 for external API calls
- **Validation:** Pydantic 2.9+ for request/response models
- **Testing:** pytest 8.4.1+

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - backend/uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Database Configuration
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** Intelligent database detection with PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - PostgreSQL migration completed August 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Models:** Comprehensive schema supporting DailyPrediction, PriceLog, AIPrediction, BaselineModel, and ModelPerformance

### Current Production Status
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Deployment:** Docker-based deployment with render.yaml configuration
- **Completed Phases:** 0-6 including PostgreSQL migration
- **Remaining Features:** PWA configuration, backup/restore endpoints
- **Active Scheduler:** 6 jobs running successfully in America/Chicago timezone
- **AI System:** GPT-5 powered predictions with 8AM automated generation
- **Health Monitoring:** /healthz endpoint with comprehensive status checks

### Key Features (Production Ready)

#### Core Prediction System
- **Manual Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with comprehensive market analysis, confidence scoring, and reasoning
- **Baseline Model:** Statistical fallback model for reliability
- **Prediction Intervals:** 68% confidence intervals with hit rate tracking

#### Automated Data Collection
- **Scheduled Jobs:** Automated capture of Open/Noon/2PM/Close prices via yfinance
- **Market Timing:** America/Chicago timezone with market holiday detection
- **Price Logging:** Comprehensive price history with timestamp tracking
- **Data Integrity:** Robust error handling and data validation

#### Option Strategy Engine
- **Structure Selection:** Automated Iron Condor vs Iron Butterfly recommendations
- **Multi-Horizon:** 0DTE, 1W, and 1M option suggestions
- **Delta Targeting:** Intelligent strike selection based on prediction accuracy
- **Risk Management:** IVR filtering and position sizing recommendations

#### Performance Analytics
- **Rolling Metrics:** 20-day range hit percentage and median absolute error
- **Calibration System:** Data-driven tips for improving prediction accuracy
- **Historical Analysis:** Complete prediction history with trend analysis
- **Model Comparison:** AI vs baseline vs manual prediction tracking

#### User Interface
- **Mobile-First Design:** Optimized for one-handed mobile trading
- **Real-time Charts:** Predicted bands vs actual price movement visualization
- **Loading States:** Skeleton screens and performance optimizations
- **Error Handling:** Comprehensive exception system with user-friendly messages

### Key Project Files

#### Documentation
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **PostgreSQL Status:** @POSTGRESQL_STATUS.md
- **Project Reality Check:** @PROJECT_REALITY_CHECK.md

#### Backend Core
- **Main Application:** @backend/app/main.py (FastAPI app with 40+ endpoints)
- **Database Models:** @backend/app/models.py (comprehensive schema for PostgreSQL/SQLite)
- **Configuration:** @backend/app/config.py (intelligent database detection)
- **Exception Handling:** @backend/app/exceptions.py (comprehensive exception system)

#### AI & Prediction System
- **AI Predictor:** @backend/app/ai_predictor.py (GPT-5 with technical indicators and regime detection)
- **Baseline Model:** @backend/app/baseline_model.py (statistical fallback predictions)
- **Market Data:** @backend/app/providers.py (yfinance integration with caching)
- **Scheduler:** @backend/app/scheduler.py (APScheduler with timezone handling)

#### API Routers
- **Predictions:** @backend/app/routers/predictions.py
- **AI Endpoints:** @backend/app/routers/ai.py
- **Market Data:** @backend/app/routers/market.py
- **Suggestions:** @backend/app/routers/suggestions.py
- **Health Monitoring:** @backend/app/routers/health.py
- **Admin Tools:** @backend/app/routers/admin.py
- **Database Fix:** @backend/app/routers/database_fix.py
- **Scheduler Control:** @backend/app/routers/scheduler.py
- **Version Info:** @backend/app/routers/version.py

#### Frontend Core
- **Main App:** @src/App.tsx (React 19, mobile-optimized)
- **Main Component:** @src/components/generated/SPYTaTrackerApp.tsx
- **API Client:** @src/utils/apiClient.ts (comprehensive API integration)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @src/utils/errorHandling.ts

#### Testing
- **Backend Tests:** @backend/tests/ (pytest with FastAPI test client)
- **Frontend Tests:** @src/test/ (Vitest + Testing Library)
- **E2E Tests:** @tests/ (Playwright for data integrity)
- **Test Configuration:** @vitest.config.ts, @backend/tests/conftest.py

#### Deployment
- **Docker:** @Dockerfile (production container)
- **Render Config:** @render.yaml (cloud deployment)
- **Scripts:** @start.sh, @start-production.sh, @monitor.sh
- **Database:** @docker-compose.yml (PostgreSQL container)
EOF < /dev/null