from dataclasses import dataclass
from typing import List, Optional, Tuple
import math


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


def generate_suggestions(
    current_price: Optional[float] = None,
    bias: str = "Neutral",
    rangeHit20: float = 0.0,
    pred_low: Optional[float] = None,
    pred_high: Optional[float] = None,
    iv: float = 0.18  # Default 18% IV for MVP
) -> List[Suggestion]:
    """Generate option structure suggestions based on EM and market conditions"""
    
    suggestions: List[Suggestion] = []
    
    # If no current price, try to use prediction midpoint
    if current_price is None:
        if pred_low is not None and pred_high is not None:
            current_price = (pred_low + pred_high) / 2.0
        else:
            # Can't generate suggestions without a price
            return suggestions
    
    # Determine structure: IC if Neutral bias and good hit rate, else IB
    use_ic = (bias == "Neutral" and rangeHit20 >= 0.65)
    
    # Generate suggestions for each tenor
    tenors = [
        {"name": "0DTE", "days": 1, "ic_delta": 0.12, "min_credit_ic": 0.30},
        {"name": "1W", "days": 7, "ic_delta": 0.18, "min_credit_ic": 0.50},
        {"name": "1M", "days": 30, "ic_delta": 0.20, "min_credit_ic": 1.20},
    ]
    
    for tenor_info in tenors:
        tenor = tenor_info["name"]
        days = tenor_info["days"]
        
        # Calculate expected move for this tenor
        em = calculate_expected_move(current_price, iv, days)
        
        if use_ic:
            # Iron Condor suggestion
            suggestion = Suggestion(
                tenor=tenor,
                strategy="Iron Condor",
                short_delta=tenor_info["ic_delta"],
                long_delta=tenor_info["ic_delta"] / 2.0,  # Long legs at half delta
                min_credit=tenor_info["min_credit_ic"],
                expected_move=em,
                rationale=f"IC selected: Neutral bias with {rangeHit20:.0%} hit rate",
                note=f"Target ±{tenor_info['ic_delta']:.0f}Δ shorts, EM={em:.2f}, min credit ${tenor_info['min_credit_ic']:.2f}"
            )
            
            # Add management notes
            if tenor == "0DTE":
                suggestion.note += "; Manage at 25% profit or 2x loss"
            elif tenor == "1W":
                suggestion.note += "; Manage at 25-50% profit"
            elif tenor == "1M":
                suggestion.note += "; Manage at 30-50% profit early"
                
        else:
            # Iron Butterfly suggestion
            pred_mid = (pred_low + pred_high) / 2.0 if pred_low and pred_high else current_price
            
            # Skew center strike based on bias
            center_strike = pred_mid
            if bias == "Up":
                center_strike = pred_mid + (em * 0.1)  # Skew 10% of EM upward
            elif bias == "Down":
                center_strike = pred_mid - (em * 0.1)  # Skew 10% of EM downward
            
            # Wings at 0.75x expected move
            wing_width = em * 0.75
            
            suggestion = Suggestion(
                tenor=tenor,
                strategy="Iron Butterfly",
                center_strike=center_strike,
                wings=wing_width,
                expected_move=em,
                rationale=f"IB selected: {bias} bias or hit rate {rangeHit20:.0%} < 65%",
                note=f"Center near {center_strike:.0f}, wings ±{wing_width:.0f} (0.75× EM={em:.2f})"
            )
            
            # Add management notes
            if tenor == "0DTE":
                suggestion.note += "; Manage at 10-15% profit quickly"
            elif tenor == "1W":
                suggestion.note += "; Manage at 15-25% profit"
            elif tenor == "1M":
                suggestion.note += "; Manage at 20-30% profit"
        
        suggestions.append(suggestion)
    
    return suggestions
