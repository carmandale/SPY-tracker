# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-20-fix-future-price-display-#42/spec.md

> Created: 2025-08-20
> Version: 1.0.0

## Endpoints

### Modified Endpoints

#### GET /day/{date}
**Current Behavior:** Returns all price fields regardless of time
**New Behavior:** Returns time-filtered price fields based on current time vs. market checkpoints

**Response Changes:**
- Historical dates (before today): No change, returns all available prices
- Future dates: No change, returns null for all actual prices (only prediction data)
- Today's date: Returns null for future checkpoint prices

**Example Responses:**

**Historical Date (2025-08-19 accessed on 2025-08-20):**
```json
{
  "date": "2025-08-19",
  "preMarket": 545.20,
  "open": 545.80,
  "noon": 546.50,
  "twoPM": 545.90,
  "close": 547.10,
  "predLow": 544.00,
  "predHigh": 548.00,
  "rangeHit": true,
  "absErrorToClose": 0.90
}
```

**Today at 9:21 AM CST (2025-08-20):**
```json
{
  "date": "2025-08-20",
  "preMarket": 547.30,
  "open": 547.85,
  "noon": null,
  "twoPM": null,
  "close": null,
  "predLow": 546.50,
  "predHigh": 549.00,
  "rangeHit": null,
  "absErrorToClose": null
}
```

**Today at 2:15 PM CST (2025-08-20):**
```json
{
  "date": "2025-08-20",
  "preMarket": 547.30,
  "open": 547.85,
  "noon": 548.20,
  "twoPM": 547.95,
  "close": null,
  "predLow": 546.50,
  "predHigh": 549.00,
  "rangeHit": null,
  "absErrorToClose": null
}
```

#### GET /history
**Current Behavior:** Returns all entries with complete price data
**New Behavior:** Applies time filtering to today's entry only

**Response Changes:**
- Today's entry: Time-filtered prices (null for future checkpoints)
- Historical entries: No change, complete price data
- Pagination and sorting: No change

**Example Response at 10:30 AM CST:**
```json
{
  "predictions": [
    {
      "date": "2025-08-20",
      "preMarket": 547.30,
      "open": 547.85,
      "noon": null,
      "twoPM": null,
      "close": null,
      "rangeHit": null,
      "predLow": 546.50,
      "predHigh": 549.00
    },
    {
      "date": "2025-08-19",
      "preMarket": 545.20,
      "open": 545.80,
      "noon": 546.50,
      "twoPM": 545.90,
      "close": 547.10,
      "rangeHit": true,
      "predLow": 544.00,
      "predHigh": 548.00
    }
  ],
  "total": 42,
  "page": 1,
  "size": 20
}
```

#### GET /ai/predictions/{date}
**Current Behavior:** Returns AI predictions with all actual prices filled
**New Behavior:** Applies same time filtering to actual_price fields

**Response Changes:**
- `actual_price` field: null for future checkpoints
- `prediction_error` field: null when actual_price is null
- `interval_hit` field: null when actual_price is null

### Helper Endpoint (New)

#### GET /market/checkpoint-status/{date}
**Purpose:** Allow frontend to query which checkpoints are available for a given date

**Response:**
```json
{
  "date": "2025-08-20",
  "current_time": "2025-08-20T09:21:00-06:00",
  "available_checkpoints": ["premarket", "open"],
  "next_checkpoint": {
    "name": "noon",
    "time": "2025-08-20T12:00:00-06:00",
    "minutes_until": 159
  }
}
```

## Controllers

### New Utility Functions

#### market_time.py
```python
from datetime import datetime, date, time
from typing import List, Optional, Dict
from pytz import timezone

def get_available_checkpoints(target_date: date, current_time: datetime = None) -> List[str]:
    """Get list of checkpoints that have occurred for the given date."""
    
def is_checkpoint_available(checkpoint: str, target_date: date, current_time: datetime = None) -> bool:
    """Check if a specific checkpoint is available for the given date."""
    
def get_next_checkpoint(target_date: date, current_time: datetime = None) -> Optional[Dict]:
    """Get information about the next upcoming checkpoint."""
    
def filter_daily_prediction(prediction: DailyPrediction, current_time: datetime = None) -> Dict:
    """Apply time-based filtering to a DailyPrediction object."""
```

#### predictions.py (Modified Routes)
```python
@router.get("/day/{date}")
async def get_day(date: str, db: Session = Depends(get_db)):
    """Get daily prediction data with time-based filtering."""
    target_date = datetime.strptime(date, "%Y-%m-%d").date()
    prediction = get_daily_prediction(db, target_date)
    
    if prediction:
        return filter_daily_prediction(prediction, datetime.now())
    else:
        return create_empty_day_response(target_date)

@router.get("/history")
async def get_history(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    """Get prediction history with time filtering applied to today's entry."""
    predictions = get_prediction_history(db, page, size)
    current_time = datetime.now()
    
    # Apply filtering to each prediction
    filtered_predictions = []
    for pred in predictions:
        if pred.date == current_time.date():
            # Apply time filtering to today's entry
            filtered_predictions.append(filter_daily_prediction(pred, current_time))
        else:
            # Return complete data for historical entries
            filtered_predictions.append(pred.to_dict())
    
    return {
        "predictions": filtered_predictions,
        "total": len(predictions),
        "page": page,
        "size": size
    }
```

## Error Handling

### Time Zone Edge Cases
- **DST Transitions:** Handle spring forward/fall back correctly
- **Server Timezone:** Ensure consistent America/Chicago conversion regardless of server location
- **Invalid Dates:** Graceful handling of weekends, holidays, invalid dates

### API Error Responses
```json
{
  "error": {
    "message": "Invalid date format. Use YYYY-MM-DD.",
    "type": "ValidationError",
    "details": {"provided_date": "2025-13-45"}
  }
}
```

## Testing Scenarios

### Time-Based Test Cases
1. **Pre-market (7:00 AM CST):** Only prediction data, all actual prices null
2. **Market Open (8:35 AM CST):** Pre-market and open available, others null  
3. **Mid-day (1:30 PM CST):** Pre-market, open, noon available, 2PM and close null
4. **After Close (4:00 PM CST):** All checkpoints available
5. **Weekend/Holiday:** Historical behavior, no current-day filtering needed
6. **Historical Date:** All checkpoints available regardless of current time
7. **Future Date:** All actual prices null, only prediction data

### Edge Case Testing
- **DST Transition Days:** Verify correct checkpoint timing
- **Early Market Close:** Handle 1:00 PM close on half-days
- **System Clock Issues:** Graceful degradation if time service fails
- **Database Timezone Consistency:** Ensure stored times interpreted correctly