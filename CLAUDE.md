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
- **No Global Agent-OS:** This project does not reference global ~/.agent-os standards - all configuration is project-local

## Project-Specific Configuration

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed
- **Project Exception:** This project uses yarn instead of npm organizational standard for historical reasons

### Development Servers
- **Frontend:** Port 3000 - `yarn dev` (Vite 6.2.0 dev server)
- **Backend:** Port 8000 - `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Proxy Configuration:** Vite proxy configured for API routes (/day, /ai, /metrics, /suggestions, /market-status, /accuracy)

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

### Key Implemented Features (All Working)
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring, reasoning, and 68% confidence intervals
- **Advanced Technical Analysis:** RSI, MACD, Bollinger Bands, moving averages, volume analysis, VIX integration
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance (6 active scheduled jobs)
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips, model performance comparison
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends (41+ predictions tracked)
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement (Recharts integration)
- **Market Data Integration:** Live SPY pricing, market status, volatility data, support/resistance levels
- **Baseline Models:** Statistical fallback predictions when AI service unavailable
- **Database Management:** Health monitoring, data integrity fixes, migration support

### Key Project Files
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Backend API:** @backend/app/main.py (52+ endpoints across 9 routers with comprehensive error handling)
- **Database:** @backend/app/models.py (supports both SQLite and PostgreSQL)
- **Frontend:** @src/App.tsx (React 19.0.0, mobile-optimized with Vite 6.2.0, TypeScript 5.7.2)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with advanced technical analysis including RSI, MACD, Bollinger Bands, volume analysis)
- **Performance:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system with custom SPYTrackerException types)
- **Testing:** Vitest for frontend, pytest for backend, Playwright for E2E testing
- **API Version:** v2.0.0 (FastAPI application)

## Technical Architecture Details

### API Routers & Endpoints (9 Total Routers)
- **predictions.router:** Core prediction CRUD operations
- **admin.router:** Administrative functions and data management  
- **market.router:** Market data and status endpoints
- **suggestions.router:** Options strategy recommendations (IC/IB)
- **ai.router:** AI prediction generation and management
- **scheduler.router:** Job scheduling and monitoring
- **version.router:** Application version and health status
- **database_fix.router:** Database maintenance and integrity fixes
- **health.router:** Health checks and monitoring endpoints

### Database Architecture
- **Models:** DailyPrediction, PriceLog, AIPrediction, BaselineModel, ModelPerformance
- **Dual Database Support:** PostgreSQL (production) and SQLite (development/fallback)
- **Migration System:** SQL-based migrations with runner scripts
- **Data Integrity:** Automated duplicate cleanup and validation

### Frontend Architecture  
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with hot module replacement
- **Styling:** Tailwind CSS v4.0.9 with custom design system
- **Components:** shadcn/ui component library integration
- **State Management:** React hooks and context (no external state library)
- **Charts:** Recharts for data visualization
- **Forms:** React Hook Form with Zod validation
- **Animations:** Framer Motion 12.4.10

### AI & Market Data Integration
- **Primary AI:** OpenAI GPT-5 (gpt-5-turbo-20241121) with reasoning effort configuration
- **Fallback Models:** Statistical baseline models for service resilience  
- **Market Data:** yfinance integration for real-time SPY pricing
- **Technical Indicators:** Comprehensive TA including RSI, MACD, Bollinger Bands, moving averages
- **External Data:** VIX volatility, ES futures correlation analysis
- **Prompt Versioning:** v3.0.0 with enhanced expert analysis and regime detection

### Performance & Monitoring
- **Caching:** Memory cache with TTL for API responses
- **Performance Utilities:** Debouncing, throttling, lazy loading (performance.ts)
- **Error Handling:** Structured exception hierarchy with detailed logging
- **Health Monitoring:** Multiple health check endpoints with scheduler status
- **Web Vitals:** FCP, LCP, FID, CLS, TTFB tracking capabilities

### Development & Testing
- **Package Management:** yarn (frontend), uv (backend) with committed lock files
- **Code Quality:** ESLint 9.21, Prettier 3.5.3, TypeScript strict mode disabled for rapid prototyping
- **Testing Stack:** 
  - Frontend: Vitest with jsdom environment and Testing Library
  - Backend: pytest with fixtures and async support  
  - E2E: Playwright with data integrity test suites
- **Development Proxy:** Vite proxy for seamless API integration during development
EOF < /dev/null