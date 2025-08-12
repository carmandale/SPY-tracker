"""
AI Prediction API endpoints for SPY TA Tracker.
Demonstrates the GPT-4/5 prediction system with real data integration.
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .database import get_db
from .models import AIPrediction, DailyPrediction
from .ai_predictor import ai_predictor
from .config import settings


class AIPredictionResponse(BaseModel):
    """API response model for AI predictions."""
    checkpoint: str
    predicted_price: float
    confidence: float
    reasoning: str
    actual_price: Optional[float] = None
    prediction_error: Optional[float] = None


class DayPredictionsResponse(BaseModel):
    """API response for a full day's AI predictions."""
    date: str
    market_context: str
    pre_market_price: Optional[float] = None
    predictions: List[AIPredictionResponse]
    accuracy_summary: Optional[Dict[str, Any]] = None
    sentiment: Optional[Dict[str, Any]] = None


def get_ai_predictions_for_date(target_date: date, db: Session = Depends(get_db)) -> DayPredictionsResponse:
    """
    Generate or retrieve AI predictions for a specific date.
    
    This endpoint demonstrates the full AI prediction workflow:
    1. Generate GPT-4/5 predictions based on market analysis
    2. Store predictions in database with confidence scores
    3. Compare with actual prices when available
    4. Calculate accuracy metrics
    """
    
    # Check if we already have predictions for this date
    existing_predictions = db.query(AIPrediction).filter(AIPrediction.date == target_date).all()
    
    ai_preview = None
    if not existing_predictions:
        # Generate new AI predictions
        try:
            day_predictions = ai_predictor.generate_predictions(target_date)
            ai_preview = day_predictions
            
            # Store predictions in database
            for pred in day_predictions.predictions:
                ai_pred = AIPrediction(
                    date=target_date,
                    checkpoint=pred.checkpoint,
                    predicted_price=pred.predicted_price,
                    confidence=pred.confidence,
                    reasoning=pred.reasoning,
                    market_context=day_predictions.market_context
                )
                db.add(ai_pred)
            
            db.commit()
            existing_predictions = db.query(AIPrediction).filter(AIPrediction.date == target_date).all()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI prediction generation failed: {str(e)}")
    else:
        # We already have stored predictions; still generate a fresh preview for analysis/sentiment display
        try:
            ai_preview = ai_predictor.generate_predictions(target_date)
        except Exception:
            ai_preview = None
    
    # Get actual prices if available
    actual_data = db.query(DailyPrediction).filter(DailyPrediction.date == target_date).first()
    
    # Build response
    predictions = []
    total_error = 0
    accurate_predictions = 0
    
    # Group predictions by checkpoint to avoid duplicates
    checkpoint_map = {}
    for ai_pred in existing_predictions:
        # Keep only the most recent prediction for each checkpoint
        if ai_pred.checkpoint not in checkpoint_map or ai_pred.id > checkpoint_map[ai_pred.checkpoint].id:
            checkpoint_map[ai_pred.checkpoint] = ai_pred
    
    # Process unique predictions
    for checkpoint in ["open", "noon", "twoPM", "close"]:
        if checkpoint not in checkpoint_map:
            continue
            
        ai_pred = checkpoint_map[checkpoint]
        
        # Get actual price for this checkpoint
        actual_price = None
        if actual_data:
            if ai_pred.checkpoint == "open":
                actual_price = actual_data.open
            elif ai_pred.checkpoint == "noon":
                actual_price = actual_data.noon
            elif ai_pred.checkpoint == "twoPM":
                actual_price = actual_data.twoPM
            elif ai_pred.checkpoint == "close":
                actual_price = actual_data.close
        
        # Calculate prediction error if we have actual price
        prediction_error = None
        if actual_price is not None:
            prediction_error = abs(ai_pred.predicted_price - actual_price)
            total_error += prediction_error
            
            # Update database record with actual price and error
            if ai_pred.actual_price is None:  # Only update once
                ai_pred.actual_price = actual_price
                ai_pred.prediction_error = prediction_error
                db.add(ai_pred)
            
            # Count as accurate if within $1.00
            if prediction_error <= 1.0:
                accurate_predictions += 1
        
        predictions.append(AIPredictionResponse(
            checkpoint=ai_pred.checkpoint,
            predicted_price=ai_pred.predicted_price,
            confidence=ai_pred.confidence,
            reasoning=ai_pred.reasoning,
            actual_price=actual_price,
            prediction_error=prediction_error
        ))
    
    db.commit()
    
    # Calculate accuracy summary
    accuracy_summary = None
    if total_error > 0:
        accuracy_summary = {
            "mean_absolute_error": total_error / len([p for p in predictions if p.actual_price is not None]),
            "accuracy_rate": accurate_predictions / len([p for p in predictions if p.actual_price is not None]),
            "predictions_with_actuals": len([p for p in predictions if p.actual_price is not None]),
            "total_predictions": len(predictions)
        }
    
    return DayPredictionsResponse(
        date=target_date.isoformat(),
        market_context=(ai_preview.market_context if ai_preview else (existing_predictions[0].market_context if existing_predictions else "No context available")),
        pre_market_price=actual_data.preMarket if actual_data else None,
        predictions=predictions,
        accuracy_summary=accuracy_summary,
        sentiment=(ai_preview.sentiment if ai_preview else None),
    )


class AIPredictCreateResponse(BaseModel):
    date: str
    predLow: float
    predHigh: float
    source: str
    locked: bool
    analysis: str
    lookbackDays: int


def _compute_band_from_ai(preds: List[AIPrediction]) -> Optional[Dict[str, float]]:
    if not preds:
        return None
    prices = [p.predicted_price for p in preds]
    return {"low": float(min(prices)), "high": float(max(prices))}


