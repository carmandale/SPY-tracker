"""
Administrative endpoints for SPY Tracker.
Handles data backfilling, migrations, cleanup, and maintenance operations.
"""

from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
import yfinance as yf

from ..database import get_db
from ..models import DailyPrediction, AIPrediction
from ..config import settings
from ..capture import refresh_actuals_for_date
from ..ai_predictor import AIPredictor

router = APIRouter(prefix="/admin", tags=["admin"])


def _update_derived_fields(pred: DailyPrediction) -> None:
    """Update absErrorToClose and rangeHit based on current data"""
    if pred.close is not None and pred.predHigh is not None and pred.predLow is not None:
        mid_pred = (pred.predHigh + pred.predLow) / 2.0
        pred.absErrorToClose = abs(pred.close - mid_pred)
        pred.rangeHit = bool(pred.predLow <= pred.close <= pred.predHigh)


@router.post("/backfill-actuals/{target_date}")
def backfill_actuals_for_day(target_date: date, db: Session = Depends(get_db)):
    """Backfill actual Open/Noon/2PM/Close prices for a given date using yfinance.

    - Noon is approximated as the mid of High/Low
    - 2PM is approximated as 30% High + 70% Low
    """
    try:
        ticker = yf.Ticker(settings.symbol)
        hist = ticker.history(start=target_date, end=target_date, interval="1d")
        if hist.empty:
            # Some providers require end to be +1 day to include the row
            hist = ticker.history(start=target_date, end=target_date.fromordinal(target_date.toordinal()+1), interval="1d")
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No market data for {target_date}")

        row = hist.iloc[0]
        open_p = float(row.Open)
        high_p = float(row.High)
        low_p = float(row.Low)
        close_p = float(row.Close)
        noon_p = (high_p + low_p) / 2
        two_pm_p = high_p * 0.3 + low_p * 0.7

        # Upsert DailyPrediction
        pred = db.query(DailyPrediction).filter(DailyPrediction.date == target_date).first()
        if pred is None:
            pred = DailyPrediction(date=target_date)
            db.add(pred)

        pred.open = open_p
        pred.noon = noon_p
        pred.twoPM = two_pm_p
        pred.close = close_p
        _update_derived_fields(pred)
        db.commit()
        db.refresh(pred)

        return {"status": "success", "date": target_date.isoformat(), "open": open_p, "noon": noon_p, "twoPM": two_pm_p, "close": close_p}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backfill failed: {str(e)}")


@router.get("/backfill-actuals/{target_date}")
def backfill_actuals_for_day_get(target_date: date, db: Session = Depends(get_db)):
    """GET variant of backfill for convenience."""
    return backfill_actuals_for_day(target_date, db)


@router.post("/refresh-actuals-intraday/{target_date}")
def refresh_actuals_intraday(target_date: date, force: bool = False, db: Session = Depends(get_db)):
    """Recompute actuals for a date from 1‑minute bars, optionally overwriting existing values."""
    try:
        filled = refresh_actuals_for_date(db, target_date, force=force)
        return {"status": "success", "filled": filled, "force": force, "date": target_date}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")


@router.post("/refresh-actuals-intraday-range")
def refresh_actuals_intraday_range(start_date: date, end_date: date, force: bool = False, db: Session = Depends(get_db)):
    """Recompute actuals for a date range from 1‑minute bars."""
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="start_date must be <= end_date")
        results = []
        d = start_date
        while d <= end_date:
            results.append({"date": d, "filled": refresh_actuals_for_date(db, d, force=force)})
            d = date.fromordinal(d.toordinal() + 1)
        return {"status": "success", "results": results, "force": force}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh range failed: {str(e)}")


