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
- **Frontend:** Port 3000 - `yarn dev` (Vite 6.2.0)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Tech Stack (Current Versions)
- **Frontend:** React 19.0.0, TypeScript 5.7.2, Vite 6.2.0, Tailwind CSS 4.0.9
- **Backend:** FastAPI 0.111+, Python 3.10+, SQLAlchemy 2.0, Pydantic 2.9+
- **AI System:** GPT-5 (configurable), OpenAI API 1.46.0+
- **Database:** PostgreSQL (production), SQLite (development fallback)
- **Testing:** Vitest 3.2.4 (frontend), pytest 8.4.1+ (backend), Playwright 1.55.0 (E2E)
- **UI Components:** shadcn/ui (New York style), Lucide React icons, Framer Motion 12.4.10

### Database Configuration
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** Intelligent database detection with PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Auto-Detection:** System automatically detects available database (PostgreSQL preferred, SQLite fallback)

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Branch:** Main branch for production deployments
- **Deployment:** Docker-based deployment via render.yaml configuration
- **Health Check:** /healthz endpoint for monitoring
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)
- **PWA Ready:** Manifest and icons configured (service worker pending)

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, reasoning, and prediction intervals
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips, model performance comparison
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement using Recharts
- **Market Data Integration:** Live SPY pricing, market status, volatility data, VIX integration
- **Comprehensive Error Handling:** Custom exception system with user-friendly error messages
- **Mobile-First Design:** Responsive design optimized for mobile trading workflows
- **Advanced AI Analysis:** Technical indicators (RSI, MACD, Bollinger Bands), market regime detection, sentiment analysis
- **Baseline Model Fallback:** Statistical baseline predictions when AI service unavailable

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with full error handling)
- **Database Models:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Frontend App:** @src/App.tsx (React 19 entry point)
- **Main UI Component:** @src/components/generated/SPYTaTrackerApp.tsx (main app interface)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical analysis)
- **AI Endpoints:** @backend/app/routers/ai.py (AI prediction API routes)
- **Database Config:** @backend/app/config.py (intelligent database detection)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **API Client:** @src/utils/apiClient.ts (frontend API communication)
- **Schemas:** @src/lib/schemas.ts (TypeScript data validation)
- **Component Library:** @components.json (shadcn/ui configuration)

### Available Scripts & Commands

#### Frontend (run from root directory)
- `yarn dev` - Start development server (Vite) on port 3000
- `yarn build` - Build production bundle
- `yarn test` - Run Vitest unit tests
- `yarn test:ui` - Run tests with UI interface
- `yarn test:coverage` - Run tests with coverage report
- `yarn e2e` - Run Playwright E2E tests
- `yarn lint` - Run ESLint
- `yarn format` - Format code with Prettier
- `yarn preview` - Preview production build

#### Backend (run from backend/ directory)
- `uv run uvicorn app.main:app --reload --port 8000` - Start development server
- `uv run pytest` - Run Python unit tests
- `uv add [package]` - Add new Python dependency
- `uv sync` - Sync dependencies from uv.lock

#### Docker & Database
- `docker-compose up -d` - Start PostgreSQL container (port 5433)
- `docker-compose down` - Stop PostgreSQL container
- `./monitor.sh` - Check system health (production)
- `./restart.sh` - Restart production services
- `./start-production.sh` - Start production deployment

### Environment Configuration

#### Required Environment Variables
- `DATABASE_URL` - Database connection string (auto-detected if not set)
- `OPENAI_API_KEY` - OpenAI API key for GPT predictions
- `TIMEZONE` - Trading timezone (default: "America/Chicago")

#### Development Setup
1. Clone repository
2. Install frontend: `yarn install`
3. Setup backend: `cd backend && uv sync`
4. Start PostgreSQL: `docker-compose up -d` (optional - SQLite fallback available)
5. Start backend: `cd backend && uv run uvicorn app.main:app --reload --port 8000`
6. Start frontend: `yarn dev`
7. Access application at http://localhost:3000

### Production Deployment (Render.com)
- **Service Type:** Docker web service
- **Health Check:** /healthz endpoint
- **Auto Deploy:** Enabled on main branch
- **Environment:** Oregon region, starter plan
- **Configuration:** render.yaml defines deployment settings
- **Static Files:** Backend serves built frontend assets

### Testing Strategy
- **Frontend:** Vitest for unit tests, Playwright for E2E tests
- **Backend:** pytest for API and database tests
- **Coverage:** Available for both frontend and backend
- **CI/CD:** Configured for automated testing on deployment

### API Architecture
- **Base URL:** `/` for frontend routes, API routes under various endpoints
- **Error Handling:** Standardized error responses with SPYTrackerException system
- **Validation:** Pydantic schemas for request/response validation
- **Documentation:** OpenAPI/Swagger documentation available at `/docs`
- **CORS:** Configured for frontend-backend communication

### Key Development Notes
- **Timezone:** All times in America/Chicago (CST/CDT) for trading hours
- **Database Migration:** Completed successfully from SQLite to PostgreSQL
- **AI Model:** Currently using GPT-5, configurable in backend/app/config.py
- **Market Data:** Real-time SPY data via yfinance, with VIX integration
- **Scheduling:** APScheduler handles automated price capture and predictions
- **Mobile First:** UI optimized for mobile trading workflows
- **Production Ready:** Comprehensive error handling, logging, and monitoring

EOF < /dev/null