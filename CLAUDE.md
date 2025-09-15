# SPY TA Tracker - Claude Code Instructions

## Project Overview

**SPY TA Tracker** is a mobile-first options trading assistant that helps experienced traders track their SPY predictions and receive data-driven iron condor/butterfly suggestions. The application combines manual prediction tracking with AI-powered price predictions using GPT-5.

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
- **Quick Start:** Use `./start.sh` to run both servers automatically

### Database Policy
- **Production:** PostgreSQL on Render (managed service) - **LIVE**
- **Local Development:** PostgreSQL via Docker (port 5433) or SQLite fallback
- **Connection:** Set via DATABASE_URL environment variable
- **Intelligent Detection:** Database configuration auto-detects available databases
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
- **AI Predictions:** GPT-5 powered price predictions with confidence scoring and comprehensive reasoning
- **Automated Data Collection:** Scheduled capture of Open/Noon/2PM/Close prices via yfinance
- **Option Suggestions:** Iron Condor/Butterfly recommendations for 0DTE, 1W, 1M horizons
- **Performance Tracking:** 20-day rolling metrics, range hit percentage, calibration tips
- **Historical Analysis:** Complete prediction history with accuracy metrics and trends
- **Real-time Visualization:** Charts showing predicted bands vs actual price movement
- **Market Data Integration:** Live SPY pricing, market status, volatility data (VIX, ES futures)
- **Technical Analysis:** RSI, MACD, Bollinger Bands, moving averages, support/resistance
- **Baseline Fallback:** Statistical baseline model when AI predictions fail

## Technical Stack

### Frontend
- **Framework:** React 19.0.0 with TypeScript 5.7.2
- **Build Tool:** Vite 6.2.0
- **Styling:** Tailwind CSS 4.0.9 with @tailwindcss/vite
- **UI Components:** shadcn/ui with lucide-react icons
- **State Management:** React hooks and context
- **Forms:** React Hook Form with Zod validation
- **Charts:** Recharts for data visualization
- **Animation:** Framer Motion
- **Testing:** Vitest with @testing-library/react, Playwright for E2E

### Backend
- **Framework:** FastAPI 0.111+ with Uvicorn
- **Database:** SQLAlchemy 2.0 with PostgreSQL/SQLite support
- **Scheduler:** APScheduler 3.10 for automated price capture
- **AI Integration:** OpenAI API (GPT-5) for predictions
- **Market Data:** yfinance, pandas for analysis
- **Validation:** Pydantic 2.9+ for data validation
- **Testing:** pytest for unit tests

### Development Tools
- **Linting:** ESLint 9.21 + Prettier 3.5.3 for frontend
- **Type Checking:** TypeScript strict mode
- **Environment:** python-dotenv for configuration
- **Package Managers:** yarn (frontend), uv (backend)

## Key Project Files

### Configuration & Documentation
- **Product Requirements:** @SPY-tracker-PRD.md
- **Deployment Status:** @DEPLOYMENT_STATUS.md (production environment details)
- **Environment Template:** @.env.example (comprehensive configuration guide)
- **Docker Setup:** @docker-compose.yml (full stack with PostgreSQL)

### Backend Architecture
- **Main Application:** @backend/app/main.py (40+ endpoints with comprehensive error handling)
- **Database Models:** @backend/app/models.py (SQLAlchemy models with PostgreSQL/SQLite support)
- **AI Prediction System:** @backend/app/ai_predictor.py (GPT-5 with technical indicators and fallback)
- **Baseline Models:** @backend/app/baseline_model.py (statistical fallback predictions)
- **Configuration:** @backend/app/config.py (intelligent database detection)
- **Exception Handling:** @backend/app/exceptions.py (comprehensive exception system)
- **Market Data:** @backend/app/providers.py (yfinance integration)
- **Scheduling:** @backend/app/scheduler.py (automated market data capture)
- **API Routers:** @backend/app/routers/ (modular endpoint organization)

### Frontend Architecture
- **Main App:** @src/App.tsx (React 19, mobile-optimized)
- **Core Component:** @src/components/generated/SPYTaTrackerApp.tsx (main application shell)
- **Screen Components:** @src/components/generated/ (Dashboard, History, Metrics, Predict screens)
- **API Client:** @src/utils/apiClient.ts (centralized API communication)
- **Performance Utils:** @src/utils/performance.ts (caching, debouncing, lazy loading)
- **Error Handling:** @src/utils/errorHandling.ts (user-friendly error management)
- **Type Definitions:** @src/lib/schemas.ts (Zod schemas and TypeScript types)

