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

### Development Best Practices
- **Code Style:** Follow existing patterns, use TypeScript strict mode
- **Database:** Intelligent detection prefers PostgreSQL, falls back to SQLite
- **Error Handling:** Use custom exception classes (@backend/app/exceptions.py)
- **API Design:** RESTful endpoints with comprehensive validation
- **Testing:** Write tests before merging, maintain >80% coverage
- **Performance:** Use caching, debouncing, lazy loading where appropriate
- **Mobile:** Mobile-first design with touch optimization
- **Security:** Never commit `.env` files, use environment variables

### Common Development Tasks
- **Add new API endpoint:** Create in appropriate router under `backend/app/routers/`
- **Add frontend component:** Follow existing patterns in `src/components/`
- **Database changes:** Use migration scripts in `backend/app/migrations/`
- **Testing:** Use `yarn test` (frontend), `pytest` (backend), `yarn e2e` (E2E)
- **Debugging:** Check logs, use health endpoints, verify scheduler status

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Production:** Dockerized deployment on Render.com with health checks

### Available Scripts
- **Frontend:** `yarn dev`, `yarn build`, `yarn test`, `yarn e2e`, `yarn lint`, `yarn format`
- **Backend:** Use `uv` commands - virtual environment managed automatically
- **Testing:** Vitest (frontend), pytest (backend), Playwright (E2E)
- **Development Tools:** ESLint 9.21, Prettier 3.5.3, TypeScript 5.7.2

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

### Production Deployment
- **Platform:** Render.com using Docker deployment
- **Configuration:** @render.yaml (web service with health checks)
- **Dockerfile:** Multi-stage build with static file serving
- **Health Endpoint:** `/healthz` with scheduler status monitoring
- **Environment:** OPENAI_API_KEY and DATABASE_URL configured via Render dashboard
- **Static Files:** Frontend build served by FastAPI StaticFiles
- **Timezone:** America/Chicago for market hours scheduling
- **Auto-Deploy:** Enabled from main branch commits

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, reasoning, and technical analysis
  - **Model:** GPT-5 (gpt-5-turbo-20241121) with reasoning effort optimization
  - **Fallback:** Statistical baseline model when AI service unavailable
  - **Analysis:** RSI, MACD, Bollinger Bands, volume analysis, support/resistance levels
  - **Market Context:** VIX integration, ES futures correlation, regime detection
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement (Recharts)
- **Market Data Integration:** Live SPY pricing, market status, volatility data
- **Production Ready:** Comprehensive error handling, loading states, mobile optimization

### Technical Architecture

#### Frontend Stack (React 19)
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with hot module replacement
- **Styling:** Tailwind CSS 4.0.9 with shadcn/ui components
- **Forms:** React Hook Form 7.54.2 with Zod 3.24.2 validation
- **Charts:** Recharts 2.15.1 for real-time price visualization
- **Animation:** Framer Motion 12.4.10 for smooth UI transitions
- **State:** React 19 hooks and context (no external state manager)
- **Mobile:** Mobile-first responsive design with touch optimization

#### Backend Stack (FastAPI)
- **Framework:** FastAPI 0.111+ with Uvicorn 0.30+ (ASGI server)
- **Database:** SQLAlchemy 2.0 ORM with PostgreSQL/SQLite support
- **Validation:** Pydantic 2.9+ for request/response validation
- **Scheduling:** APScheduler 3.10 for automated price capture (America/Chicago timezone)
- **Market Data:** yfinance 0.2.65+ for real-time SPY/VIX/ES futures data
- **AI Integration:** OpenAI API 1.46+ with GPT-5 model
- **HTTP Client:** httpx 0.27 for external API calls
- **Database Drivers:** psycopg2-binary for PostgreSQL

#### Testing & Quality
- **Frontend Tests:** Vitest 3.2.4 with jsdom environment and React Testing Library
- **Backend Tests:** pytest 8.4.1 with comprehensive API endpoint coverage
- **E2E Tests:** Playwright 1.55.0 with data integrity validation
- **Code Quality:** ESLint 9.21 + Prettier 3.5.3 for consistent formatting
- **Type Safety:** Full TypeScript coverage with strict configuration

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with 10 router modules)
- **Database Models:** @backend/app/models.py (DailyPrediction, AIPrediction, PriceLog)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical analysis)
- **Baseline Model:** @backend/app/baseline_model.py (statistical fallback predictor)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized)
- **API Client:** @src/utils/apiClient.ts (with error handling and caching)
- **Performance:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Configuration:** @backend/app/config.py (intelligent database detection)
- **Testing Setup:** @src/test/setup.ts (Vitest configuration with mocks)

### Project Structure
```
SPY-tracker/
├── src/                     # React frontend source
│   ├── components/         # UI components including generated screens
│   ├── utils/             # API client, performance utilities
│   ├── hooks/             # Custom React hooks
│   └── lib/               # Shared utilities and schemas
├── backend/                # FastAPI backend
│   ├── app/               # Main application code
│   │   ├── routers/       # API route modules (10 routers)
│   │   ├── migrations/    # Database migration scripts
│   │   └── tests/         # Backend test suite
│   └── static/            # Built frontend files
├── tests/                 # E2E tests (Playwright)
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── .agent-os/             # Agent OS configuration
```
EOF < /dev/null