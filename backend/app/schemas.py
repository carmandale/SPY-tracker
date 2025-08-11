from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DailyPredictionBase(BaseModel):
    date: date
    preMarket: Optional[float] = None
    predLow: Optional[float] = None
    predHigh: Optional[float] = None
    source: Optional[str] = None  # 'ai' | 'manual'
    locked: Optional[bool] = None
    bias: Optional[str] = None
    volCtx: Optional[str] = None
    dayType: Optional[str] = None
    keyLevels: Optional[str] = Field(default=None, description="Key levels as text (e.g., '580 support, 585 resistance')")
    notes: Optional[str] = None
    open: Optional[float] = None
    noon: Optional[float] = None
    twoPM: Optional[float] = None
    close: Optional[float] = None
    realizedLow: Optional[float] = None
    realizedHigh: Optional[float] = None
    rangeHit: Optional[bool] = None
    absErrorToClose: Optional[float] = None


class DailyPredictionCreate(DailyPredictionBase):
    pass


class DailyPredictionRead(DailyPredictionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PriceLogCreate(BaseModel):
    date: date
    checkpoint: str
    price: float


class MetricsRead(BaseModel):
    count_days: int
    avg_abs_error: Optional[float]
    range_hit_rate: Optional[float]


