import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Calendar, Target, CheckCircle, XCircle, Filter } from 'lucide-react';
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
        const resp = await fetch(`http://localhost:8000/history?limit=20`);
        if (!resp.ok) {
          console.error('Failed to fetch history:', resp.status);
          return;
        }
        const data = await resp.json();
        
        const items: HistoricalPrediction[] = data.items.map((item: any) => ({
          id: String(item.id),
          date: item.date,
          low: item.predLow ?? 0,
          high: item.predHigh ?? 0,
          bias: (item.bias || 'neutral') as any,
          actualLow: item.actualLow ?? 0,
          actualHigh: item.actualHigh ?? 0,
          rangeHit: !!item.rangeHit,
          notes: item.notes || `${item.source === 'ai' ? '🤖 AI' : '📝 Manual'} prediction`,
          dayType: (item.dayType || 'normal') as any,
          error: item.error ?? 0,
        }));
        
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
    return new Date(dateString).toLocaleDateString('en-US', {
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
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <Calendar className="w-4 h-4 text-[#A7B3C5]" />
                  <span className="font-medium">{formatDate(prediction.date)}</span>
                  {getDayTypeBadge(prediction.dayType)}
                </div>
                
                <div className="flex items-center gap-2">
                  {getBiasIcon(prediction.bias)}
                  {prediction.rangeHit ? <CheckCircle className="w-5 h-5 text-[#16A34A]" /> : <XCircle className="w-5 h-5 text-[#DC2626]" />}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <p className="text-xs text-[#A7B3C5] mb-1">Predicted</p>
                    <p className="text-sm font-mono">
                      ${prediction.low.toFixed(2)} - ${prediction.high.toFixed(2)}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-[#A7B3C5] mb-1">Actual</p>
                    <p className="text-sm font-mono">
                      ${prediction.actualLow.toFixed(2)} - ${prediction.actualHigh.toFixed(2)}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <p className="text-xs text-[#A7B3C5] mb-1">Error</p>
                  <p className={`text-sm font-mono font-bold ${prediction.error < 1 ? 'text-[#16A34A]' : prediction.error < 2 ? 'text-[#E8ECF2]' : 'text-[#DC2626]'}`}>
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
                <div className="space-y-3">
                  {/* Range Visualization */}
                  <div>
                    <p className="text-xs text-[#A7B3C5] mb-2">Range Comparison</p>
                    <div className="relative h-8 bg-white/5 rounded-lg overflow-hidden">
                      {/* Predicted Range */}
                      <div className="absolute top-0 h-4 bg-[#006072]/30 border border-[#006072]" style={{
                  left: '10%',
                  width: '60%'
                }} />
                      {/* Actual Range */}
                      <div className="absolute bottom-0 h-4 bg-[#E8ECF2]/30 border border-[#E8ECF2]" style={{
                  left: '15%',
                  width: '55%'
                }} />
                    </div>
                    <div className="flex justify-between text-xs text-[#A7B3C5] mt-1">
                      <span>Predicted</span>
                      <span>Actual</span>
                    </div>
                  </div>

                  {/* Notes */}
                  <div>
                    <p className="text-xs text-[#A7B3C5] mb-1">Analysis Notes</p>
                    <p className="text-sm text-[#E8ECF2] bg-white/5 rounded-lg p-3">
                      {prediction.notes}
                    </p>
                  </div>

                  {/* Performance Metrics */}
                  <div className="grid grid-cols-3 gap-4 pt-2 border-t border-white/8">
                    <div className="text-center">
                      <p className="text-xs text-[#A7B3C5] mb-1">Range Width</p>
                      <p className="text-sm font-mono">
                        ${(prediction.high - prediction.low).toFixed(2)}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-[#A7B3C5] mb-1">Actual Width</p>
                      <p className="text-sm font-mono">
                        ${(prediction.actualHigh - prediction.actualLow).toFixed(2)}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-[#A7B3C5] mb-1">Hit Rate</p>
                      <p className={`text-sm font-mono font-bold ${prediction.rangeHit ? 'text-[#16A34A]' : 'text-[#DC2626]'}`}>
                        {prediction.rangeHit ? '100%' : '0%'}
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