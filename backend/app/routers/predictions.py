"""
Core prediction endpoints for SPY Tracker.
Handles daily predictions, price logging, and history retrieval.
"""

from datetime import date
from typing import Optional
from statistics import median

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from ..database import get_db
from ..models import DailyPrediction, PriceLog
from ..schemas import DailyPredictionCreate, DailyPredictionRead, PriceLogCreate
from ..capture import refresh_actuals_for_date
from ..exceptions import DataNotFoundException

router = APIRouter(prefix="", tags=["predictions"])


def _serialize_prediction(pred: DailyPrediction) -> DailyPredictionRead:
    return DailyPredictionRead(
        id=pred.id,
        date=pred.date,
        preMarket=pred.preMarket,
        predLow=pred.predLow,
        predHigh=pred.predHigh,
        source=pred.source,
        locked=pred.locked,
        bias=pred.bias,
        volCtx=pred.volCtx,
        dayType=pred.dayType,
        keyLevels=pred.keyLevels,
        notes=pred.notes,
        open=pred.open,
        noon=pred.noon,
        twoPM=pred.twoPM,
        close=pred.close,
        realizedLow=pred.realizedLow,
        realizedHigh=pred.realizedHigh,
        rangeHit=pred.rangeHit,
        absErrorToClose=pred.absErrorToClose,
        created_at=pred.created_at,
        updated_at=pred.updated_at,
    )


def _update_derived_fields(pred: DailyPrediction) -> None:
    """Update absErrorToClose and rangeHit based on current data"""
    if pred.close is not None and pred.predHigh is not None and pred.predLow is not None:
        mid_pred = (pred.predHigh + pred.predLow) / 2.0
        pred.absErrorToClose = abs(pred.close - mid_pred)
        pred.rangeHit = bool(pred.predLow <= pred.close <= pred.predHigh)


# Original endpoint - keep for backward compatibility
@router.post("/prediction", response_model=DailyPredictionRead)
def create_or_update_prediction(payload: DailyPredictionCreate, db: Session = Depends(get_db)):
    pred = db.query(DailyPrediction).filter(DailyPrediction.date == payload.date).first()
    if pred is None:
        pred = DailyPrediction(date=payload.date)
        db.add(pred)

    # Apply all data directly (keyLevels is now a string)
    data = payload.model_dump()
    for k, v in data.items():
        setattr(pred, k, v)

    _update_derived_fields(pred)
    db.commit()
    db.refresh(pred)
    return _serialize_prediction(pred)


# New PRD-compatible alias with path parameter
class PredictionBodyOnly(BaseModel):
    """Prediction data without date field for path param endpoints"""
    preMarket: Optional[float] = None
    predLow: Optional[float] = None
    predHigh: Optional[float] = None
    bias: Optional[str] = None
    volCtx: Optional[str] = None
    dayType: Optional[str] = None
    keyLevels: Optional[str] = None
    notes: Optional[str] = None


@router.post("/prediction/{date}", response_model=DailyPredictionRead)
def create_or_update_prediction_by_date(
    date: date = Path(..., description="Date for prediction"),
    payload: PredictionBodyOnly = Body(...),
    db: Session = Depends(get_db)
):
    """PRD-compatible endpoint with date in path"""
    # Create a full payload with date from path
    full_data = payload.model_dump()
    full_data["date"] = date
    full_payload = DailyPredictionCreate(**full_data)
    return create_or_update_prediction(full_payload, db)


@router.get("/day/{day}", response_model=DailyPredictionRead)
def get_day(day: date, db: Session = Depends(get_db)):
    # Lazy refresh for today to eagerly fill missing actuals
    try:
        if day == date.today():
            refresh_actuals_for_date(db, day)
    except Exception:
        pass

    pred = db.query(DailyPrediction).filter(DailyPrediction.date == day).first()
    if pred is None:
        raise DataNotFoundException(
            f"No prediction data found for {day.isoformat()}",
            {"date": day.isoformat(), "hint": "Try entering a prediction for this date first"}
        )
    return _serialize_prediction(pred)


