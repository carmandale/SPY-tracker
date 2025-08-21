# SPY Tracker Core Requirements

## Daily Schedule (CST/CDT)
- **8:00 AM CST:** Generate AI predictions for Open, Noon, 2PM, Close
- **8:30 AM CST:** Capture ACTUAL open price (9:30 AM ET)
- **12:00 PM CST:** Capture ACTUAL noon price (1:00 PM ET)
- **2:00 PM CST:** Capture ACTUAL 2pm price (3:00 PM ET)
- **3:00 PM CST:** Capture ACTUAL close price (4:00 PM ET)

## Data Rules
1. **Predictions happen ONCE at 8 AM** - Never later, never repeated
2. **Actual prices update ONLY after they occur** - No fake/placeholder values
3. **NO weekend dates in database** - Monday-Friday only
4. **NO fake/placeholder prices** - Use real market data only
5. **Missing data shows as null** - Not fake values like 540.0

## Current Week Status (FAILURES)
- **Monday 8/18:** ❌ INVALID - This is SUNDAY (weekend data error)
- **Tuesday 8/19:** ⚠️ LATE - Predictions created at 1:00 PM (5 hours late)
- **Wednesday 8/20:** ⚠️ LATE - Predictions created at 1:00 PM (5 hours late)
- **Thursday 8/21:** ❌ FAILED - No predictions at all (TODAY)

## Expected Behavior
- **Monday 8/19:** Should have predictions at 8:00 AM CST
- **Tuesday 8/20:** Should have predictions at 8:00 AM CST
- **Wednesday 8/21:** Should have predictions at 8:00 AM CST
- **Thursday 8/22:** Should have predictions at 8:00 AM CST
- **Friday 8/23:** Should have predictions at 8:00 AM CST

## Scheduler Requirements
1. **Timezone:** America/Chicago (handles CST/CDT automatically)
2. **Weekday filter:** Monday-Friday only (day_of_week='1-5')
3. **Job execution:** Must complete successfully or alert
4. **Error handling:** Log failures, don't create fake data
5. **Idempotency:** Running twice shouldn't create duplicates

## Data Integrity Rules
1. **Date validation:** Reject weekend dates before insert
2. **Price validation:** Prices must be > 0 and < 10000
3. **Source tracking:** Always mark data source (ai, manual, etc.)
4. **Timestamp tracking:** Record created_at and updated_at
5. **Prediction lock:** Lock predictions after market close