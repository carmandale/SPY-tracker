# SPY TA Tracker - Claude Code Instructions

## Project Overview

SPY TA Tracker is a **live production application** that provides AI-powered SPY options trading assistance. It features GPT-5 predictions, automated price tracking, option strategy suggestions (Iron Condors/Butterflies), and comprehensive performance analytics. The application is currently deployed and actively tracking predictions with 41+ historical data points.

### Production Status
- **Status:** ✅ **LIVE IN PRODUCTION**
- **Production URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL (Render managed service)
- **AI Model:** GPT-5 with comprehensive market analysis
- **Deployment Platform:** Render.com with Docker containerization
- **Monitoring:** Health checks via `/health/critical` endpoint

## Architecture Overview

This is a **full-stack TypeScript/Python application** with the following architecture:

### Frontend (React 19 + TypeScript)
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0 with modern ESM builds
- **UI Framework:** Tailwind CSS v4.0.9 with shadcn/ui components
- **Charts & Visualization:** Recharts for price charts and performance metrics
- **Mobile-First:** Optimized for one-handed mobile trading usage
- **PWA Support:** Complete manifest.json configuration with app icons

### Backend (FastAPI + Python)
- **Framework:** FastAPI 0.111+ with Python 3.10+
- **Database:** Dual support for PostgreSQL (production) and SQLite (development)
- **ORM:** SQLAlchemy 2.0 with Pydantic 2.9+ for data validation
- **AI System:** OpenAI GPT-5 integration with comprehensive market analysis
- **Scheduler:** APScheduler for automated price capture (America/Chicago timezone)
- **Market Data:** yfinance integration with real-time SPY data

### API Structure (10 Router Modules)
- **Core APIs:** Predictions, Market Data, AI Endpoints, Option Suggestions
- **Admin APIs:** Database management, health checks, scheduler control
- **Comprehensive Error Handling:** Custom exception system with user-friendly messages

## Project-Specific Configuration

### Package Managers (CRITICAL - DO NOT CHANGE)
- **Frontend:** Use `yarn` (NOT npm) - yarn.lock is committed
- **Backend:** Use `uv` (NOT pip) - uv.lock is committed

### Tech Stack Versions (Current)
- **Frontend:** React 19.0.0, TypeScript 5.7.2, Vite 6.2.0, Tailwind CSS 4.0.9
- **Backend:** FastAPI 0.111+, SQLAlchemy 2.0, Pydantic 2.9+, OpenAI 1.46+
- **Testing:** Vitest 3.2.4 (frontend), pytest 8.4.1 (backend), Playwright 1.55.0 (E2E)
- **AI Model:** GPT-5 (`gpt-5`) with enhanced market analysis capabilities

### Development Commands
- **Frontend:** `yarn dev` (port 3000 with proxy to backend)
- **Backend:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- **Full Stack:** Use `./start.sh` script for complete local setup
- **Production:** `./start-production.sh` for production deployment

### Testing Commands
- **Frontend Tests:** `yarn test` (Vitest with jsdom)
- **Backend Tests:** `cd backend && pytest` 
- **E2E Tests:** `yarn e2e` (Playwright)
- **Linting:** `yarn lint` (ESLint 9.21), `yarn format` (Prettier 3.5.3)

### Database Configuration
- **Production:** PostgreSQL on Render.com (managed service) - ✅ **LIVE**
- **Local Development:** Intelligent detection - PostgreSQL (Docker port 5433) with SQLite fallback
- **Connection:** DATABASE_URL environment variable with automatic detection
- **Migration Status:** ✅ **COMPLETE** - PostgreSQL migration completed August 2025
- **Historical Data:** 41+ AI predictions actively tracked with performance metrics
- **Models:** 4 core tables - DailyPrediction, PriceLog, AIPrediction, ModelPerformance

### Environment Configuration
- **Template:** `.env.example` provides comprehensive configuration guide
- **Security:** Never commit actual `.env` files to version control
- **Required:** OPENAI_API_KEY for AI predictions, DATABASE_URL for persistence
- **Multiple Platforms:** Configured for Render, Vercel, and Docker deployment

