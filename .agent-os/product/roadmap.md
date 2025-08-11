# Product Roadmap

> Last Updated: 2025-08-11
> Version: 1.0.0
> Status: Active Development

## Phase 0: Already Completed

The following features have been implemented:

- [x] Project scaffolding with React 19 + Vite frontend - Complete project structure `XS`
- [x] FastAPI backend with SQLAlchemy models - Database schema and API structure `S`
- [x] APScheduler configuration for market hours - CST timezone scheduling `XS`
- [x] Core database models (DailyPrediction, PriceLog) - SQLite persistence layer `S`
- [x] Basic API endpoints structure - CRUD operations scaffolded `S`
- [x] CORS configuration for frontend-backend communication - Development setup `XS`
- [x] Initial component structure - Dashboard, History, Metrics, Predict screens `S`

## Phase 1: Core Day Loop (Current - MVP Target)

**Goal:** Enable morning predictions and automated price tracking
**Success Criteria:** Can enter predictions and see results next day
**Duration:** 1 week

### Must-Have Features

- [ ] Morning prediction form UI - Input fields for low/high/bias/context `M`
- [ ] Manual price capture endpoints - Record open/noon/2PM/close `S`
- [ ] Prediction persistence - Save and retrieve daily predictions `S`
- [ ] Basic chart visualization - Show predicted band vs actual prices `M`
- [ ] Dashboard view with today's data - Current prediction and prices `M`

### Should-Have Features

- [ ] Pre-market price snapshot - Capture at 8:00 AM CST `S`
- [ ] Automated scheduled price capture - Replace manual with scheduled jobs `M`
- [ ] Range hit calculation - Score prediction accuracy `S`

### Dependencies

- Frontend form validation with Zod
- Chart library integration (Recharts already installed)
- Timezone handling for CST/CDT

## Phase 2: Suggestions Engine

**Goal:** Generate IC/IB suggestions based on predictions
**Success Criteria:** Display actionable option structures for 0DTE/1W/1M
**Duration:** 1 week

### Must-Have Features

- [ ] Suggestion generation logic - IC vs IB selection algorithm `L`
- [ ] Delta target calculations - Compute optimal strike positions `M`
- [ ] Three horizon suggestions - 0DTE, 1-week, 1-month structures `M`
- [ ] Suggestion display cards - Mobile-optimized UI components `M`

### Should-Have Features

- [ ] Expected move calculations - Use IV for position sizing `M`
- [ ] Management notes - Profit targets and exit strategies `S`
- [ ] Risk filters - Skip low IVR scenarios `S`

### Dependencies

- Option Greeks calculations
- Volatility data integration (stub values for MVP)

## Phase 3: Performance & Calibration

**Goal:** Track accuracy and provide calibration feedback
**Success Criteria:** Display rolling metrics and improvement tips
**Duration:** 1 week

### Must-Have Features

- [ ] History page implementation - List past predictions with outcomes `M`
- [ ] Metrics calculation - 20-day rolling RangeHit% and MAE `M`
- [ ] Calibration tips engine - Data-driven improvement suggestions `M`
- [ ] Metrics dashboard - Visual performance indicators `M`

### Should-Have Features

- [ ] Realized low/high capture - EOD data from provider `M`
- [ ] Accuracy trend analysis - Improving/worsening indicators `S`
- [ ] Export functionality - CSV download of history `S`

### Dependencies

- Historical data accumulation (need 20+ days)
- Statistical calculations library

## Phase 4: Data Provider Integration

**Goal:** Automate market data collection
**Success Criteria:** Real-time SPY prices without manual entry
**Duration:** 1 week

### Must-Have Features

- [ ] yfinance integration - Live SPY price fetching `M`
- [ ] Scheduled data pulls - Automated price updates `M`
- [ ] Fallback handling - Cache last good price on failures `S`
- [ ] IV data integration - Real implied volatility for suggestions `L`

### Should-Have Features

- [ ] Option chain data - Actual strikes and bid/ask spreads `L`
- [ ] Market status detection - Handle holidays and half-days `M`
- [ ] Data provider abstraction - Interface for multiple sources `M`

## Phase 5: Polish & Production

**Goal:** Production-ready application
**Success Criteria:** Reliable, performant, user-friendly
**Duration:** 2 weeks

### Must-Have Features

- [ ] Comprehensive error handling - User-friendly error messages `M`
- [ ] Loading states and skeletons - Smooth UI transitions `S`
- [ ] Mobile responsiveness testing - Ensure all screens work on phones `M`
- [ ] Performance optimization - Sub-2s load times `M`
- [ ] Deployment configuration - Production environment setup `L`

### Should-Have Features

- [ ] PWA configuration - Installable mobile app `M`
- [ ] Backup and restore - Data export/import `M`
- [ ] Advanced analytics - Deeper performance insights `L`
- [ ] Multi-ticker support preparation - Architecture for expansion `XL`

### Dependencies

- Production hosting solution
- SSL certificates
- Domain configuration
EOF < /dev/null