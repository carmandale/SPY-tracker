# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-08-16-official-price-capture-fix-#8/spec.md

> Created: 2025-08-16
> Version: 1.0.0

## Test Coverage

### Unit Tests

**YFinanceProvider**
- Test get_daily_ohlc with valid trading day
- Test get_daily_ohlc with weekend/holiday (should return None)
- Test get_official_checkpoint_price for each checkpoint type
- Test timezone conversion for market hours
- Test price validation logic (reasonable ranges, non-zero values)
- Test error handling when yfinance API fails

**Scheduler Functions**
- Test capture_price with official price success
- Test capture_price with fallback to current price
- Test price logging and database updates
- Test timezone handling for CST scheduler

### Integration Tests

**Price Capture Workflow**
- End-to-end test of scheduled price capture
- Test database persistence of official prices
- Test that official prices differ from current prices (when market closed)
- Test admin refresh endpoints

**Admin Endpoints**
- Test refresh single day with valid date
- Test refresh date range
- Test status monitoring endpoint
- Test error handling for invalid dates

### Mocking Requirements

- **yfinance API responses:** Mock successful and failed API calls
- **Market hours:** Mock different times of day for testing
- **Database state:** Mock existing predictions for price updates
- **Timezone handling:** Mock different date/time scenarios