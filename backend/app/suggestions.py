from dataclasses import dataclass
from typing import List, Optional, Tuple
import math
import logging

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class Suggestion:
    tenor: str  # 0DTE, 1W, 1M
    strategy: str  # IC/IB
    short_delta: Optional[float] = None
    long_delta: Optional[float] = None
    min_credit: Optional[float] = None
    expected_move: Optional[float] = None
    wings: Optional[float] = None
    center_strike: Optional[float] = None
    put_short_strike: Optional[float] = None
    put_long_strike: Optional[float] = None
    call_short_strike: Optional[float] = None
    call_long_strike: Optional[float] = None
    max_profit: Optional[float] = None
    max_loss: Optional[float] = None
    breakeven_lower: Optional[float] = None
    breakeven_upper: Optional[float] = None
    profit_target: Optional[float] = None
    stop_loss: Optional[float] = None
    rationale: str = ""
    note: str = ""
    management_notes: str = ""


def calculate_expected_move(current_price: float, iv: float, days_to_expiry: int) -> float:
    """Calculate expected move using EM ≈ S * IV * sqrt(T/365)"""
    if current_price <= 0 or iv <= 0 or days_to_expiry <= 0:
        return 0.0
    return current_price * iv * math.sqrt(days_to_expiry / 365.0)


def round_to_strike(price: float, interval: float = 1.0) -> float:
    """Round price to nearest valid strike price (typically $1 intervals for SPY)"""
    return round(price / interval) * interval


def calculate_strike_from_delta(current_price: float, delta: float, iv: float, days: int, is_call: bool = True) -> float:
    """
    Approximate strike price for a given delta using simplified Black-Scholes.
    This is a rough approximation for MVP - real implementation would use proper Greeks.
    """
    # Simplified approximation: strikes move roughly linearly with delta near ATM
    # For puts: strike ≈ current_price * (1 - delta * iv * sqrt(days/365))
    # For calls: strike ≈ current_price * (1 + delta * iv * sqrt(days/365))
    time_factor = math.sqrt(days / 365.0)
    
    if is_call:
        strike = current_price * (1 + delta * iv * time_factor * 2.5)  # 2.5 is approximation factor
    else:
        strike = current_price * (1 - delta * iv * time_factor * 2.5)
    
    return round_to_strike(strike)


def calculate_ic_metrics(wing_width: float, credit: float) -> Tuple[float, float]:
    """Calculate max profit and max loss for Iron Condor"""
    max_profit = credit
    max_loss = wing_width - credit
    return max_profit, max_loss


def calculate_ib_metrics(wing_width: float, credit: float) -> Tuple[float, float]:
    """Calculate max profit and max loss for Iron Butterfly"""
    max_profit = credit
    max_loss = wing_width - credit
    return max_profit, max_loss


