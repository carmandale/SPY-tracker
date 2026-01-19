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
- **Status:** ✅ **LIVE IN PRODUCTION** - All core features implemented
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

### Database Architecture
- **Production:** PostgreSQL on Render.com (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Models:** DailyPrediction, PriceLog, AIPrediction, BaselineModel, ModelPerformance
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; configuration via environment variables

### Current Production Status
- **Application:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed Phases:** 0-6 including full PostgreSQL migration
- **Remaining (Nice-to-have):** PWA service workers, CSV export functionality
- **Scheduler:** 6 active jobs running (8AM AI predictions, price capture)
- **AI System:** GPT-5 powered predictions with baseline model fallback

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and reasoning
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (FastAPI 0.111+ with 40+ endpoints)
- **Database Models:** @backend/app/models.py (SQLAlchemy 2.0, PostgreSQL/SQLite)
- **Frontend:** @src/App.tsx (React 19.0.0, mobile-first SPA)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with baseline fallback)
- **Performance Utils:** @src/utils/performance.ts (optimization utilities)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Configuration:** @backend/app/config.py (environment-based settings)
- **Routers:** @backend/app/routers/ (predictions, AI, market, admin, health)
## Tech Stack & Versions

### Frontend (React 19 + Vite)
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0
- **UI Framework:** Tailwind CSS v4.0.9 with shadcn/ui components
- **Animation:** Framer Motion 12.4.10
- **Charts:** Recharts 2.15.1
- **Forms:** React Hook Form 7.54.2 + Zod 3.24.2
- **Icons:** Lucide React 0.477.0
- **Testing:** Vitest 3.2.4, Playwright 1.55.0

### Backend (FastAPI + Python)
- **Framework:** FastAPI 0.111+ with Uvicorn
- **ORM:** SQLAlchemy 2.0 with Pydantic 2.9+
- **Scheduler:** APScheduler 3.10 for market data collection
- **AI Service:** OpenAI 1.46+ (GPT-5) with baseline model fallback
- **Market Data:** yfinance 0.2.65+, httpx 0.27
- **Database:** PostgreSQL (psycopg2-binary) + SQLite fallback
- **Testing:** pytest 8.4.1

### Development & Testing
- **Frontend Testing:** Vitest (unit), Playwright (e2e), Testing Library
- **Backend Testing:** pytest with PostgreSQL integration tests
- **Linting:** ESLint 9.21 + Prettier 3.5.3
- **Type Safety:** TypeScript (frontend), Pydantic (backend)

## API Endpoints

The application provides 40+ REST endpoints organized by functionality:

### Core Prediction Endpoints
- `POST /prediction/{date}` - Create/update daily predictions
- `GET /day/{date}` - Get complete day data (predictions + prices)
- `GET /history` - Retrieve prediction history with metrics
- `GET /metrics` - Get performance metrics and calibration tips

### AI Prediction System
- `POST /ai/predict/{date}` - Generate AI predictions for trading day
- `GET /ai/predictions/{date}` - Retrieve AI predictions with confidence
- `GET /accuracy/ai` - AI prediction accuracy metrics

### Market Data & Suggestions
- `POST /capture/{date}` - Log price checkpoints (open/noon/2PM/close)
- `GET /suggestions/{date}` - Get option strategy suggestions (IC/IB)
- `GET /market-status` - Current market status and SPY price

### Admin & Maintenance
- `GET /admin/scheduler/status` - Scheduler status and job details
- `GET /healthz` - Health check endpoint
- `GET /version` - Application version and build info
- Database fix endpoints for data integrity

## Scheduled Jobs (America/Chicago Timezone)

6 automated jobs handle market data collection:

- **8:00 AM CDT:** AI predictions generation + pre-market capture
- **8:30 AM CDT:** Market open price capture
- **12:00 PM CDT:** Noon price capture  
- **2:00 PM CDT:** 2PM price capture
- **3:00 PM CDT:** Market close + realized high/low calculation
- **Daily:** Health checks and performance metric updates

## Testing Strategy

### Frontend Testing
- **Unit Tests:** Vitest with React Testing Library
- **E2E Tests:** Playwright for cross-browser testing
- **Coverage:** Component rendering, API integration, user flows

### Backend Testing
- **Unit Tests:** pytest with comprehensive endpoint coverage
- **Integration Tests:** PostgreSQL database integration
- **AI System Tests:** GPT-5 and baseline model validation

### Test Files Structure
- `backend/tests/` - Python test suite (15+ test files)
- `tests/` - Playwright e2e tests
- `src/test/` - Frontend unit tests and setup

## Error Handling & Monitoring

### Exception System
- Custom `SPYTrackerException` hierarchy in `backend/app/exceptions.py`
- Comprehensive error handlers for validation, market data, and AI services
- Structured error responses with details and troubleshooting hints

### Health Monitoring
- `/healthz` endpoint with scheduler status
- Database connection monitoring
- AI service availability checks
- Market data provider status

## Environment Configuration

The application uses intelligent environment detection:

### Key Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (production)
- `OPENAI_API_KEY` - GPT-5 API access
- `TIMEZONE` - Default: America/Chicago
- `DEBUG` - Enable debug mode (development)

### Configuration Files
- `backend/app/config.py` - Centralized settings with intelligent defaults
- Environment loading: Root `.env` → `backend/.env` (without override)
- Automatic PostgreSQL detection with SQLite fallback

EOF < /dev/null