@router.post("/simulate-simple/{num_days}")
def admin_simulate_simple(num_days: int = Path(..., ge=1, le=60), db: Session = Depends(get_db)):
    """Generate and persist AI simulation data for the last N trading days (idempotent)."""
    try:
        symbol = settings.symbol
        predictor = AIPredictor()
        today = datetime.now().date()
        start = today - timedelta(days=num_days * 3)
        spy = yf.Ticker(symbol)
        hist = spy.history(start=start, end=today + timedelta(days=1), interval="1d")
        dates = [idx.date() for idx in hist.index if idx.date() <= today][-num_days:]

        saved = []
        for d in dates:
            # Generate predictions
            day_preds = predictor.generate_predictions(d, lookback_days=settings.ai_lookback_days)
            row = hist.loc[hist.index.date == d]
            if row.empty:
                continue
            r = row.iloc[0]
            actuals = {
                "open": float(r.Open),
                "noon": float((r.High + r.Low) / 2.0),
                "twoPM": float(r.High * 0.3 + r.Low * 0.7),
                "close": float(r.Close),
            }
            # Upsert DailyPrediction
            pred = db.query(DailyPrediction).filter(DailyPrediction.date == d).first()
            if pred is None:
                pred = DailyPrediction(date=d)
                db.add(pred)
            prices = [p.predicted_price for p in day_preds.predictions]
            if prices:
                pred.predLow = min(prices)
                pred.predHigh = max(prices)
            pred.source = "ai_simulation"
            pred.locked = True
            pred.open = actuals["open"]
            pred.noon = actuals["noon"]
            pred.twoPM = actuals["twoPM"]
            pred.close = actuals["close"]
            _update_derived_fields(pred)

            # Upsert AIPrediction per checkpoint
            for p in day_preds.predictions:
                existing = db.query(AIPrediction).filter(
                    AIPrediction.date == d,
                    AIPrediction.checkpoint == p.checkpoint,
                ).first()
                if existing:
                    existing.actual_price = actuals.get(p.checkpoint)
                    existing.prediction_error = (
                        abs(p.predicted_price - existing.actual_price)
                        if existing.actual_price is not None else None
                    )
                    if not (existing.market_context or '').startswith('[SIMULATION]'):
                        existing.market_context = f"[SIMULATION] {day_preds.market_context}"
                    db.add(existing)
                else:
                    db.add(AIPrediction(
                        date=d,
                        checkpoint=p.checkpoint,
                        predicted_price=p.predicted_price,
                        confidence=p.confidence,
                        reasoning=f"[SIM] {p.reasoning}",
                        market_context=f"[SIMULATION] {day_preds.market_context}",
                        actual_price=actuals.get(p.checkpoint),
                        prediction_error=(
                            abs(p.predicted_price - actuals.get(p.checkpoint))
                            if actuals.get(p.checkpoint) is not None else None
                        ),
                    ))
            db.commit()
            saved.append(d.isoformat())

        return {"status": "success", "saved_dates": saved, "count": len(saved)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/fix-duplicate-ai-predictions")
def fix_duplicate_ai_predictions(db: Session = Depends(get_db)):
    """Run the AI prediction deduplication migration."""
    try:
        from ..migration_runner import MigrationRunner
        
        # Close the current DB session to avoid conflicts
        db.close()
        
        # Run migration with dedicated connection
        runner = MigrationRunner(str(settings.database_url).replace("sqlite:///", ""))
        analysis = runner.get_duplicate_analysis()
        
        if analysis['duplicate_count'] == 0:
            return {
                "status": "success",
                "message": "No duplicates found - migration not needed",
                "analysis": analysis
            }
        
        # Run the migration
        result = runner.run_migration("001_add_ai_prediction_unique_constraint.sql")
        
        return {
            "status": "success",
            "message": "AI prediction duplicates fixed successfully",
            "before": analysis,
            "after": result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Migration failed: {str(e)}",
            "hint": "Try stopping the server and running: python backend/fix_duplicates.py"
        }


@router.get("/analyze-ai-prediction-duplicates") 
def analyze_ai_prediction_duplicates(db: Session = Depends(get_db)):
    """Analyze current AI prediction duplicate situation."""
    try:
        from ..migration_runner import MigrationRunner
        
        # Close the current DB session to avoid conflicts
        db.close()
        
        runner = MigrationRunner(str(settings.database_url).replace("sqlite:///", ""))
        analysis = runner.get_duplicate_analysis()
        
        return {
            "status": "success",
            "analysis": analysis,
            "recommendation": "Run /admin/fix-duplicate-ai-predictions to fix" if analysis['duplicate_count'] > 0 else "No action needed"
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Analysis failed: {str(e)}"
        }


@router.post("/cleanup-future-data")
def cleanup_future_data(db: Session = Depends(get_db)):
    """Remove any predictions or AI predictions for future dates."""
    today = datetime.now().date()
    
    # Delete future DailyPredictions
    future_preds = db.query(DailyPrediction).filter(DailyPrediction.date > today).all()
    for pred in future_preds:
        db.delete(pred)
    
    # Delete future AIPredictions
    future_ai_preds = db.query(AIPrediction).filter(AIPrediction.date > today).all()
    for pred in future_ai_preds:
        db.delete(pred)
    
    db.commit()
    
    return {
        "status": "success",
        "cleaned_up": {
            "daily_predictions": len(future_preds),
            "ai_predictions": len(future_ai_preds)
        },
        "cutoff_date": today.isoformat()
    }