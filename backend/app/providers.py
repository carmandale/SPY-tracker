from abc import ABC, abstractmethod
from datetime import datetime, timezone, time as time_module, timedelta, date
from typing import Optional, Dict, Any, Tuple
import json
import os
import logging
from pathlib import Path

import yfinance as yf
import pandas as pd
import pytz

# Set up logging
logger = logging.getLogger(__name__)


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
    
    @abstractmethod
    def get_official_price(self, symbol: str, checkpoint: str) -> Optional[float]:
        """Get official OHLC price for a specific checkpoint"""
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
            logger.error(f"Error fetching price for {symbol}: {e}")
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
            logger.error(f"Error fetching market data for {symbol}: {e}")
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
    
    def get_official_price(self, symbol: str, checkpoint: str) -> Optional[float]:
        """Get official OHLC price for a specific checkpoint.
        
        For open: gets official market open price
        For noon/2PM: gets price at specific time
        For close: gets official closing price
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # For premarket, just get current price
            if checkpoint == "preMarket":
                return self.get_price(symbol)
            
            # Get today's 1-minute data
            hist = ticker.history(period="1d", interval="1m")
            if hist is None or len(hist) == 0:
                return self.get_price(symbol)  # Fallback to current price
            
            # Convert index to ET timezone for proper time matching
            et_offset = -5 if self._is_dst(datetime.now()) else -4
            hist.index = hist.index.tz_convert(f'Etc/GMT{-et_offset}')
            
            if checkpoint == "open":
                # Get the official open price (first trade of the day)
                return float(hist["Open"].iloc[0])
            elif checkpoint == "close":
                # Get the official close price (last trade of the day)
                return float(hist["Close"].iloc[-1])
            elif checkpoint == "noon":
                # Get price at 12:00 PM ET
                target_time = hist.index[0].replace(hour=12, minute=0, second=0)
                # Find closest minute to noon
                time_diff = abs(hist.index - target_time)
                closest_idx = time_diff.argmin()
                return float(hist["Close"].iloc[closest_idx])
            elif checkpoint == "twoPM":
                # Get price at 2:00 PM ET
                target_time = hist.index[0].replace(hour=14, minute=0, second=0)
                # Find closest minute to 2PM
                time_diff = abs(hist.index - target_time)
                closest_idx = time_diff.argmin()
                return float(hist["Close"].iloc[closest_idx])
            else:
                return self.get_price(symbol)
                
        except Exception as e:
            logger.error(f"Error getting official price for {symbol} at {checkpoint}: {e}")
            # Fallback to current price
            return self.get_price(symbol)
    
    def get_daily_ohlc(self, symbol: str, target_date: date) -> Optional[Dict[str, float]]:
        """Get official OHLC prices for a specific trading day.
        
        Returns a dictionary with keys: 'open', 'high', 'low', 'close'
        Returns None if no data available (weekend, holiday, or API failure)
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get daily data for the specific date
            end_date = target_date + timedelta(days=1)
            hist = ticker.history(start=target_date, end=end_date, interval="1d")
            
            if hist is None or len(hist) == 0:
                logger.warning(f"No OHLC data available for {symbol} on {target_date}")
                return None
            
            # Extract OHLC values
            row = hist.iloc[0]
            ohlc = {
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close'])
            }
            
            return ohlc
            
        except Exception as e:
            logger.error(f"Error getting daily OHLC for {symbol} on {target_date}: {e}")
            return None
    
    def get_official_checkpoint_price(self, symbol: str, checkpoint: str, target_date: date) -> Optional[float]:
        """Get official price for a specific checkpoint on a target date.
        
        For open/close: Uses daily OHLC data
        For noon/twoPM: Uses minute-level data to find price at specific time
        """
        try:
            if checkpoint in ['open', 'close']:
                # Use daily OHLC data for open/close
                ohlc = self.get_daily_ohlc(symbol, target_date)
                if ohlc is None:
                    logger.warning(f"No daily data for {symbol} on {target_date}, falling back to current price")
                    return self.get_price(symbol)
                
                return ohlc[checkpoint]
            
            elif checkpoint in ['noon', 'twoPM']:
                # Use minute-level data for intraday prices
                ticker = yf.Ticker(symbol)
                
                # Get minute data for the specific date
                end_date = target_date + timedelta(days=1)
                hist = ticker.history(start=target_date, end=end_date, interval="1m")
                
                if hist is None or len(hist) == 0:
                    logger.warning(f"No minute data for {symbol} on {target_date}, falling back to current price")
                    return self.get_price(symbol)
                
                # Convert to Eastern Time for accurate time matching
                # Use pytz timezone names for reliability
                et_tz = pytz.timezone('US/Eastern')
                hist.index = hist.index.tz_convert(et_tz)
                
                # Determine target time in ET
                if checkpoint == 'noon':
                    target_hour, target_minute = 12, 0
                elif checkpoint == 'twoPM':
                    target_hour, target_minute = 14, 0
                else:
                    raise ValueError(f"Unknown intraday checkpoint: {checkpoint}")
                
                # Find the closest minute to target time
                target_time = hist.index[0].replace(hour=target_hour, minute=target_minute, second=0)
                time_diff = abs(hist.index - target_time)
                closest_idx = time_diff.argmin()
                
                return float(hist['Close'].iloc[closest_idx])
                
            else:
                # For premarket or unknown checkpoints, use current price
                return self.get_price(symbol)
                
        except Exception as e:
            logger.error(f"Error getting official checkpoint price for {symbol} at {checkpoint} on {target_date}: {e}")
            # Fallback to current price
            return self.get_price(symbol)
    
    def validate_official_price(self, price: Optional[float], symbol: str, checkpoint: str) -> bool:
        """Validate that an official price is reasonable for the given symbol.
        
        Returns True if price passes basic sanity checks, False otherwise.
        """
        if price is None:
            return False
        
        try:
            price = float(price)
        except (ValueError, TypeError):
            return False
        
        # Basic range checks for SPY (adjust for other symbols if needed)
        if symbol.upper() == 'SPY':
            # SPY should be between $50 and $2000 (very wide range for safety)
            min_price = 50.0
            max_price = 2000.0
        else:
            # Generic stock price range
            min_price = 1.0
            max_price = 10000.0
        
        # Check if price is within reasonable bounds
        if price <= 0 or price < min_price or price > max_price:
            logger.warning(f"Invalid price {price} for {symbol} at {checkpoint} - outside range [{min_price}, {max_price}]")
            return False
        
        return True


# Enhanced default provider with caching and market data
default_provider = YFinanceProvider()


