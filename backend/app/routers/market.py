"""
Market data endpoints for SPY Tracker.
Handles real-time market data retrieval and status checks.
"""

from datetime import datetime, timezone
from fastapi import APIRouter

from ..config import settings
from ..providers import default_provider
from ..exceptions import MarketDataException

router = APIRouter(tags=["market"])


@router.get("/market-data/{symbol}")
def get_market_data(symbol: str = "SPY"):
    """Get comprehensive market data including price, IV, volume, etc."""
    try:
        market_data = default_provider.get_market_data(symbol.upper())
        
        if not market_data:
            raise MarketDataException(
                f"Market data not available for {symbol.upper()}",
                {"symbol": symbol.upper(), "provider": "yfinance"}
            )
        
        # Add market status
        market_data["market_open"] = default_provider.is_market_open()
        
        return {
            "symbol": symbol.upper(),
            "data": market_data,
            "provider": "yfinance",
            "cached": False  # Could implement cache detection later
        }
        
    except MarketDataException:
        raise
    except Exception as e:
        raise MarketDataException(
            f"Failed to fetch market data for {symbol.upper()}",
            {"symbol": symbol.upper(), "error": str(e)}
        )


@router.get("/market-status")
def get_market_status():
    """Get current market status"""
    try:
        is_open = default_provider.is_market_open()
        current_price = default_provider.get_price(settings.symbol)
        
        return {
            "market_open": is_open,
            "current_time_utc": datetime.now(timezone.utc).isoformat(),
            "symbol": settings.symbol,
            "current_price": current_price,
            "status": "open" if is_open else "closed"
        }
        
    except Exception as e:
        raise MarketDataException(
            "Failed to get market status",
            {"error": str(e), "hint": "Market data provider may be unavailable"}
        )