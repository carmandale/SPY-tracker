# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-20-fix-future-price-display-#42/spec.md

> Created: 2025-08-20
> Version: 1.0.0

## Technical Requirements

### Core Time Logic Implementation

**Market Checkpoint Definition:**
- Pre-market: 8:00 AM CST/CDT
- Open: 8:30 AM CST/CDT  
- Noon: 12:00 PM CST/CDT
- 2PM: 2:00 PM CST/CDT
- Close: 3:00 PM CST/CDT (4:00 PM ET)

**Time Filtering Logic:**
```python
def get_available_checkpoints(target_date: date, current_time: datetime) -> List[str]:
    """
    Returns list of checkpoints that have occurred for the given date.
    For historical dates (before today), returns all checkpoints.
    For future dates, returns empty list.
    For today, returns checkpoints based on current time.
    """
    if target_date < current_time.date():
        return ["premarket", "open", "noon", "twoPM", "close"]
    elif target_date > current_time.date():
        return []
    else:
        # Today - check against actual times
        available = []
        chicago_time = current_time.astimezone(timezone('America/Chicago'))
        
        if chicago_time.time() >= time(8, 0):  # 8:00 AM
            available.append("premarket")
        if chicago_time.time() >= time(8, 30):  # 8:30 AM
            available.append("open")
        if chicago_time.time() >= time(12, 0):  # 12:00 PM
            available.append("noon")
        if chicago_time.time() >= time(14, 0):  # 2:00 PM
            available.append("twoPM")
        if chicago_time.time() >= time(15, 0):  # 3:00 PM
            available.append("close")
            
        return available
```

**Price Filtering Implementation:**
```python
def filter_prices_by_time(prediction: DailyPrediction, current_time: datetime) -> Dict:
    """Filter price fields based on available checkpoints."""
    available_checkpoints = get_available_checkpoints(prediction.date, current_time)
    
    return {
        "date": prediction.date.isoformat(),
        "premarket": prediction.preMarket if "premarket" in available_checkpoints else None,
        "open": prediction.open if "open" in available_checkpoints else None,
        "noon": prediction.noon if "noon" in available_checkpoints else None,
        "twoPM": prediction.twoPM if "twoPM" in available_checkpoints else None,
        "close": prediction.close if "close" in available_checkpoints else None,
        # Always show prediction data and metadata
        "predLow": prediction.predLow,
        "predHigh": prediction.predHigh,
        "bias": prediction.bias,
        # ... other fields
    }
```

### API Response Format Changes

**Before (Current Behavior):**
```json
{
  "date": "2025-08-20",
  "premarket": 545.50,
  "open": 546.25,
  "noon": 547.80,
  "twoPM": 546.90,
  "close": 548.15,
  "predLow": 545.00,
  "predHigh": 549.00
}
```

**After (Time-Filtered at 9:21am CST):**
```json
{
  "date": "2025-08-20",
  "premarket": 545.50,
  "open": 546.25,
  "noon": null,
  "twoPM": null,
  "close": null,
  "predLow": 545.00,
  "predHigh": 549.00
}
```

### Database Changes

**No schema changes required** - this is purely a business logic change in data retrieval and presentation.

**Model Enhancement:**
```python
class DailyPrediction(Base):
    # ... existing fields ...
    
    def to_dict_filtered(self, current_time: datetime = None) -> Dict:
        """Return dictionary representation with time-based filtering."""
        if current_time is None:
            current_time = datetime.now(timezone('America/Chicago'))
        
        return filter_prices_by_time(self, current_time)
```

### Frontend Handling

**Null Value Display Logic:**
```typescript
function formatPrice(price: number | null, label: string): string {
  if (price === null) {
    return `${label}: Not yet available`;
  }
  return `${label}: $${price.toFixed(2)}`;
}

function getCheckpointStatus(checkpoint: string, currentTime: Date): 'completed' | 'pending' | 'upcoming' {
  const chicagoTime = new Date(currentTime.toLocaleString("en-US", {timeZone: "America/Chicago"}));
  const hour = chicagoTime.getHours();
  const minute = chicagoTime.getMinutes();
  
  switch (checkpoint) {
    case 'premarket':
      return hour >= 8 ? 'completed' : 'upcoming';
    case 'open':
      return (hour > 8 || (hour === 8 && minute >= 30)) ? 'completed' : 'upcoming';
    case 'noon':
      return hour >= 12 ? 'completed' : 'upcoming';
    case 'twoPM':
      return hour >= 14 ? 'completed' : 'upcoming';
    case 'close':
      return hour >= 15 ? 'completed' : 'upcoming';
    default:
      return 'upcoming';
  }
}
```

## Approach

1. **Centralized Time Logic** - Create utility functions in `backend/app/utils/market_time.py` for consistent time handling
2. **Model-Level Filtering** - Add filtering methods to the `DailyPrediction` model for clean separation of concerns
3. **Endpoint Updates** - Modify existing endpoints to use filtered responses without changing API contracts
4. **Frontend Adaptation** - Update UI components to handle null values gracefully with appropriate user messaging
5. **Comprehensive Testing** - Test time edge cases, timezone handling, and regression scenarios

## External Dependencies

- **pytz** - Already installed for timezone handling
- **datetime** - Standard library for time operations
- No new external dependencies required

## Risk Mitigation

- **Timezone Consistency** - Use centralized timezone conversion to avoid DST issues
- **Historical Data Preservation** - Ensure filtering only applies to current date, never modify stored data
- **API Backward Compatibility** - Maintain existing response structure, only change which fields are null
- **Testing Coverage** - Extensive time-scenario testing to catch edge cases
- **Gradual Rollout** - Test thoroughly in development before production deployment