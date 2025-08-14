# SPY TA Tracker

Mobile-first options trading assistant for tracking SPY predictions and generating iron condor/butterfly suggestions.

## Quick Start

### Prerequisites
- Node.js 18+ and Yarn
- Python 3.10+ and uv
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd SPY-tracker
```

2. Install frontend dependencies:
```bash
yarn install
```

3. Install backend dependencies:
```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip sync requirements.txt
cd ..
```

### Running the Application

Preferred (single command):
```bash
bash start.sh
```

Environment variables:
- Backend port: `API_PORT` (default 8000)
- Frontend port: `PORT` (default 3000)

The script will:
- Load `.env` and `.env.local`
- Create/activate `backend/.venv` via uv
- Install backend deps via `uv pip sync pyproject.toml` (or requirements)
- Start FastAPI and Vite in the background with reload

Access:
- Frontend: http://localhost:3000
- Backend:  http://localhost:8000

## Tech Stack

### Frontend
- **Framework:** React 19 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS v4
- **Charts:** Recharts (not Chart.js)
- **UI Components:** shadcn/ui
- **Package Manager:** Yarn

### Backend
- **Framework:** FastAPI
- **Database:** SQLite with SQLAlchemy
- **Scheduler:** APScheduler (CST/CDT timezone)
- **Package Manager:** uv (not pip)
- **Market Data:** yfinance (future integration)

## Project Structure

```
SPY-tracker/
├── src/                    # React frontend source
│   ├── components/         # UI components
│   ├── hooks/             # Custom React hooks
│   └── lib/               # Utilities
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   │   ├── main.py       # API endpoints
│   │   ├── models.py     # Database models
│   │   ├── scheduler.py  # Market hours scheduler
│   │   └── suggestions.py # Options strategy logic
│   └── requirements.txt   # Python dependencies
├── .agent-os/            # Agent OS documentation
│   └── product/          # Product specs and roadmap
└── package.json          # Frontend dependencies
```

## Features

### Current (Phase 0 - Complete)
- ✅ Project scaffolding with monorepo structure
- ✅ FastAPI backend with SQLAlchemy models
- ✅ APScheduler for market hours (CST)
- ✅ Core API endpoints
- ✅ Initial React component structure

### In Progress (Phase 1 - MVP)
- 🚧 Morning prediction entry form
- 🚧 Price capture (manual and automated)
- 🚧 Chart visualization of predictions vs actuals
- 🚧 Dashboard with current day view

### Planned
- Phase 2: IC/IB suggestions engine
- Phase 3: Performance metrics and calibration
- Phase 4: Live market data integration
- Phase 5: Production deployment

## API Documentation

When the backend is running, view interactive API docs at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Development

### Package Managers (Important!)
- **Frontend:** Use `yarn` (not npm)
- **Backend:** Use `uv` (not pip)

### Environment Files
- Frontend: `.env.local` (PORT=3000)
- Backend: `backend/.env` (see backend/.env.example)

### Git Workflow
- All work must be linked to GitHub issues
- Use conventional commits: `feat:`, `fix:`, `chore:`, etc.
- Create PRs for all changes

## Agent OS Integration

This project uses Agent OS for structured development. See:
- `.agent-os/product/` - Product documentation
- `CLAUDE.md` - AI assistant instructions

To create a new feature spec:
```
/create-spec
```

## License

Private - All rights reserved

## Support

For issues or questions, create a GitHub issue.
## Deployment (Render, single Docker service)

This app is deployed as a single Render Web Service running a multi-stage Docker image that serves BOTH the API and the SPA at the same origin.

### How it works
- `Dockerfile` builds the React frontend (`yarn build`) to `dist/` and copies it into the backend at `backend/static/`.
- Uvicorn runs FastAPI (`app.main:app`). FastAPI mounts `/assets/*` and serves `index.html` for all SPA routes.
- `VITE_API_URL` is baked for same-origin; the client resolves the API base to `window.location.origin`.
- APScheduler runs in-process to capture prices and auto-create the morning AI band.

### Render service settings
- Type: Web Service (Docker)
- Port: inferred from Uvicorn, health check path `/healthz`
- Environment variables (set in Render):
  - `OPENAI_API_KEY` (required for AI)
  - `FRONTEND_ORIGIN` (optional; CORS origin; `*` allowed)
  - `DATABASE_URL` (optional; default SQLite).
- Persistent storage options:
  - SQLite: attach a Render Disk mounted at `/app/backend` so `sqlite:///./spy_tracker.db` persists.
  - Postgres: set `DATABASE_URL` instead.

### CI-free deploy
1) Push to `main`.
2) In Render → Service → Manual Deploy:
   - Use “Deploy latest commit”. If new routes aren’t visible, run “Clear build cache & deploy”.

### Useful runtime endpoints
- Health: `GET /healthz`
- Scheduler status: `GET /scheduler/status`
- Trigger a job manually: `POST /scheduler/trigger/{job_id}` (`ai_predict_0800`, `capture_open`, etc.)
- AI create (idempotent for a date): `POST /ai/predict/{YYYY-MM-DD}`
- Day fetch: `GET /day/{YYYY-MM-DD}`
- History (paginated): `GET /history?limit=20&offset=0`
- Metrics: `GET /metrics`

### Admin helpers (for ops)
- Backfill actuals (Open/Noon/2PM/Close) from yfinance and recompute derived fields:
  - `GET /admin/backfill-actuals/{YYYY-MM-DD}`
- Persist last N trading days of AI simulation data (idempotent):
  - `GET /admin/simulate-simple/{N}` (e.g., `10`)

Note: If an admin route returns the SPA (HTML), clear Render build cache and redeploy to ensure new routes are loaded.

### Morning automation (CST/CDT)
- APScheduler registers:
  - `ai_predict_0800` – create & lock AI prediction daily at 08:00 CST (Mon–Fri)
  - Price captures at 08:00, 08:30, 12:00, 14:00, 15:00
- Verify: `GET /scheduler/status` shows next run times in `America/Chicago`.

### Local production test via Docker
```bash
docker build -t spy-tracker:test --build-arg VITE_API_URL=/ .
docker run -p 8000:8000 -e FRONTEND_ORIGIN=http://localhost:8000 spy-tracker:test
# Verify
curl -fsS http://localhost:8000/healthz
```

## Local development (Postgres, best-practice)

We use Postgres locally for full parity with production.

### Quick start
1) Start Postgres (Docker):
```
docker run --name spydb -d \
  -e POSTGRES_USER=spy -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=spy \
  -p 5432:5432 postgres:16
```
2) Create `backend/.env`:
```
DATABASE_URL=postgresql+psycopg2://spy:pass@localhost:5432/spy
OPENAI_API_KEY=sk-... # optional
```
3) Run backend and frontend:
```
# backend
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# frontend
yarn && yarn dev
```
4) Verify and seed:
```
curl -fsS http://localhost:8000/healthz
curl -fsS http://localhost:8000/simulation/quick/10 > /dev/null
curl -fsS "http://localhost:8000/history?limit=10"
```

### Policies
- Never commit local `.env` files.
- Prefer per-branch DB names to isolate experiments.
- Use Postgres both locally and in prod to avoid drift.
