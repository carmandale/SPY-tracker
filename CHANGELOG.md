# Changelog

All notable changes to SPY TA Tracker are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### To Do
- Implement PWA configuration with manifest.json and service worker
- Add backup/restore endpoints for data export/import

### Added
- Admin API responses now include `detail` key in error payloads for consistent client handling
- `get_ny_now()` helper returning timezone-aware Eastern Time `datetime` for market-aware logic
- Documentation updates covering QA/testing playbook for admin endpoints and scheduler logging

### Fixed
- Admin price refresh endpoint now respects `force` flag and avoids redundant overwrites
- Scheduler tests aligned with structured logging to eliminate print-based assertions
- Admin test suite refactored to use dependency overrides for reliable database mocking

## [2.1.0] - 2025-08-18
### Added
- Next prediction countdown indicator on dashboard (#30)
  - Real-time countdown to next 8 AM CST AI prediction
  - Smart detection of weekends and market holidays
  - Different displays for market open/closed states
  - Automatic 60-second refresh interval
  - Replaces confusing "No Data Available" message during off-hours
- Deployment version status display (#30)
  - Version footer showing current version, commit, and environment
  - Color-coded environment indicators (production/staging/development)
  - Deployment date and build number tracking
  - Link to GitHub commit for verification
  - Fallback data when API is unavailable
- Backend version and changelog API endpoints
  - `/api/version` for deployment information
  - `/api/scheduler/next-prediction` for countdown data
  - `/api/changelog` for version history
- Comprehensive US market holiday detection (2025-2026)
- Enhanced error handling with fallback behavior
- API client extensions with proper caching strategies

## [2.0.0] - 2025-08-16
### Production Deployment 🚀
- **Live URL**: https://spy-tracker.onrender.com
- **Deployment Platform**: Render.com
- **Commit**: 4d90a08 (main branch)

### Added
- PostgreSQL database migration from SQLite (#13)
- GPT-5 powered AI predictions with confidence scoring
- Comprehensive technical indicators (RSI, MACD, Bollinger Bands)
- Advanced error handling system with custom exceptions
- Performance optimizations (caching, debouncing, lazy loading)
- Docker Compose configuration for local PostgreSQL
- Production deployment configurations for multiple platforms
- Skeleton loading states with shimmer animations
- Volume analysis and institutional activity indicators
- Support and resistance level detection
- Market regime detection (trending/range-bound/volatile)
- Enhanced AI analysis with sentiment and market dynamics
- Baseline statistical model as fallback

### Changed
- Database backend from SQLite to PostgreSQL for production
- AI model upgraded from GPT-4 to GPT-5
- Scheduler timezone handling improved for CST/CDT
- Frontend performance with React 19 optimizations
- Mobile responsiveness enhanced with touch optimization

### Fixed
- Scheduler reliability issues in production environment
- Timezone inconsistencies in price capture jobs
- Database connection pooling for better performance
- CORS configuration for production deployment

## [1.5.0] - 2025-08-11
### Added
- Option suggestions engine (Iron Condor/Butterfly) for 0DTE/1W/1M
- Delta target calculations for optimal strike positions
- Expected move calculations using implied volatility
- Management notes with profit targets and exit strategies
- Performance tracking with 20-day rolling metrics
- Calibration tips engine for prediction improvement
- Historical analysis with accuracy metrics
- Real-time chart visualization of predicted vs actual prices

### Changed
- Dashboard UI to display comprehensive market data
- Prediction form with enhanced input validation
- History page with sortable/filterable data grid

## [1.0.0] - 2025-08-05
### Initial Release
### Added
- Core morning prediction entry system
- Automated price capture at market checkpoints
- Basic dashboard with today's prediction display
- APScheduler for automated market hours tasks
- yfinance integration for live SPY data
- FastAPI backend with SQLAlchemy ORM
- React 19 frontend with TypeScript
- Tailwind CSS v4 for styling
- Mobile-first responsive design
- CST/CDT timezone support

### Technical Stack
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4
- **Backend**: FastAPI, SQLAlchemy, APScheduler
- **Database**: SQLite (initial), PostgreSQL (v2.0.0+)
- **Package Managers**: Yarn (frontend), uv (backend)

---

## Version History Summary

| Version | Date | Status | Key Features |
|---------|------|--------|--------------|
| 2.0.0 | 2025-08-16 | Production | PostgreSQL, GPT-5, Full AI Integration |
| 1.5.0 | 2025-08-11 | Beta | Suggestions Engine, Performance Tracking |
| 1.0.0 | 2025-08-05 | Alpha | Core Prediction System |

## Deployment Tracking

### Production (Render.com)
- **Current Version**: 2.0.0
- **Last Deploy**: 2025-08-16
- **Commit Hash**: 4d90a08
- **Status**: ✅ Live and operational
- **URL**: https://spy-tracker.onrender.com

### Monitoring
- Health Check: `/healthz`
- Version Endpoint: `/api/version` (to be implemented)
- Scheduler Status: `/api/scheduler/status`

---

*For contribution guidelines and development setup, see [README.md](./README.md)*