def create_ai_prediction_for_date(
    target_date: date,
    lookback_days: int,
    db: Session,
) -> AIPredictCreateResponse:
    # Do not overwrite existing locked day
    existing_day = db.query(DailyPrediction).filter(DailyPrediction.date == target_date).first()
    if existing_day and existing_day.locked:
        raise HTTPException(status_code=409, detail="Prediction already locked for this date")

    # Generate new AI predictions and store
    day_predictions = ai_predictor.generate_predictions(target_date, lookback_days=lookback_days)

    # persist per-checkpoint predictions
    for pred in day_predictions.predictions:
        db.add(
            AIPrediction(
                date=target_date,
                checkpoint=pred.checkpoint,
                predicted_price=pred.predicted_price,
                confidence=pred.confidence,
                reasoning=pred.reasoning,
                market_context=day_predictions.market_context,
            )
        )

    # Ensure pending inserts are flushed so queries can see them (autoflush is disabled)
    db.flush()

    # derive band from just-added rows (or directly from memory if needed)
    stored_preds = db.query(AIPrediction).filter(AIPrediction.date == target_date).all()
    if not stored_preds:
        # fallback to in-memory predictions list
        band_prices = [p.predicted_price for p in day_predictions.predictions]
        band = {"low": float(min(band_prices)), "high": float(max(band_prices))} if band_prices else None
    else:
        band = _compute_band_from_ai(stored_preds)
    if not band:
        raise HTTPException(status_code=500, detail="AI did not produce predictions")

    if existing_day is None:
        existing_day = DailyPrediction(date=target_date)
        db.add(existing_day)

    existing_day.predLow = band["low"]
    existing_day.predHigh = band["high"]
    existing_day.source = "ai"
    existing_day.locked = True
    db.commit()
    db.refresh(existing_day)

    return AIPredictCreateResponse(
        date=target_date.isoformat(),
        predLow=existing_day.predLow,
        predHigh=existing_day.predHigh,
        source=existing_day.source or "ai",
        locked=bool(existing_day.locked),
        analysis=day_predictions.market_context,
        lookbackDays=lookback_days,
    )


def get_ai_accuracy_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Calculate overall AI prediction accuracy metrics.
    
    Returns comprehensive accuracy analysis including:
    - Mean Absolute Error by checkpoint
    - Confidence calibration analysis  
    - Prediction accuracy trends
    """
    
    # Get all predictions with actual prices
    predictions_with_actuals = db.query(AIPrediction).filter(
        AIPrediction.actual_price.isnot(None)
    ).all()
    
    if not predictions_with_actuals:
        return {
            "message": "No AI predictions with actual prices yet",
            "total_predictions": 0
        }
    
    # Calculate metrics by checkpoint
    checkpoint_metrics = {}
    confidence_buckets = {"high": [], "medium": [], "low": []}
    
    for pred in predictions_with_actuals:
        checkpoint = pred.checkpoint
        error = pred.prediction_error
        confidence = pred.confidence
        
        # Checkpoint metrics
        if checkpoint not in checkpoint_metrics:
            checkpoint_metrics[checkpoint] = {"errors": [], "confidences": []}
        checkpoint_metrics[checkpoint]["errors"].append(error)
        checkpoint_metrics[checkpoint]["confidences"].append(confidence)
        
        # Confidence calibration
        if confidence >= 0.7:
            confidence_buckets["high"].append(error)
        elif confidence >= 0.5:
            confidence_buckets["medium"].append(error)
        else:
            confidence_buckets["low"].append(error)
    
    # Calculate summary statistics
    results = {
        "total_predictions": len(predictions_with_actuals),
        "overall_mae": sum(p.prediction_error for p in predictions_with_actuals) / len(predictions_with_actuals),
        "checkpoint_performance": {},
        "confidence_calibration": {}
    }
    
    # Checkpoint performance
    for checkpoint, data in checkpoint_metrics.items():
        errors = data["errors"]
        results["checkpoint_performance"][checkpoint] = {
            "mean_absolute_error": sum(errors) / len(errors),
            "accuracy_rate_1dollar": len([e for e in errors if e <= 1.0]) / len(errors),
            "total_predictions": len(errors),
            "avg_confidence": sum(data["confidences"]) / len(data["confidences"])
        }
    
    # Confidence calibration
    for bucket, errors in confidence_buckets.items():
        if errors:
            results["confidence_calibration"][bucket] = {
                "mean_absolute_error": sum(errors) / len(errors),
                "count": len(errors)
            }
    
    return results


# Example usage endpoint for demonstration
def demo_ai_prediction_system(target_date: date = None, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Demonstration endpoint showing the complete AI prediction workflow.
    
    This shows how the system:
    1. Uses GPT-4/5 to analyze market conditions
    2. Generates predictions with confidence scores  
    3. Tracks accuracy against real prices
    4. Provides performance analytics
    """
    
    if target_date is None:
        target_date = datetime.now().date()
    
    # Get AI predictions
    predictions_response = get_ai_predictions_for_date(target_date, db)
    
    # Get accuracy metrics  
    accuracy_metrics = get_ai_accuracy_metrics(db)
    
    return {
        "demo_description": "SPY TA Tracker AI Prediction System",
        "features": [
            "GPT-4/5 powered price predictions for Open/Noon/2PM/Close",
            "Real-time accuracy tracking vs actual SPY prices", 
            "Confidence calibration and performance analytics",
            "Market context analysis for prediction reasoning"
        ],
        "target_date": target_date.isoformat(),
        "predictions": predictions_response,
        "accuracy_metrics": accuracy_metrics,
        "next_steps": [
            "Add OPENAI_API_KEY to environment variables",
            "Enable real-time price scheduling",
            "Integrate with frontend UI for visualization"
        ]
    }