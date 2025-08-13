"""
Historical simulation system for SPY TA Tracker.
Generates backdated AI predictions using only historically available data.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import yfinance as yf
from sqlalchemy.orm import Session

from .ai_predictor import AIPredictor, DayPredictions
from .models import DailyPrediction, AIPrediction, PriceLog
from .database import get_db


@dataclass
class SimulationDay:
    """Results for a single simulation day."""
    date: date
    predictions: DayPredictions
    actual_prices: Dict[str, float]  # open, noon, twoPM, close
    errors: Dict[str, float]  # prediction errors by checkpoint
    accuracy_metrics: Dict[str, Any]


@dataclass
class SimulationResults:
    """Complete simulation results."""
    start_date: date
    end_date: date
    total_days: int
    simulation_days: List[SimulationDay]
    overall_metrics: Dict[str, Any]
    performance_summary: Dict[str, Any]


class HistoricalSimulator:
    """Generate backdated AI predictions using only historically available data."""
    
    def __init__(self):
        self.ai_predictor = AIPredictor()
        self.symbol = "SPY"
    
    def run_simulation(
        self, 
        end_date: date, 
        num_days: int = 10,
        lookback_days: int = 5,
        db: Session = None
    ) -> SimulationResults:
        """
        Run historical simulation for specified number of trading days.
        
        Args:
            end_date: Last trading day to simulate (working backward)
            num_days: Number of trading days to simulate
            lookback_days: Days of history to provide to AI for each prediction
            db: Database session (optional, for storing results)
        
        Returns:
            SimulationResults with predictions vs actuals
        """
        print(f"🔬 Starting historical simulation: {num_days} days ending {end_date}")
        
        # Get trading days by fetching SPY history
        spy = yf.Ticker(self.symbol)
        
        # Fetch extra days to ensure we have enough trading days
        buffer_start = end_date - timedelta(days=num_days * 3)
        hist = spy.history(start=buffer_start, end=end_date + timedelta(days=1), interval="1d")
        
        # Get actual trading days (dates where market was open)
        trading_days = [d.date() for d in hist.index if d.date() <= end_date]
        
        if len(trading_days) < num_days:
            raise ValueError(f"Insufficient trading days. Found {len(trading_days)}, need {num_days}")
        
        # Select the last N trading days
        simulation_dates = trading_days[-num_days:]
        
        print(f"📅 Simulation dates: {simulation_dates[0]} to {simulation_dates[-1]}")
        
        # Run simulation for each day
        simulation_days = []
        for sim_date in simulation_dates:
            print(f"🎯 Simulating {sim_date}...")
            sim_day = self._simulate_single_day(sim_date, lookback_days, hist, db)
            simulation_days.append(sim_day)
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(simulation_days)
        performance_summary = self._generate_performance_summary(simulation_days)
        
        return SimulationResults(
            start_date=simulation_dates[0],
            end_date=simulation_dates[-1], 
            total_days=len(simulation_dates),
            simulation_days=simulation_days,
            overall_metrics=overall_metrics,
            performance_summary=performance_summary
        )
    
    def _simulate_single_day(
        self, 
        target_date: date, 
        lookback_days: int, 
        full_history: Any,  # yfinance DataFrame
        db: Session = None
    ) -> SimulationDay:
        """Simulate predictions for a single day using time-aware data filtering."""
        
        # Create time-aware AI predictor that only sees historical data
        historical_predictor = TimeAwareAIPredictor(target_date)
        
        # Generate predictions using only data available before target_date
        day_predictions = historical_predictor.generate_predictions(target_date, lookback_days)
        
        # Get actual prices for this day from historical data
        target_row = full_history.loc[full_history.index.date == target_date]
        
        if target_row.empty:
            raise ValueError(f"No market data found for {target_date}")
        
        actual_row = target_row.iloc[0]
        actual_prices = {
            "open": float(actual_row.Open),
            "noon": float(actual_row.High + actual_row.Low) / 2,  # Approximate noon as mid-range
            "twoPM": float(actual_row.High * 0.3 + actual_row.Low * 0.7),  # Approximate 2PM
            "close": float(actual_row.Close)
        }
        
        # Calculate prediction errors
        errors = {}
        accuracy_metrics = {}
        
        for pred in day_predictions.predictions:
            if pred.checkpoint in actual_prices:
                actual = actual_prices[pred.checkpoint]
                error = abs(pred.predicted_price - actual)
                errors[pred.checkpoint] = error
                
                # Calculate accuracy (within $1, $2, etc.)
                accuracy_metrics[pred.checkpoint] = {
                    "predicted": pred.predicted_price,
                    "actual": actual,
                    "error": error,
                    "accurate_1dollar": error <= 1.0,
                    "accurate_2dollar": error <= 2.0,
                    "confidence": pred.confidence
                }
        
        # Store in database if session provided
        if db:
            self._store_simulation_results(target_date, day_predictions, actual_prices, db)
        
        return SimulationDay(
            date=target_date,
            predictions=day_predictions,
            actual_prices=actual_prices,
            errors=errors,
            accuracy_metrics=accuracy_metrics
        )
    
    def _store_simulation_results(
        self, 
        target_date: date, 
        predictions: DayPredictions, 
        actuals: Dict[str, float], 
        db: Session
    ):
        """Store simulation results in database for analysis."""
        
        # Store DailyPrediction record
        existing_pred = db.query(DailyPrediction).filter(DailyPrediction.date == target_date).first()
        if not existing_pred:
            # Create AI-derived prediction band
            prices = [p.predicted_price for p in predictions.predictions]
            pred_low, pred_high = min(prices), max(prices)
            
            daily_pred = DailyPrediction(
                date=target_date,
                predLow=pred_low,
                predHigh=pred_high,
                source="ai_simulation",
                locked=True,
                open=actuals.get("open"),
                noon=actuals.get("noon"), 
                twoPM=actuals.get("twoPM"),
                close=actuals.get("close")
            )
            
            # Calculate derived fields
            if daily_pred.close and daily_pred.predHigh and daily_pred.predLow:
                mid_pred = (daily_pred.predHigh + daily_pred.predLow) / 2.0
                daily_pred.absErrorToClose = abs(daily_pred.close - mid_pred)
                daily_pred.rangeHit = bool(daily_pred.predLow <= daily_pred.close <= daily_pred.predHigh)
            
            db.add(daily_pred)
        
        # Store individual AI predictions (idempotent)
        for pred in predictions.predictions:
            actual_price = actuals.get(pred.checkpoint)
            prediction_error = abs(pred.predicted_price - actual_price) if actual_price is not None else None

            existing = db.query(AIPrediction).filter(
                AIPrediction.date == target_date,
                AIPrediction.checkpoint == pred.checkpoint,
            ).first()

            if existing:
                # Update actuals if we have them now; keep original predicted values
                if actual_price is not None:
                    existing.actual_price = actual_price
                    existing.prediction_error = prediction_error
                # Ensure market_context is tagged as simulation for visibility
                if not (existing.market_context or '').startswith('[SIMULATION]'):
                    existing.market_context = f"[SIMULATION] {predictions.market_context}"
                db.add(existing)
            else:
                ai_pred = AIPrediction(
                    date=target_date,
                    checkpoint=pred.checkpoint,
                    predicted_price=pred.predicted_price,
                    confidence=pred.confidence,
                    reasoning=f"[SIM] {pred.reasoning}",
                    market_context=f"[SIMULATION] {predictions.market_context}",
                    actual_price=actual_price,
                    prediction_error=prediction_error,
                )
                db.add(ai_pred)
        
        db.commit()
        print(f"✅ Stored simulation results for {target_date}")
    
    def _calculate_overall_metrics(self, simulation_days: List[SimulationDay]) -> Dict[str, Any]:
        """Calculate aggregate metrics across all simulation days."""
        
        all_errors = []
        checkpoint_metrics = {"open": [], "noon": [], "twoPM": [], "close": []}
        confidence_buckets = {"high": [], "medium": [], "low": []}
        
        for day in simulation_days:
            for checkpoint, error in day.errors.items():
                all_errors.append(error)
                checkpoint_metrics[checkpoint].append(error)
                
                # Find corresponding prediction for confidence
                pred = next((p for p in day.predictions.predictions if p.checkpoint == checkpoint), None)
                if pred:
                    confidence = pred.confidence
                    if confidence >= 0.7:
                        confidence_buckets["high"].append(error)
                    elif confidence >= 0.5:
                        confidence_buckets["medium"].append(error)
                    else:
                        confidence_buckets["low"].append(error)
        
        # Calculate overall statistics
        overall_mae = sum(all_errors) / len(all_errors) if all_errors else 0
        overall_accuracy_1dollar = len([e for e in all_errors if e <= 1.0]) / len(all_errors) if all_errors else 0
        overall_accuracy_2dollar = len([e for e in all_errors if e <= 2.0]) / len(all_errors) if all_errors else 0
        
        # Checkpoint-specific metrics
        checkpoint_stats = {}
        for checkpoint, errors in checkpoint_metrics.items():
            if errors:
                checkpoint_stats[checkpoint] = {
                    "mean_absolute_error": sum(errors) / len(errors),
                    "accuracy_1dollar": len([e for e in errors if e <= 1.0]) / len(errors),
                    "accuracy_2dollar": len([e for e in errors if e <= 2.0]) / len(errors),
                    "total_predictions": len(errors)
                }
        
        # Confidence calibration
        confidence_stats = {}
        for bucket, errors in confidence_buckets.items():
            if errors:
                confidence_stats[bucket] = {
                    "mean_absolute_error": sum(errors) / len(errors),
                    "accuracy_1dollar": len([e for e in errors if e <= 1.0]) / len(errors),
                    "count": len(errors)
                }
        
        return {
            "total_predictions": len(all_errors),
            "overall_mae": overall_mae,
            "overall_accuracy_1dollar": overall_accuracy_1dollar, 
            "overall_accuracy_2dollar": overall_accuracy_2dollar,
            "checkpoint_performance": checkpoint_stats,
            "confidence_calibration": confidence_stats
        }
    
    def _generate_performance_summary(self, simulation_days: List[SimulationDay]) -> Dict[str, Any]:
        """Generate human-readable performance summary."""
        
        if not simulation_days:
            return {"message": "No simulation data available"}
        
        total_days = len(simulation_days)
        total_predictions = sum(len(day.errors) for day in simulation_days)
        
        # Best and worst days
        day_errors = [(day.date, sum(day.errors.values()) / len(day.errors)) for day in simulation_days if day.errors]
        best_day = min(day_errors, key=lambda x: x[1]) if day_errors else None
        worst_day = max(day_errors, key=lambda x: x[1]) if day_errors else None
        
        # Range hit analysis (using predicted bands)
        range_hits = 0
        for day in simulation_days:
            if day.predictions.predictions:
                prices = [p.predicted_price for p in day.predictions.predictions]
                pred_low, pred_high = min(prices), max(prices)
                actual_close = day.actual_prices.get("close")
                if actual_close and pred_low <= actual_close <= pred_high:
                    range_hits += 1
        
        range_hit_rate = range_hits / total_days if total_days > 0 else 0
        
        return {
            "simulation_period": f"{simulation_days[0].date} to {simulation_days[-1].date}",
            "total_trading_days": total_days,
            "total_predictions": total_predictions,
            "best_day": {"date": best_day[0].isoformat(), "mae": round(best_day[1], 2)} if best_day else None,
            "worst_day": {"date": worst_day[0].isoformat(), "mae": round(worst_day[1], 2)} if worst_day else None,
            "range_hit_rate": round(range_hit_rate, 3),
            "grade": self._assign_grade(day_errors)
        }
    
    def _assign_grade(self, day_errors: List[Tuple[date, float]]) -> str:
        """Assign letter grade based on average performance."""
        if not day_errors:
            return "N/A"
        
        avg_mae = sum(error for _, error in day_errors) / len(day_errors)
        
        if avg_mae <= 1.0:
            return "A"
        elif avg_mae <= 1.5:
            return "B"
        elif avg_mae <= 2.0:
            return "C" 
        elif avg_mae <= 3.0:
            return "D"
        else:
            return "F"


class TimeAwareAIPredictor(AIPredictor):
    """AI predictor that only uses data available before the target date."""
    
    def __init__(self, simulation_date: date):
        super().__init__()
        self.simulation_date = simulation_date
    
    def _gather_market_context(self, target_date: date, lookback_days: int = 5) -> Dict:
        """Override to prevent future data leakage during simulation."""
        
        # Ensure we only use data before the simulation date
        spy = yf.Ticker(self.symbol)
        end_date = target_date  # This should be the simulation date
        start_date = target_date - timedelta(days=lookback_days * 3)
        
        # Critical: Only fetch data up to (but not including) the target date
        hist = spy.history(start=start_date, end=target_date, interval="1d")
        
        if hist.empty:
            raise ValueError(f"No historical data available for simulation date {target_date}")
        
        # For simulation, use the previous day's close as "pre-market"
        pre_market_price = float(hist['Close'].iloc[-1]) if len(hist) > 0 else None
        
        # Calculate technical levels from available history only
        recent_high = hist['High'].tail(lookback_days).max()
        recent_low = hist['Low'].tail(lookback_days).min()
        prev_close = hist['Close'].iloc[-1] if len(hist) > 0 else None
        
        # Calculate volatility from historical returns only
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5) if len(returns) > 1 else 0
        
        def safe_format_price(value, fallback="N/A"):
            if value is None:
                return fallback
            try:
                return f"${float(value):.2f}"
            except (ValueError, TypeError):
                return fallback
        
        context = {
            "target_date": target_date.isoformat(),
            "simulation_note": f"HISTORICAL SIMULATION - Only data through {target_date} used",
            "pre_market_price": pre_market_price,
            "previous_close": float(prev_close) if prev_close else None,
            "recent_high": float(recent_high),
            "recent_low": float(recent_low),
            "annualized_volatility": float(volatility),
            "recent_prices": [
                {
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": float(row.Open),
                    "high": float(row.High),
                    "low": float(row.Low),
                    "close": float(row.Close),
                    "volume": int(row.Volume)
                }
                for idx, row in hist.tail(lookback_days).iterrows()
            ],
            "summary": f"[SIMULATION] SPY analysis for {target_date}: Using data through {hist.index[-1].strftime('%Y-%m-%d')}, "
                      f"Previous close {safe_format_price(prev_close)}, {lookback_days}-day range {safe_format_price(recent_low)}-{safe_format_price(recent_high)}"
        }
        
        return context


# Global instance
historical_simulator = HistoricalSimulator()