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

Open two terminal windows:

**Terminal 1 - Frontend (Port 3000):**
```bash
yarn dev
```

**Terminal 2 - Backend (Port 8000):**
```bash
cd backend
uv run uvicorn app.main:app --reload --reload-exclude .venv --reload-dir app --host 127.0.0.1 --port 8000
```

Access the application at http://localhost:3000

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
