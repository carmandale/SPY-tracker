"""
Accuracy metrics calculation for SPY TA Tracker predictions.

This module provides functions to calculate various accuracy metrics
for predictions, including MAE, hit rates, and interval coverage.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
import statistics
import math
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .models import AIPrediction, ModelPerformance, DailyPrediction


def calculate_prediction_accuracy(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    model_name: Optional[str] = None,
    checkpoint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate comprehensive accuracy metrics for predictions.
    
    Args:
        db: Database session
        start_date: Start date for analysis (inclusive)
        end_date: End date for analysis (inclusive)
        model_name: Filter by model name (e.g., 'llm', 'baseline', 'ensemble')
        checkpoint: Filter by checkpoint (e.g., 'open', 'noon', 'twoPM', 'close')
        
    Returns:
        Dictionary with accuracy metrics
    """
    # Build query for predictions with actual prices
    query = db.query(AIPrediction).filter(AIPrediction.actual_price.isnot(None))
    
    # Apply filters
    if start_date:
        query = query.filter(AIPrediction.date >= start_date)
    if end_date:
        query = query.filter(AIPrediction.date <= end_date)
    if model_name:
        query = query.filter(AIPrediction.source == model_name)
    if checkpoint:
        query = query.filter(AIPrediction.checkpoint == checkpoint)
    
    # Execute query
    predictions = query.all()
    
    if not predictions:
        return {
            "message": "No predictions with actual prices found for the specified criteria",
            "total_predictions": 0
        }
    
    # Calculate basic metrics
    abs_errors = [abs(p.predicted_price - p.actual_price) for p in predictions]
    mae = sum(abs_errors) / len(abs_errors)
    
    # Calculate RMSE
    squared_errors = [(p.predicted_price - p.actual_price) ** 2 for p in predictions]
    rmse = math.sqrt(sum(squared_errors) / len(squared_errors))
    
    # Calculate hit rates
    hit_rate_1dollar = len([e for e in abs_errors if e <= 1.0]) / len(abs_errors)
    hit_rate_2dollar = len([e for e in abs_errors if e <= 2.0]) / len(abs_errors)
    
    # Calculate interval coverage (if intervals available)
    interval_predictions = [p for p in predictions if p.interval_low is not None and p.interval_high is not None]
    if interval_predictions:
        in_interval = [
            p.actual_price >= p.interval_low and p.actual_price <= p.interval_high
            for p in interval_predictions
        ]
        interval_coverage = sum(in_interval) / len(in_interval)
    else:
        interval_coverage = None
    
    # Calculate metrics by checkpoint
    checkpoint_metrics = {}
    for ckpt in ["open", "noon", "twoPM", "close"]:
        ckpt_preds = [p for p in predictions if p.checkpoint == ckpt]
        if ckpt_preds:
            ckpt_errors = [abs(p.predicted_price - p.actual_price) for p in ckpt_preds]
            ckpt_mae = sum(ckpt_errors) / len(ckpt_errors)
            ckpt_hit_rate = len([e for e in ckpt_errors if e <= 1.0]) / len(ckpt_errors)
            
            # Interval coverage for this checkpoint
            ckpt_interval_preds = [p for p in ckpt_preds if p.interval_low is not None and p.interval_high is not None]
            if ckpt_interval_preds:
                ckpt_in_interval = [
                    p.actual_price >= p.interval_low and p.actual_price <= p.interval_high
                    for p in ckpt_interval_preds
                ]
                ckpt_interval_coverage = sum(ckpt_in_interval) / len(ckpt_interval_preds)
            else:
                ckpt_interval_coverage = None
            
            checkpoint_metrics[ckpt] = {
                "mae": ckpt_mae,
                "hit_rate_1dollar": ckpt_hit_rate,
                "count": len(ckpt_preds),
                "interval_coverage": ckpt_interval_coverage
            }
    
    # Calculate metrics by model source
    source_metrics = {}
    for source in set(p.source for p in predictions if p.source):
        source_preds = [p for p in predictions if p.source == source]
        if source_preds:
            source_errors = [abs(p.predicted_price - p.actual_price) for p in source_preds]
            source_mae = sum(source_errors) / len(source_errors)
            source_hit_rate = len([e for e in source_errors if e <= 1.0]) / len(source_errors)
            
            source_metrics[source] = {
                "mae": source_mae,
                "hit_rate_1dollar": source_hit_rate,
                "count": len(source_preds)
            }
    
    # Calculate rolling metrics (last 10 trading days)
    dates = sorted(set(p.date for p in predictions))
    if len(dates) >= 5:
        recent_dates = dates[-5:]
        recent_preds = [p for p in predictions if p.date in recent_dates]
        recent_errors = [abs(p.predicted_price - p.actual_price) for p in recent_preds]
        recent_mae = sum(recent_errors) / len(recent_errors) if recent_errors else None
        recent_hit_rate = len([e for e in recent_errors if e <= 1.0]) / len(recent_errors) if recent_errors else None
    else:
        recent_mae = None
        recent_hit_rate = None
    
    return {
        "total_predictions": len(predictions),
        "date_range": {
            "start": min(p.date for p in predictions).isoformat(),
            "end": max(p.date for p in predictions).isoformat(),
            "days": len(dates)
        },
        "overall_metrics": {
            "mae": mae,
            "rmse": rmse,
            "hit_rate_1dollar": hit_rate_1dollar,
            "hit_rate_2dollar": hit_rate_2dollar,
            "interval_coverage": interval_coverage
        },
        "checkpoint_metrics": checkpoint_metrics,
        "source_metrics": source_metrics,
        "recent_metrics": {
            "days": len(recent_dates) if 'recent_dates' in locals() else 0,
            "mae": recent_mae,
            "hit_rate_1dollar": recent_hit_rate
        }
    }


