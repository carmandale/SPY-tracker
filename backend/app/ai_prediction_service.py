"""
AI Prediction Service - Handles AI prediction operations with deduplication.
Implements reliable patterns for managing AI predictions.
"""

from datetime import date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, and_

from .models import AIPrediction, DailyPrediction
from .ai_predictor import ai_predictor, DayPredictions, PricePrediction
from .exceptions import DataNotFoundException, PredictionLockedException


class AIPredictionService:
    """Service for managing AI predictions with deduplication and reliability."""
    
    @staticmethod
    def get_unique_predictions_for_date(db: Session, target_date: date) -> List[AIPrediction]:
        """
        Get exactly one prediction per checkpoint for a date.
        Uses most recent prediction if duplicates exist.
        
        Args:
            db: Database session
            target_date: Date to get predictions for
            
        Returns:
            List of AIPrediction objects (max 4: open, noon, twoPM, close)
        """
        # Get all predictions for the date, ordered by creation time (newest first)
        all_predictions = db.query(AIPrediction).filter(
            AIPrediction.date == target_date
        ).order_by(desc(AIPrediction.created_at)).all()
        
        # Deduplicate by checkpoint, keeping the most recent
        checkpoint_map = {}
        for pred in all_predictions:
            if pred.checkpoint not in checkpoint_map:
                checkpoint_map[pred.checkpoint] = pred
        
        # Return in consistent order
        result = []
        for checkpoint in ["open", "noon", "twoPM", "close"]:
            if checkpoint in checkpoint_map:
                result.append(checkpoint_map[checkpoint])
        
        return result
    
    @staticmethod
    def compute_band_from_predictions(predictions: List[AIPrediction]) -> Optional[Dict[str, float]]:
        """
        Compute prediction band (low/high) from unique predictions.
        
        Args:
            predictions: List of unique AI predictions
            
        Returns:
            Dict with 'low' and 'high' keys, or None if no predictions
        """
        if not predictions:
            return None
            
        prices = [pred.predicted_price for pred in predictions]
        return {
            "low": float(min(prices)),
            "high": float(max(prices))
        }
    
    @staticmethod
    def create_predictions_atomic(
        db: Session,
        target_date: date,
        day_predictions: DayPredictions,
        replace_existing: bool = True
    ) -> List[AIPrediction]:
        """
        Atomically create AI predictions for a date.
        
        Args:
            db: Database session
            target_date: Date for predictions
            day_predictions: AI generated predictions
            replace_existing: If True, delete existing predictions first
            
        Returns:
            List of created AIPrediction objects
            
        Raises:
            IntegrityError: If unique constraint violation occurs
        """
        created_predictions = []
        
        try:
            # If replacing, delete existing predictions first
            if replace_existing:
                db.query(AIPrediction).filter(
                    AIPrediction.date == target_date
                ).delete()
                db.flush()  # Ensure deletions are committed
            
            # Create new predictions
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
                created_predictions.append(ai_pred)
            
            # Flush to detect constraint violations before commit
            db.flush()
            
            return created_predictions
            
        except IntegrityError as e:
            db.rollback()
            if "uq_ai_prediction_date_checkpoint" in str(e) or "UNIQUE constraint failed" in str(e):
                # Handle duplicate constraint violation gracefully
                if not replace_existing:
                    # If not replacing, this means duplicates already exist
                    # Return existing predictions instead
                    return AIPredictionService.get_unique_predictions_for_date(db, target_date)
                else:
                    # This shouldn't happen if we deleted first, re-raise
                    raise
            else:
                # Other integrity error, re-raise
                raise
    
    @staticmethod
    def create_or_update_daily_prediction(
        db: Session,
        target_date: date,
        band: Dict[str, float],
        source: str = "ai",
        locked: bool = True
    ) -> DailyPrediction:
        """
        Create or update DailyPrediction with AI-derived band.
        
        Args:
            db: Database session
            target_date: Date for prediction
            band: Dict with 'low' and 'high' keys
            source: Source of prediction ("ai" or "manual")
            locked: Whether prediction should be locked
            
        Returns:
            Updated DailyPrediction object
            
        Raises:
            PredictionLockedException: If trying to update locked prediction
        """
        existing_day = db.query(DailyPrediction).filter(
            DailyPrediction.date == target_date
        ).first()
        
        if existing_day and existing_day.locked and existing_day.source != source:
            raise PredictionLockedException(
                f"Prediction for {target_date} is locked with source '{existing_day.source}'",
                {"date": target_date.isoformat(), "current_source": existing_day.source}
            )
        
        if existing_day is None:
            existing_day = DailyPrediction(date=target_date)
            db.add(existing_day)
        
        # Update prediction band
        existing_day.predLow = band["low"]
        existing_day.predHigh = band["high"]
        existing_day.source = source
        existing_day.locked = locked
        
        db.flush()
        return existing_day
    
    @staticmethod
    def get_or_create_predictions_for_date(
        db: Session,
        target_date: date,
        force_regenerate: bool = False
    ) -> tuple[List[AIPrediction], Optional[str]]:
        """
        Get existing predictions or generate new ones if needed.
        
        Args:
            db: Database session
            target_date: Date for predictions
            force_regenerate: If True, regenerate even if predictions exist
            
        Returns:
            Tuple of (predictions_list, market_context)
        """
        # Check for existing predictions
        existing_predictions = AIPredictionService.get_unique_predictions_for_date(db, target_date)
        
        market_context = None
        if existing_predictions:
            # Use existing market context from first prediction
            market_context = existing_predictions[0].market_context
        
        # Generate new predictions if needed
        if not existing_predictions or force_regenerate:
            try:
                # Generate AI predictions
                day_predictions = ai_predictor.generate_predictions(target_date)
                
                # Store predictions atomically
                existing_predictions = AIPredictionService.create_predictions_atomic(
                    db, target_date, day_predictions, replace_existing=force_regenerate
                )
                
                market_context = day_predictions.market_context
                
                # Commit the transaction
                db.commit()
                
            except Exception as e:
                db.rollback()
                # If generation fails and we have existing predictions, use those
                if existing_predictions and not force_regenerate:
                    return existing_predictions, market_context
                else:
                    raise
        
        return existing_predictions, market_context
    
    @staticmethod
    def update_actual_prices(db: Session, target_date: date, daily_prediction: DailyPrediction):
        """
        Update AI predictions with actual prices from DailyPrediction.
        
        Args:
            db: Database session
            target_date: Date to update
            daily_prediction: DailyPrediction with actual prices
        """
        predictions = AIPredictionService.get_unique_predictions_for_date(db, target_date)
        
        for pred in predictions:
            # Get actual price for this checkpoint
            actual_price = None
            if pred.checkpoint == "open" and daily_prediction.open is not None:
                actual_price = daily_prediction.open
            elif pred.checkpoint == "noon" and daily_prediction.noon is not None:
                actual_price = daily_prediction.noon
            elif pred.checkpoint == "twoPM" and daily_prediction.twoPM is not None:
                actual_price = daily_prediction.twoPM
            elif pred.checkpoint == "close" and daily_prediction.close is not None:
                actual_price = daily_prediction.close
            
            # Update if we have actual price and haven't updated before
            if actual_price is not None and pred.actual_price is None:
                pred.actual_price = actual_price
                pred.prediction_error = abs(pred.predicted_price - actual_price)
                db.add(pred)
        
        db.flush()