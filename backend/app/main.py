from datetime import date
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    # derived fields
    if pred.close is not None and pred.predHigh is not None and pred.predLow is not None:
        mid_pred = (pred.predHigh + pred.predLow) / 2.0
        pred.absErrorToClose = abs(pred.close - mid_pred)
        pred.rangeHit = bool(pred.predLow <= pred.close <= pred.predHigh)

    db.commit()
    db.refresh(pred)
    return _serialize_prediction(pred)


@app.get("/day/{day}", response_model=DailyPredictionRead)
def get_day(day: date, db: Session = Depends(get_db)):
    pred = db.query(DailyPrediction).filter(DailyPrediction.date == day).first()
    if pred is None:
        raise HTTPException(status_code=404, detail="Not found")
    return _serialize_prediction(pred)


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

    db.commit()
    return {"status": "ok"}


@app.get("/suggestions/{day}")
def get_suggestions(day: date):
    suggestions = generate_suggestions()
    return {"date": day.isoformat(), "suggestions": [s.__dict__ for s in suggestions]}


@app.get("/metrics", response_model=MetricsRead)
def get_metrics(db: Session = Depends(get_db)):
    total = db.query(DailyPrediction).count()
    if total == 0:
        return MetricsRead(count_days=0, avg_abs_error=None, range_hit_rate=None)
    rows = db.query(DailyPrediction).all()
    abs_errs = [r.absErrorToClose for r in rows if r.absErrorToClose is not None]
    range_hits = [1 for r in rows if r.rangeHit]
    avg_abs = sum(abs_errs) / len(abs_errs) if abs_errs else None
    hit_rate = (sum(range_hits) / total) if total else None
    return MetricsRead(count_days=total, avg_abs_error=avg_abs, range_hit_rate=hit_rate)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