def update_model_performance(db: Session, target_date: date) -> Dict[str, Any]:
    """
    Calculate and store daily performance metrics for all prediction models.
    
    Args:
        db: Database session
        target_date: Date to calculate metrics for
        
    Returns:
        Dictionary with performance metrics
    """
    # Get all predictions for the target date with actual prices
    predictions = db.query(AIPrediction).filter(
        AIPrediction.date == target_date,
        AIPrediction.actual_price.isnot(None)
    ).all()
    
    if not predictions:
        return {
            "message": f"No predictions with actual prices found for {target_date}",
            "date": target_date.isoformat()
        }
    
    # Group predictions by source
    sources = {}
    for pred in predictions:
        source = pred.source or "unknown"
        if source not in sources:
            sources[source] = []
        sources[source].append(pred)
    
    # Calculate metrics for each source
    results = {}
    for source, preds in sources.items():
        # Calculate MAE
        abs_errors = [abs(p.predicted_price - p.actual_price) for p in preds]
        mae = sum(abs_errors) / len(abs_errors)
        
        # Calculate RMSE
        squared_errors = [(p.predicted_price - p.actual_price) ** 2 for p in preds]
        rmse = math.sqrt(sum(squared_errors) / len(squared_errors))
        
        # Calculate hit rate
        hit_rate_1dollar = len([e for e in abs_errors if e <= 1.0]) / len(abs_errors)
        
        # Calculate interval coverage
        interval_preds = [p for p in preds if p.interval_low is not None and p.interval_high is not None]
        if interval_preds:
            in_interval = [
                p.actual_price >= p.interval_low and p.actual_price <= p.interval_high
                for p in interval_preds
            ]
            interval_coverage = sum(in_interval) / len(in_interval)
        else:
            interval_coverage = None
        
        # Store or update performance record
        perf = db.query(ModelPerformance).filter(
            ModelPerformance.date == target_date,
            ModelPerformance.model_name == source
        ).first()
        
        if not perf:
            perf = ModelPerformance(
                date=target_date,
                model_name=source
            )
            db.add(perf)
        
        perf.mae = mae
        perf.rmse = rmse
        perf.hit_rate_1dollar = hit_rate_1dollar
        perf.interval_coverage = interval_coverage
        
        results[source] = {
            "mae": mae,
            "rmse": rmse,
            "hit_rate_1dollar": hit_rate_1dollar,
            "interval_coverage": interval_coverage,
            "count": len(preds)
        }
    
    db.commit()
    
    return {
        "date": target_date.isoformat(),
        "models": results
    }


def get_model_performance_history(
    db: Session,
    model_name: Optional[str] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get historical performance metrics for prediction models.
    
    Args:
        db: Database session
        model_name: Filter by model name
        days: Number of days to include
        
    Returns:
        Dictionary with performance history
    """
    # Calculate start date
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Build query
    query = db.query(ModelPerformance).filter(
        ModelPerformance.date >= start_date,
        ModelPerformance.date <= end_date
    ).order_by(ModelPerformance.date)
    
    if model_name:
        query = query.filter(ModelPerformance.model_name == model_name)
    
    # Execute query
    performances = query.all()
    
    if not performances:
        return {
            "message": "No performance data found for the specified criteria",
            "total_days": 0
        }
    
    # Group by model
    models = {}
    for perf in performances:
        if perf.model_name not in models:
            models[perf.model_name] = []
        models[perf.model_name].append({
            "date": perf.date.isoformat(),
            "mae": perf.mae,
            "rmse": perf.rmse,
            "hit_rate_1dollar": perf.hit_rate_1dollar,
            "interval_coverage": perf.interval_coverage
        })
    
    # Calculate averages
    averages = {}
    for model, perfs in models.items():
        maes = [p["mae"] for p in perfs if p["mae"] is not None]
        rmses = [p["rmse"] for p in perfs if p["rmse"] is not None]
        hit_rates = [p["hit_rate_1dollar"] for p in perfs if p["hit_rate_1dollar"] is not None]
        coverages = [p["interval_coverage"] for p in perfs if p["interval_coverage"] is not None]
        
        averages[model] = {
            "avg_mae": sum(maes) / len(maes) if maes else None,
            "avg_rmse": sum(rmses) / len(rmses) if rmses else None,
            "avg_hit_rate": sum(hit_rates) / len(hit_rates) if hit_rates else None,
            "avg_interval_coverage": sum(coverages) / len(coverages) if coverages else None,
            "days": len(perfs)
        }
    
    return {
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "models": models,
        "averages": averages
    }

