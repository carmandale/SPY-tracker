# Technical Stack

> Last Updated: 2025-08-11
> Version: 1.0.0

## Core Technologies

**Application Framework:** FastAPI 0.111+ (Backend), React 19.0.0 (Frontend)
**Database System:** SQLite with SQLAlchemy 2.0
**JavaScript Framework:** React 19 with TypeScript
**CSS Framework:** Tailwind CSS v4.0.9

## Package Managers (CRITICAL - DO NOT CHANGE)

**Python Package Manager:** uv
**JavaScript Package Manager:** yarn

⚠️ **IMPORTANT**: Always use the package managers specified above. 
- Python: Use `uv` (NOT pip)
- JavaScript: Use `yarn` (NOT npm)

**Project Exception Note:** This project uses yarn instead of the organizational npm standard for historical reasons and dependency compatibility.

## Development Environment

**Project Structure:** monorepo
**Frontend Port:** 3000
**Backend Port:** 8000

### Startup Commands

**Frontend:** `yarn dev`
**Backend:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`

**Quick Start:** Run both services in separate terminals

### Environment Files

- **Frontend:** `.env.local` (contains PORT=3000)
- **Backend:** `backend/.env` (contains API_PORT=8000)

## Testing Strategy

**Frontend Testing:** Vitest (to be configured)
**Backend Testing:** pytest (to be configured)
**E2E Testing:** Playwright (to be configured)

## Additional Configuration

**UI Component Library:** shadcn/ui components
**Font Provider:** System fonts
**Icon Library:** lucide-react
**State Management:** React hooks and context
**Forms:** React Hook Form with Zod validation
**Charts:** Recharts
**Animations:** Framer Motion

## Backend Technologies

**Web Framework:** FastAPI with Uvicorn
**ORM:** SQLAlchemy 2.0
**Validation:** Pydantic 2.9+
**Task Scheduler:** APScheduler 3.10
**Market Data:** yfinance 0.2.65+
**HTTP Client:** httpx 0.27
**Environment:** python-dotenv

## Build Tools

**Frontend Bundler:** Vite 6.2.0
**TypeScript:** 5.7.2
**Linting:** ESLint 9.21 + Prettier 3.5.3
**Backend Package Manager:** uv with pyproject.toml

## Deployment

**Application Hosting:** TBD (local development for MVP)
**Database Hosting:** Local SQLite file
**Asset Hosting:** Vite static build
**Deployment Solution:** TBD

## Repository

**Code Repository:** https://github.com/[username]/SPY-tracker (to be created)

---

**⚠️ AGENT OS REMINDER**: Before making ANY changes to package management, startup commands, or environment configuration, ALWAYS check this file first to maintain consistency.
EOF < /dev/null