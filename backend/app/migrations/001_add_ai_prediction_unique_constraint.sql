-- Migration: Add unique constraint to prevent duplicate AI predictions
-- Purpose: Ensure only one AI prediction per date/checkpoint combination
-- Date: 2025-01-08

-- Step 1: Remove existing duplicates before adding constraint
DELETE FROM ai_predictions 
WHERE id NOT IN (
    -- Keep only the most recent prediction for each date/checkpoint
    SELECT MAX(id) 
    FROM ai_predictions 
    GROUP BY date, checkpoint
);

-- Step 2: Add unique constraint 
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_predictions_date_checkpoint 
ON ai_predictions(date, checkpoint);

-- Step 3: Verify constraint works
-- This should fail if constraint is working:
-- INSERT INTO ai_predictions (date, checkpoint, predicted_price, confidence) 
-- VALUES ('2025-01-01', 'open', 500.0, 0.8), ('2025-01-01', 'open', 501.0, 0.8);