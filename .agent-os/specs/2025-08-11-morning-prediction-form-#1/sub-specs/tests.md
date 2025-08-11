# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-08-11-morning-prediction-form-#1/spec.md

> Created: 2025-08-11
> Version: 1.0.0

## Test Coverage

### Unit Tests

**PredictionForm Component**
- Renders all form fields correctly
- Validates required fields (predLow, predHigh)
- Validates number input ranges (0-1000)
- Validates text input character limits (keyLevels 200, notes 500)
- Displays validation errors appropriately
- Handles form submission with valid data
- Prevents submission with invalid data
- Shows loading state during submission
- Displays success message after successful submission

**Form Validation Schema**
- Validates number inputs for predLow and predHigh
- Validates enum selections for bias, volCtx, dayType
- Validates optional string fields with length limits
- Rejects invalid data types and out-of-range values

### Integration Tests

**API Integration**
- Successfully submits prediction data to /prediction/{date} endpoint
- Handles network errors gracefully with user feedback
- Passes correct date format in CST timezone
- Includes pre-market price capture on successful submission
- Updates form state appropriately after API response

**Form Workflow**
- Complete user workflow from form entry to successful save
- Navigation to prediction form from dashboard
- Form reset after successful submission
- Error recovery scenarios (retry after failure)

### Mobile Responsiveness Tests

**Touch Interactions**
- Segmented controls work properly with touch
- Number inputs show appropriate mobile keyboards
- Form is usable with one-handed operation
- All interactive elements meet 44px minimum touch target
- Form scrolls properly on small screens

### Mocking Requirements

- **API Calls:** Mock /prediction/{date} endpoint responses (success/failure)
- **Date/Time:** Mock current date and timezone for consistent testing
- **Network Conditions:** Mock slow connections and network failures
- **Pre-market Data:** Mock pre-market price fetching during form submission

## Test Environment Setup

### Frontend Testing Framework
- **Vitest:** Unit and integration testing
- **@testing-library/react:** Component testing utilities
- **@testing-library/user-event:** User interaction simulation
- **Mock Service Worker (MSW):** API mocking for integration tests

### Test Data
- Valid prediction form data sets
- Invalid data sets for validation testing
- Mock API responses for various scenarios
- Edge cases (market holidays, DST transitions)

## Coverage Requirements

- **Minimum Coverage:** 90% for form component and validation logic
- **Critical Paths:** 100% coverage for form submission and API integration
- **Edge Cases:** All validation scenarios and error conditions must be tested
- **Performance:** Form response time validation (≤100ms for input feedback)