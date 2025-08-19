-- Migration to add prompt_version column to ai_predictions table
-- This fixes the 500 errors on /ai/predictions/* endpoints

ALTER TABLE ai_predictions 
ADD COLUMN IF NOT EXISTS prompt_version VARCHAR(50);

-- Set a default value for existing rows
UPDATE ai_predictions 
SET prompt_version = 'v1.0.0' 
WHERE prompt_version IS NULL;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_ai_predictions_prompt_version 
ON ai_predictions(prompt_version);