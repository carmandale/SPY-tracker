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
- **Active Specs:** @.agent-os/specs/ (no active specs currently - all previous specs completed)
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

### Database Policy (Dev & Prod)
- Use Postgres in production and for local development.
- Local dev connection string example:
  - `postgresql+psycopg2://spy:pass@localhost:5432/spy`
- Do not commit `.env` files; prefer `backend/.env` locally.
- Use per-branch DB names when doing risky changes.

### Current Development Phase
- **Active:** Phase 5 - Polish & Production
- **Focus:** Production-ready application with error handling, performance optimization, and deployment configuration
- **Completed:** Phases 0-4 (Core Day Loop, Suggestions Engine, Performance & Calibration, Data Provider Integration)
- **Status:** All core MVP features implemented including AI predictions, option suggestions, metrics, and automated data collection

### Key Implemented Features
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
- **Backend API:** @backend/app/main.py (comprehensive REST API with 40+ endpoints)
- **Database Models:** @backend/app/models.py (DailyPrediction, PriceLog, AIPrediction)
- **Frontend App:** @src/App.tsx (React 19 with TypeScript)
- **AI System:** @backend/app/ai_predictor.py (GPT-5 integration)
- **Option Suggestions:** @backend/app/suggestions.py (IC/IB algorithms)
EOF < /dev/null