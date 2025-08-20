# Spec Requirements Document

> Spec: Fix Future Price Display Issue #42
> Created: 2025-08-20
> GitHub Issue: #42
> Status: Planning

## Overview

Fix the critical bug where the dashboard, predict page, and history page display actual prices for market checkpoints that haven't occurred yet. Currently, at 9:21am CST, the application shows all four prices (open, noon, 2PM, close) for today when only the open price should be available. This creates confusion and undermines the app's reliability for real-time trading decisions.

## User Stories

### Real-Time Trading Accuracy Story

As a SPY options trader using the app during market hours, I want to see only the actual market prices that have already occurred so that I can make informed trading decisions based on accurate, time-appropriate data without being misled by future price displays.

The trader checks the dashboard at 9:21am CST expecting to see only pre-market and open prices, but currently sees all checkpoints filled in, creating confusion about what data is real vs. predicted.

### Market Timing Reliability Story

As a user tracking prediction accuracy, I want the history page to show only realized prices for time checkpoints that have passed so that I can accurately assess my prediction performance without contamination from future data that shouldn't be visible yet.

When reviewing yesterday's predictions at 10am, all prices should be visible, but when reviewing today's performance, only open (and pre-market) should show until noon passes, then noon price appears, etc.

### API Data Integrity Story

As a frontend developer consuming the API, I want endpoints to return null for future price checkpoints so that the UI can properly distinguish between actual market data and unavailable future data, enabling appropriate display states and user messaging.

The API should implement proper time-aware filtering so frontend components can render with correct loading states and data availability indicators.

## Spec Scope

1. **Time-Aware Price Filtering** - Implement logic to check current time against market checkpoint times and only return actual prices for passed checkpoints
2. **API Endpoint Updates** - Modify all prediction and daily data endpoints to filter future prices based on current time
3. **Market Hours Awareness** - Ensure proper handling of market holidays, early closures, and weekend scenarios
4. **Timezone Consistency** - Maintain consistent America/Chicago timezone handling across all time checks
5. **Frontend State Updates** - Update UI components to properly handle null values for future prices

## Out of Scope

- Changing the underlying database schema or price capture scheduling
- Modifying the AI prediction system timing or logic
- Adding new time checkpoints or market data sources
- Implementing price prediction display (predictions should remain separate from actual prices)
- Complex market calendar integration beyond basic holiday detection

## Expected Deliverable

1. **Time-filtered API responses** - All endpoints returning daily prediction data check current time and return null for future checkpoint prices
2. **Consistent market checkpoint logic** - Centralized function to determine which checkpoints have occurred based on current America/Chicago time
3. **Updated frontend handling** - UI components properly display loading states or "Not yet available" for future prices
4. **Comprehensive testing** - Tests covering various time scenarios including pre-market, during market hours, and after close
5. **Zero regression** - Historical data and completed days remain fully accessible without changes

## Spec Documentation

- Tasks: @.agent-os/specs/2025-08-20-fix-future-price-display-#42/tasks.md
- Technical Specification: @.agent-os/specs/2025-08-20-fix-future-price-display-#42/sub-specs/technical-spec.md
- API Specification: @.agent-os/specs/2025-08-20-fix-future-price-display-#42/sub-specs/api-spec.md
- Tests Specification: @.agent-os/specs/2025-08-20-fix-future-price-display-#42/sub-specs/tests.md