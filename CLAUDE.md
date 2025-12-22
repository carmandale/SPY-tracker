# SPY TA Tracker - Claude Code Instructions

> **Project Status:** ✅ LIVE IN PRODUCTION  
> **URL:** https://spy-tracker.onrender.com  
> **Database:** PostgreSQL (Render managed service)  
> **Last Updated:** December 22, 2024  

## 📋 Project Overview

SPY TA Tracker is a **mobile-first options trading assistant** that helps experienced traders track their SPY predictions and receive AI-powered iron condor/butterfly suggestions. The application features GPT-5 powered price predictions, automated market data collection, and comprehensive performance analytics.

## 🔗 Agent OS Documentation

### Product Context
- **Mission & Vision:** @.agent-os/product/mission.md
- **Technical Architecture:** @.agent-os/product/tech-stack.md
- **Development Roadmap:** @.agent-os/product/roadmap.md
- **Decision History:** @.agent-os/product/decisions.md

### Development Standards
- **Code Style:** @~/.agent-os/standards/code-style.md
- **Best Practices:** @~/.agent-os/standards/best-practices.md

### Project Management
- **Active Specs:** None - all core features completed
- **Production URL:** https://spy-tracker.onrender.com (**LIVE**)
- **Remaining Work:** PWA configuration, backup/restore endpoints (nice-to-have)
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

## 🛠️ Technical Stack

### Frontend
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0
- **UI Framework:** Tailwind CSS 4.0.9
- **Components:** shadcn/ui with Lucide icons
- **Charts:** Recharts 2.15.1
- **Forms:** React Hook Form with Zod validation
- **Testing:** Vitest 3.2.4 + Playwright 1.55.0 (227 test files)

### Backend
- **Framework:** FastAPI 0.111+ with Uvicorn
- **Database:** SQLAlchemy 2.0 + PostgreSQL 16
- **AI Integration:** OpenAI GPT-5 with technical analysis
- **Scheduling:** APScheduler 3.10 (6 active jobs)
- **Market Data:** yfinance 0.2.65+
- **Testing:** pytest 8.4.1+ (15 test files)
- **API Endpoints:** 49 endpoints across 9 router modules

### Package Managers (CRITICAL)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Development Commands
- **Frontend:** `yarn dev` (Port 3000)
- **Backend:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Full Stack:** `./start.sh` (starts PostgreSQL + both servers)
- **Production:** `./start-production.sh`

### Database Configuration
- **Production:** PostgreSQL on Render (managed service) - **LIVE** ✅
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via `DATABASE_URL` environment variable
- **Migration Status:** **COMPLETE** - Issue #13 closed August 16, 2025
- **Historical Data:** 41+ predictions loaded and actively tracking
- **Intelligent Detection:** Automatic database type detection with fallback
- **Environment Files:** 
  - `.env.example` (template)
  - `backend/.env.example` (backend-specific)
  - Never commit `.env` files with real credentials

### Production Environment
- **Status:** **LIVE IN PRODUCTION** on Render.com ✅
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **Health Check:** `/healthz` endpoint
- **Deployment:** Docker-based with render.yaml configuration
- **Scheduler:** 6 jobs running in America/Chicago timezone:
  - 8:00 AM: AI Predictions + Pre-market capture
  - 8:30 AM: Market Open capture
  - 12:00 PM: Noon price capture
  - 2:00 PM: 2PM price capture
  - 3:00 PM: Market Close capture
- **Completed Phases:** 0-6 including PostgreSQL migration
- **Remaining (Nice-to-have):** PWA configuration, backup/restore endpoints

### ✅ Implemented Features (All Working)

#### Core Functionality
- **Morning Predictions:** Form-based entry of low/high predictions with bias, volatility context, and notes
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and comprehensive reasoning
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends

#### Technical Features
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data, VIX tracking
- **AI Technical Analysis:** RSI, MACD, Bollinger Bands, moving averages, support/resistance
- **Advanced Error Handling:** Comprehensive exception system with user-friendly messages
- **Mobile Optimization:** Touch-friendly interface with loading states and skeletons
- **Performance Optimization:** Caching, debouncing, lazy loading
- **Health Monitoring:** System health checks and automated recovery

### 📁 Key Project Files

#### Documentation
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **README:** @README.md (quick start guide)

#### Backend Core
- **Main Application:** @backend/app/main.py (FastAPI app with 49 endpoints)
- **Database Models:** @backend/app/models.py (PostgreSQL/SQLite support)
- **Configuration:** @backend/app/config.py (intelligent database detection)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 with comprehensive technical analysis)
- **Error Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Scheduler:** @backend/app/scheduler.py (market hours automation)

#### Backend API Routers
- **Predictions:** @backend/app/routers/predictions.py
- **AI Endpoints:** @backend/app/routers/ai.py
- **Market Data:** @backend/app/routers/market.py
- **Suggestions:** @backend/app/routers/suggestions.py
- **Admin Tools:** @backend/app/routers/admin.py
- **Health Checks:** @backend/app/routers/health.py
- **Version Info:** @backend/app/routers/version.py

#### Frontend Core
- **Main App:** @src/App.tsx (React 19, mobile-optimized)
- **Main Component:** @src/components/generated/SPYTaTrackerApp.tsx
- **API Client:** @src/utils/apiClient.ts (error handling, retries)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Schemas:** @src/lib/schemas.ts (Zod validation)

#### Configuration
- **Vite Config:** @vite.config.ts (development proxy, build settings)
- **Vitest Config:** @vitest.config.ts (testing framework)
- **TypeScript:** @tsconfig.json (strict type checking)
- **Tailwind:** Uses built-in CSS config
- **Docker:** @Dockerfile, @docker-compose.yml
- **Render Deploy:** @render.yaml

#### Environment
- **Templates:** @.env.example, @backend/.env.example
- **Package Management:** @package.json, @backend/pyproject.toml
- **Lock Files:** @yarn.lock, @backend/uv.lock