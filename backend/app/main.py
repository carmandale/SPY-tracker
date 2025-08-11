from datetime import date
from typing import Optional
from statistics import median

from fastapi import Depends, FastAPI, HTTPException, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from .config import settings
from .database import Base, engine, get_db
from .models import DailyPrediction, PriceLog
from .schemas import (
    DailyPredictionCreate,
    DailyPredictionRead,
    MetricsRead,
    PriceLogCreate,
)
from .scheduler import start_scheduler
from .suggestions import generate_suggestions


app = FastAPI(title=settings.app_name)

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
    key_levels_list = (
        [float(x) for x in pred.keyLevels.split(",") if x]
        if getattr(pred, "keyLevels", None)
        else None
    )
    return DailyPredictionRead(
        id=pred.id,
        date=pred.date,
        preMarket=pred.preMarket,
        predLow=pred.predLow,
        predHigh=pred.predHigh,
        bias=pred.bias,
        volCtx=pred.volCtx,
        dayType=pred.dayType,
        keyLevels=key_levels_list,
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

    # Map keyLevels list to comma-separated string
    data = payload.model_dump()
    key_levels_list = data.pop("keyLevels", None)
    if key_levels_list is not None:
        data["keyLevels"] = ",".join(str(x) for x in key_levels_list)

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
    keyLevels: Optional[list[float]] = None
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
        raise HTTPException(status_code=404, detail="Not found")
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
        raise HTTPException(status_code=404, detail="No prediction found for this date")
    
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


@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """Get 20-day rolling metrics"""
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
            "medianAbsErr20": None
        }
    
    # Calculate rangeHit20
    range_hits = [p for p in recent_preds if p.rangeHit is True]
    rangeHit20 = len(range_hits) / count_days if count_days > 0 else None
    
    # Calculate medianAbsErr20
    abs_errors = [p.absErrorToClose for p in recent_preds if p.absErrorToClose is not None]
    medianAbsErr20 = median(abs_errors) if abs_errors else None
    
    return {
        "count_days": count_days,
        "rangeHit20": rangeHit20,
        "medianAbsErr20": medianAbsErr20
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
