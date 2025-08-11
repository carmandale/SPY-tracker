import { z } from 'zod'

/**
 * Validation schema for morning prediction form
 * Based on SPY TA Tracker PRD requirements
 */
export const PredictionFormSchema = z.object({
  predLow: z
    .number({ required_error: 'Predicted low is required' })
    .min(0, 'Must be greater than 0')
    .max(1000, 'Must be less than 1000')
    .multipleOf(0.01, 'Must be a valid price (2 decimal places)'),
  
  predHigh: z
    .number({ required_error: 'Predicted high is required' })
    .min(0, 'Must be greater than 0')
    .max(1000, 'Must be less than 1000')
    .multipleOf(0.01, 'Must be a valid price (2 decimal places)'),
  
  bias: z.enum(['Up', 'Neutral', 'Down'], {
    required_error: 'Please select a bias'
  }),
  
  volCtx: z.enum(['Low', 'Medium', 'High'], {
    required_error: 'Please select volatility context'
  }),
  
  dayType: z.enum(['Range', 'Trend', 'Reversal'], {
    required_error: 'Please select day type'
  }),
  
  keyLevels: z
    .string()
    .max(200, 'Key levels must be 200 characters or less')
    .optional(),
  
  notes: z
    .string()
    .max(500, 'Notes must be 500 characters or less')
    .optional()
}).refine((data) => data.predHigh > data.predLow, {
  message: 'Predicted high must be greater than predicted low',
  path: ['predHigh']
})

export type PredictionFormData = z.infer<typeof PredictionFormSchema>

/**
 * Default values for the prediction form
 */
export const defaultPredictionValues: Partial<PredictionFormData> = {
  bias: 'Neutral',
  volCtx: 'Medium',
  dayType: 'Range',
  keyLevels: '',
  notes: ''
}