from datetime import date, datetime, timezone
from typing import Optional
from statistics import median

from fastapi import Depends, FastAPI, HTTPException, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, ValidationError

from .config import settings
from .database import Base, engine, get_db
from .models import DailyPrediction, PriceLog, AIPrediction
from .providers import default_provider
from .schemas import (
    DailyPredictionCreate,
    DailyPredictionRead,
    MetricsRead,
    PriceLogCreate,
)
from .scheduler import start_scheduler
from .suggestions import generate_suggestions
from .exceptions import (
    SPYTrackerException,
    DataNotFoundException,
    MarketDataException,
    PredictionLockedException,
    spy_tracker_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)


app = FastAPI(title=settings.app_name)

# Register exception handlers
app.add_exception_handler(SPYTrackerException, spy_tracker_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Use FRONTEND_ORIGIN from settings
origins = [settings.frontend_origin] if settings.frontend_origin != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)
_scheduler = start_scheduler(get_db)


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
@app.post("/prediction", response_model=DailyPredictionRead)
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


@app.post("/prediction/{date}", response_model=DailyPredictionRead)
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


@app.get("/day/{day}", response_model=DailyPredictionRead)
def get_day(day: date, db: Session = Depends(get_db)):
    pred = db.query(DailyPrediction).filter(DailyPrediction.date == day).first()
    if pred is None:
        raise DataNotFoundException(
            f"No prediction data found for {day.isoformat()}",
            {"date": day.isoformat(), "hint": "Try entering a prediction for this date first"}
        )
    return _serialize_prediction(pred)


# Original endpoint - keep for backward compatibility
@app.post("/log/{checkpoint}")
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


@app.post("/capture/{date}")
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
@app.post("/recompute/{date}", response_model=DailyPredictionRead)
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


@app.get("/suggestions/{day}")
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


@app.get("/history")
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
        
        history_items.append({
            "id": pred.id,
            "date": pred.date.isoformat(),
            "predLow": pred.predLow,
            "predHigh": pred.predHigh,
            "bias": pred.bias,
            "actualLow": pred.realizedLow or pred.open,  # Use open as fallback
            "actualHigh": pred.realizedHigh or pred.close,  # Use close as fallback
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


@app.get("/metrics")
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


@app.get("/market-data/{symbol}")
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


@app.get("/market-status")
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


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# AI Prediction Endpoints
from .ai_endpoints import (
    get_ai_predictions_for_date,
    get_ai_accuracy_metrics,
    demo_ai_prediction_system,
    create_ai_prediction_for_date,
)
from .config import settings

@app.get("/ai/predictions/{target_date}")
def get_ai_predictions_endpoint(target_date: date, db: Session = Depends(get_db)):
    """Generate or retrieve AI predictions for a specific date."""
    return get_ai_predictions_for_date(target_date, db)

@app.get("/ai/accuracy")  
def get_ai_accuracy_endpoint(db: Session = Depends(get_db)):
    """Get AI prediction accuracy metrics."""
    return get_ai_accuracy_metrics(db)

@app.get("/ai/demo/{target_date}")
def ai_demo_date(target_date: date, db: Session = Depends(get_db)):
    """Demonstration of the complete AI prediction system for specific date."""
    return demo_ai_prediction_system(target_date, db)

@app.get("/ai/demo")
def ai_demo_today(db: Session = Depends(get_db)):
    """Demonstration of AI prediction system for today."""
    return demo_ai_prediction_system(None, db)


@app.post("/ai/predict/{target_date}")
def ai_predict_create(
    target_date: date,
    lookbackDays: int = None,
    db: Session = Depends(get_db),
):
    """Create AI prediction for a date and lock the day (create-only)."""
    if lookbackDays is None:
        lookbackDays = settings.ai_lookback_days
    return create_ai_prediction_for_date(target_date, lookbackDays, db)
