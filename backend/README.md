# SPY TA Tracker Backend

FastAPI backend for SPY TA Tracker - options trading prediction and suggestion system.

## Setup

### Prerequisites
- Python 3.10+
- uv (Python package manager)

### Installation

1. Create virtual environment and install dependencies:
```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip sync requirements.txt
```

2. Copy environment variables:
```bash
cp .env.example .env
# Edit .env as needed
```

## Running the Server

### Development (with auto-reload)
```bash
uv run uvicorn app.main:app --reload --reload-exclude .venv --reload-dir app --host 127.0.0.1 --port 8000
```

### Production
```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## API Endpoints

### Health Check
- `GET /healthz` - Health check endpoint

### Predictions
- `POST /prediction` - Create/update prediction (date in body)
- `POST /prediction/{date}` - Create/update prediction (date in path)
- `GET /day/{date}` - Get prediction and prices for a specific date

### Price Capture
- `POST /log/{checkpoint}` - Log price for checkpoint (date in body)
- `POST /capture/{date}` - Capture price for date (checkpoint in body)
- `POST /recompute/{date}` - Recompute derived fields (absErrorToClose, rangeHit)

### Analytics
- `GET /metrics` - Get 20-day rolling metrics:
  - `rangeHit20` - Percentage of predictions that hit the range
  - `medianAbsErr20` - Median absolute error to close
- `GET /suggestions/{date}` - Get option structure suggestions for date

## Scheduler

The backend runs scheduled jobs to capture market prices at key times (America/Chicago timezone):
- 08:00 CST - Pre-market snapshot
- 08:30 CST - Market open
- 12:00 CST - Noon checkpoint
- 14:00 CST - 2 PM checkpoint
- 15:00 CST - Market close

## Suggestions Logic

The suggestions engine uses Expected Move (EM) calculations:
- EM ≈ S × IV × √(T/365)
- Default IV: 18% (0.18)

Structure selection:
- **Iron Condor (IC)**: Selected when bias is Neutral AND rangeHit20 ≥ 65%
- **Iron Butterfly (IB)**: Selected for directional bias OR when rangeHit20 < 65%

Delta targets:
- 0DTE: ±10-15Δ (IC), center at prediction midpoint (IB)
- 1W: ±15-20Δ (IC), wings at 0.75× EM (IB)
- 1M: ±20Δ (IC), wings at 0.75× EM (IB)

## Database

SQLite database with SQLAlchemy ORM. Main models:
- `DailyPrediction` - Stores predictions, actual prices, and derived metrics
- `PriceLog` - Audit log of all price captures

## Environment Variables

See `.env.example` for all configuration options:
- `APP_NAME` - Application name
- `DEBUG` - Debug mode (true/false)
- `DATABASE_URL` - Database connection string
- `TIMEZONE` - Market timezone (America/Chicago)
- `SYMBOL` - Trading symbol (SPY)
- `FRONTEND_ORIGIN` - CORS origin for frontend (* for all)

## Development Notes

- Package manager: **uv** (not pip)
- Auto-reload excludes `.venv` to prevent thrashing
- All times are in CST/CDT (America/Chicago)
- Weekdays only for scheduler jobs
EOF < /dev/null