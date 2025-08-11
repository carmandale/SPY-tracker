import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Save, TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle } from 'lucide-react';
interface PredictionForm {
  low: string;
  high: string;
  bias: 'bullish' | 'bearish' | 'neutral';
  volumeContext: string;
  dayType: 'opex' | 'fomc' | 'earnings' | 'normal';
  keyLevels: string;
  notes: string;
  preMarket: boolean;
}
export function PredictScreen() {
  const [form, setForm] = useState<PredictionForm>({
    low: '',
    high: '',
    bias: 'neutral',
    volumeContext: '',
    dayType: 'normal',
    keyLevels: '',
    notes: '',
    preMarket: false
  });
  const [errors, setErrors] = useState<Partial<PredictionForm>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const biasOptions = [{
    value: 'bearish',
    label: 'Bearish',
    icon: TrendingDown,
    color: 'text-[#DC2626]'
  }, {
    value: 'neutral',
    label: 'Neutral',
    icon: Minus,
    color: 'text-[#A7B3C5]'
  }, {
    value: 'bullish',
    label: 'Bullish',
    icon: TrendingUp,
    color: 'text-[#16A34A]'
  }] as const;
  const dayTypeOptions = [{
    value: 'normal',
    label: 'Normal'
  }, {
    value: 'opex',
    label: 'OpEx'
  }, {
    value: 'fomc',
    label: 'FOMC'
  }, {
    value: 'earnings',
    label: 'Earnings'
  }] as const;
  const validateForm = (): boolean => {
    const newErrors: Partial<PredictionForm> = {};
    if (!form.low || isNaN(Number(form.low))) {
      newErrors.low = 'Valid low price required';
    }
    if (!form.high || isNaN(Number(form.high))) {
      newErrors.high = 'Valid high price required';
    }
    if (form.low && form.high && Number(form.low) >= Number(form.high)) {
      newErrors.high = 'High must be greater than low';
    }
    if (!form.notes.trim()) {
      newErrors.notes = 'Notes are required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  const handleSave = async () => {
    if (!validateForm()) return;
    setIsSaving(true);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsSaving(false);
    setShowSuccess(true);

    // Hide success message after 3 seconds
    setTimeout(() => setShowSuccess(false), 3000);

    // Reset form
    setForm({
      low: '',
      high: '',
      bias: 'neutral',
      volumeContext: '',
      dayType: 'normal',
      keyLevels: '',
      notes: '',
      preMarket: false
    });
  };
  const getCurrentTime = () => {
    return new Date().toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'America/Chicago'
    });
  };
  return <div className="p-4 space-y-6">
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
      {showSuccess && <motion.div initial={{
      opacity: 0,
      y: -50
    }} animate={{
      opacity: 1,
      y: 0
    }} exit={{
      opacity: 0,
      y: -50
    }} className="fixed top-20 left-4 right-4 z-50 bg-[#16A34A] text-white rounded-xl p-4 flex items-center gap-3">
          <CheckCircle className="w-5 h-5" />
          <span className="font-medium">Prediction saved successfully!</span>
        </motion.div>}

      {/* Price Range */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <h2 className="text-lg font-semibold mb-4">Price Range</h2>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
              Low Price
            </label>
            <input type="number" step="0.01" value={form.low} onChange={e => setForm(prev => ({
            ...prev,
            low: e.target.value
          }))} className={`w-full bg-[#0B0D12] border rounded-lg px-3 py-3 text-lg font-mono focus:outline-none focus:ring-2 focus:ring-[#006072] transition-colors ${errors.low ? 'border-[#DC2626]' : 'border-white/8'}`} placeholder="582.50" />
            {errors.low && <p className="text-xs text-[#DC2626] mt-1 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.low}
              </p>}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
              High Price
            </label>
            <input type="number" step="0.01" value={form.high} onChange={e => setForm(prev => ({
            ...prev,
            high: e.target.value
          }))} className={`w-full bg-[#0B0D12] border rounded-lg px-3 py-3 text-lg font-mono focus:outline-none focus:ring-2 focus:ring-[#006072] transition-colors ${errors.high ? 'border-[#DC2626]' : 'border-white/8'}`} placeholder="587.25" />
            {errors.high && <p className="text-xs text-[#DC2626] mt-1 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.high}
              </p>}
          </div>
        </div>

        {form.low && form.high && Number(form.high) > Number(form.low) && <div className="mt-4 p-3 bg-[#0B0D12] rounded-lg">
            <p className="text-sm text-[#A7B3C5]">
              Range: <span className="font-mono font-bold text-[#E8ECF2]">
                ${(Number(form.high) - Number(form.low)).toFixed(2)}
              </span> ({((Number(form.high) - Number(form.low)) / Number(form.low) * 100).toFixed(2)}%)
            </p>
          </div>}
      </motion.div>

      {/* Bias Selection */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.1
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <h2 className="text-lg font-semibold mb-4">Market Bias</h2>
        
        <div className="grid grid-cols-3 gap-2">
          {biasOptions.map(option => {
          const Icon = option.icon;
          const isSelected = form.bias === option.value;
          return <motion.button key={option.value} onClick={() => setForm(prev => ({
            ...prev,
            bias: option.value
          }))} whileTap={{
            scale: 0.98
          }} className={`p-3 rounded-lg border transition-all ${isSelected ? 'border-[#006072] bg-[#006072]/10' : 'border-white/8 hover:border-white/20'}`}>
                <Icon className={`w-5 h-5 mx-auto mb-2 ${option.color}`} />
                <span className="text-sm font-medium">{option.label}</span>
              </motion.button>;
        })}
        </div>
      </motion.div>

      {/* Context & Details */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.2
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8 space-y-4">
        <h2 className="text-lg font-semibold">Context & Details</h2>
        
        {/* Day Type */}
        <div>
          <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
            Day Type
          </label>
          <div className="grid grid-cols-2 gap-2">
            {dayTypeOptions.map(option => <button key={option.value} onClick={() => setForm(prev => ({
            ...prev,
            dayType: option.value
          }))} className={`p-2 rounded-lg border text-sm transition-all ${form.dayType === option.value ? 'border-[#006072] bg-[#006072]/10 text-[#006072]' : 'border-white/8 text-[#A7B3C5] hover:border-white/20'}`}>
                {option.label}
              </button>)}
          </div>
        </div>

        {/* Volume Context */}
        <div>
          <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
            Volume Context
          </label>
          <input type="text" value={form.volumeContext} onChange={e => setForm(prev => ({
          ...prev,
          volumeContext: e.target.value
        }))} className="w-full bg-[#0B0D12] border border-white/8 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#006072] transition-colors" placeholder="e.g., Low volume expected, Holiday week" />
        </div>

        {/* Key Levels */}
        <div>
          <label className="block text-sm font-medium text-[#A7B3C5] mb-2">
            Key Levels
          </label>
          <input type="text" value={form.keyLevels} onChange={e => setForm(prev => ({
          ...prev,
          keyLevels: e.target.value
        }))} className="w-full bg-[#0B0D12] border border-white/8 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#006072] transition-colors" placeholder="e.g., 580 support, 590 resistance" />
        </div>

        {/* Pre-market Toggle */}
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-[#A7B3C5]">
            Pre-market Analysis
          </label>
          <button onClick={() => setForm(prev => ({
          ...prev,
          preMarket: !prev.preMarket
        }))} className={`relative w-12 h-6 rounded-full transition-colors ${form.preMarket ? 'bg-[#006072]' : 'bg-white/20'}`}>
            <motion.div animate={{
            x: form.preMarket ? 24 : 2
          }} transition={{
            type: "spring",
            stiffness: 500,
            damping: 30
          }} className="absolute top-1 w-4 h-4 bg-white rounded-full" />
          </button>
        </div>
      </motion.div>

      {/* Notes */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.3
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <label className="block text-lg font-semibold mb-2">
          Analysis Notes
        </label>
        <textarea value={form.notes} onChange={e => setForm(prev => ({
        ...prev,
        notes: e.target.value
      }))} rows={4} className={`w-full bg-[#0B0D12] border rounded-lg px-3 py-3 focus:outline-none focus:ring-2 focus:ring-[#006072] transition-colors resize-none ${errors.notes ? 'border-[#DC2626]' : 'border-white/8'}`} placeholder="Describe your analysis, key factors, and reasoning for this prediction..." />
        {errors.notes && <p className="text-xs text-[#DC2626] mt-1 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            {errors.notes}
          </p>}
      </motion.div>

      {/* Save Button */}
      <motion.button onClick={handleSave} disabled={isSaving} whileTap={{
      scale: 0.98
    }} className="w-full bg-[#006072] text-white py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed">
        {isSaving ? <motion.div animate={{
        rotate: 360
      }} transition={{
        duration: 1,
        repeat: Infinity,
        ease: "linear"
      }}>
            <Save className="w-5 h-5" />
          </motion.div> : <Save className="w-5 h-5" />}
        {isSaving ? 'Saving Prediction...' : 'Save Prediction'}
      </motion.button>
    </div>;
}