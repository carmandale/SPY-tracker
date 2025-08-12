#!/usr/bin/env python3
"""
Script to clean up duplicate AI predictions in the database.
Keeps only the most recent prediction for each date+checkpoint combination.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.database import SessionLocal
from backend.app.models import AIPrediction
from sqlalchemy import desc

def cleanup_duplicate_predictions():
    """Remove duplicate AI predictions, keeping only the most recent for each date+checkpoint."""
    db = SessionLocal()
    
    try:
        # Get all predictions ordered by date and checkpoint
        all_predictions = db.query(AIPrediction).order_by(
            AIPrediction.date, 
            AIPrediction.checkpoint,
            desc(AIPrediction.id)
        ).all()
        
        seen = set()
        duplicates_removed = 0
        
        for pred in all_predictions:
            key = (pred.date, pred.checkpoint)
            
            if key in seen:
                # This is a duplicate - remove it
                db.delete(pred)
                duplicates_removed += 1
                print(f"Removing duplicate: {pred.date} - {pred.checkpoint} (ID: {pred.id})")
            else:
                # First occurrence - keep it
                seen.add(key)
        
        if duplicates_removed > 0:
            db.commit()
            print(f"\n✅ Removed {duplicates_removed} duplicate predictions")
        else:
            print("✅ No duplicate predictions found")
            
    except Exception as e:
        print(f"❌ Error cleaning duplicates: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicate_predictions()