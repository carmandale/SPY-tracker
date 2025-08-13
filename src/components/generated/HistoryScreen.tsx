import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Calendar, Target, CheckCircle, XCircle, Filter, Activity, Clock } from 'lucide-react';
import { api } from '../../utils/apiClient';

interface CheckpointData {
  checkpoint: string;
  predicted_price: number;
  actual_price: number | null;
  confidence: number;
  reasoning: string;
  prediction_error: number | null;
}

interface HistoricalPrediction {
  id: string;
  date: string;
  low: number;
  high: number;
  bias: 'bullish' | 'bearish' | 'neutral';
  actualLow: number;
  actualHigh: number;
  rangeHit: boolean;
  notes: string;
  dayType: 'opex' | 'fomc' | 'earnings' | 'normal';
  error: number;
  source?: 'ai' | 'manual' | 'ai_simulation';
  // Checkpoint prices from DailyPrediction
  open?: number;
  noon?: number;
  twoPM?: number;
  close?: number;
  // AI Prediction data for detailed breakdown
  aiPredictions?: CheckpointData[];
}
type FilterType = 'all' | 'hits' | 'misses' | 'week' | 'month';
export function HistoryScreen() {
  const [filter, setFilter] = useState<FilterType>('all');
  const [expandedCard, setExpandedCard] = useState<string | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalPrediction[]>([]);

  useEffect(() => {
    // Fetch historical data from new history endpoint
    const load = async () => {
      try {
        const data = await api.getHistory(20, 0);
        
        // Process items and fetch AI prediction data
        const items: HistoricalPrediction[] = await Promise.all(
          data.items.map(async (item: any) => {
            let aiPredictions: CheckpointData[] = [];
            
            // Fetch AI predictions for this date if source is AI
            if (item.source === 'ai' || item.source === 'ai_simulation') {
              try {
                const aiResp = await fetch(`http://localhost:8000/ai/predictions/${item.date}`);
                if (aiResp.ok) {
                  const aiData = await aiResp.json();
                  aiPredictions = aiData.predictions.map((pred: any) => ({
                    checkpoint: pred.checkpoint,
                    predicted_price: pred.predicted_price,
                    actual_price: pred.actual_price,
                    confidence: pred.confidence,
                    reasoning: pred.reasoning,
                    prediction_error: pred.prediction_error
                  }));
                }
              } catch (e) {
                console.warn('Failed to fetch AI predictions for', item.date);
              }
            }
            
            return {
              id: String(item.id),
              date: item.date,
              low: item.predLow ?? 0,
              high: item.predHigh ?? 0,
              bias: (item.bias || 'neutral') as any,
              actualLow: item.actualLow ?? 0,
              actualHigh: item.actualHigh ?? 0,
              rangeHit: !!item.rangeHit,
              notes: item.notes || `${item.source === 'ai' ? '🤖 AI prediction' : item.source === 'ai_simulation' ? '🔬 AI simulation' : '📝 Manual prediction'}`,
              dayType: (item.dayType || 'normal') as any,
              error: item.error ?? 0,
              source: item.source,
              open: item.open,
              noon: item.noon,
              twoPM: item.twoPM,
              close: item.close,
              aiPredictions
            };
          })
        );
        
        setHistoricalData(items);
      } catch (e) {
        console.error('Failed to load history', e);
      }
    };
    load();
  }, []);

  // Enhanced static sample data for testing when no real data available
  const staticData: HistoricalPrediction[] = [{
    id: '1',
    date: '2024-01-15',
    low: 582.50,
    high: 587.25,
    bias: 'bullish',
    actualLow: 583.10,
    actualHigh: 586.80,
    rangeHit: true,
    notes: 'Strong support at 582, expecting bounce on Fed news',
    dayType: 'fomc',
    error: 0.45
  }, {
    id: '2',
    date: '2024-01-14',
    low: 578.00,
    high: 583.50,
    bias: 'neutral',
    actualLow: 576.25,
    actualHigh: 584.75,
    rangeHit: false,
    notes: 'Consolidation expected after Friday selloff',
    dayType: 'normal',
    error: 1.75
  }, {
    id: '3',
    date: '2024-01-13',
    low: 575.25,
    high: 580.75,
    bias: 'bearish',
    actualLow: 576.50,
    actualHigh: 579.90,
    rangeHit: true,
    notes: 'Weakness in tech, expecting continued selling',
    dayType: 'normal',
    error: 0.85
  }, {
    id: '4',
    date: '2024-01-12',
    low: 580.00,
    high: 585.00,
    bias: 'bullish',
    actualLow: 582.75,
    actualHigh: 588.25,
    rangeHit: false,
    notes: 'OpEx pin expected around 582.50',
    dayType: 'opex',
    error: 3.25
  }, {
    id: '5',
    date: '2024-01-11',
    low: 577.50,
    high: 582.25,
    bias: 'neutral',
    actualLow: 578.00,
    actualHigh: 581.75,
    rangeHit: true,
    notes: 'Low volume day, tight range expected',
    dayType: 'normal',
    error: 0.25
  }, {
    id: '6',
    date: '2024-01-10',
    low: 574.75,
    high: 579.50,
    bias: 'bearish',
    actualLow: 573.25,
    actualHigh: 578.80,
    rangeHit: true,
    notes: '🤖 AI prediction - Technical breakdown below 575',
    dayType: 'normal',
    error: 0.70
  }, {
    id: '7',
    date: '2024-01-09',
    low: 572.00,
    high: 576.75,
    bias: 'neutral',
    actualLow: 570.50,
    actualHigh: 577.25,
    rangeHit: false,
    notes: '📝 Manual prediction - Range trading expected',
    dayType: 'normal',
    error: 1.50
  }];
  const filterOptions = [{
    value: 'all' as const,
    label: 'All',
    count: historicalData.length
  }, {
    value: 'hits' as const,
    label: 'Hits',
    count: historicalData.filter(d => d.rangeHit).length
  }, {
    value: 'misses' as const,
    label: 'Misses',
    count: historicalData.filter(d => !d.rangeHit).length
  }, {
    value: 'week' as const,
    label: 'This Week',
    count: 5
  }, {
    value: 'month' as const,
    label: 'This Month',
    count: historicalData.length
  }] as any[];
  const filteredData = (historicalData.length ? historicalData : staticData).filter(item => {
    switch (filter) {
      case 'hits':
        return item.rangeHit;
      case 'misses':
        return !item.rangeHit;
      case 'week':
        // Simulate last 7 days
        return true;
      case 'month':
        // Simulate last 30 days
        return true;
      default:
        return true;
    }
  });
  const getBiasIcon = (bias: string) => {
    switch (bias) {
      case 'bullish':
        return <TrendingUp className="w-4 h-4 text-[#16A34A]" />;
      case 'bearish':
        return <TrendingDown className="w-4 h-4 text-[#DC2626]" />;
      default:
        return <Minus className="w-4 h-4 text-[#A7B3C5]" />;
    }
  };
  const getDayTypeBadge = (dayType: string) => {
    const colors = {
      fomc: 'bg-[#DC2626] text-white',
      opex: 'bg-[#006072] text-white',
      earnings: 'bg-[#16A34A] text-white',
      normal: 'bg-white/10 text-[#A7B3C5]'
    };
    return <span className={`px-2 py-1 text-xs rounded-full font-medium ${colors[dayType as keyof typeof colors]}`}>
        {dayType.toUpperCase()}
      </span>;
  };
  const formatDate = (dateString: string) => {
    // Parse as local date to avoid timezone issues
    // "2025-08-11" should be Aug 11, not shifted to Aug 10
    const [year, month, day] = dateString.split('-').map(Number);
    const localDate = new Date(year, month - 1, day);
    return localDate.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };
  const calculateAccuracy = () => {
    const hits = filteredData.filter(d => d.rangeHit).length;
    return Math.round(hits / filteredData.length * 100);
  };
  const calculateAvgError = () => {
    const totalError = filteredData.reduce((sum, d) => sum + d.error, 0);
    return (totalError / filteredData.length).toFixed(2);
  };

  // Trading visualization helpers
  const getCheckpointAccuracy = (prediction: HistoricalPrediction) => {
    if (!prediction.aiPredictions?.length) return [];
    
    return prediction.aiPredictions.map(ai => ({
      checkpoint: ai.checkpoint,
      isAccurate: ai.prediction_error !== null && ai.prediction_error < 2.0, // Within $2
      error: ai.prediction_error,
      confidence: ai.confidence,
      hasActual: ai.actual_price !== null
    }));
  };

  const getCheckpointIcon = (checkpoint: string) => {
    const iconMap: { [key: string]: string } = {
      'open': '🔔',
      'noon': '🕛', 
      'twoPM': '🕐',
      'close': '🔚'
    };
    return iconMap[checkpoint] || '⏱️';
  };

  const formatCheckpointName = (checkpoint: string) => {
    const nameMap: { [key: string]: string } = {
      'open': 'Open',
      'noon': 'Noon',
      'twoPM': '2PM',
      'close': 'Close'
    };
    return nameMap[checkpoint] || checkpoint;
  };

  const calculateRangeSizing = (prediction: HistoricalPrediction) => {
    const predictedWidth = prediction.high - prediction.low;
    const actualWidth = prediction.actualHigh - prediction.actualLow;
    const difference = actualWidth - predictedWidth;
    
    return {
      predictedWidth,
      actualWidth,
      difference,
      isWider: difference > 0,
      percentDiff: predictedWidth > 0 ? (difference / predictedWidth) * 100 : 0
    };
  };
  return <div className="p-4 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-xl font-semibold mb-2">Prediction History</h1>
        <div className="flex items-center justify-center gap-4 text-sm">
          <div className="flex items-center gap-1">
            <Target className="w-4 h-4 text-[#16A34A]" />
            <span className="text-[#A7B3C5]">Accuracy:</span>
            <span className="font-mono font-bold text-[#16A34A]">{calculateAccuracy()}%</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-[#A7B3C5]">Avg Error:</span>
            <span className="font-mono font-bold text-[#E8ECF2]">${calculateAvgError()}</span>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} className="bg-[#12161D] rounded-xl p-2 border border-white/8">
        <div className="flex items-center gap-1 overflow-x-auto">
          <Filter className="w-4 h-4 text-[#A7B3C5] mr-2 flex-shrink-0" />
          {filterOptions.map(option => <button key={option.value} onClick={() => setFilter(option.value)} className={`px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${filter === option.value ? 'bg-[#006072] text-white' : 'text-[#A7B3C5] hover:text-[#E8ECF2] hover:bg-white/5'}`}>
              {option.label}
              <span className="ml-1 text-xs opacity-75">({option.count})</span>
            </button>)}
        </div>
      </motion.div>

      {/* History Cards */}
      <div className="space-y-3">
        {filteredData.map((prediction, index) => <motion.div key={prediction.id} initial={{
        opacity: 0,
        y: 20
      }} animate={{
        opacity: 1,
        y: 0
      }} transition={{
        delay: index * 0.1
      }} className="bg-[#12161D] rounded-xl border border-white/8 overflow-hidden">
            <button onClick={() => setExpandedCard(expandedCard === prediction.id ? null : prediction.id)} className="w-full p-4 text-left hover:bg-white/2 transition-colors">
              {/* Header with enhanced status indicators */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <Calendar className="w-4 h-4 text-[#A7B3C5]" />
                  <span className="font-medium">{formatDate(prediction.date)}</span>
                  {getDayTypeBadge(prediction.dayType)}
                  {prediction.source === 'ai' && <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full">AI</span>}
                </div>
                
                <div className="flex items-center gap-3">
                  {getBiasIcon(prediction.bias)}
                  {/* Checkpoint accuracy indicators */}
                  {prediction.aiPredictions && (
                    <div className="flex items-center gap-1">
                      {getCheckpointAccuracy(prediction).slice(0, 4).map((checkpoint, idx) => (
                        <div key={idx} 
                             className={`w-2 h-2 rounded-full ${
                               !checkpoint.hasActual ? 'bg-[#A7B3C5]/30' :
                               checkpoint.isAccurate ? 'bg-[#16A34A]' : 'bg-[#DC2626]'
                             }`}
                             title={`${formatCheckpointName(checkpoint.checkpoint)}: ${checkpoint.error ? `±$${checkpoint.error?.toFixed(2)}` : 'Pending'}`}
                        />
                      ))}
                    </div>
                  )}
                  {/* Primary range hit indicator (larger) */}
                  {prediction.rangeHit ? 
                    <CheckCircle className="w-6 h-6 text-[#16A34A]" /> : 
                    <XCircle className="w-6 h-6 text-[#DC2626]" />
                  }
                </div>
              </div>

              {/* Enhanced range visualization with proper scaling */}
              <div className="mb-4">
                {(() => {
                  // Only show visualization if we have actual range data
                  if (!prediction.actualLow || !prediction.actualHigh) {
                    return (
                      <div className="text-center py-2 text-[#A7B3C5] text-xs">
                        Day incomplete - no range comparison available
                      </div>
                    );
                  }

                  // Calculate price range for scaling
                  const allPrices = [prediction.low, prediction.high, prediction.actualLow, prediction.actualHigh];
                  const minPrice = Math.min(...allPrices);
                  const maxPrice = Math.max(...allPrices);
                  const totalRange = maxPrice - minPrice;
                  
                  // Add 5% padding on each side
                  const padding = totalRange * 0.05;
                  const chartMin = minPrice - padding;
                  const chartMax = maxPrice + padding;
                  const chartRange = chartMax - chartMin;
                  
                  // Calculate positions and widths as percentages
                  const predLeft = ((prediction.low - chartMin) / chartRange) * 100;
                  const predWidth = ((prediction.high - prediction.low) / chartRange) * 100;
                  const actualLeft = ((prediction.actualLow - chartMin) / chartRange) * 100;
                  const actualWidth = ((prediction.actualHigh - prediction.actualLow) / chartRange) * 100;
                  
                  return (
                    <>
                      <div className="relative h-8 bg-white/5 rounded-lg overflow-hidden">
                        {/* Price scale markers */}
                        <div className="absolute inset-x-0 top-0 h-full flex items-center justify-between px-1 text-[10px] text-[#A7B3C5]/60">
                          <span>${chartMin.toFixed(1)}</span>
                          <span>${chartMax.toFixed(1)}</span>
                        </div>
                        
                        {/* Predicted range bar */}
                        <div 
                          className="absolute top-1 h-3 bg-[#006072]/40 border border-[#006072] rounded-sm" 
                          style={{
                            left: `${predLeft}%`,
                            width: `${Math.max(predWidth, 1)}%`
                          }} 
                        >
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-[8px] text-white font-bold">PRED</span>
                          </div>
                        </div>
                        
                        {/* Actual range bar */}
                        <div 
                          className={`absolute bottom-1 h-3 border rounded-sm ${
                            prediction.rangeHit ? 'bg-[#16A34A]/40 border-[#16A34A]' : 'bg-[#DC2626]/40 border-[#DC2626]'
                          }`}
                          style={{
                            left: `${actualLeft}%`,
                            width: `${Math.max(actualWidth, 1)}%`
                          }} 
                        >
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-[8px] text-white font-bold">ACT</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Range labels with precise values */}
                      <div className="flex justify-between text-xs text-[#A7B3C5] mt-1">
                        <span>Pred: ${prediction.low.toFixed(2)} - ${prediction.high.toFixed(2)} (${(prediction.high - prediction.low).toFixed(2)})</span>
                        <span>Actual: ${prediction.actualLow.toFixed(2)} - ${prediction.actualHigh.toFixed(2)} (${(prediction.actualHigh - prediction.actualLow).toFixed(2)})</span>
                      </div>
                    </>
                  );
                })()}
              </div>

              {/* Summary metrics */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-6">
                  <div>
                    <p className="text-xs text-[#A7B3C5] mb-1">Range Hit</p>
                    <p className={`text-sm font-bold ${prediction.rangeHit ? 'text-[#16A34A]' : 'text-[#DC2626]'}`}>
                      {prediction.rangeHit ? 'HIT' : 'MISS'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-[#A7B3C5] mb-1">Width Δ</p>
                    <p className="text-sm font-mono">
                      {(() => {
                        const sizing = calculateRangeSizing(prediction);
                        return `${sizing.difference > 0 ? '+' : ''}${sizing.difference.toFixed(2)}`;
                      })()}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <p className="text-xs text-[#A7B3C5] mb-1">Error</p>
                  <p className={`text-lg font-mono font-bold ${prediction.error < 1 ? 'text-[#16A34A]' : prediction.error < 2 ? 'text-[#E8ECF2]' : 'text-[#DC2626]'}`}>
                    ${prediction.error.toFixed(2)}
                  </p>
                </div>
              </div>
            </button>

            {/* Expanded Details */}
            {expandedCard === prediction.id && <motion.div initial={{
          height: 0,
          opacity: 0
        }} animate={{
          height: 'auto',
          opacity: 1
        }} exit={{
          height: 0,
          opacity: 0
        }} transition={{
          duration: 0.2
        }} className="border-t border-white/8 p-4 bg-[#0B0D12]">
                <div className="space-y-4">
                  {/* AI Checkpoint Breakdown */}
                  {prediction.aiPredictions && prediction.aiPredictions.length > 0 && (
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <Activity className="w-4 h-4 text-[#006072]" />
                        <p className="text-sm font-semibold text-[#E8ECF2]">Checkpoint Analysis</p>
                      </div>
                      <div className="space-y-2">
                        {prediction.aiPredictions.map((ai, idx) => (
                          <div key={idx} className="bg-white/5 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <span className="text-sm">{getCheckpointIcon(ai.checkpoint)}</span>
                                <span className="font-medium text-sm">{formatCheckpointName(ai.checkpoint)}</span>
                                <div className={`w-2 h-2 rounded-full ${
                                  !ai.actual_price ? 'bg-[#A7B3C5]/30' :
                                  (ai.prediction_error && ai.prediction_error < 2.0) ? 'bg-[#16A34A]' : 'bg-[#DC2626]'
                                }`} />
                              </div>
                              <div className="flex items-center gap-3">
                                <span className="text-xs text-[#A7B3C5]">
                                  Confidence: {(ai.confidence * 100).toFixed(0)}%
                                </span>
                                {ai.prediction_error && (
                                  <span className={`text-sm font-mono font-bold ${
                                    ai.prediction_error < 1 ? 'text-[#16A34A]' : 
                                    ai.prediction_error < 2 ? 'text-[#E8ECF2]' : 'text-[#DC2626]'
                                  }`}>
                                    ±${ai.prediction_error.toFixed(2)}
                                  </span>
                                )}
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-4 text-xs">
                              <div>
                                <span className="text-[#A7B3C5]">Predicted:</span>
                                <span className="ml-2 font-mono">${ai.predicted_price.toFixed(2)}</span>
                              </div>
                              <div>
                                <span className="text-[#A7B3C5]">Actual:</span>
                                <span className="ml-2 font-mono">
                                  {ai.actual_price ? `$${ai.actual_price.toFixed(2)}` : 'Pending'}
                                </span>
                              </div>
                            </div>
                            
                            {ai.reasoning && (
                              <div className="mt-2 pt-2 border-t border-white/10">
                                <p className="text-xs text-[#A7B3C5] italic">{ai.reasoning}</p>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Enhanced Range Analysis */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Target className="w-4 h-4 text-[#006072]" />
                      <p className="text-sm font-semibold text-[#E8ECF2]">Range Performance</p>
                    </div>
                    
{(() => {
                      // Same scaling logic as compact view
                      if (!prediction.actualLow || !prediction.actualHigh) {
                        return (
                          <div className="text-center py-3 text-[#A7B3C5] text-sm">
                            Day incomplete - no range analysis available
                          </div>
                        );
                      }

                      const allPrices = [prediction.low, prediction.high, prediction.actualLow, prediction.actualHigh];
                      const minPrice = Math.min(...allPrices);
                      const maxPrice = Math.max(...allPrices);
                      const totalRange = maxPrice - minPrice;
                      const padding = totalRange * 0.05;
                      const chartMin = minPrice - padding;
                      const chartMax = maxPrice + padding;
                      const chartRange = chartMax - chartMin;
                      
                      const predLeft = ((prediction.low - chartMin) / chartRange) * 100;
                      const predWidth = ((prediction.high - prediction.low) / chartRange) * 100;
                      const actualLeft = ((prediction.actualLow - chartMin) / chartRange) * 100;
                      const actualWidth = ((prediction.actualHigh - prediction.actualLow) / chartRange) * 100;
                      
                      return (
                        <div className="relative h-12 bg-white/5 rounded-lg overflow-hidden mb-3">
                          {/* Price scale with more detail */}
                          <div className="absolute inset-x-0 top-0 h-full flex items-center justify-between px-2 text-xs text-[#A7B3C5]/60">
                            <span>${chartMin.toFixed(2)}</span>
                            <span className="text-[10px]">{((chartMax + chartMin) / 2).toFixed(2)}</span>
                            <span>${chartMax.toFixed(2)}</span>
                          </div>
                          
                          {/* Predicted Range */}
                          <div 
                            className="absolute top-1 h-4 bg-[#006072]/40 border border-[#006072] flex items-center justify-center rounded-sm"
                            style={{
                              left: `${predLeft}%`,
                              width: `${Math.max(predWidth, 2)}%`
                            }}
                          >
                            <span className="text-xs text-white font-bold">PRED</span>
                          </div>
                          
                          {/* Actual Range */}
                          <div 
                            className={`absolute bottom-1 h-4 border flex items-center justify-center rounded-sm ${
                              prediction.rangeHit ? 'bg-[#16A34A]/40 border-[#16A34A]' : 'bg-[#DC2626]/40 border-[#DC2626]'
                            }`}
                            style={{
                              left: `${actualLeft}%`,
                              width: `${Math.max(actualWidth, 2)}%`
                            }}
                          >
                            <span className="text-xs text-white font-bold">ACT</span>
                          </div>
                        </div>
                      );
                    })()}

                    {/* Range metrics grid */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-[#A7B3C5] mb-1">Predicted Width</p>
                        <p className="text-sm font-mono font-bold">
                          ${(prediction.high - prediction.low).toFixed(2)}
                        </p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-[#A7B3C5] mb-1">Actual Width</p>
                        <p className="text-sm font-mono font-bold">
                          ${(prediction.actualHigh - prediction.actualLow).toFixed(2)}
                        </p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-[#A7B3C5] mb-1">Width Difference</p>
                        <p className={`text-sm font-mono font-bold ${
                          calculateRangeSizing(prediction).difference > 0 ? 'text-[#DC2626]' : 'text-[#16A34A]'
                        }`}>
                          {(() => {
                            const diff = calculateRangeSizing(prediction).difference;
                            return `${diff > 0 ? '+' : ''}${diff.toFixed(2)}`;
                          })()}
                        </p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-[#A7B3C5] mb-1">Hit Status</p>
                        <p className={`text-sm font-bold ${prediction.rangeHit ? 'text-[#16A34A]' : 'text-[#DC2626]'}`}>
                          {prediction.rangeHit ? '✓ HIT' : '✗ MISS'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Analysis Notes */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="w-4 h-4 text-[#006072]" />
                      <p className="text-sm font-semibold text-[#E8ECF2]">Trading Notes</p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3">
                      <p className="text-sm text-[#E8ECF2]">
                        {prediction.notes || 'No trading notes available for this prediction.'}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>}
          </motion.div>)}
      </div>

      {/* Empty State */}
      {filteredData.length === 0 && <motion.div initial={{
      opacity: 0
    }} animate={{
      opacity: 1
    }} className="text-center py-12">
          <Calendar className="w-12 h-12 text-[#A7B3C5] mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No predictions found</h3>
          <p className="text-[#A7B3C5] mb-4">
            {filter === 'all' ? 'Start making predictions to see your history here.' : `No predictions match the "${filter}" filter.`}
          </p>
          <button onClick={() => setFilter('all')} className="px-4 py-2 bg-[#006072] text-white rounded-lg font-medium">
            {filter === 'all' ? 'Make First Prediction' : 'Show All'}
          </button>
        </motion.div>}
    </div>;
}