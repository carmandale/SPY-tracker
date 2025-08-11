from sqlalchemy import Column, Integer, String, Float, Date, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base


class DailyPrediction(Base):
    __tablename__ = "daily_predictions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    preMarket = Column(Float, nullable=True)
    predLow = Column(Float, nullable=True)
    predHigh = Column(Float, nullable=True)
    bias = Column(String, nullable=True)
    volCtx = Column(String, nullable=True)
    dayType = Column(String, nullable=True)
    keyLevels = Column(String, nullable=True)  # comma-separated
    notes = Column(String, nullable=True)
    open = Column(Float, nullable=True)
    noon = Column(Float, nullable=True)
    twoPM = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    realizedLow = Column(Float, nullable=True)
    realizedHigh = Column(Float, nullable=True)
    rangeHit = Column(Boolean, default=False)
    absErrorToClose = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PriceLog(Base):
    __tablename__ = "price_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    checkpoint = Column(String, index=True, nullable=False)  # premarket|open|noon|twoPM|close
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


