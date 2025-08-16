from sqlalchemy import Column, Integer, String, Float, Date, Boolean, DateTime, UniqueConstraint
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
    # AI governance
    source = Column(String, nullable=True)  # 'ai' | 'manual'
    locked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PriceLog(Base):
    __tablename__ = "price_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    checkpoint = Column(String, index=True, nullable=False)  # premarket|open|noon|twoPM|close
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    __table_args__ = (
        UniqueConstraint('date', 'checkpoint', name='uq_ai_prediction_date_checkpoint'),
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    checkpoint = Column(String, index=True, nullable=False)  # open|noon|twoPM|close
    predicted_price = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    reasoning = Column(String, nullable=True)
    market_context = Column(String, nullable=True)  # Summary of market conditions
    actual_price = Column(Float, nullable=True)  # Filled when real price comes in
    prediction_error = Column(Float, nullable=True)  # |predicted - actual|
    # Prediction intervals (68% confidence)
    interval_low = Column(Float, nullable=True)  # Lower bound of 68% confidence interval
    interval_high = Column(Float, nullable=True)  # Upper bound of 68% confidence interval
    interval_hit = Column(Boolean, nullable=True)  # Whether actual price was within interval
    # Source tracking
    source = Column(String, nullable=True)  # 'llm', 'baseline', 'ensemble'
    model = Column(String, nullable=True)  # Model name/version if applicable
    prompt_version = Column(String, nullable=True)  # Track prompt version for reproducibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BaselineModel(Base):
    """Statistical baseline model configuration and performance tracking."""
    __tablename__ = "baseline_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    parameters = Column(String, nullable=True)  # JSON string of model parameters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ModelPerformance(Base):
    """Daily performance metrics for prediction models."""
    __tablename__ = "model_performance"
    __table_args__ = (
        UniqueConstraint('date', 'model_name', name='uq_model_performance_date_model'),
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    model_name = Column(String, index=True, nullable=False)  # 'llm', 'baseline', 'ensemble', etc.
    mae = Column(Float, nullable=True)  # Mean absolute error
    rmse = Column(Float, nullable=True)  # Root mean squared error
    hit_rate_1dollar = Column(Float, nullable=True)  # % of predictions within $1
    interval_coverage = Column(Float, nullable=True)  # % of actuals within predicted intervals
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

