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
- **Backend:** Use `uv` (NOT pip) - uv.lock and pyproject.toml committed

### Tech Stack (Current Versions)
- **Frontend:** React 19.0.0, TypeScript 5.7.2, Vite 6.2.0, Tailwind CSS 4.0.9
- **Backend:** FastAPI 0.111+, Python >=3.10, SQLAlchemy 2.0+, Pydantic 2.9+
- **AI/ML:** OpenAI API (GPT-5), yfinance 0.2.65+, pandas 2.3.1+
- **Testing:** Vitest 3.2.4, Playwright 1.55.0, pytest 8.4.1
- **Database:** PostgreSQL (production), SQLite (fallback)

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Full Stack:** Use API proxy in vite.config.ts for local development

### Available Scripts
**Frontend:**
- `yarn dev` - Start development server with hot reload
- `yarn build` - Production build with static file generation
- `yarn test` - Run Vitest unit tests
- `yarn test:ui` - Run Vitest with UI interface
- `yarn lint` - ESLint code checking
- `yarn format` - Prettier code formatting
- `yarn e2e` - Run Playwright end-to-end tests

**Backend:**
- `uv sync` - Install dependencies (replaces pip install)
- `uv run pytest` - Run Python tests
- `uv run uvicorn app.main:app --reload` - Start development server

### Testing Infrastructure
- **Unit Tests:** Vitest with jsdom environment, React Testing Library
- **E2E Tests:** Playwright for critical user flows and data integrity
- **Python Tests:** pytest with test database isolation
- **Test Files:** `*.test.ts`, `*.spec.ts`, and `test_*.py` patterns
- **Coverage:** Vitest coverage reporting configured
- **CI/CD:** GitHub Actions integration (tests run on PR/push)

### Database Configuration
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** Intelligent database detection with PostgreSQL/SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - PostgreSQL migration completed
- **Historical Data:** 41+ predictions actively tracked with AI comparison
- **Environment:** Root `.env` loads first, then `backend/.env` without override
- **Intelligence:** `use_intelligent_database_detection: true` for auto-config

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **Production URL:** https://spy-tracker.onrender.com
- **Repository:** https://github.com/carmandale/SPY-tracker
- **Database:** PostgreSQL (Render managed service)
- **Deployment:** Docker-based with render.yaml configuration
- **Health Check:** `/healthz` endpoint configured
- **PWA Ready:** Manifest, icons, and service worker configured
- **Active Jobs:** Automated scheduler with 8AM GPT-5 AI predictions

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry with bias, volatility context, key levels, and notes
- **AI Predictions:** GPT-5 powered predictions with confidence intervals and expert reasoning
- **Technical Analysis:** RSI, MACD, Bollinger Bands, volume analysis, support/resistance
- **Automated Data Collection:** Scheduled capture at Open/Noon/2PM/Close via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics with calibration tips and accuracy trends
- **Historical Analysis:** Complete prediction history with AI vs manual comparison
- **Real-time Visualization:** Recharts integration with predicted bands vs actual movement
- **Market Data Integration:** Live SPY, VIX, ES futures with market status detection
- **Error Handling:** Comprehensive exception system with user-friendly error responses
- **Mobile Optimization:** PWA-ready with responsive design and performance optimization

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with exception handling)
- **Database Models:** @backend/app/models.py (DailyPrediction, AIPrediction, PriceLog)
- **Database Utils:** @backend/app/database_utils.py (intelligent detection & config)
- **Frontend Root:** @src/App.tsx (React 19, mobile-first, PWA-ready)
- **AI Predictor:** @backend/app/ai_predictor.py (GPT-5 with prompt v3.0.0)
- **Baseline Model:** @backend/app/baseline_model.py (statistical fallback)
- **AI Endpoints:** @backend/app/routers/ai.py (prediction API routes)
- **AI Service:** @backend/app/ai_prediction_service.py (prediction management)
- **Scheduler:** @backend/app/scheduler.py (APScheduler with America/Chicago timezone)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, web vitals)
- **Exception System:** @backend/app/exceptions.py (custom SPYTrackerException hierarchy)
- **API Schemas:** @backend/app/schemas.py (Pydantic models for validation)
- **Configuration:** @backend/app/config.py (intelligent environment loading)

## AI Prediction System Details

### Current AI Configuration
- **Model:** GPT-5 (gpt-5) with reasoning effort "minimal"
- **Prompt Version:** v3.0.0 (comprehensive expert analysis)
- **API Provider:** OpenAI API with chat completions
- **Fallback:** Statistical baseline model for reliability
- **Schedule:** Automated 8:00 AM CST predictions
- **Checkpoints:** Open, Noon, 2PM, Close price predictions
- **Technical Analysis:** RSI, MACD, Bollinger Bands, volume analysis
- **Market Data:** SPY, VIX, ES futures integration
- **Confidence Intervals:** 68% prediction intervals with calibration
- **Error Tracking:** Prediction accuracy metrics and improvement suggestions

### Performance Optimization
- **Frontend:** React 19 concurrent features, lazy loading, code splitting
- **Caching:** API response caching with TTL, memory optimization
- **Bundle Size:** Production build <200KB target
- **Mobile:** Touch-optimized, viewport-fit=cover, PWA manifest
- **Error Boundaries:** Comprehensive error handling with user-friendly messages
- **Loading States:** Skeleton components and loading animations

## Development Workflow

### Getting Started
1. Clone repository: `git clone https://github.com/carmandale/SPY-tracker`
2. Frontend setup: `yarn install && yarn dev`
3. Backend setup: `cd backend && uv sync && source .venv/bin/activate`
4. Database: Automatic detection (PostgreSQL Docker or SQLite fallback)
5. Environment: Copy `.env.example` to `.env` and configure

### Making Changes
1. Always use TodoWrite tool for task tracking
2. Follow established patterns in component and API design
3. Run tests before committing: `yarn test && uv run pytest`
4. Format code: `yarn format`
5. Test E2E flows: `yarn e2e`

### Deployment
- **Production:** Automatic deployment to Render on main branch push
- **Health Check:** Monitor `/healthz` endpoint
- **Logs:** Use Render dashboard for production monitoring
- **Database:** Managed PostgreSQL on Render with backup

EOF < /dev/null