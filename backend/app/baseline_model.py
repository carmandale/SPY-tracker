"""
Statistical baseline model for SPY price predictions.

This module provides a simple statistical baseline model for predicting
SPY prices at key checkpoints. It uses a combination of:
1. Previous close anchor
2. Pre-market price (if available)
3. Average True Range (ATR) for volatility estimation
4. Time-of-day seasonality patterns
5. Mean reversion tendencies

The baseline serves as a comparison point for LLM predictions and
can be used as a fallback when LLM predictions are unavailable.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import math
import statistics
import numpy as np
import pandas as pd
import yfinance as yf

from .timezone_utils import ET, get_checkpoint_datetime
from .models import AIPrediction


class BaselinePredictor:
    """Statistical baseline model for SPY price predictions."""
    
    def __init__(self, symbol: str = "SPY", lookback_days: int = 20):
        """
        Initialize the baseline predictor.
        
        Args:
            symbol: Ticker symbol to predict
            lookback_days: Number of trading days to use for statistics
        """
        self.symbol = symbol
        self.lookback_days = lookback_days
        self.seasonality = None  # Will be populated on first use
    
    def predict(self, target_date: date, pre_market_price: Optional[float] = None,
                previous_close: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Generate predictions for the target date.
        
        Args:
            target_date: Date to predict
            pre_market_price: Pre-market price if available
            previous_close: Previous day's closing price if available
            
        Returns:
            List of prediction dictionaries with checkpoint, price, and intervals
        """
        # Get market data if not provided
        market_data = self._get_market_data(target_date, previous_close)
        if not market_data:
            return []
        
        previous_close = market_data.get('previous_close')
        if not previous_close:
            return []
        
        # Use provided pre-market price or default to previous close
        anchor_price = pre_market_price if pre_market_price is not None else previous_close
        
        # Get ATR for volatility estimation
        atr = market_data.get('atr', previous_close * 0.01)  # Default to 1% if unavailable
        
        # Get intraday seasonality patterns
        if self.seasonality is None:
            self.seasonality = self._calculate_seasonality()
        
        # Generate predictions for each checkpoint
        predictions = []
        
        # Define checkpoints
        checkpoints = ["open", "noon", "twoPM", "close"]
        
        for i, checkpoint in enumerate(checkpoints):
            # Get seasonality factor for this checkpoint
            seasonality_factor = self.seasonality.get(checkpoint, 0)
            
            # Calculate expected drift based on seasonality and time of day
            if checkpoint == "open":
                # Open prediction based on pre-market
                if pre_market_price is not None:
                    # Small mean reversion from pre-market to open
                    drift = (pre_market_price - previous_close) * 0.8
                else:
                    drift = 0
            elif checkpoint == "noon":
                # Noon often shows continuation of morning trend
                morning_drift = predictions[0]["predicted_price"] - previous_close if predictions else 0
                drift = morning_drift * 1.2 + seasonality_factor * atr
            elif checkpoint == "twoPM":
                # 2PM often shows some mean reversion
                morning_drift = predictions[0]["predicted_price"] - previous_close if predictions else 0
                midday_drift = predictions[1]["predicted_price"] - previous_close if len(predictions) > 1 else 0
                drift = (morning_drift + midday_drift) / 2 + seasonality_factor * atr
            else:  # close
                # Close often reverts somewhat to the day's average
                if len(predictions) >= 3:
                    day_avg = sum(p["predicted_price"] for p in predictions) / len(predictions)
                    drift = (day_avg - previous_close) * 0.7 + seasonality_factor * atr
                else:
                    drift = seasonality_factor * atr
            
            # Calculate predicted price
            predicted_price = previous_close + drift
            
            # Calculate confidence intervals based on time of day
            # Intervals widen as the day progresses
            interval_width = atr * (0.5 + i * 0.1)  # Wider intervals later in day
            interval_low = predicted_price - interval_width / 2
            interval_high = predicted_price + interval_width / 2
            
            # Add prediction
            predictions.append({
                "checkpoint": checkpoint,
                "predicted_price": predicted_price,
                "confidence": 0.7 - (i * 0.05),  # Decreasing confidence through day
                "reasoning": f"Baseline: {checkpoint} prediction using ATR and seasonality",
                "interval_low": interval_low,
                "interval_high": interval_high,
                "source": "baseline"
            })
        
        return predictions
    
    def _get_market_data(self, target_date: date, 
                         previous_close: Optional[float] = None) -> Dict[str, Any]:
        """
        Get market data for the target date and preceding period.
        
        Args:
            target_date: Date to get data for
            previous_close: Previous day's closing price if available
            
        Returns:
            Dictionary with market data
        """
        try:
            # Calculate date range
            end_date = target_date
            start_date = end_date - timedelta(days=self.lookback_days * 2)  # Extra days for weekends/holidays
            
            # Get historical data
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                return {}
            
            # Calculate ATR
            high_low = hist['High'] - hist['Low']
            high_close = abs(hist['High'] - hist['Close'].shift())
            low_close = abs(hist['Low'] - hist['Close'].shift())
            
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.rolling(window=14).mean().iloc[-1]
            
            # Get previous close if not provided
            if previous_close is None:
                previous_close = hist['Close'].iloc[-1]
            
            return {
                'previous_close': float(previous_close),
                'atr': float(atr),
                'recent_high': float(hist['High'].tail(5).max()),
                'recent_low': float(hist['Low'].tail(5).min()),
                'volume_avg': float(hist['Volume'].tail(5).mean())
            }
            
        except Exception as e:
            print(f"Error getting market data: {e}")
            return {}
    
    def _calculate_seasonality(self) -> Dict[str, float]:
        """
        Calculate intraday seasonality patterns based on historical data.
        
        Returns:
            Dictionary mapping checkpoints to average price changes
        """
        try:
            # For simplicity, we'll use some reasonable defaults based on
            # typical SPY intraday patterns
            # In a production system, this would be calculated from actual data
            
            # These values represent typical % of daily range by checkpoint
            # Positive values indicate tendency to rise, negative to fall
            return {
                "open": 0.0,      # Neutral at open
                "noon": 0.2,      # Slight upward bias by noon
                "twoPM": 0.1,     # Slight mean reversion in afternoon
                "close": 0.15     # Slight upward bias into close
            }
            
        except Exception as e:
            print(f"Error calculating seasonality: {e}")
            return {"open": 0.0, "noon": 0.0, "twoPM": 0.0, "close": 0.0}


# Global instance
baseline_predictor = BaselinePredictor()

