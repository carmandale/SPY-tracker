"""
Option suggestions and P&L calculation endpoints for SPY Tracker.
Handles Iron Condor/Butterfly suggestions and profit/loss calculations.
"""

from datetime import date, datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models import DailyPrediction
from ..suggestions import generate_suggestions
from ..pl_calculations import pl_calculator

router = APIRouter(tags=["suggestions"])


@router.get("/suggestions/{day}")
def get_suggestions(day: date, db: Session = Depends(get_db)):
    # Get prediction for the day to extract needed data
    pred = db.query(DailyPrediction).filter(DailyPrediction.date == day).first()
    
    # Get last 20 days for range hit calculation
    recent_preds = (
        db.query(DailyPrediction)
        .filter(DailyPrediction.date <= day)
        .order_by(desc(DailyPrediction.date))
        .limit(20)
        .all()
    )
    
    # Calculate rangeHit20
    range_hits = [p for p in recent_preds if p.rangeHit is True]
    rangeHit20 = len(range_hits) / len(recent_preds) if recent_preds else 0.0
    
    # Get current price (use close or latest available)
    current_price = None
    if pred:
        current_price = pred.close or pred.twoPM or pred.noon or pred.open or pred.preMarket
        if current_price is None and pred.predHigh and pred.predLow:
            current_price = (pred.predHigh + pred.predLow) / 2.0
    
    suggestions = generate_suggestions(
        current_price=current_price,
        bias=pred.bias if pred else "Neutral",
        rangeHit20=rangeHit20,
        pred_low=pred.predLow if pred else None,
        pred_high=pred.predHigh if pred else None
    )
    
    return {"date": day.isoformat(), "suggestions": [s.__dict__ for s in suggestions]}


@router.get("/suggestions/{day}/pl-data")
def get_pl_data_for_suggestions(day: date, db: Session = Depends(get_db)):
    """Get P&L visualization data for all suggestions on a given date"""
    # Get suggestions for the day
    suggestions_response = get_suggestions(day, db)
    suggestions = suggestions_response["suggestions"]
    
    pl_data_list = []
    
    for suggestion in suggestions:
        strategy_type = suggestion.get("strategy")
        # Get actual current price from prediction data, use a reasonable fallback
        pred = db.query(DailyPrediction).filter(DailyPrediction.date == day).first()
        current_price = 635.0  # Default SPY price
        if pred:
            current_price = pred.close or pred.twoPM or pred.noon or pred.open or pred.preMarket
            if current_price is None and pred.predHigh and pred.predLow:
                current_price = (pred.predHigh + pred.predLow) / 2.0
        
        try:
            if strategy_type == "Iron Condor":
                pl_data = pl_calculator.calculate_iron_condor_pl(
                    put_long=suggestion.get("put_long_strike", 0),
                    put_short=suggestion.get("put_short_strike", 0),
                    call_short=suggestion.get("call_short_strike", 0),
                    call_long=suggestion.get("call_long_strike", 0),
                    credit_received=suggestion.get("max_profit", 1.0),
                    current_price=current_price,
                    price_range_pct=0.08,  # ±8% focused range for better readability
                    resolution=50  # Reduced resolution for mobile performance
                )
                
            elif strategy_type == "Iron Butterfly":
                pl_data = pl_calculator.calculate_iron_butterfly_pl(
                    put_long=suggestion.get("put_long_strike", 0),
                    center_strike=suggestion.get("center_strike", current_price),
                    call_long=suggestion.get("call_long_strike", 0),
                    credit_received=suggestion.get("max_profit", 1.0),
                    current_price=current_price,
                    price_range_pct=0.08,  # ±8% focused range for better readability
                    resolution=50
                )
            else:
                continue  # Skip unknown strategy types
                
            # Calculate current P&L at current price
            current_pl = pl_calculator.calculate_current_pl(
                strategy_type=strategy_type,
                strikes={
                    'put_long': suggestion.get("put_long_strike"),
                    'put_short': suggestion.get("put_short_strike"), 
                    'call_short': suggestion.get("call_short_strike"),
                    'call_long': suggestion.get("call_long_strike"),
                    'center_strike': suggestion.get("center_strike")
                } if strategy_type == "Iron Condor" else {
                    'put_long': suggestion.get("put_long_strike"),
                    'center_strike': suggestion.get("center_strike"),
                    'call_long': suggestion.get("call_long_strike")
                },
                credit_received=suggestion.get("max_profit", 1.0),
                current_price=current_price
            )
            
            # Add strike prices for chart markers
            strikes = {}
            if strategy_type == "Iron Condor":
                strikes = {
                    "put_long_strike": suggestion.get("put_long_strike"),
                    "put_short_strike": suggestion.get("put_short_strike"),
                    "call_short_strike": suggestion.get("call_short_strike"),
                    "call_long_strike": suggestion.get("call_long_strike")
                }
            elif strategy_type == "Iron Butterfly":
                strikes = {
                    "put_long_strike": suggestion.get("put_long_strike"),
                    "center_strike": suggestion.get("center_strike"),
                    "call_long_strike": suggestion.get("call_long_strike")
                }
            
            # Convert to serializable format
            pl_data_dict = {
                "tenor": suggestion.get("tenor"),
                "strategy": strategy_type,
                "points": [
                    {
                        "underlying_price": point.underlying_price,
                        "total_pl": point.total_pl,
                        "put_spread_pl": point.put_spread_pl,
                        "call_spread_pl": point.call_spread_pl
                    }
                    for point in pl_data.points
                ],
                "breakeven_lower": pl_data.breakeven_lower,
                "breakeven_upper": pl_data.breakeven_upper,
                "max_profit": pl_data.max_profit,
                "max_loss": pl_data.max_loss,
                "current_price": pl_data.current_price,
                "profit_zone_start": pl_data.profit_zone_start,
                "profit_zone_end": pl_data.profit_zone_end,
                "current_pl": current_pl,
                "strikes": strikes  # Add strike prices for chart markers
            }
            
            pl_data_list.append(pl_data_dict)
            
        except Exception as e:
            # Log error but continue with other suggestions
            print(f"Error calculating P&L for {strategy_type}: {e}")
            continue
    
    return {
        "date": day.isoformat(),
        "pl_data": pl_data_list
    }


@router.get("/pl/current/{suggestion_id}")
def get_current_pl(
    suggestion_id: str,
    current_price: float,
    strategy_type: str,
    put_long: Optional[float] = None,
    put_short: Optional[float] = None,
    call_short: Optional[float] = None,
    call_long: Optional[float] = None,
    center_strike: Optional[float] = None,
    credit_received: float = 1.0
):
    """Get real-time P&L for a specific suggestion at current market price"""
    try:
        if strategy_type == "Iron Condor":
            strikes = {
                'put_long': put_long,
                'put_short': put_short,
                'call_short': call_short,
                'call_long': call_long
            }
        elif strategy_type == "Iron Butterfly":
            strikes = {
                'put_long': put_long,
                'center_strike': center_strike,
                'call_long': call_long
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid strategy type")
        
        current_pl = pl_calculator.calculate_current_pl(
            strategy_type=strategy_type,
            strikes=strikes,
            credit_received=credit_received,
            current_price=current_price
        )
        
        return {
            "suggestion_id": suggestion_id,
            "current_price": current_price,
            "current_pl": current_pl,
            "strategy_type": strategy_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"P&L calculation failed: {str(e)}")