### Deployment & Operations
- **Render Config:** @render.yaml (production deployment configuration)
- **Docker:** @Dockerfile (containerized deployment)
- **Startup Scripts:** @start.sh, @start-production.sh (automated environment setup)
- **Health Monitoring:** @scripts/health-check.sh (production monitoring)
## Development Commands

### Frontend Development
```bash
# Install dependencies
yarn install

# Start development server (port 3000)
yarn dev

# Build for production
yarn build

# Run tests
yarn test
yarn test:run  # run once
yarn test:coverage  # with coverage

# Linting and formatting
yarn lint
yarn format
yarn format:check

# E2E tests
yarn e2e
```

### Backend Development
```bash
# Navigate to backend
cd backend

# Install dependencies with uv
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip sync pyproject.toml

# Start development server (port 8000)
uvicorn app.main:app --reload --port 8000

# Run tests
pytest
```

### Full Stack Development
```bash
# Automated setup and start (recommended)
./start.sh

# Production setup
./start-production.sh

# Monitor production
./monitor.sh
```

## Environment Configuration

### Required Environment Variables
- **DATABASE_URL**: Database connection string
- **OPENAI_API_KEY**: OpenAI API key for AI predictions
- **TIMEZONE**: America/Chicago (for market hours)
- **SYMBOL**: SPY (target trading symbol)

### Optional Environment Variables
- **DEBUG**: Enable/disable debug mode (default: true)
- **FRONTEND_ORIGIN**: CORS configuration (default: *)
- **API_PORT**: Backend server port (default: 8000)
- **PORT**: Frontend server port (default: 3000)
- **OPENAI_MODEL**: AI model to use (default: gpt-5)
- **OPENAI_MAX_COMPLETION_TOKENS**: Token limit (default: 600)
- **AI_LOOKBACK_DAYS**: Historical context days (default: 5)

## AI Prediction System

The application uses a sophisticated AI prediction system:

### GPT-5 Integration
- **Model**: GPT-5 with reasoning effort configuration
- **Context**: Technical indicators (RSI, MACD, Bollinger Bands)
- **Market Data**: VIX, ES futures, support/resistance levels
- **Output**: Confidence-scored predictions with detailed reasoning
- **Intervals**: 68% confidence intervals for all predictions

### Fallback System
- **Baseline Model**: Statistical predictions when AI fails
- **Emergency Fallback**: Simple volatility-based predictions
- **Error Handling**: Comprehensive logging and graceful degradation

### Technical Indicators
- RSI (14-day) for momentum analysis
- MACD for trend identification
- Bollinger Bands for volatility analysis
- Moving averages (SMA/EMA) for trend confirmation
- Volume analysis for institutional activity
- Support/resistance level detection

## Database Architecture

### Intelligent Database Detection
- **Auto-Detection**: Automatically detects available PostgreSQL or falls back to SQLite
- **PostgreSQL**: Primary database for production and development
- **SQLite**: Fallback database for quick testing
- **Docker Integration**: Automatic PostgreSQL container management

### Data Models
- **DailyPrediction**: Manual and AI predictions with governance
- **PriceLog**: Historical price data capture
- **AIPrediction**: AI prediction tracking with confidence intervals
- **BaselineModel**: Statistical model configuration
- **ModelPerformance**: Performance metrics for all prediction models

## Testing Strategy

### Frontend Testing
- **Unit Tests**: Vitest with @testing-library/react
- **Component Testing**: React Testing Library
- **E2E Tests**: Playwright for full user workflows
- **Type Checking**: TypeScript strict mode

### Backend Testing
- **Unit Tests**: pytest with comprehensive coverage
- **API Testing**: FastAPI TestClient
- **Database Testing**: PostgreSQL and SQLite test suites
- **Integration Tests**: Full workflow testing

## Production Deployment

### Render.com Configuration
- **Platform**: Render.com with Docker deployment
- **Database**: PostgreSQL managed service
- **Health Checks**: /healthz endpoint monitoring
- **Environment**: Secure environment variable management

### Performance Optimizations
- **Caching**: Memory caching for API responses
- **Debouncing**: Input debouncing for performance
- **Lazy Loading**: Component and resource lazy loading
- **Bundle Optimization**: Vite production build optimization

## Important Development Notes

1. **Always use the specified package managers**: yarn for frontend, uv for backend
2. **Environment files**: Never commit .env files; use .env.example as template
3. **Database**: Use intelligent detection or explicitly set DATABASE_URL
4. **API Development**: All endpoints include comprehensive error handling
5. **Mobile First**: UI is optimized for mobile devices with responsive design
6. **Time Zone**: All times are in America/Chicago for market hours
7. **AI Fallbacks**: System gracefully handles AI service failures
8. **Testing**: Run tests before committing changes
9. **Production**: Use health monitoring scripts for production deployments
10. **Documentation**: Update documentation when adding new features