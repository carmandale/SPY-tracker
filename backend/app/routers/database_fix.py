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