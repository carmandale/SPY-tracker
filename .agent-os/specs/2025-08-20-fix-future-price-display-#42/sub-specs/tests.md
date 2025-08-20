# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-08-20-fix-future-price-display-#42/spec.md

> Created: 2025-08-20
> Version: 1.0.0

## Test Coverage

### Unit Tests

#### Market Time Logic Tests
**File:** `backend/tests/test_market_time.py`

```python
class TestMarketTimeLogic:
    def test_get_available_checkpoints_historical_date(self):
        """Historical dates should return all checkpoints."""
        
    def test_get_available_checkpoints_future_date(self):
        """Future dates should return no checkpoints."""
        
    def test_get_available_checkpoints_today_pre_market(self):
        """At 7:30 AM CST, no checkpoints should be available."""
        
    def test_get_available_checkpoints_today_after_open(self):
        """At 9:00 AM CST, premarket and open should be available."""
        
    def test_get_available_checkpoints_today_midday(self):
        """At 1:30 PM CST, premarket, open, and noon should be available."""
        
    def test_get_available_checkpoints_today_after_close(self):
        """At 4:00 PM CST, all checkpoints should be available."""
        
    def test_dst_transition_spring_forward(self):
        """Test checkpoint times during DST spring transition."""
        
    def test_dst_transition_fall_back(self):
        """Test checkpoint times during DST fall transition."""
        
    def test_is_checkpoint_available_edge_cases(self):
        """Test exact checkpoint times (8:30:00, 12:00:00, etc.)."""
        
    def test_get_next_checkpoint_during_market(self):
        """Test next checkpoint calculation during market hours."""
        
    def test_get_next_checkpoint_after_close(self):
        """Test next checkpoint calculation after market close."""
```

#### Price Filtering Tests
**File:** `backend/tests/test_price_filtering.py`

```python
class TestPriceFiltering:
    def test_filter_daily_prediction_historical(self):
        """Historical predictions should not be filtered."""
        
    def test_filter_daily_prediction_today_early(self):
        """Today's prediction at 8:00 AM should show only premarket."""
        
    def test_filter_daily_prediction_today_midday(self):
        """Today's prediction at 1:00 PM should show first three prices."""
        
    def test_filter_daily_prediction_today_after_close(self):
        """Today's prediction after 3:00 PM should show all prices."""
        
    def test_filter_preserves_prediction_data(self):
        """Filtering should never affect prediction fields."""
        
    def test_filter_preserves_metadata(self):
        """Filtering should preserve non-price fields."""
        
    def test_null_price_handling(self):
        """Test filtering when some actual prices are already null."""
```

### API Integration Tests

#### Endpoint Time Filtering Tests
**File:** `backend/tests/test_api_time_filtering.py`

```python
class TestAPITimeFiltering:
    def test_get_day_historical_date(self):
        """GET /day/{date} with historical date returns complete data."""
        
    def test_get_day_today_early_morning(self):
        """GET /day/{today} at 8:00 AM returns filtered data."""
        
    def test_get_day_today_after_open(self):
        """GET /day/{today} at 9:00 AM returns partial data."""
        
    def test_get_day_today_after_close(self):
        """GET /day/{today} after 3:00 PM returns complete data."""
        
    def test_get_history_filters_today_only(self):
        """GET /history filters today's entry but not historical entries."""
        
    def test_ai_predictions_time_filtering(self):
        """AI prediction endpoints respect time filtering."""
        
    def test_invalid_date_handling(self):
        """Test API response for invalid date formats."""
        
    def test_weekend_date_handling(self):
        """Test API response for weekend dates."""
```

#### Response Format Tests
**File:** `backend/tests/test_api_responses.py`

```python
class TestAPIResponses:
    def test_null_values_in_json_response(self):
        """Verify null values are properly serialized in JSON."""
        
    def test_response_schema_consistency(self):
        """Response format should be consistent with/without filtering."""
        
    def test_api_documentation_accuracy(self):
        """OpenAPI schema should reflect time filtering behavior."""
```

### Frontend Tests

#### Component Null Handling Tests
**File:** `src/__tests__/price-display.test.tsx`

```typescript
describe('Price Display Components', () => {
  test('DashboardView handles null prices gracefully', () => {
    // Test null price rendering
  });
  
  test('PriceGrid shows appropriate loading states', () => {
    // Test "Not yet available" messaging
  });
  
  test('HistoryView displays incomplete data correctly', () => {
    // Test partial data display in history
  });
  
  test('Price formatting handles null values', () => {
    // Test formatPrice utility function
  });
});
```

#### Time State Management Tests
**File:** `src/__tests__/time-state.test.tsx`

