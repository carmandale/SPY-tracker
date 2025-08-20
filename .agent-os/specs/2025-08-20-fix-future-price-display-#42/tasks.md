# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-08-20-fix-future-price-display-#42/spec.md

> Created: 2025-08-20
> Status: Ready for Implementation

## Tasks

### Phase 1: Core Time Logic Implementation

- [ ] **Create time checkpoint utility function** `S`
  - Implement function to determine which checkpoints have occurred based on current America/Chicago time
  - Handle market checkpoints: premarket (8:00am), open (8:30am), noon (12:00pm), 2pm (2:00pm), close (3:00pm)
  - Account for weekends and basic holidays
  - Location: `backend/app/utils/market_time.py`

- [ ] **Add time-aware price filtering to DailyPrediction model** `M`
  - Create method to filter price fields based on current time
  - Return null for future checkpoints
  - Preserve all data for historical dates (before today)
  - Location: `backend/app/models.py`

### Phase 2: API Endpoint Updates

- [ ] **Update /day/{date} endpoint** `M`
  - Apply time filtering to returned daily prediction data
  - Ensure future prices return as null for current date
  - Maintain full data for historical dates
  - Location: `backend/app/routers/predictions.py`

- [ ] **Update /history endpoint** `S`
  - Apply time filtering to today's entry only
  - Ensure historical entries show complete data
  - Location: `backend/app/routers/predictions.py`

- [ ] **Update AI predictions endpoints** `S`
  - Ensure AI prediction endpoints also respect time filtering
  - Apply filtering to any endpoint returning daily prediction data
  - Location: `backend/app/routers/ai.py`

### Phase 3: Frontend Updates

- [ ] **Update Dashboard price display** `M`
  - Handle null values for future prices
  - Show appropriate loading/placeholder states
  - Display "Market opens at 8:30am" type messages for future checkpoints
  - Location: `src/components/generated/DashboardView.tsx`

- [ ] **Update Predict page price display** `S`
  - Handle null values in price tiles
  - Show appropriate states for unrealized checkpoints
  - Location: `src/components/generated/PredictView.tsx`

- [ ] **Update History page display** `S`
  - Handle null values for today's incomplete prices
  - Show "In progress" or similar indicators
  - Location: `src/components/generated/HistoryView.tsx`

### Phase 4: Testing & Validation

- [ ] **Write unit tests for time logic** `M`
  - Test checkpoint determination at various times
  - Test edge cases (holidays, weekends, early close)
  - Test timezone handling
  - Location: `backend/tests/test_market_time.py`

- [ ] **Write API endpoint tests** `M`
  - Test time filtering behavior for current vs historical dates
  - Test various time scenarios during market hours
  - Verify null handling for future checkpoints
  - Location: `backend/tests/test_time_filtering.py`

- [ ] **Manual testing across time scenarios** `S`
  - Test behavior before market open (8:00-8:30am)
  - Test during market hours (8:30am-3:00pm)
  - Test after market close (after 3:00pm)
  - Verify weekend and holiday handling

### Phase 5: Documentation & Cleanup

- [ ] **Update API documentation** `XS`
  - Document time filtering behavior in endpoint descriptions
  - Add examples showing null values for future prices
  - Location: FastAPI auto-generated docs

- [ ] **Verify no regressions** `S`
  - Ensure historical data display unchanged
  - Verify completed days show all prices
  - Confirm AI predictions and manual price capture still function
  - Test production deployment with time filtering

## Acceptance Criteria

- [ ] At 9:21am CST, dashboard shows only pre-market and open prices for today
- [ ] At 12:05pm CST, dashboard shows pre-market, open, and noon prices for today
- [ ] Historical dates (yesterday and before) always show complete price data
- [ ] Frontend properly handles null values with appropriate UI states
- [ ] API endpoints return consistent time-filtered responses
- [ ] No regression in core functionality (price capture, AI predictions, suggestions)