# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-08-20-fix-frontend-data-issues-#36/spec.md

> Created: 2025-08-20
> Version: 1.0.0

## Test Coverage

### Unit Tests

**HistoryView Component**
- Test that past trading days show as "complete" when all data points are present
- Test that past trading days show as "incomplete" when data points are missing
- Test that current trading day shows appropriate status based on time of day
- Test that weekend dates are handled correctly
- Test that holidays are handled appropriately

**Data Completion Logic**
- Test isPastTradingDay() function with various dates
- Test isComplete() function with different data scenarios
- Test that all four checkpoints (open, noon, 2PM, close) are properly verified

### Integration Tests

**History Page Data Display**
- Test that API correctly returns historical data with proper completion status
- Test that frontend correctly interprets and displays the completion status
- Test that clicking on incomplete vs complete items behaves appropriately

**Manifest Loading**
- Test that manifest.json loads without errors
- Test that PWA installation prompts work correctly
- Test that all manifest properties are properly recognized

**External Resources**
- Test that all CSS resources load successfully
- Test that application renders correctly even if external fonts fail
- Test that fallback fonts are applied when needed

### Manual Testing Checklist

**Browser Console Verification**
- [ ] No manifest.json warnings in Chrome DevTools
- [ ] No manifest.json warnings in Safari
- [ ] No CSS 403 errors in network tab
- [ ] No other console errors related to resource loading

**History Page Verification**
- [ ] Past Monday (2025-08-18) shows as "complete" if data exists
- [ ] Past weekdays with data show as "complete"
- [ ] Current day before close shows as "incomplete"
- [ ] Weekend days are properly identified

**PWA Verification**
- [ ] PWA installation prompt appears when appropriate
- [ ] App can be installed successfully
- [ ] Installed app launches without errors

### Mocking Requirements

- **Date/Time Mocking:** Mock current date/time to test different scenarios (past dates, current day at different times)
- **API Response Mocking:** Mock various data states (complete data, partial data, no data)
- **External Resource Mocking:** Mock Google Fonts loading to test fallback behavior

## Test Scenarios

### Scenario 1: Past Trading Day with Complete Data
**Given:** A past trading day (2025-08-18) with all price points
**When:** User views the History page
**Then:** The day shows as "complete" with all data displayed

### Scenario 2: Past Trading Day with Partial Data
**Given:** A past trading day with only some price points
**When:** User views the History page
**Then:** The day shows as "incomplete" with available data displayed

### Scenario 3: Current Trading Day Before Close
**Given:** Current trading day at 2:30 PM ET
**When:** User views the History page
**Then:** The day shows as "incomplete" with real-time updates

### Scenario 4: Manifest Loading
**Given:** User loads the application
**When:** Browser parses manifest.json
**Then:** No parsing errors occur and PWA features work

### Scenario 5: External CSS Loading
**Given:** User loads the application
**When:** Browser requests external CSS resources
**Then:** All resources load successfully or fallbacks apply gracefully