### Current Production Status
- **Deployment:** ✅ **LIVE ON RENDER.COM** with Docker containerization
- **URL:** https://spy-tracker.onrender.com
- **Database:** PostgreSQL with 41+ historical predictions
- **AI System:** GPT-5 powered predictions with 8AM CST automated generation
- **Scheduler:** 6 active jobs (pre-market, open, noon, 2PM, close + AI predictions)
- **PWA Ready:** Complete manifest.json and app icons configured
- **Health Monitoring:** `/health/critical` endpoint with comprehensive system checks

### Development Phases Completed
- ✅ **Phase 0-6:** Complete MVP with PostgreSQL migration
- ✅ **AI Enhancement:** GPT-5 integration with market analysis
- ✅ **Production Deployment:** Render.com with health monitoring
- ✅ **PWA Foundation:** Manifest and icons ready (service worker pending)
- 🔄 **Future:** Advanced analytics, backup/restore endpoints

### Core Features (All Production-Ready)

#### AI-Powered Prediction System
- **GPT-5 Integration:** Advanced market analysis with technical indicators (RSI, MACD, Bollinger Bands)
- **Daily Automation:** 8:00 AM CST automated prediction generation with confidence scoring
- **Market Context:** VIX analysis, ES futures data, support/resistance levels, regime detection
- **Prediction Intervals:** 68% confidence bands with calibrated accuracy tracking
- **Fallback System:** Baseline statistical model when AI service unavailable

#### Options Trading Intelligence
- **Strategy Suggestions:** Automated Iron Condor/Iron Butterfly recommendations
- **Multi-Timeframe:** 0DTE, 1-week, and 1-month option strategies
- **Delta Targeting:** Precise strike selection based on predicted ranges and volatility
- **P&L Calculations:** Comprehensive profit/loss analysis with management notes

#### Performance Analytics
- **Accuracy Tracking:** 20-day rolling hit rates and calibration metrics
- **AI vs Manual:** Performance comparison between AI and manual predictions
- **Trend Analysis:** Accuracy improvement detection with alerts
- **Historical Dashboard:** Complete prediction history with searchable interface

#### Market Data & Automation
- **Real-time Integration:** yfinance-powered SPY price capture every trading day
- **Timezone Intelligence:** America/Chicago scheduling with DST handling
- **Market Hours:** Automated open/noon/2PM/close price logging
- **Holiday Detection:** Smart scheduling that respects market holidays

### Key Project Files & Architecture

#### Core Configuration
- **Project Requirements:** @SPY-tracker-PRD.md (comprehensive product specification)
- **Environment Setup:** @.env.example (complete configuration template)
- **Deployment Config:** @render.yaml, @vercel.json, @docker-compose.yml

#### Backend Architecture (@backend/app/)
- **Main Application:** `main.py` - FastAPI app with 10+ routers and static file serving
- **Database Models:** `models.py` - 4 core models with PostgreSQL/SQLite dual support
- **AI Predictor:** `ai_predictor.py` - GPT-5 integration with comprehensive market analysis
- **API Routers:** `routers/` directory - 10 organized router modules
- **Error Handling:** `exceptions.py` - Custom exception hierarchy with user-friendly messages
- **Configuration:** `config.py` - Intelligent database detection and settings management

#### Frontend Architecture (@src/)
- **Main App:** `App.tsx` - React 19 with dark theme and mobile optimization
- **Generated Components:** `components/generated/` - Core UI components
- **API Client:** `utils/apiClient.ts` - Centralized API communication with error handling
- **Performance Utils:** `utils/performance.ts` - Caching, debouncing, lazy loading
- **Schema Validation:** `lib/schemas.ts` - Zod schemas for type-safe data validation

#### Deployment & Operations
- **Health Monitoring:** `backend/app/routers/health.py` - Comprehensive system health checks
- **Production Status:** @DEPLOYMENT_STATUS.md (detailed production environment info)
- **Scripts:** `./start.sh`, `./start-production.sh`, `./monitor.sh` for operations

#### Testing Infrastructure
- **Frontend Tests:** Vitest with jsdom environment, React Testing Library
- **Backend Tests:** pytest with comprehensive database and API testing
- **E2E Tests:** Playwright for full application testing
- **Test Config:** `vitest.config.ts`, `backend/tests/conftest.py`
EOF < /dev/null