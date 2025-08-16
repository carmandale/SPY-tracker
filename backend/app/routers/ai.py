"""
AI prediction and simulation endpoints for SPY Tracker.
Handles GPT-powered predictions, historical simulations, and accuracy metrics.
"""

from datetime import date, datetime
from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Body, Path
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from ..exceptions import DataNotFoundException, ValidationException

# Set up logging
logger = logging.getLogger(__name__)
from ..capture import refresh_actuals_for_date
from ..ai_endpoints import (
    get_ai_predictions_for_date,
    get_ai_accuracy_metrics,
    demo_ai_prediction_system,
    create_ai_prediction_for_date,
)
from ..historical_simulation import historical_simulator
from ..accuracy_metrics import calculate_prediction_accuracy

router = APIRouter(tags=["ai"])


@router.get("/ai/predictions/{target_date}")
def get_ai_predictions_endpoint(target_date: date, db: Session = Depends(get_db)):
    """Generate or retrieve AI predictions for a specific date.
    Eagerly attempts to fill today's actuals before returning.
    """
    try:
        if target_date == date.today():
            refresh_actuals_for_date(db, target_date)
    except Exception as e:
        logger.warning(f"Could not refresh actuals for {target_date}: {e}")
    
    try:
        return get_ai_predictions_for_date(target_date, db)
    except DataNotFoundException as e:
        logger.warning(f"No AI predictions found for {target_date}")
        raise
    except Exception as e:
        logger.error(f"Failed to get AI predictions for {target_date}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to retrieve AI predictions", "date": target_date.isoformat(), "reason": str(e)}
        )


@router.get("/ai/accuracy")  
def get_ai_accuracy_endpoint(db: Session = Depends(get_db)):
    """Get AI prediction accuracy metrics."""
    try:
        return get_ai_accuracy_metrics(db)
    except Exception as e:
        logger.error(f"Failed to get AI accuracy metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to calculate accuracy metrics", "reason": str(e)}
        )


@router.get("/ai/demo/{target_date}")
def ai_demo_date(target_date: date, db: Session = Depends(get_db)):
    """Demonstration of the complete AI prediction system for specific date."""
    return demo_ai_prediction_system(target_date, db)


@router.get("/ai/demo")
def ai_demo_today(db: Session = Depends(get_db)):
    """Demonstration of AI prediction system for today."""
    return demo_ai_prediction_system(None, db)


@router.post("/ai/predict/{target_date}")
def ai_predict_create(
    target_date: date,
    lookbackDays: int = None,
    db: Session = Depends(get_db),
):
    """Create AI prediction for a date and lock the day (create-only)."""
    if lookbackDays is None:
        lookbackDays = settings.ai_lookback_days
    
    try:
        return create_ai_prediction_for_date(target_date, lookbackDays, db)
    except ValidationException as e:
        logger.warning(f"Validation error creating AI prediction for {target_date}: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Failed to create AI prediction for {target_date}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to create AI prediction", "date": target_date.isoformat(), "reason": str(e)}
        )


# Historical Simulation Endpoints
@router.post("/simulation/run")
def run_historical_simulation(
    end_date: date = Body(..., description="Last trading day to simulate"),
    num_days: int = Body(10, description="Number of trading days to simulate"),
    lookback_days: int = Body(5, description="Days of history for AI context"),
    store_results: bool = Body(True, description="Store results in database"),
    db: Session = Depends(get_db)
):
    """
    Run historical simulation generating backdated AI predictions.
    
    This endpoint:
    1. Uses GPT-5 to predict prices using only historically available data
    2. Compares predictions against actual market outcomes
    3. Provides comprehensive accuracy analysis
    4. Optionally stores results in database for review
    """
    try:
        # Run simulation
        db_session = db if store_results else None
        results = historical_simulator.run_simulation(
            end_date=end_date,
            num_days=num_days, 
            lookback_days=lookback_days,
            db=db_session
        )
        
        # Convert to serializable format
        simulation_data = {
            "simulation_id": f"sim_{end_date.isoformat()}_{num_days}days",
            "parameters": {
                "end_date": end_date.isoformat(),
                "num_days": num_days,
                "lookback_days": lookback_days,
                "stored_in_db": store_results
            },
            "date_range": {
                "start_date": results.start_date.isoformat(),
                "end_date": results.end_date.isoformat(),
                "total_days": results.total_days
            },
            "overall_metrics": results.overall_metrics,
            "performance_summary": results.performance_summary,
            "daily_results": [
                {
                    "date": day.date.isoformat(),
                    "predictions": [
                        {
                            "checkpoint": pred.checkpoint,
                            "predicted_price": pred.predicted_price,
                            "confidence": pred.confidence,
                            "reasoning": pred.reasoning
                        }
                        for pred in day.predictions.predictions
                    ],
                    "actual_prices": day.actual_prices,
                    "errors": day.errors,
                    "market_context": day.predictions.market_context
                }
                for day in results.simulation_days
            ]
        }
        
        return {
            "status": "success",
            "message": f"Simulation completed for {num_days} trading days ending {end_date}",
            "results": simulation_data
        }
        
    except ValidationException as e:
        logger.warning(f"Simulation validation error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid simulation parameters", "reason": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Simulation failed for {num_days} days ending {end_date}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Simulation failed", "reason": str(e), "parameters": {"end_date": end_date.isoformat(), "num_days": num_days}}
        )


@router.get("/simulation/quick/{num_days}")
def quick_simulation(
    num_days: int = Path(..., description="Number of recent trading days to simulate"),
    db: Session = Depends(get_db)
):
    """Quick simulation using recent trading days (convenience endpoint)."""
    # Use today as end date (will find most recent trading day)
    end_date = datetime.now().date()
    
    return run_historical_simulation(
        end_date=end_date,
        num_days=num_days,
        lookback_days=5,
        store_results=True,
        db=db
    )


# Accuracy Metrics Endpoints
@router.get("/accuracy/metrics")
def get_accuracy_metrics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    model_name: Optional[str] = None,
    checkpoint: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get comprehensive accuracy metrics for predictions."""
    try:
        metrics = calculate_prediction_accuracy(
            db=db,
            start_date=start_date,
            end_date=end_date,
            model_name=model_name,
            checkpoint=checkpoint
        )
        
        return {
            "status": "success",
            "metrics": metrics,
            "filters": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "model_name": model_name,
                "checkpoint": checkpoint
            }
        }
        
    except Exception as e:
        logger.error(f"Accuracy calculation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Accuracy calculation failed", "reason": str(e), "filters": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "model_name": model_name,
                "checkpoint": checkpoint
            }}
        )