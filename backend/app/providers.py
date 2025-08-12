from abc import ABC, abstractmethod
from datetime import datetime, timezone, time as time_module
from typing import Optional, Dict, Any, Tuple
import json
import os
from pathlib import Path

import yfinance as yf


class PriceProvider(ABC):
    @abstractmethod
    def get_price(self, symbol: str) -> Optional[float]:
        raise NotImplementedError
    
    @abstractmethod
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data including price, IV, volume, etc."""
        raise NotImplementedError
    
    @abstractmethod
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        raise NotImplementedError


class YFinanceProvider(PriceProvider):
    def __init__(self):
        self.cache_file = Path("/tmp/spy_cache.json")
        self.cache_duration = 60  # Cache for 60 seconds
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price with fallback to cached value"""
        try:
            # Try to get fresh data
            ticker = yf.Ticker(symbol)
            price = ticker.fast_info.last_price
            
            if price is None:
                # Fallback to recent history
                hist = ticker.history(period="1d", interval="1m")
                if hist is not None and len(hist) > 0:
                    price = float(hist["Close"].iloc[-1])
            
            if price is not None:
                # Cache the good price
                self._cache_price(symbol, float(price))
                return float(price)
            else:
                # Use cached value if available
                return self._get_cached_price(symbol)
                
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            # Fallback to cached value
            return self._get_cached_price(symbol)
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data including IV estimates"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get basic price info
            price = self.get_price(symbol)
            if price is None:
                return {}
            
            # Get recent history for volatility calculation
            hist = ticker.history(period="30d")
            if hist is None or len(hist) == 0:
                return {"price": price}
            
            # Calculate realized volatility (simplified)
            returns = hist["Close"].pct_change().dropna()
            realized_vol = returns.std() * (252 ** 0.5) if len(returns) > 1 else 0.20
            
            # Get volume info
            current_volume = hist["Volume"].iloc[-1] if len(hist) > 0 else 0
            avg_volume = hist["Volume"].rolling(20).mean().iloc[-1] if len(hist) >= 20 else current_volume
            
            return {
                "price": price,
                "volume": int(current_volume),
                "avg_volume": int(avg_volume) if avg_volume else int(current_volume),
                "volume_ratio": float(current_volume / avg_volume) if avg_volume > 0 else 1.0,
                "realized_volatility": float(realized_vol),
                "implied_volatility": float(realized_vol * 1.2),  # Rough estimate for MVP
                "high_52w": float(hist["High"].max()),
                "low_52w": float(hist["Low"].min()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching market data for {symbol}: {e}")
            # Return basic data if available
            price = self.get_price(symbol)
            return {"price": price} if price else {}
    
    def is_market_open(self) -> bool:
        """Check if US market is open (simplified version)"""
        try:
            now = datetime.now(timezone.utc)
            
            # Convert to Eastern Time (market time)
            et_offset = -5 if self._is_dst(now) else -4
            market_time = now.replace(tzinfo=timezone.utc).astimezone(
                timezone(timedelta(hours=et_offset))
            )
            
            # Check if it's a weekday
            if market_time.weekday() > 4:  # Saturday = 5, Sunday = 6
                return False
            
            # Check market hours (9:30 AM - 4:00 PM ET)
            market_open = time_module(9, 30)
            market_close = time_module(16, 0)
            current_time = market_time.time()
            
            return market_open <= current_time <= market_close
            
        except Exception:
            # Conservative fallback - assume market is open during likely hours
            return True
    
    def _cache_price(self, symbol: str, price: float) -> None:
        """Cache price data with timestamp"""
        try:
            cache_data = {
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f)
        except Exception:
            pass  # Ignore cache errors
    
    def _get_cached_price(self, symbol: str) -> Optional[float]:
        """Get cached price if recent enough"""
        try:
            if not self.cache_file.exists():
                return None
                
            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)
            
            if cache_data.get("symbol") != symbol:
                return None
            
            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cache_data["timestamp"])
            now = datetime.now(timezone.utc)
            
            if (now - cached_time).total_seconds() < self.cache_duration:
                return cache_data.get("price")
                
        except Exception:
            pass  # Ignore cache errors
        
        return None
    
    def _is_dst(self, dt: datetime) -> bool:
        """Simple DST check for US Eastern Time"""
        # Simplified: assume DST from March to November
        return 3 <= dt.month <= 10


# Enhanced default provider with caching and market data
default_provider = YFinanceProvider()


