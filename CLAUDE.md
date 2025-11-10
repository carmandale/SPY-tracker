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

## Tech Stack & Versions (Verified)

### Frontend Stack
- **React:** 19.0.0 (latest with improved performance)
- **TypeScript:** 5.7.2 
- **Vite:** 6.2.0 (build tool and dev server)
- **Tailwind CSS:** 4.0.9 (styling framework)
- **Recharts:** 2.15.1 (data visualization)
- **Framer Motion:** 12.4.10 (animations)
- **Zod:** 3.24.2 (schema validation)
- **Testing:** Vitest 3.2.4 + Playwright 1.55.0

### Backend Stack
- **FastAPI:** 0.111-0.116 (async web framework)
- **Python:** ≥3.10 (required minimum version)
- **SQLAlchemy:** 2.0+ (ORM with PostgreSQL support)
- **Pydantic:** 2.9-2.12 (data validation)
- **APScheduler:** 3.10+ (job scheduling)
- **OpenAI:** 1.46.0+ (GPT-5 API integration)
- **yfinance:** 0.2.65+ (market data)
- **Testing:** pytest 8.4.1+

### Infrastructure
- **Production:** Render.com with Docker deployment
- **Database:** PostgreSQL (production), SQLite (local fallback)
- **Package Managers:** uv (Python), yarn (Node.js)
- **Build:** Multi-stage Docker with Node.js 20 + Python 3.11

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && uv run uvicorn app.main:app --reload --port 8000`
- **Alternative Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Health Endpoint:** `/healthz` for monitoring and deployment health checks
- **Environment:** Never commit `.env` files; use `.env.example` as template

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Remaining (Nice-to-have):** Service worker configuration for offline support, backup/restore endpoints
- **PWA Status:** Manifest.json configured with app icons, shortcuts, and mobile optimization
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)

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
- **Backend API:** @backend/app/main.py (40+ endpoints with full error handling)
- **Database:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Frontend:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators and regime detection)
- **Performance:** @src/utils/performance.ts (caching, debouncing, lazy loading, web vitals tracking)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system with custom handlers)
- **Testing:** Frontend: Vitest + Playwright E2E, Backend: pytest (configured)
- **AI Configuration:** @backend/app/config.py (OpenAI GPT-5 model settings, reasoning effort controls)

## API Structure & Routing

The backend provides a comprehensive REST API with the following router modules:

### Core API Routers
- **Predictions** (`/prediction/*`) - Daily prediction CRUD operations
- **Market Data** (`/market/*`) - Live SPY pricing and market status
- **AI Predictions** (`/ai/*`) - GPT-5 powered price predictions with confidence scoring
- **Suggestions** (`/suggestions/*`) - Iron Condor/Butterfly option strategy recommendations
- **Admin** (`/admin/*`) - Administrative endpoints for data management
- **Database Fix** (`/database-fix/*`) - Data integrity and weekend data repair tools
- **Scheduler** (`/scheduler/*`) - Job scheduling status and management
- **Health** (`/health`, `/healthz`) - Application health monitoring
- **Version** (`/version`) - Application version and build information

### Key API Features
- **Error Handling:** Comprehensive exception system with standardized error responses
- **CORS:** Configured for frontend-backend communication
- **Static File Serving:** Frontend build served from `/backend/static/`
- **Health Checks:** `/healthz` endpoint for deployment monitoring
- **Database Abstraction:** Supports both PostgreSQL (production) and SQLite (development)

## Available Commands

### Frontend Commands (yarn)
```bash
yarn dev          # Start development server (port 3000)
yarn build        # Production build
yarn preview      # Preview production build
yarn lint         # ESLint code checking
yarn format       # Prettier code formatting
yarn test         # Run Vitest unit tests
yarn test:ui      # Vitest UI mode
yarn test:coverage # Test coverage report
yarn e2e          # Playwright end-to-end tests
```

### Backend Commands (uv)
```bash
# Development mode
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Production mode
cd backend && uv run uvicorn app.main:app --port 8000

# Testing
cd backend && uv run pytest

# Direct Python execution
cd backend && uv run python -m app.main
```

### Legacy Backend Commands (venv)
```bash
# If using virtual environment instead of uv
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000
```
EOF < /dev/null