# Original endpoint - keep for backward compatibility
@router.post("/log/{checkpoint}")
def log_checkpoint(checkpoint: str, payload: PriceLogCreate, db: Session = Depends(get_db)):
    if checkpoint not in {"preMarket", "open", "noon", "twoPM", "close"}:
        raise HTTPException(status_code=400, detail="Invalid checkpoint")

    db.add(PriceLog(date=payload.date, checkpoint=checkpoint, price=payload.price))

    pred = db.query(DailyPrediction).filter(DailyPrediction.date == payload.date).first()
    if pred is None:
        pred = DailyPrediction(date=payload.date)
        db.add(pred)

    if checkpoint == "preMarket":
        pred.preMarket = payload.price
    elif checkpoint == "open":
        pred.open = payload.price
    elif checkpoint == "noon":
        pred.noon = payload.price
    elif checkpoint == "twoPM":
        pred.twoPM = payload.price
    elif checkpoint == "close":
        pred.close = payload.price

    _update_derived_fields(pred)
    db.commit()
    return {"status": "ok"}


# New PRD-compatible capture endpoint
class CaptureRequest(BaseModel):
    checkpoint: str
    price: float


@router.post("/capture/{date}")
def capture_price(
    date: date = Path(..., description="Date for price capture"),
    payload: CaptureRequest = Body(...),
    db: Session = Depends(get_db)
):
    """PRD-compatible endpoint for price capture"""
    if payload.checkpoint not in {"preMarket", "open", "noon", "twoPM", "close"}:
        raise HTTPException(status_code=400, detail="Invalid checkpoint")
    
    # Reuse existing logic
    price_log_data = PriceLogCreate(date=date, checkpoint=payload.checkpoint, price=payload.price)
    return log_checkpoint(payload.checkpoint, price_log_data, db)


# New recompute endpoint
@router.post("/recompute/{date}", response_model=DailyPredictionRead)
def recompute_day(
    date: date = Path(..., description="Date to recompute"),
    db: Session = Depends(get_db)
):
    """Recompute derived fields for a given date"""
    pred = db.query(DailyPrediction).filter(DailyPrediction.date == date).first()
    if pred is None:
        raise DataNotFoundException(
            f"No prediction found for {date.isoformat()}",
            {"date": date.isoformat(), "action": "recompute"}
        )
    
    _update_derived_fields(pred)
    db.commit()
    db.refresh(pred)
    return _serialize_prediction(pred)


