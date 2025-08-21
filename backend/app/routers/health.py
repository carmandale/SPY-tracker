"""
Health and monitoring endpoints for SPY Tracker.
Critical system health checks and data integrity monitoring.
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db
from ..models import DailyPrediction, AIPrediction
from ..timezone_utils import get_ny_now

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/critical")
def critical_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Critical health check endpoint for monitoring system integrity.
    
    Returns comprehensive status of:
    - Today's prediction existence
    - Scheduler health
    - Data integrity checks
    - Weekend data presence
    - Future price validation
    """
    
    # Get current time in ET
    now_et = get_ny_now()
    today = now_et.date()
    
    # Check if today is a weekday
    is_weekday = today.weekday() < 5  # Monday = 0, Friday = 4
    
    # Check for today's prediction
    today_prediction = db.query(DailyPrediction).filter(
        DailyPrediction.date == today
    ).first()
    
    today_prediction_exists = False
    today_prediction_time = None
    today_has_prices = False
    
    if today_prediction:
        today_prediction_exists = bool(
            today_prediction.predLow is not None and 
            today_prediction.predHigh is not None
        )
        today_prediction_time = today_prediction.created_at.isoformat() if today_prediction.created_at else None
        today_has_prices = any([
            today_prediction.open,
            today_prediction.noon,
            today_prediction.twoPM,
            today_prediction.close
        ])
    
    # Check for weekend data (should not exist)
    weekend_check = text("""
        SELECT COUNT(*) as count
        FROM daily_predictions
        WHERE EXTRACT(DOW FROM date) IN (0, 6)
    """)
    weekend_count = db.execute(weekend_check).scalar()
    no_weekend_data = weekend_count == 0
    
    # Check for future prices (should not exist)
    future_prices_check = text("""
        SELECT COUNT(*) as count
        FROM daily_predictions
        WHERE date > :today
        AND (open IS NOT NULL OR noon IS NOT NULL OR "twoPM" IS NOT NULL OR close IS NOT NULL)
    """)
    future_count = db.execute(future_prices_check, {"today": today}).scalar()
    
    # Check today's future prices based on current time
    invalid_today_prices = []
    if today_prediction and is_weekday:
        # Check based on ET time
        if now_et.hour < 16 and today_prediction.close is not None:
            invalid_today_prices.append("close exists before 4 PM ET")
        if now_et.hour < 15 and today_prediction.twoPM is not None:
            invalid_today_prices.append("twoPM exists before 3 PM ET")
        if now_et.hour < 13 and today_prediction.noon is not None:
            invalid_today_prices.append("noon exists before 1 PM ET")
        if (now_et.hour < 9 or (now_et.hour == 9 and now_et.minute < 30)) and today_prediction.open is not None:
            invalid_today_prices.append("open exists before 9:30 AM ET")
    
    no_future_prices = future_count == 0 and len(invalid_today_prices) == 0
    
    # Check scheduler health (via import to avoid circular dependency)
    scheduler_healthy = False
    scheduler_jobs = 0
    try:
        from ..routers.scheduler import get_scheduler_status
        scheduler_info = get_scheduler_status()
        scheduler_healthy = scheduler_info.running
        scheduler_jobs = scheduler_info.jobs_count
    except Exception:
        pass
    
    # Check AI predictions for today
    today_ai_predictions = db.query(AIPrediction).filter(
        AIPrediction.date == today
    ).count()
    
    # Historical data check - last 5 weekdays should have data
    five_days_ago = today - timedelta(days=7)
    recent_predictions = db.query(DailyPrediction).filter(
        DailyPrediction.date >= five_days_ago,
        DailyPrediction.date < today
    ).all()
    
    weekday_predictions = [p for p in recent_predictions if p.date.weekday() < 5]
    recent_data_complete = len(weekday_predictions) >= 3  # At least 3 of last 5 weekdays
    
    # Overall health status
    all_checks_pass = all([
        not is_weekday or today_prediction_exists,  # Only required on weekdays
        scheduler_healthy,
        no_weekend_data,
        no_future_prices,
        recent_data_complete
    ])
    
    return {
        "status": "healthy" if all_checks_pass else "unhealthy",
        "timestamp": now_et.isoformat(),
        "current_time_et": now_et.strftime("%Y-%m-%d %H:%M:%S ET"),
        "is_weekday": is_weekday,
        "checks": {
            "today_prediction_exists": today_prediction_exists,
            "today_prediction_time": today_prediction_time,
            "today_has_prices": today_has_prices,
            "today_ai_predictions": today_ai_predictions,
            "scheduler_healthy": scheduler_healthy,
            "scheduler_jobs": scheduler_jobs,
            "data_integrity": {
                "no_weekend_data": no_weekend_data,
                "weekend_records_found": weekend_count,
                "no_future_prices": no_future_prices,
                "future_records_found": future_count,
                "invalid_today_prices": invalid_today_prices,
                "recent_data_complete": recent_data_complete,
                "recent_weekday_count": len(weekday_predictions)
            }
        },
        "alerts": _generate_alerts(
            is_weekday=is_weekday,
            today_prediction_exists=today_prediction_exists,
            scheduler_healthy=scheduler_healthy,
            no_weekend_data=no_weekend_data,
            no_future_prices=no_future_prices,
            today_has_prices=today_has_prices,
            current_hour_et=now_et.hour
        )
    }


