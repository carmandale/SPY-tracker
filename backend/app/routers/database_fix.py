"""
Emergency database fix endpoint to add missing prompt_version column.
This will be deployed to production and executed once to fix the schema.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from ..database import SessionLocal
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/fix-prompt-version-column")
def fix_prompt_version_column():
    """
    Emergency endpoint to add the missing prompt_version column to ai_predictions table.
    This fixes the 500 errors on /ai/predictions/* endpoints.
    """
    db = SessionLocal()
    try:
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ai_predictions' 
            AND column_name = 'prompt_version'
        """)
        
        result = db.execute(check_query).fetchone()
        
        if result:
            return {
                "status": "already_exists",
                "message": "Column 'prompt_version' already exists in ai_predictions table"
            }
        
        # Add the column
        alter_query = text("""
            ALTER TABLE ai_predictions 
            ADD COLUMN prompt_version VARCHAR(50)
        """)
        
        db.execute(alter_query)
        db.commit()
        
        # Verify it was added
        verify_result = db.execute(check_query).fetchone()
        
        if verify_result:
            # Get all columns for confirmation
            all_columns_query = text("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = 'ai_predictions'
                ORDER BY ordinal_position
            """)
            
            columns = db.execute(all_columns_query).fetchall()
            column_list = [{"name": col[0], "type": col[1]} for col in columns]
            
            return {
                "status": "success",
                "message": "Column 'prompt_version' added successfully",
                "columns": column_list
            }
        else:
            raise Exception("Failed to verify column creation")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add prompt_version column: {e}")
        raise HTTPException(status_code=500, detail=f"Database fix failed: {str(e)}")
    finally:
        db.close()

@router.get("/check-ai-predictions-schema")
def check_ai_predictions_schema():
    """Check the current schema of ai_predictions table."""
    db = SessionLocal()
    try:
        query = text("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'ai_predictions'
            ORDER BY ordinal_position
        """)
        
        columns = db.execute(query).fetchall()
        
        if not columns:
            return {
                "status": "error",
                "message": "Table 'ai_predictions' not found",
                "columns": []
            }
        
        column_list = [
            {
                "name": col[0],
                "type": col[1],
                "max_length": col[2],
                "nullable": col[3] == "YES"
            }
            for col in columns
        ]
        
        has_prompt_version = any(col["name"] == "prompt_version" for col in column_list)
        
        return {
            "status": "success",
            "has_prompt_version": has_prompt_version,
            "columns": column_list,
            "message": f"prompt_version column {'exists' if has_prompt_version else 'is MISSING'}"
        }
        
    except Exception as e:
        logger.error(f"Failed to check schema: {e}")
        raise HTTPException(status_code=500, detail=f"Schema check failed: {str(e)}")
    finally:
        db.close()


@router.post("/fix-weekend-data")
def fix_weekend_data():
    """Remove any predictions that are on weekends (Saturday=5, Sunday=6)."""
    db = SessionLocal()
    try:
        # PostgreSQL-specific query to find weekend data
        find_weekend_query = text("""
            SELECT id, date, EXTRACT(DOW FROM date) as day_of_week
            FROM daily_predictions
            WHERE EXTRACT(DOW FROM date) IN (0, 6)
        """)
        
        weekend_records = db.execute(find_weekend_query).fetchall()
        
        if not weekend_records:
            return {
                "status": "success",
                "message": "No weekend data found",
                "deleted_count": 0
            }
        
        # Delete weekend records
        delete_query = text("""
            DELETE FROM daily_predictions
            WHERE EXTRACT(DOW FROM date) IN (0, 6)
        """)
        
        result = db.execute(delete_query)
        deleted_count = result.rowcount
        
        # Also delete AI predictions for weekend dates
        delete_ai_query = text("""
            DELETE FROM ai_predictions
            WHERE EXTRACT(DOW FROM date) IN (0, 6)
        """)
        
        ai_result = db.execute(delete_ai_query)
        ai_deleted_count = ai_result.rowcount
        
        db.commit()
        
        deleted_dates = [{"id": r[0], "date": str(r[1]), "day_of_week": int(r[2])} for r in weekend_records]
        
        return {
            "status": "success",
            "message": f"Deleted {deleted_count} weekend predictions and {ai_deleted_count} AI predictions",
            "deleted_predictions": deleted_count,
            "deleted_ai_predictions": ai_deleted_count,
            "deleted_dates": deleted_dates
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to fix weekend data: {e}")
        raise HTTPException(status_code=500, detail=f"Weekend data fix failed: {str(e)}")
    finally:
        db.close()


@router.post("/clear-future-prices")
def clear_future_prices():
    """Clear any prices that shouldn't exist yet based on current time."""
    from datetime import datetime
    from ..timezone_utils import get_ny_now
    
    db = SessionLocal()
    try:
        # Get current time in ET
        now_et = get_ny_now()
        today = now_et.date()
        current_hour = now_et.hour
        current_minute = now_et.minute
        
        updates = []
        
        # Clear today's future prices based on ET time
        if current_hour < 16 or (current_hour == 16 and current_minute < 0):  # Before 4 PM ET
            update = text("UPDATE daily_predictions SET close = NULL WHERE date = :date")
            result = db.execute(update, {"date": today})
            if result.rowcount > 0:
                updates.append(f"Cleared close price for {today} (before 4 PM ET)")
        
        if current_hour < 15:  # Before 3 PM ET
            update = text("UPDATE daily_predictions SET \"twoPM\" = NULL WHERE date = :date")
            result = db.execute(update, {"date": today})
            if result.rowcount > 0:
                updates.append(f"Cleared 2PM price for {today} (before 3 PM ET)")
        
        if current_hour < 13:  # Before 1 PM ET
            update = text("UPDATE daily_predictions SET noon = NULL WHERE date = :date")
            result = db.execute(update, {"date": today})
            if result.rowcount > 0:
                updates.append(f"Cleared noon price for {today} (before 1 PM ET)")
        
        if current_hour < 9 or (current_hour == 9 and current_minute < 30):  # Before 9:30 AM ET
            update = text("UPDATE daily_predictions SET open = NULL WHERE date = :date")
            result = db.execute(update, {"date": today})
            if result.rowcount > 0:
                updates.append(f"Cleared open price for {today} (before 9:30 AM ET)")
        
        # Clear all prices for future dates
        future_update = text("""
            UPDATE daily_predictions 
            SET open = NULL, noon = NULL, "twoPM" = NULL, close = NULL
            WHERE date > :date
        """)
        future_result = db.execute(future_update, {"date": today})
        if future_result.rowcount > 0:
            updates.append(f"Cleared all prices for {future_result.rowcount} future dates")
        
        db.commit()
        
        return {
            "status": "success",
            "current_time_et": now_et.isoformat(),
            "updates": updates,
            "update_count": len(updates)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear future prices: {e}")
        raise HTTPException(status_code=500, detail=f"Clear future prices failed: {str(e)}")
    finally:
        db.close()