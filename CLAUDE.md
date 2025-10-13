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

## Current Tech Stack

### Frontend Stack
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0
- **CSS Framework:** Tailwind CSS 4.0.9
- **UI Components:** shadcn/ui components with lucide-react icons
- **State Management:** React hooks and context (React Hook Form + Zod validation)
- **Charts:** Recharts 2.15.1
- **Animations:** Framer Motion 12.4.10
- **Testing:** Vitest 3.2.4, Playwright 1.55.0, Testing Library
- **Linting:** ESLint 9.21.0, Prettier 3.5.3

### Backend Stack
- **Framework:** FastAPI 0.111-0.116 with Uvicorn
- **Database:** SQLAlchemy 2.0 with PostgreSQL (Psycopg2) and SQLite fallback
- **Data Validation:** Pydantic 2.9-2.12
- **Task Scheduler:** APScheduler 3.10
- **Market Data:** yfinance 0.2.65
- **AI Integration:** OpenAI 1.46+ (GPT-5 powered predictions)
- **HTTP Client:** httpx 0.27
- **Data Processing:** pandas 2.3.1, numpy 2.2.6
- **Testing:** pytest 8.4.1
- **Environment:** python-dotenv 1.0

### Development Infrastructure
- **Package Managers:** yarn (frontend), uv (backend)
- **Containerization:** Docker with multi-stage builds
- **Database:** PostgreSQL 16 via Docker Compose (dev), Render managed (prod)
- **Deployment:** Render.com with Docker
- **Monitoring:** Health checks, logging, scheduler status

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Servers
- **Frontend:** Port 3000 - `yarn dev`
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Quick Start:** `bash start.sh` - Automated script that starts both services with proper environment loading

### Database Configuration
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker Compose (port 5433) or SQLite fallback
- **Connection:** Intelligent database detection via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - PostgreSQL migration Issue #13 closed August 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Docker Setup:** `docker-compose up db` for local PostgreSQL with Adminer on port 8080
- **Testing:** Dedicated test database container (port 5434) with tmpfs for speed

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Deployment:** Automated via render.yaml with Docker builds
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Architecture:** FastAPI backend serving static React build (SPA)
- **Health Monitoring:** `/healthz` endpoint with scheduler status
- **Active Jobs:** 6 scheduled jobs running in America/Chicago timezone
- **AI Integration:** GPT-5 powered predictions at 8:00 AM CST daily
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, technical analysis, and reasoning
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data (VIX, ES futures)
- **Technical Indicators:** RSI, MACD, Bollinger Bands, moving averages, volume analysis
- **Baseline Models:** Statistical fallback predictors when AI unavailable
- **Database Integrity:** Automatic data fixes and weekend/future price handling
- **Mobile Optimization:** PWA-ready with responsive design and performance optimizations

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (FastAPI with comprehensive router structure)
- **Database:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Frontend:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators)
- **Performance:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Configuration:** @backend/app/config.py (intelligent database detection)
- **Startup Logic:** @backend/app/startup.py (database init, scheduler setup, AI warmup)

### API Router Structure (9 modules)
- **predictions.py** - Core prediction CRUD operations
- **admin.py** - Administrative and maintenance endpoints
- **market.py** - Market data and status endpoints
- **suggestions.py** - Option strategy suggestions and P&L calculations
- **ai.py** - AI predictions and simulations
- **scheduler.py** - Scheduler management endpoints
- **health.py** - Health monitoring and status checks
- **version.py** - Version information and system status
- **database_fix.py** - Database maintenance and integrity operations

## Development Workflow

### Getting Started
1. **Environment Setup:** Ensure Node.js 18+, Python 3.10+, yarn, and uv are installed
2. **Clone & Install:** `git clone <repo>`, `yarn install`, `cd backend && uv venv && uv pip sync pyproject.toml`
3. **Database Setup:** Run `docker-compose up db` for PostgreSQL or rely on SQLite fallback
4. **Start Development:** Use `bash start.sh` for both services or run individually

### Available Scripts
- **Frontend:** `yarn dev` (port 3000), `yarn build`, `yarn test`, `yarn lint`, `yarn format`
- **Backend:** `uvicorn app.main:app --reload --port 8000` (from backend/.venv)
- **Database:** `docker-compose up db` (PostgreSQL), `docker-compose up test-db` (testing)
- **Testing:** `yarn test` (frontend), `pytest` (backend), `yarn e2e` (end-to-end)

### Environment Variables
- **Root .env:** Backend configuration (DATABASE_URL, OPENAI_API_KEY)
- **Frontend .env.local:** PORT=3000, VITE_API_URL (auto-set in dev)
- **Backend .env:** Additional backend-specific variables if needed
- **Production:** Environment variables managed via Render dashboard

## Testing Strategy

### Frontend Testing
- **Unit Tests:** Vitest with React Testing Library
- **E2E Tests:** Playwright for critical user workflows
- **Component Tests:** Individual component testing with jsdom

### Backend Testing
- **Unit Tests:** pytest with database fixtures
- **Integration Tests:** Full API endpoint testing
- **Database Tests:** PostgreSQL and SQLite compatibility testing

## Deployment Architecture

### Production Environment
- **Platform:** Render.com with Docker deployment
- **Build Process:** Multi-stage Dockerfile (Node.js frontend build + Python backend)
- **Static Serving:** FastAPI serves React build via StaticFiles mount
- **Database:** Managed PostgreSQL with automatic backups
- **Health Monitoring:** `/healthz` endpoint for uptime monitoring

### CI/CD Pipeline
- **Build:** Automated Docker builds on git push
- **Testing:** Automated test suite execution
- **Deployment:** Zero-downtime deployment via Render
- **Monitoring:** Health checks and scheduler job monitoring

## Important Development Notes

### AI Prediction System
- **Model:** GPT-5 with 600 token limit and minimal reasoning effort
- **Fallback:** Statistical baseline model when OpenAI unavailable
- **Schedule:** Daily 8:00 AM CST generation with technical analysis
- **Data Sources:** SPY prices, VIX, ES futures, technical indicators

### Database Intelligence
- **Auto-Detection:** Intelligent PostgreSQL vs SQLite selection based on environment
- **Migration Support:** Automatic schema migrations and data integrity fixes
- **Development:** Docker Compose PostgreSQL with Adminer web interface
- **Testing:** Dedicated test database with tmpfs for performance

### Mobile-First Design
- **Responsive:** Mobile-optimized UI with touch-friendly interactions
- **Performance:** Lazy loading, caching, debouncing for smooth mobile experience
- **PWA Ready:** Manifest and service worker configuration available

### Scheduler System
- **Timezone:** America/Chicago (handles CST/CDT automatically)
- **Jobs:** 6 scheduled jobs for market data collection and AI predictions
- **Resilience:** Job failure handling and automatic retry mechanisms
EOF < /dev/null