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
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Unified Start:** Use `./start.sh` script for simultaneous frontend/backend startup

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Auto-Detection:** Intelligent database detection with fallback to SQLite when PostgreSQL unavailable

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)
- **AI Model:** GPT-5 (gpt-5) with enhanced technical analysis and reasoning
- **Health Checks:** Available at `/healthz` endpoint for monitoring
- **CLI Management:** Render CLI integration with scripts for deployment and monitoring

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, reasoning, and technical indicators
- **Advanced AI Analysis:** Includes RSI, MACD, Bollinger Bands, support/resistance levels, market regime detection
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, VIX, ES futures, market status, volatility data
- **Error Handling:** Comprehensive exception system with user-friendly error responses
- **Testing Suite:** Vitest (frontend), pytest (backend), Playwright (E2E) configured
- **Performance Optimization:** Caching, debouncing, lazy loading, web vitals tracking

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with full error handling)
- **Database Models:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Database Utils:** @backend/app/database_utils.py (intelligent database detection)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **Main Component:** @src/components/generated/SPYTaTrackerApp.tsx (generated UI components)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators)
- **AI Endpoints:** @backend/app/ai_endpoints.py (AI prediction service layer)
- **Scheduler:** @backend/app/scheduler.py (APScheduler with market hours timing)
- **Configuration:** @backend/app/config.py (settings with environment detection)
- **Performance:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Startup Logic:** @backend/app/startup.py (database init, scheduler, AI warmup)
- **Testing Config:** @vitest.config.ts (frontend), @backend/tests/ (backend pytest)
- **Build Tools:** @vite.config.ts (Vite 6.2.0), @package.json (yarn scripts)
- **Deployment:** @render.yaml (Render configuration), @Dockerfile (containerization)
- **Documentation:** @docs/ (deployment guides, PostgreSQL setup, Docker compose)

## Current Tech Stack Versions (Verified)

### Frontend Dependencies
- **React:** 19.0.0 (latest stable)
- **TypeScript:** 5.7.2
- **Vite:** 6.2.0 (build tool)
- **Tailwind CSS:** 4.0.9 (with @tailwindcss/vite plugin)
- **Framer Motion:** 12.4.10 (animations)
- **Recharts:** 2.15.1 (data visualization)
- **React Hook Form:** 7.54.2 + Zod 3.24.2 (form handling)
- **Lucide React:** 0.477.0 (icons)
- **ESLint:** 9.21.0, **Prettier:** 3.5.3

### Backend Dependencies
- **Python:** >=3.10 required
- **FastAPI:** 0.111-0.116 (web framework)
- **Uvicorn:** 0.30-0.32 (ASGI server)
- **SQLAlchemy:** 2.0-2.1 (ORM)
- **Pydantic:** 2.9-2.12 (data validation)
- **APScheduler:** 3.10-4.0 (task scheduling)
- **OpenAI:** 1.46.0-2.0 (AI integration)
- **yfinance:** 0.2.65-0.3 (market data)
- **psycopg2-binary:** 2.9-2.10 (PostgreSQL adapter)
- **pytest:** 8.4.1+ (testing framework)

### Development Tools
- **Testing:** Vitest 3.2.4 (frontend), pytest 8.4.1+ (backend), Playwright 1.55.0 (E2E)
- **Package Managers:** yarn (frontend), uv (backend Python)
- **Deployment:** Docker + Render.com
- **Database:** PostgreSQL 16 (production), SQLite (local fallback)

## AI System Configuration

### Model & API Settings
- **Primary Model:** GPT-5 (gpt-5) via OpenAI API
- **Temperature:** 0.2 (deterministic predictions)
- **Max Completion Tokens:** 600
- **Reasoning Effort:** minimal (for GPT-5 reasoning models)
- **Lookback Days:** 5 (historical data analysis)

### AI Features
- **Technical Analysis:** RSI, MACD, Bollinger Bands, moving averages
- **Market Data:** SPY, VIX, ES futures integration
- **Prediction Types:** Open, Noon, 2PM, Close prices with confidence intervals
- **Fallback System:** Statistical baseline model when AI fails
- **Accuracy Tracking:** Comprehensive performance metrics and calibration

### Scheduler Configuration
- **Timezone:** America/Chicago (handles CST/CDT automatically)
- **AI Predictions:** Daily at 8:00 AM (weekdays only)
- **Price Capture:** Open (8:30), Noon (12:00), 2PM (14:00), Close (15:00)
- **Market Holidays:** Automatic detection and skip
- **Job Count:** 6 active scheduled jobs

## Development Workflow Commands

### Frontend Development
```bash
yarn install           # Install dependencies
yarn dev              # Start development server (port 3000)
yarn build            # Production build
yarn preview          # Preview production build
yarn lint             # Run ESLint
yarn format           # Format code with Prettier
yarn test             # Run Vitest tests
yarn test:ui          # Run tests with UI
yarn e2e              # Run E2E tests with Playwright
```

### Backend Development
```bash
cd backend
uv venv                           # Create virtual environment
source .venv/bin/activate        # Activate (Linux/Mac)
uv pip sync pyproject.toml       # Install dependencies
uvicorn app.main:app --reload --port 8000  # Start server
pytest                           # Run tests
```

### Unified Development
```bash
./start.sh            # Start both frontend and backend
./monitor.sh          # Monitor running services
./restart.sh          # Restart services
```

### Production Deployment
```bash
# Render CLI (after setup)
render services list              # List services
render services logs <id>         # View logs
render shell <id>                # Connect to service shell
render deploy --service-id <id>   # Manual deployment

# Health checks
curl https://spy-tracker.onrender.com/healthz
curl https://spy-tracker.onrender.com/scheduler/status
```

## Database Architecture

### Models & Relationships
- **DailyPrediction:** Main predictions with user/AI entries, locking mechanism
- **PriceLog:** Historical price checkpoints with timestamps
- **AIPrediction:** AI-specific predictions with confidence intervals and reasoning
- **BaselineModel:** Statistical model configurations
- **ModelPerformance:** Daily accuracy metrics for different models

### Database Features
- **Intelligent Detection:** Automatic PostgreSQL vs SQLite selection
- **Migration System:** SQL-based migrations with version tracking
- **Connection Pooling:** SQLAlchemy engine with optimized settings
- **Backup Support:** Data export/import endpoints (planned)
- **Development Tools:** Query scripts and data verification utilities

## Testing & Quality Assurance

### Test Coverage
- **Frontend:** Component tests with Testing Library + Vitest
- **Backend:** API tests with pytest + SQLAlchemy fixtures
- **E2E:** Full user workflows with Playwright
- **Integration:** Database, AI services, scheduler testing

### Code Quality
- **Linting:** ESLint 9.21 with modern rules
- **Formatting:** Prettier 3.5.3 with consistent configuration
- **Type Safety:** Full TypeScript coverage, Pydantic validation
- **Error Handling:** Comprehensive exception system with user-friendly messages
- **Performance:** Web vitals tracking, optimization utilities
EOF < /dev/null