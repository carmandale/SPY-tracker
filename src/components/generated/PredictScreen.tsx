import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, TrendingUp, TrendingDown, Minus } from 'lucide-react';
interface PredictionData {
  predictedLow: number;
  predictedHigh: number;
  bias: 'up' | 'neutral' | 'down';
  volatilityContext: string;
  dayType: string;
  notes: string;
  date: Date;
}
interface PredictScreenProps {
  currentPrice: number;
  onSavePrediction: (prediction: PredictionData) => void;
  existingPrediction: PredictionData | null;
}
export function PredictScreen({
  currentPrice,
  onSavePrediction,
  existingPrediction
}: PredictScreenProps) {
  const [formData, setFormData] = useState({
    predictedLow: '',
    predictedHigh: '',
    bias: 'neutral' as 'up' | 'neutral' | 'down',
    volatilityContext: 'normal',
    dayType: 'regular',
    notes: ''
  });
  useEffect(() => {
    if (existingPrediction) {
      setFormData({
        predictedLow: existingPrediction.predictedLow.toString(),
        predictedHigh: existingPrediction.predictedHigh.toString(),
        bias: existingPrediction.bias,
        volatilityContext: existingPrediction.volatilityContext,
        dayType: existingPrediction.dayType,
        notes: existingPrediction.notes
      });
    }
  }, [existingPrediction]);
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const prediction: PredictionData = {
      predictedLow: parseFloat(formData.predictedLow),
      predictedHigh: parseFloat(formData.predictedHigh),
      bias: formData.bias,
      volatilityContext: formData.volatilityContext,
      dayType: formData.dayType,
      notes: formData.notes,
      date: new Date()
    };
    onSavePrediction(prediction);
  };
  const biasOptions = [{
    value: 'up',
    label: 'Up',
    icon: TrendingUp,
    color: 'text-green-400 border-green-400'
  }, {
    value: 'neutral',
    label: 'Neutral',
    icon: Minus,
    color: 'text-blue-400 border-blue-400'
  }, {
    value: 'down',
    label: 'Down',
    icon: TrendingDown,
    color: 'text-red-400 border-red-400'
  }] as any[];
  const volatilityOptions = [{
    value: 'low',
    label: 'Low Vol'
  }, {
    value: 'normal',
    label: 'Normal Vol'
  }, {
    value: 'high',
    label: 'High Vol'
  }, {
    value: 'extreme',
    label: 'Extreme Vol'
  }] as any[];
  const dayTypeOptions = [{
    value: 'regular',
    label: 'Regular Day'
  }, {
    value: 'opex',
    label: 'OPEX'
  }, {
    value: 'fomc',
    label: 'FOMC'
  }, {
    value: 'earnings',
    label: 'Earnings Heavy'
  }, {
    value: 'holiday',
    label: 'Holiday'
  }] as any[];
  return <div className="p-4 space-y-6">
      {/* Pre-market Price Display */}
      <section className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <h2 className="text-lg font-semibold text-gray-200 mb-2">Pre-Market SPY</h2>
        <div className="text-2xl font-mono font-bold text-green-400">
          ${currentPrice.toFixed(2)}
        </div>
        <div className="text-sm text-gray-400 mt-1">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </section>

      {/* Morning Prediction Form */}
      <section>
        <h2 className="text-lg font-semibold text-gray-200 mb-4">Morning Prediction</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Predicted Range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="predictedLow" className="block text-sm font-medium text-gray-300 mb-2">
                Predicted Low
              </label>
              <input type="number" id="predictedLow" step="0.01" value={formData.predictedLow} onChange={e => setFormData(prev => ({
              ...prev,
              predictedLow: e.target.value
            }))} className="w-full px-3 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent touch-manipulation" placeholder="580.00" required />
            </div>
            <div>
              <label htmlFor="predictedHigh" className="block text-sm font-medium text-gray-300 mb-2">
                Predicted High
              </label>
              <input type="number" id="predictedHigh" step="0.01" value={formData.predictedHigh} onChange={e => setFormData(prev => ({
              ...prev,
              predictedHigh: e.target.value
            }))} className="w-full px-3 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent touch-manipulation" placeholder="590.00" required />
            </div>
          </div>

          {/* Bias Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">Directional Bias</label>
            <div className="grid grid-cols-3 gap-3">
              {biasOptions.map(option => {
              const Icon = option.icon;
              return <motion.button key={option.value} type="button" whileTap={{
                scale: 0.98
              }} onClick={() => setFormData(prev => ({
                ...prev,
                bias: option.value as any
              }))} className={`p-3 rounded-lg border-2 transition-colors touch-manipulation ${formData.bias === option.value ? `${option.color} bg-gray-700` : 'border-gray-600 text-gray-400 hover:border-gray-500'}`}>
                    <Icon className="w-5 h-5 mx-auto mb-1" />
                    <div className="text-sm font-medium">{option.label}</div>
                  </motion.button>;
            })}
            </div>
          </div>

          {/* Volatility Context */}
          <div>
            <label htmlFor="volatilityContext" className="block text-sm font-medium text-gray-300 mb-2">
              Volatility Context
            </label>
            <select id="volatilityContext" value={formData.volatilityContext} onChange={e => setFormData(prev => ({
            ...prev,
            volatilityContext: e.target.value
          }))} className="w-full px-3 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent touch-manipulation">
              {volatilityOptions.map(option => <option key={option.value} value={option.value}>
                  {option.label}
                </option>)}
            </select>
          </div>

          {/* Day Type */}
          <div>
            <label htmlFor="dayType" className="block text-sm font-medium text-gray-300 mb-2">
              Day Type
            </label>
            <select id="dayType" value={formData.dayType} onChange={e => setFormData(prev => ({
            ...prev,
            dayType: e.target.value
          }))} className="w-full px-3 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent touch-manipulation">
              {dayTypeOptions.map(option => <option key={option.value} value={option.value}>
                  {option.label}
                </option>)}
            </select>
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-300 mb-2">
              Notes
            </label>
            <textarea id="notes" rows={3} value={formData.notes} onChange={e => setFormData(prev => ({
            ...prev,
            notes: e.target.value
          }))} className="w-full px-3 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none touch-manipulation" placeholder="Additional context, market conditions, etc..." />
          </div>

          {/* Save Button */}
          <motion.button type="submit" whileTap={{
          scale: 0.98
        }} className="w-full flex items-center justify-center space-x-2 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold text-white transition-colors touch-manipulation">
            <Save className="w-5 h-5" />
            <span>Save Prediction</span>
          </motion.button>
        </form>
      </section>
    </div>;
}