def generate_suggestions(
    current_price: Optional[float] = None,
    bias: str = "Neutral",
    rangeHit20: float = 0.0,
    pred_low: Optional[float] = None,
    pred_high: Optional[float] = None,
    iv: Optional[float] = None
) -> List[Suggestion]:
    """Generate option structure suggestions based on EM and market conditions"""
    
    suggestions: List[Suggestion] = []
    
    # Validate IV - use reasonable default if not provided
    if iv is None or iv <= 0:
        # Use a reasonable market-based default (around 15% for SPY historically)
        iv = 0.15
        logger.warning(f"Invalid or missing IV, using default {iv:.1%}")
    elif iv > 1.0:
        # IV should be decimal, not percentage
        logger.warning(f"IV appears to be percentage ({iv}), converting to decimal")
        iv = iv / 100.0
    
    # If no current price, try to use prediction midpoint
    if current_price is None:
        if pred_low is not None and pred_high is not None:
            current_price = (pred_low + pred_high) / 2.0
            logger.info(f"Using prediction midpoint as current price: ${current_price:.2f}")
        else:
            # Can't generate suggestions without a price
            logger.error("Cannot generate suggestions without a current price or predictions")
            return suggestions
    
    # Validate current price
    if current_price <= 0:
        logger.error(f"Invalid current price: ${current_price}")
        return suggestions
    
    # Determine structure: IC if Neutral bias and good hit rate, else IB
    use_ic = (bias == "Neutral" and rangeHit20 >= 0.65)
    
    # Generate suggestions for each tenor
    tenors = [
        {"name": "0DTE", "days": 1, "ic_delta": 0.12, "min_credit_ic": 0.30, "wing_width": 5.0},
        {"name": "1W", "days": 7, "ic_delta": 0.18, "min_credit_ic": 0.50, "wing_width": 10.0},
        {"name": "1M", "days": 30, "ic_delta": 0.20, "min_credit_ic": 1.20, "wing_width": 15.0},
    ]
    
    for tenor_info in tenors:
        tenor = tenor_info["name"]
        days = tenor_info["days"]
        wing_width = tenor_info["wing_width"]
        
        # Calculate expected move for this tenor
        em = calculate_expected_move(current_price, iv, days)
        
        if use_ic:
            # Iron Condor suggestion with actual strike calculations
            short_delta = tenor_info["ic_delta"]
            long_delta = tenor_info["ic_delta"] / 2.0  # Long legs at half delta
            
            # Calculate strike prices from deltas
            put_short_strike = calculate_strike_from_delta(current_price, short_delta, iv, days, is_call=False)
            put_long_strike = round_to_strike(put_short_strike - wing_width)
            call_short_strike = calculate_strike_from_delta(current_price, short_delta, iv, days, is_call=True)
            call_long_strike = round_to_strike(call_short_strike + wing_width)
            
            # Calculate estimated credit (simplified for MVP - 30% of wing width is typical)
            estimated_credit = wing_width * 0.30
            max_profit, max_loss = calculate_ic_metrics(wing_width, estimated_credit)
            
            # Calculate breakevens
            breakeven_lower = put_short_strike - estimated_credit
            breakeven_upper = call_short_strike + estimated_credit
            
            # Calculate profit target and stop loss
            profit_target = max_profit * 0.25 if tenor == "0DTE" else max_profit * 0.40
            stop_loss = estimated_credit * 2.0  # Stop at 2x credit received
            
            suggestion = Suggestion(
                tenor=tenor,
                strategy="Iron Condor",
                short_delta=short_delta,
                long_delta=long_delta,
                min_credit=tenor_info["min_credit_ic"],
                expected_move=em,
                wings=wing_width,
                put_short_strike=put_short_strike,
                put_long_strike=put_long_strike,
                call_short_strike=call_short_strike,
                call_long_strike=call_long_strike,
                max_profit=max_profit,
                max_loss=max_loss,
                breakeven_lower=breakeven_lower,
                breakeven_upper=breakeven_upper,
                profit_target=profit_target,
                stop_loss=stop_loss,
                rationale=f"IC selected: Neutral bias with {rangeHit20:.0%} hit rate",
                note=f"Strikes: {put_long_strike:.0f}/{put_short_strike:.0f}/{call_short_strike:.0f}/{call_long_strike:.0f}"
            )
            
            # Add management notes
            if tenor == "0DTE":
                suggestion.management_notes = "Manage at 25% profit or 2x loss. Watch gamma risk after 2PM."
            elif tenor == "1W":
                suggestion.management_notes = "Manage at 25-50% profit. Consider rolling at 21 DTE if tested."
            elif tenor == "1M":
                suggestion.management_notes = "Manage at 30-50% profit early. Defend tested side at 50% loss."
                
        else:
            # Iron Butterfly suggestion with actual strike calculations
            pred_mid = (pred_low + pred_high) / 2.0 if pred_low and pred_high else current_price
            
            # Skew center strike based on bias
            center_adjustment = 0.0
            if bias == "Up":
                center_adjustment = em * 0.1  # Skew 10% of EM upward
            elif bias == "Down":
                center_adjustment = -em * 0.1  # Skew 10% of EM downward
            
            center_strike = round_to_strike(pred_mid + center_adjustment)
            
            # Calculate wing strikes
            ib_wing_width = em * 0.75  # Wings at 0.75x expected move
            put_long_strike = round_to_strike(center_strike - ib_wing_width)
            call_long_strike = round_to_strike(center_strike + ib_wing_width)
            
            # For IB, short strikes are at the center
            put_short_strike = center_strike
            call_short_strike = center_strike
            
            # Calculate estimated credit (IB typically captures 40% of wing width)
            estimated_credit = ib_wing_width * 0.40
            max_profit, max_loss = calculate_ib_metrics(ib_wing_width, estimated_credit)
            
            # Calculate breakevens
            breakeven_lower = center_strike - estimated_credit
            breakeven_upper = center_strike + estimated_credit
            
            # Calculate profit target and stop loss
            profit_target = max_profit * 0.15 if tenor == "0DTE" else max_profit * 0.25
            stop_loss = estimated_credit * 1.5  # Tighter stop for IB
            
            suggestion = Suggestion(
                tenor=tenor,
                strategy="Iron Butterfly",
                center_strike=center_strike,
                wings=ib_wing_width,
                expected_move=em,
                put_short_strike=put_short_strike,
                put_long_strike=put_long_strike,
                call_short_strike=call_short_strike,
                call_long_strike=call_long_strike,
                max_profit=max_profit,
                max_loss=max_loss,
                breakeven_lower=breakeven_lower,
                breakeven_upper=breakeven_upper,
                profit_target=profit_target,
                stop_loss=stop_loss,
                rationale=f"IB selected: {bias} bias or hit rate {rangeHit20:.0%} < 65%",
                note=f"Butterfly at {center_strike:.0f} with wings {put_long_strike:.0f}/{call_long_strike:.0f}"
            )
            
            # Add management notes
            if tenor == "0DTE":
                suggestion.management_notes = "Manage at 10-15% profit quickly. High gamma risk near center."
            elif tenor == "1W":
                suggestion.management_notes = "Manage at 15-25% profit. Convert to IC if breached early."
            elif tenor == "1M":
                suggestion.management_notes = "Manage at 20-30% profit. Consider butterfly roll if trending."
        
        suggestions.append(suggestion)
    
    return suggestions
