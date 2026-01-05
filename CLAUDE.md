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

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Intelligent Detection:** Automated database type detection with fallback support

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints
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
- **Health Monitoring:** Critical health checks and data integrity monitoring
- **Error Handling:** Comprehensive exception system with structured error responses
- **Testing Framework:** Vitest (frontend), pytest (backend), Playwright (E2E) configured
- **Performance Optimization:** Caching, debouncing, lazy loading, memory management

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with full error handling)
- **Database Models:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Health Monitoring:** @backend/app/routers/health.py (critical system health checks)
- **Configuration:** @backend/app/config.py (intelligent environment detection)
- **Baseline Model:** @backend/app/baseline_model.py (statistical fallback predictions)
- **API Routes:** @backend/app/routers/ (modular endpoint organization)

## Testing & Quality Assurance

### Testing Framework
- **Frontend Testing:** Vitest with React Testing Library and jsdom
- **Backend Testing:** pytest with database fixtures and integration tests
- **E2E Testing:** Playwright for full user journey testing
- **Data Integrity:** Automated tests for weekend data and future prices validation

### Code Quality Tools
- **Frontend Linting:** ESLint 9.21 with TypeScript support
- **Code Formatting:** Prettier 3.5.3
- **Type Checking:** TypeScript 5.7.2 with strict configuration
- **Build Tool:** Vite 6.2.0 with React plugin

### Performance Monitoring
- **Web Vitals:** FCP, LCP, FID, CLS tracking
- **API Performance:** Response time monitoring with debug logging
- **Memory Management:** Intelligent caching with TTL
- **Bundle Optimization:** Lazy loading and code splitting

## Environment Configuration

### Environment Variables (Critical)
- **OPENAI_API_KEY:** Required for AI predictions (GPT-5)
- **DATABASE_URL:** PostgreSQL connection string for production
- **VITE_API_URL:** Frontend API base URL configuration

### Development Environment Setup
1. **Prerequisites:** Node.js 20+, Python 3.11+, Docker (optional)
2. **Frontend Setup:** `yarn install` (uses yarn.lock)
3. **Backend Setup:** `cd backend && uv sync` (uses uv.lock)
4. **Database:** Automatic detection of PostgreSQL/SQLite

### Production Deployment
- **Platform:** Render.com with Docker containers
- **Database:** Managed PostgreSQL service
- **Build Process:** Multi-stage Docker build (Node.js + Python)
- **Health Checks:** `/healthz` endpoint with comprehensive monitoring
- **Auto-Deploy:** Enabled from main branch

## AI & Analytics Features

### AI Prediction System
- **Model:** GPT-5 (gpt-5-turbo-20241121) with reasoning effort
- **Prompt Version:** v3.0.0 (tracked for reproducibility)
- **Technical Analysis:** RSI, MACD, Bollinger Bands, moving averages
- **Market Context:** VIX, ES futures, support/resistance levels
- **Fallback System:** Baseline statistical model when AI unavailable
- **Confidence Intervals:** 68% prediction intervals for risk assessment

### Data Sources & Integrations
- **Market Data:** yfinance for SPY, VIX, and ES futures data
- **Scheduling:** APScheduler with America/Chicago timezone
- **Price Capture:** Automated at Open/Noon/2PM/Close (ET)
- **Historical Analysis:** 5-day lookback with technical indicator calculation

## Architecture & Patterns

### Backend Architecture
- **API Framework:** FastAPI 0.111+ with automatic OpenAPI documentation
- **Database ORM:** SQLAlchemy 2.0 with async support
- **Validation:** Pydantic 2.9+ for request/response schemas
- **Error Handling:** Custom exception hierarchy with structured responses
- **Modular Design:** Router-based endpoint organization

### Frontend Architecture
- **Framework:** React 19 with TypeScript and Vite
- **Styling:** Tailwind CSS v4.0.9 with custom design system
- **State Management:** React hooks and context patterns
- **Component Library:** shadcn/ui with Framer Motion animations
- **Charts:** Recharts for data visualization

### Security & Best Practices
- **CORS Configuration:** Restricted origins for production
- **Environment Separation:** Clear development vs production configs
- **Secret Management:** Environment variables with secure defaults
- **Input Validation:** Comprehensive Zod schemas and Pydantic models
- **Error Boundaries:** Graceful error handling and user feedback

## Monitoring & Observability

### Health Monitoring
- **Critical Health Check:** `/health/critical` endpoint
- **Data Integrity:** Weekend data and future price validation
- **Scheduler Health:** Job status and execution monitoring
- **AI Accuracy Tracking:** Prediction error analysis and trend detection

### Logging & Debugging
- **Structured Logging:** Comprehensive request/response logging
- **Token Usage:** OpenAI API usage tracking and optimization
- **Database Queries:** SQL query logging for performance analysis
- **Error Tracking:** Detailed exception information with context

## Development Workflow

### Branch Strategy
- **Main Branch:** Production-ready code with auto-deploy
- **Feature Branches:** Descriptive naming with task context
- **Testing:** Required before merge to main

### Deployment Process
1. **Code Push:** Git push triggers Render auto-deploy
2. **Docker Build:** Multi-stage build with optimized layers
3. **Health Check:** Automatic validation of deployed services
4. **Monitoring:** Real-time health and performance tracking

### Maintenance Tasks
- **Data Cleanup:** Automated removal of invalid weekend/future data
- **Performance Review:** Regular analysis of prediction accuracy
- **Database Health:** Periodic integrity checks and optimization
- **Dependency Updates:** Regular security and feature updates