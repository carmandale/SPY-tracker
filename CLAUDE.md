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

### Tech Stack Versions (Current)
- **Frontend:** React 19.0.0, TypeScript 5.7.2, Vite 6.2.0
- **Backend:** FastAPI 0.111-0.115, SQLAlchemy 2.0, Python 3.10+
- **UI Framework:** Tailwind CSS 4.0.9 with shadcn/ui components
- **Charts:** Recharts 2.15.1
- **Testing:** Vitest 3.2.4 (frontend), Playwright 1.55.0 (E2E), pytest (backend)
- **AI:** GPT-5 (gpt-5 model) via OpenAI API

### Database Policy (Production)
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Environment:** Never commit `.env` files; use `.env.example` as template
- **Intelligent Detection:** Uses database_utils.py for automatic database selection

### Current Development Phase
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Completed:** Phases 0-6 including PostgreSQL migration
- **PWA Ready:** ✅ Complete manifest.json with icons and shortcuts
- **Remaining (Nice-to-have):** Backup/restore endpoints
- **Active Jobs:** 6 scheduled jobs running successfully (8AM AI predictions verified)
- **Current Version:** Backend 2.0.0

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and comprehensive market analysis
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data, VIX integration
- **Mobile-Optimized PWA:** Complete progressive web app with manifest and service-ready design
- **Advanced Analytics:** Technical indicators (RSI, MACD, Bollinger Bands), support/resistance levels
- **Error Handling:** Comprehensive exception system with user-friendly error responses
- **Health Monitoring:** Production health checks and monitoring endpoints

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (40+ endpoints with full error handling)
- **Database Models:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Frontend App:** @src/App.tsx (React 19, mobile-optimized, loading states)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with advanced technical analysis)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Configuration:** @backend/app/config.py (settings with intelligent database detection)
- **PWA Manifest:** @public/manifest.json (complete PWA configuration)
- **Testing Setup:** @vitest.config.ts, @eslint.config.js (modern testing stack)

### API Router Structure
- **Predictions:** @backend/app/routers/predictions.py (core prediction CRUD)
- **AI Endpoints:** @backend/app/routers/ai.py (GPT-5 prediction system)
- **Market Data:** @backend/app/routers/market.py (live price feeds)
- **Suggestions:** @backend/app/routers/suggestions.py (option strategy recommendations)
- **Admin Tools:** @backend/app/routers/admin.py (database management)
- **Health Checks:** @backend/app/routers/health.py (monitoring endpoints)
- **Scheduler:** @backend/app/routers/scheduler.py (job management)
- **Database Fix:** @backend/app/routers/database_fix.py (data integrity tools)

### Development Commands

#### Frontend Commands
```bash
yarn dev          # Start development server (port 3000)
yarn build        # Production build
yarn test         # Run Vitest tests
yarn test:ui      # Run tests with UI
yarn test:coverage # Run tests with coverage
yarn lint         # ESLint linting
yarn format      # Prettier formatting
yarn e2e         # Playwright E2E tests
```

#### Backend Commands
```bash
cd backend
source .venv/bin/activate  # Activate virtual environment
uvicorn app.main:app --reload --port 8000  # Start development server
uv add <package>          # Add Python dependency
uv remove <package>       # Remove Python dependency
pytest                    # Run backend tests
```

#### Environment Files
- **Frontend:** `.env.production` (for production builds)
- **Backend:** `backend/.env.example` (template for local development)
- **PostgreSQL:** `backend/.env.postgres.example` (PostgreSQL-specific config)
- **Root:** `.env.example` (main environment template)

### Production Deployment Configuration

#### Render.com (Current Deployment)
- **Service Type:** Docker web service
- **Health Check:** `/healthz` endpoint
- **Auto Deploy:** Enabled from main branch
- **Environment Variables:** `OPENAI_API_KEY`, `DATABASE_URL` (set via dashboard)

#### Docker Configuration
- **Dockerfile:** Multi-stage build with Python backend and Node.js frontend
- **Static Files:** Frontend build served directly by FastAPI
- **Port:** 8000 (production)

### AI System Details

#### GPT-5 Configuration
- **Model:** `gpt-5` (configurable via `openai_model` setting)
- **Reasoning Effort:** `minimal` (configurable)
- **Max Tokens:** 600 (configurable)
- **Temperature:** 0.2 (low for consistent predictions)
- **Prompt Version:** v3.0.0 (tracked for reproducibility)

#### Prediction System
- **Checkpoints:** Open, Noon, 2PM, Close (all Eastern Time)
- **Confidence Intervals:** 68% confidence bands for each prediction
- **Fallback:** Statistical baseline model when OpenAI API unavailable
- **Technical Analysis:** RSI, MACD, Bollinger Bands, support/resistance levels
- **Market Context:** VIX, ES futures, volume analysis, regime detection

### Database Schema

#### Core Tables
- **daily_predictions:** User and AI predictions with accuracy tracking
- **price_logs:** Scheduled price captures at market checkpoints
- **ai_predictions:** Detailed AI prediction data with confidence intervals
- **baseline_models:** Statistical model configurations
- **model_performance:** Daily performance metrics by model type

#### Migration System
- **Current:** PostgreSQL primary, SQLite fallback
- **Migration Scripts:** @backend/app/migrations/ directory
- **Database Utils:** Intelligent database detection and connection handling

### Testing Strategy

#### Frontend Testing
- **Unit Tests:** Vitest with React Testing Library
- **E2E Tests:** Playwright for full user workflows
- **Coverage:** `yarn test:coverage` for detailed reports

#### Backend Testing  
- **Unit Tests:** pytest for API endpoints and business logic
- **Database Tests:** PostgreSQL and SQLite compatibility testing
- **Integration Tests:** Full API workflow testing

### Security & Best Practices

- **API Keys:** Never committed, managed via environment variables
- **CORS:** Configured for frontend origin, restricted in production
- **Exception Handling:** Comprehensive error responses without exposing internals
- **Rate Limiting:** Consider implementing for production AI API usage
- **Data Validation:** Pydantic models for all API inputs/outputs

### Performance Optimization

#### Frontend Optimizations
- **Bundle Size:** <791KB optimized production build
- **Lazy Loading:** Components and routes loaded on demand
- **Caching:** API response caching with TTL
- **Debouncing:** User input and API calls optimized
- **Mobile-First:** Touch-optimized interface design

#### Backend Optimizations
- **Connection Pooling:** SQLAlchemy connection management
- **Scheduled Jobs:** APScheduler for automated data collection
- **Error Recovery:** Graceful fallbacks for market data and AI services
- **Health Checks:** Monitoring endpoints for production deployment

### Troubleshooting

#### Common Issues
1. **Database Connection:** Check DATABASE_URL and ensure PostgreSQL container is running
2. **AI Predictions:** Verify OPENAI_API_KEY is set and has sufficient credits
3. **Scheduler Jobs:** Check timezone configuration (America/Chicago)
4. **Frontend Build:** Ensure all dependencies installed with `yarn install`
5. **Static Files:** Production build must be generated before backend serves frontend

#### Debug Commands
```bash
# Check database status
python -c "from backend.app.config import settings; print(settings.get_resolved_database_config())"

# Test AI predictions
python test_gpt5_simple.py

# Verify production health
curl https://spy-tracker.onrender.com/healthz
```
EOF < /dev/null