# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-16-official-price-capture-fix-#8/spec.md

> Created: 2025-08-16
> Version: 1.0.0

## Technical Requirements

- **Official Price Fetching**: Use yfinance historical data with 1-minute intervals to get precise checkpoint prices
- **Timezone Handling**: Convert market data to Eastern Time for accurate time matching
- **Error Handling**: Graceful fallback to current price when historical data unavailable
- **Data Validation**: Verify official prices are reasonable (within market hours, non-zero values)
- **Logging**: Track when official vs fallback prices are used for monitoring
- **Performance**: Cache historical data requests to avoid repeated API calls for same day

## Approach Options

**Option A:** Fix existing get_official_price method with better timezone handling and validation
- Pros: Minimal code changes, builds on existing implementation
- Cons: May still have edge cases with timezone conversion

**Option B:** Rewrite price capture using end-of-day OHLC data fetch (Selected)
- Pros: More reliable, cleaner separation of real-time vs historical prices
- Cons: Requires more significant changes to capture workflow

**Rationale:** Option B provides better long-term reliability and clearer separation between real-time tracking and official price recording.

## Implementation Details

### Enhanced YFinanceProvider Methods

```python
def get_daily_ohlc(self, symbol: str, target_date: date) -> Optional[Dict[str, float]]:
    """Get official OHLC prices for a specific trading day"""
    
def get_official_checkpoint_price(self, symbol: str, checkpoint: str, target_date: date) -> Optional[float]:
    """Get official price for specific checkpoint on target date"""
    
def validate_official_price(self, price: float, symbol: str, checkpoint: str) -> bool:
    """Validate that an official price is reasonable"""
```

### Scheduler Updates

- Modify capture_price to use target_date parameter
- Add validation before storing prices
- Enhanced logging for monitoring
- Graceful fallback handling

### Admin Endpoints

- `POST /admin/refresh-official-prices/{date}` - Refresh single day
- `POST /admin/refresh-official-prices-range` - Refresh date range
- `GET /admin/price-capture-status` - Monitor capture quality

## External Dependencies

No new dependencies required - uses existing yfinance integration with enhanced error handling and validation.