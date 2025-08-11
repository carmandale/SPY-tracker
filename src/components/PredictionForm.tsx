import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion } from 'framer-motion'
import { Save, TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle } from 'lucide-react'
import { PredictionFormSchema, PredictionFormData, defaultPredictionValues } from '@/lib/schemas'

interface PredictionFormProps {
  onSubmit: (data: PredictionFormData) => Promise<void>
  isLoading?: boolean
  onSuccess?: () => void
}

export function PredictionForm({ onSubmit, isLoading = false, onSuccess }: PredictionFormProps) {
  const [showSuccess, setShowSuccess] = React.useState(false)

  const form = useForm<PredictionFormData>({
    resolver: zodResolver(PredictionFormSchema),
    defaultValues: defaultPredictionValues
  })

  const handleSubmit = async (data: PredictionFormData) => {
    try {
      await onSubmit(data)
      setShowSuccess(true)
      onSuccess?.()
      
      // Hide success message after 2 seconds (PRD requirement)
      setTimeout(() => setShowSuccess(false), 2000)
      
      // Reset form
      form.reset(defaultPredictionValues)
    } catch (error) {
      console.error('Error submitting prediction:', error)
      // Error handling will be added in API integration task
    }
  }

  const getCurrentTime = () => {
    return new Date().toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'America/Chicago'
    })
  }

  const biasOptions = [
    {
      value: 'Down' as const,
      label: 'Down',
      icon: TrendingDown,
      color: 'text-[#DC2626]'
    },
    {
      value: 'Neutral' as const,
      label: 'Neutral', 
      icon: Minus,
      color: 'text-[#A7B3C5]'
    },
    {
      value: 'Up' as const,
      label: 'Up',
      icon: TrendingUp,
      color: 'text-[#16A34A]'
    }
  ]

  const volCtxOptions = [
    { value: 'Low' as const, label: 'Low' },
    { value: 'Medium' as const, label: 'Medium' },
    { value: 'High' as const, label: 'High' }
  ]

  const dayTypeOptions = [
    { value: 'Range' as const, label: 'Range' },
    { value: 'Trend' as const, label: 'Trend' },
    { value: 'Reversal' as const, label: 'Reversal' }
  ]

  const predLow = form.watch('predLow')
  const predHigh = form.watch('predHigh')
  const showRangeCalculation = predLow && predHigh && predHigh > predLow

  return (
    <div className="p-4 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-xl font-semibold mb-2">Daily Prediction</h1>
        <p className="text-sm text-[#A7B3C5]">
          {new Date().toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'long',
            day: 'numeric',
            timeZone: 'America/Chicago'
          })} • {getCurrentTime()} CST
        </p>
      </div>

      {/* Success Toast */}
      {showSuccess && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          className="fixed top-20 left-4 right-4 z-50 bg-[#16A34A] text-white rounded-xl p-4 flex items-center gap-3"
        >
          <CheckCircle className="w-5 h-5" />
          <span className="font-medium">Prediction saved successfully!</span>
        </motion.div>
      )}

      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        {/* Price Range */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-[#12161D] rounded-xl p-4 border border-white/8"
        >
          <h2 className="text-lg font-semibold mb-4">Price Range</h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
                Predicted Low
              </label>
              <input
                type="number"
                step="0.01"
                {...form.register('predLow', { valueAsNumber: true })}
                className={`w-full bg-[#0B0D12] border rounded-lg px-3 py-3 text-lg font-mono focus:outline-none focus:ring-2 focus:ring-[#006072] transition-colors ${
                  form.formState.errors.predLow ? 'border-[#DC2626]' : 'border-white/8'
                }`}
                placeholder="582.50"
              />
              {form.formState.errors.predLow && (
                <p className="text-xs text-[#DC2626] mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {form.formState.errors.predLow.message}
                </p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
                Predicted High
              </label>
              <input
                type="number"
                step="0.01"
                {...form.register('predHigh', { valueAsNumber: true })}
                className={`w-full bg-[#0B0D12] border rounded-lg px-3 py-3 text-lg font-mono focus:outline-none focus:ring-2 focus:ring-[#006072] transition-colors ${
                  form.formState.errors.predHigh ? 'border-[#DC2626]' : 'border-white/8'
                }`}
                placeholder="587.25"
              />
              {form.formState.errors.predHigh && (
                <p className="text-xs text-[#DC2626] mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {form.formState.errors.predHigh.message}
                </p>
              )}
            </div>
          </div>

          {/* Range Calculation */}
          {showRangeCalculation && (
            <div className="mt-4 p-3 bg-[#0B0D12] rounded-lg">
              <p className="text-sm text-[#A7B3C5]">
                Range: <span className="font-mono font-bold text-[#E8ECF2]">
                  ${(predHigh - predLow).toFixed(2)}
                </span> ({((predHigh - predLow) / predLow * 100).toFixed(2)}%)
              </p>
            </div>
          )}
        </motion.div>

        {/* Bias Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-[#12161D] rounded-xl p-4 border border-white/8"
        >
          <h2 className="text-lg font-semibold mb-4">Market Bias</h2>
          
          <div className="grid grid-cols-3 gap-2">
            {biasOptions.map((option) => {
              const Icon = option.icon
              const isSelected = form.watch('bias') === option.value
              return (
                <motion.button
                  key={option.value}
                  type="button"
                  onClick={() => form.setValue('bias', option.value)}
                  whileTap={{ scale: 0.98 }}
                  className={`p-3 rounded-lg border transition-all ${
                    isSelected
                      ? 'border-[#006072] bg-[#006072]/10'
                      : 'border-white/8 hover:border-white/20'
                  }`}
                >
                  <Icon className={`w-5 h-5 mx-auto mb-2 ${option.color}`} />
                  <span className="text-sm font-medium">{option.label}</span>
                </motion.button>
              )
            })}
          </div>
          {form.formState.errors.bias && (
            <p className="text-xs text-[#DC2626] mt-2 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {form.formState.errors.bias.message}
            </p>
          )}
        </motion.div>

        {/* Context & Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-[#12161D] rounded-xl p-4 border border-white/8 space-y-4"
        >
          <h2 className="text-lg font-semibold">Context & Details</h2>
          
          {/* Volatility Context */}
          <div>
            <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
              Volatility Context
            </label>
            <div className="grid grid-cols-3 gap-2">
              {volCtxOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => form.setValue('volCtx', option.value)}
                  className={`p-2 rounded-lg border text-sm transition-all ${
                    form.watch('volCtx') === option.value
                      ? 'border-[#006072] bg-[#006072]/10 text-[#006072]'
                      : 'border-white/8 text-[#A7B3C5] hover:border-white/20'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
            {form.formState.errors.volCtx && (
              <p className="text-xs text-[#DC2626] mt-1 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {form.formState.errors.volCtx.message}
              </p>
            )}
          </div>

          {/* Day Type */}
          <div>
            <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
              Day Type
            </label>
            <div className="grid grid-cols-3 gap-2">
              {dayTypeOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => form.setValue('dayType', option.value)}
                  className={`p-2 rounded-lg border text-sm transition-all ${
                    form.watch('dayType') === option.value
                      ? 'border-[#006072] bg-[#006072]/10 text-[#006072]'
                      : 'border-white/8 text-[#A7B3C5] hover:border-white/20'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
            {form.formState.errors.dayType && (
              <p className="text-xs text-[#DC2626] mt-1 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {form.formState.errors.dayType.message}
              </p>
            )}
          </div>

          {/* Key Levels */}
          <div>
            <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
              Key Levels
            </label>
            <input
              type="text"
              {...form.register('keyLevels')}
              className={`w-full bg-[#0B0D12] border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#006072] transition-colors ${
                form.formState.errors.keyLevels ? 'border-[#DC2626]' : 'border-white/8'
              }`}
              placeholder="e.g., 580 support, 590 resistance"
              maxLength={200}
            />
            {form.formState.errors.keyLevels && (
              <p className="text-xs text-[#DC2626] mt-1 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {form.formState.errors.keyLevels.message}
              </p>
            )}
            <p className="text-xs text-[#A7B3C5] mt-1">
              {form.watch('keyLevels')?.length || 0}/200 characters
            </p>
          </div>
        </motion.div>

        {/* Notes */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-[#12161D] rounded-xl p-4 border border-white/8"
        >
          <label className="block text-lg font-semibold mb-2">
            Analysis Notes
          </label>
          <textarea
            {...form.register('notes')}
            rows={4}
            className={`w-full bg-[#0B0D12] border rounded-lg px-3 py-3 focus:outline-none focus:ring-2 focus:ring-[#006072] transition-colors resize-none ${
              form.formState.errors.notes ? 'border-[#DC2626]' : 'border-white/8'
            }`}
            placeholder="Describe your analysis, key factors, and reasoning for this prediction..."
            maxLength={500}
          />
          {form.formState.errors.notes && (
            <p className="text-xs text-[#DC2626] mt-1 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {form.formState.errors.notes.message}
            </p>
          )}
          <p className="text-xs text-[#A7B3C5] mt-1">
            {form.watch('notes')?.length || 0}/500 characters
          </p>
        </motion.div>

        {/* Save Button */}
        <motion.button
          type="submit"
          disabled={isLoading || form.formState.isSubmitting}
          whileTap={{ scale: 0.98 }}
          className="w-full bg-[#006072] text-white py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {(isLoading || form.formState.isSubmitting) ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            >
              <Save className="w-5 h-5" />
            </motion.div>
          ) : (
            <Save className="w-5 h-5" />
          )}
          {(isLoading || form.formState.isSubmitting) ? 'Saving Prediction...' : 'Save Prediction'}
        </motion.button>
      </form>
    </div>
  )
}