def _generate_alerts(
    is_weekday: bool,
    today_prediction_exists: bool,
    scheduler_healthy: bool,
    no_weekend_data: bool,
    no_future_prices: bool,
    today_has_prices: bool,
    current_hour_et: int
) -> list[str]:
    """Generate alert messages based on health check results."""
    alerts = []
    
    # Critical alerts
    if is_weekday and not today_prediction_exists and current_hour_et >= 9:
        alerts.append("CRITICAL: No predictions for today (weekday) after 9 AM ET")
    
    if not scheduler_healthy:
        alerts.append("CRITICAL: Scheduler is not running")
    
    # Data integrity alerts
    if not no_weekend_data:
        alerts.append("WARNING: Weekend data found in database")
    
    if not no_future_prices:
        alerts.append("WARNING: Future prices exist in database")
    
    # Timing alerts
    if is_weekday and current_hour_et >= 10 and not today_has_prices:
        alerts.append("WARNING: No price data captured yet (after 10 AM ET)")
    
    return alerts


@router.get("/status")
def detailed_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed status endpoint with comprehensive system information."""
    
    # Get critical health first
    critical = critical_health_check(db)
    
    # Get additional detailed information
    now_et = get_ny_now()
    today = now_et.date()
    
    # Get prediction statistics for the last 30 days
    thirty_days_ago = today - timedelta(days=30)
    recent_predictions = db.query(DailyPrediction).filter(
        DailyPrediction.date >= thirty_days_ago
    ).all()
    
    # Calculate statistics
    total_predictions = len(recent_predictions)
    predictions_with_ai = sum(1 for p in recent_predictions if p.source and 'ai' in p.source.lower())
    predictions_complete = sum(1 for p in recent_predictions if all([
        p.open, p.noon, p.twoPM, p.close
    ]))
    
    # Get AI prediction accuracy for recent days
    recent_ai = db.query(AIPrediction).filter(
        AIPrediction.date >= thirty_days_ago,
        AIPrediction.prediction_error.isnot(None)
    ).all()
    
    avg_error = None
    if recent_ai:
        errors = [p.prediction_error for p in recent_ai if p.prediction_error is not None]
        avg_error = sum(errors) / len(errors) if errors else None
    
    return {
        "critical_health": critical,
        "statistics": {
            "last_30_days": {
                "total_predictions": total_predictions,
                "ai_predictions": predictions_with_ai,
                "complete_price_captures": predictions_complete,
                "completion_rate": predictions_complete / total_predictions if total_predictions > 0 else 0
            },
            "ai_accuracy": {
                "predictions_with_actuals": len(recent_ai),
                "average_error": avg_error,
                "accuracy_improving": _check_accuracy_trend(recent_ai)
            }
        },
        "system_info": {
            "database_connected": True,
            "current_time_et": now_et.isoformat(),
            "timezone": "America/Chicago (scheduler) / America/New_York (market)",
            "deployment_environment": "production"
        }
    }


def _check_accuracy_trend(ai_predictions: list) -> Optional[str]:
    """Check if AI prediction accuracy is improving over time."""
    if len(ai_predictions) < 10:
        return None
    
    # Sort by date
    sorted_preds = sorted(ai_predictions, key=lambda x: x.date)
    
    # Compare first half vs second half average errors
    mid_point = len(sorted_preds) // 2
    first_half = sorted_preds[:mid_point]
    second_half = sorted_preds[mid_point:]
    
    first_errors = [p.prediction_error for p in first_half if p.prediction_error is not None]
    second_errors = [p.prediction_error for p in second_half if p.prediction_error is not None]
    
    if not first_errors or not second_errors:
        return None
    
    first_avg = sum(first_errors) / len(first_errors)
    second_avg = sum(second_errors) / len(second_errors)
    
    if second_avg < first_avg * 0.9:
        return "improving"
    elif second_avg > first_avg * 1.1:
        return "degrading"
    else:
        return "stable"