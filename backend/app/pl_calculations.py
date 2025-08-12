"""
P&L Calculation Engine for Option Strategies
Optimized for fast calculation of Iron Condor and Iron Butterfly profit/loss curves.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np


@dataclass
class PLPoint:
    """Single point on P&L curve"""
    underlying_price: float
    total_pl: float
    put_spread_pl: float
    call_spread_pl: float


@dataclass
class PLData:
    """Complete P&L analysis for an option strategy"""
    points: List[PLPoint]
    breakeven_lower: float
    breakeven_upper: float
    max_profit: float
    max_loss: float
    current_price: float
    profit_zone_start: float
    profit_zone_end: float


class PLCalculator:
    """High-performance P&L calculation engine"""
    
    @staticmethod
    def calculate_iron_condor_pl(
        put_long: float,
        put_short: float,
        call_short: float,
        call_long: float,
        credit_received: float,
        current_price: float,
        price_range_pct: float = 0.2,
        resolution: int = 100
    ) -> PLData:
        """
        Calculate P&L curve for Iron Condor strategy.
        
        Args:
            put_long: Long put strike price
            put_short: Short put strike price  
            call_short: Short call strike price
            call_long: Long call strike price
            credit_received: Net credit received from opening position
            current_price: Current underlying price
            price_range_pct: Price range as percentage of current price (±20% default)
            resolution: Number of points to calculate
            
        Returns:
            PLData object with complete P&L analysis
        """
        # Calculate price range for analysis - constrained by strikes
        # Add small buffer (2%) beyond the long strikes for better visualization
        buffer = 0.02
        min_price = put_long * (1 - buffer)
        max_price = call_long * (1 + buffer)
        
        # Generate price points
        prices = np.linspace(min_price, max_price, resolution)
        points = []
        
        for price in prices:
            # Put spread P&L (credit spread)
            put_intrinsic_short = max(0, put_short - price)
            put_intrinsic_long = max(0, put_long - price)
            put_spread_pl = put_intrinsic_long - put_intrinsic_short
            
            # Call spread P&L (credit spread)
            call_intrinsic_short = max(0, price - call_short)
            call_intrinsic_long = max(0, price - call_long)
            call_spread_pl = call_intrinsic_long - call_intrinsic_short
            
            # Total P&L = credit received + spread P&L
            total_pl = credit_received + put_spread_pl + call_spread_pl
            
            points.append(PLPoint(
                underlying_price=float(price),
                total_pl=float(total_pl),
                put_spread_pl=float(put_spread_pl),
                call_spread_pl=float(call_spread_pl)
            ))
        
        # Calculate breakeven points
        breakeven_lower = put_short - credit_received
        breakeven_upper = call_short + credit_received
        
        # Max profit occurs between short strikes
        max_profit = credit_received
        
        # Max loss occurs at wings
        put_spread_width = put_short - put_long
        call_spread_width = call_long - call_short
        max_loss = min(
            put_spread_width - credit_received,
            call_spread_width - credit_received
        )
        
        return PLData(
            points=points,
            breakeven_lower=breakeven_lower,
            breakeven_upper=breakeven_upper,
            max_profit=max_profit,
            max_loss=-abs(max_loss),  # Ensure negative for loss
            current_price=current_price,
            profit_zone_start=put_short,
            profit_zone_end=call_short
        )
    
    @staticmethod
    def calculate_iron_butterfly_pl(
        put_long: float,
        center_strike: float,
        call_long: float,
        credit_received: float,
        current_price: float,
        price_range_pct: float = 0.2,
        resolution: int = 100
    ) -> PLData:
        """
        Calculate P&L curve for Iron Butterfly strategy.
        
        Args:
            put_long: Long put strike price
            center_strike: Short put/call strike (ATM)
            call_long: Long call strike price
            credit_received: Net credit received from opening position
            current_price: Current underlying price
            price_range_pct: Price range as percentage of current price
            resolution: Number of points to calculate
            
        Returns:
            PLData object with complete P&L analysis
        """
        # Iron Butterfly is essentially an Iron Condor with center strikes equal
        return PLCalculator.calculate_iron_condor_pl(
            put_long=put_long,
            put_short=center_strike,
            call_short=center_strike,
            call_long=call_long,
            credit_received=credit_received,
            current_price=current_price,
            price_range_pct=price_range_pct,
            resolution=resolution
        )
    
    @staticmethod
    def calculate_current_pl(
        strategy_type: str,
        strikes: dict,
        credit_received: float,
        current_price: float
    ) -> float:
        """
        Calculate current P&L for a strategy at current underlying price.
        Fast calculation for real-time updates.
        
        Args:
            strategy_type: "Iron Condor" or "Iron Butterfly"
            strikes: Dictionary with strike prices
            credit_received: Net credit received
            current_price: Current underlying price
            
        Returns:
            Current profit/loss value
        """
        if strategy_type == "Iron Condor":
            put_long = strikes.get('put_long')
            put_short = strikes.get('put_short')
            call_short = strikes.get('call_short')
            call_long = strikes.get('call_long')
            
            # Put spread P&L
            put_intrinsic_short = max(0, put_short - current_price)
            put_intrinsic_long = max(0, put_long - current_price)
            put_spread_pl = put_intrinsic_long - put_intrinsic_short
            
            # Call spread P&L
            call_intrinsic_short = max(0, current_price - call_short)
            call_intrinsic_long = max(0, current_price - call_long)
            call_spread_pl = call_intrinsic_long - call_intrinsic_short
            
            return credit_received + put_spread_pl + call_spread_pl
            
        elif strategy_type == "Iron Butterfly":
            put_long = strikes.get('put_long')
            center = strikes.get('center_strike')
            call_long = strikes.get('call_long')
            
            # Put spread P&L
            put_intrinsic_short = max(0, center - current_price)
            put_intrinsic_long = max(0, put_long - current_price)
            put_spread_pl = put_intrinsic_long - put_intrinsic_short
            
            # Call spread P&L
            call_intrinsic_short = max(0, current_price - center)
            call_intrinsic_long = max(0, current_price - call_long)
            call_spread_pl = call_intrinsic_long - call_intrinsic_short
            
            return credit_received + put_spread_pl + call_spread_pl
        
        return 0.0


# Singleton instance for performance
pl_calculator = PLCalculator()