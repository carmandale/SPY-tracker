# SPY TA Tracker Backend (uv)

## Quickstart

1) Create venv and install deps

```
cd backend
uv venv
uv pip sync pyproject.toml
```

2) Env

- Copy `.env.example` to `.env` in `backend/`.
- Defaults are fine for local dev.

3) Run API

```
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Endpoints
- POST `/prediction`
- GET `/day/{YYYY-MM-DD}`
- POST `/log/{checkpoint}` (preMarket|open|noon|twoPM|close)
- GET `/suggestions/{YYYY-MM-DD}`
- GET `/metrics`
- GET `/healthz`

## Notes
- Time zone: America/Chicago
- Prices: yfinance (MVP)
- Scheduler: 08:30, 12:00, 14:00, 15:00 CST (weekdays)