```typescript
describe('Time State Management', () => {
  test('getCheckpointStatus returns correct states', () => {
    // Test checkpoint status calculation
  });
  
  test('UI updates when crossing checkpoint times', () => {
    // Test real-time updates (may need mocking)
  });
  
  test('Timezone handling in frontend', () => {
    // Test America/Chicago time handling
  });
});
```

### End-to-End Tests

#### Real-Time Behavior Tests
**File:** `e2e/time-filtering.spec.ts`

```typescript
describe('Time-Based Price Display', () => {
  test('Dashboard shows correct prices based on time', async () => {
    // Mock different times and verify display
  });
  
  test('History page handles incomplete current day', async () => {
    // Verify today's entry shows partial data
  });
  
  test('Price updates appear when checkpoints pass', async () => {
    // Test real-time updates (complex - may need special setup)
  });
});
```

## Mocking Requirements

### Time Mocking Strategy
```python
# Backend testing
@pytest.fixture
def mock_current_time():
    """Mock datetime.now() for consistent testing."""
    with patch('backend.app.utils.market_time.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2025, 8, 20, 9, 21, 0, tzinfo=timezone('America/Chicago'))
        yield mock_dt

# Frontend testing  
jest.mock('Date', () => {
  return class extends Date {
    constructor(...args) {
      if (args.length) {
        super(...args);
      } else {
        super('2025-08-20T09:21:00.000Z'); // Fixed time for testing
      }
    }
  };
});
```

### Market Data Mocking
```python
@pytest.fixture
def sample_daily_prediction():
    """Create sample prediction with all prices filled."""
    return DailyPrediction(
        date=date(2025, 8, 20),
        preMarket=547.30,
        open=547.85,
        noon=548.20,
        twoPM=547.95,
        close=548.15,
        predLow=546.50,
        predHigh=549.00,
        # ... other fields
    )
```

### API Response Mocking
```typescript
// Frontend API mocking
const mockApiResponse = {
  date: "2025-08-20",
  preMarket: 547.30,
  open: 547.85,
  noon: null,
  twoPM: null,
  close: null,
  predLow: 546.50,
  predHigh: 549.00
};
```

## Test Data Sets

### Time Scenarios Matrix
| Time (CST) | Premarket | Open | Noon | 2PM | Close | Test Case |
|------------|-----------|------|------|-----|-------|-----------|
| 7:30 AM    | null      | null | null | null| null  | Pre-market |
| 8:05 AM    | ✓         | null | null | null| null  | After premarket |
| 8:35 AM    | ✓         | ✓    | null | null| null  | After open |
| 12:05 PM   | ✓         | ✓    | ✓    | null| null  | After noon |
| 2:05 PM    | ✓         | ✓    | ✓    | ✓   | null  | After 2PM |
| 3:05 PM    | ✓         | ✓    | ✓    | ✓   | ✓     | After close |

### Edge Case Data Sets
- **DST Transition Dates:** March 10, 2025 (spring forward), November 2, 2025 (fall back)
- **Holiday Dates:** Memorial Day, Independence Day, Labor Day, Thanksgiving, Christmas
- **Half-Day Dates:** Day before Independence Day, Black Friday, Christmas Eve
- **Weekend Dates:** Saturday/Sunday should behave as historical dates
- **Invalid Dates:** February 30, Month 13, etc.

## Performance Testing

### Load Testing Scenarios
- **High-frequency requests:** Test filtering performance under load
- **Database query efficiency:** Ensure time filtering doesn't slow queries
- **Response time SLA:** Filtered responses should be ≤ same speed as unfiltered

### Memory Testing
- **Time zone object caching:** Ensure timezone objects are reused
- **Filtering function efficiency:** No memory leaks in filtering logic

## Acceptance Testing Checklist

### Manual Test Scenarios
- [ ] **9:21 AM CST test:** Dashboard shows premarket + open, nulls for noon/2PM/close
- [ ] **12:05 PM CST test:** Dashboard shows premarket + open + noon, nulls for 2PM/close  
- [ ] **Historical date test:** Yesterday shows complete data
- [ ] **Future date test:** Tomorrow shows only prediction data
- [ ] **Weekend test:** Saturday/Sunday behave correctly
- [ ] **API consistency test:** All endpoints return consistent time-filtered data
- [ ] **Frontend handling test:** UI gracefully handles null values
- [ ] **Regression test:** Core functionality (price capture, AI predictions) unaffected

### Automated Acceptance Criteria
All unit tests, integration tests, and E2E tests must pass with:
- **95%+ code coverage** for new time filtering logic
- **Zero regressions** in existing functionality  
- **Consistent API responses** across all endpoints
- **Proper null handling** in frontend components