@router.get("/history")
def get_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get historical predictions with pagination"""
    predictions = (
        db.query(DailyPrediction)
        .order_by(desc(DailyPrediction.date))
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    history_items = []
    for pred in predictions:
        # Calculate error from close if available
        error = None
        if pred.close and pred.predHigh and pred.predLow:
            pred_mid = (pred.predHigh + pred.predLow) / 2.0
            error = abs(pred.close - pred_mid)
        
        # Calculate actual low/high from available price points
        # For complete days (with close), show full range
        # For incomplete days, show None to avoid misleading data
        if pred.close is not None:
            # Day is complete, calculate actual range
            prices = []
            if pred.open is not None:
                prices.append(pred.open)
            if pred.noon is not None:
                prices.append(pred.noon)
            if pred.twoPM is not None:
                prices.append(pred.twoPM)
            prices.append(pred.close)
            
            actual_low = min(prices) if prices else None
            actual_high = max(prices) if prices else None
        else:
            # Day incomplete - don't show misleading partial range
            actual_low = None
            actual_high = None
        
        history_items.append({
            "id": pred.id,
            "date": pred.date.isoformat(),
            "predLow": pred.predLow,
            "predHigh": pred.predHigh,
            "bias": pred.bias,
            "actualLow": actual_low,  # Min of all captured prices
            "actualHigh": actual_high,  # Max of all captured prices
            "rangeHit": pred.rangeHit,
            "notes": pred.notes,
            "dayType": pred.dayType,
            "error": error or pred.absErrorToClose,
            "open": pred.open,
            "close": pred.close,
            "source": getattr(pred, 'source', 'manual')
        })
    
    return {
        "items": history_items,
        "total": len(history_items),
        "limit": limit,
        "offset": offset
    }


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """Get comprehensive 20-day rolling metrics with calibration tips"""
    # Get last 20 days of data
    recent_preds = (
        db.query(DailyPrediction)
        .order_by(desc(DailyPrediction.date))
        .limit(20)
        .all()
    )
    
    count_days = len(recent_preds)
    
    if count_days == 0:
        return {
            "count_days": 0,
            "rangeHit20": None,
            "medianAbsErr20": None,
            "calibration_tip": "No data available yet. Make some predictions first!",
            "trend": None,
            "accuracy_grade": "N/A"
        }
    
    # Calculate rangeHit20
    range_hits = [p for p in recent_preds if p.rangeHit is True]
    rangeHit20 = len(range_hits) / count_days if count_days > 0 else 0.0
    
    # Calculate medianAbsErr20
    abs_errors = [p.absErrorToClose for p in recent_preds if p.absErrorToClose is not None]
    medianAbsErr20 = median(abs_errors) if abs_errors else None
    
    # Generate calibration tip based on performance
    calibration_tip = generate_calibration_tip(rangeHit20, medianAbsErr20, count_days)
    
    # Calculate trend (last 5 vs previous 5)
    trend = calculate_trend(recent_preds) if count_days >= 10 else None
    
    # Assign accuracy grade
    accuracy_grade = get_accuracy_grade(rangeHit20, medianAbsErr20)
    
    return {
        "count_days": count_days,
        "rangeHit20": rangeHit20,
        "medianAbsErr20": medianAbsErr20,
        "calibration_tip": calibration_tip,
        "trend": trend,
        "accuracy_grade": accuracy_grade,
        "sample_data": count_days < 10  # Flag for insufficient data
    }


def generate_calibration_tip(range_hit_pct: float, median_error: Optional[float], count: int) -> str:
    """Generate data-driven calibration tips"""
    if count < 5:
        return "🚀 Keep tracking! Need more predictions for meaningful calibration tips."
    
    if range_hit_pct is None:
        return "📊 Complete some predictions with actual outcomes to see calibration tips."
    
    # Range hit calibration
    if range_hit_pct < 0.45:
        return "📏 Your ranges are too narrow. Try widening by 15-20% for better hit rate."
    elif range_hit_pct < 0.55:
        return "📏 Ranges slightly narrow. Consider widening by 10% to improve hit rate."
    elif range_hit_pct > 0.75:
        return "🎯 Great hit rate! You might tighten ranges by 5-10% for more precision."
    elif range_hit_pct > 0.85:
        return "🎯 Excellent accuracy! Try slightly tighter ranges to maximize edge."
    else:
        return "✅ Well-calibrated ranges! Current sizing looks optimal."


def calculate_trend(recent_preds) -> Optional[str]:
    """Calculate if accuracy is improving or declining"""
    if len(recent_preds) < 10:
        return None
    
    # Split into recent 5 and previous 5
    recent_5 = recent_preds[:5]
    previous_5 = recent_preds[5:10]
    
    recent_hits = sum(1 for p in recent_5 if p.rangeHit) / 5
    previous_hits = sum(1 for p in previous_5 if p.rangeHit) / 5
    
    diff = recent_hits - previous_hits
    
    if diff > 0.2:
        return "📈 Improving"
    elif diff < -0.2:
        return "📉 Declining"
    else:
        return "➡️ Stable"


def get_accuracy_grade(range_hit_pct: Optional[float], median_error: Optional[float]) -> str:
    """Assign letter grade based on performance"""
    if range_hit_pct is None:
        return "N/A"
    
    if range_hit_pct >= 0.8:
        return "A"
    elif range_hit_pct >= 0.7:
        return "B"
    elif range_hit_pct >= 0.6:
        return "C"
    elif range_hit_pct >= 0.5:
        return "D"
    else:
        return "F"