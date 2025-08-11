import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, RotateCcw, RefreshCw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, ReferenceLine, ReferenceArea } from 'recharts';
interface PredictionData {
  low: number;
  high: number;
  bias: 'bullish' | 'bearish' | 'neutral';
  notes: string;
}
interface PriceData {
  time: string;
  price: number | null;
  label: string;
}
interface OptionsSetup {
  type: 'Iron Condor' | 'Iron Butterfly';
  expiration: '0DTE' | '1W' | '1M';
  strikes: string;
  delta: string;
  wings: string;
  targetCredit: string;
}
export function DashboardScreen() {
  const [prediction, setPrediction] = useState<PredictionData>({
    low: 0,
    high: 0,
    bias: 'neutral',
    notes: 'Loading data...'
  });
  const [dataSource, setDataSource] = useState<string>('Loading...');
  const [locked, setLocked] = useState<boolean>(false);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);
  const [keyTimes, setKeyTimes] = useState<PriceData[]>([{
    time: '8:30',
    price: null,
    label: 'Open'
  }, {
    time: '12:00',
    price: null,
    label: 'Noon'
  }, {
    time: '14:00',
    price: null,
    label: '2:00'
  }, {
    time: '15:00',
    price: null,
    label: 'Close'
  }]);

  // Load today's data on component mount
  useEffect(() => {
    const loadTodayData = async () => {
      try {
        const today = new Date().toLocaleDateString('en-CA', {
          timeZone: 'America/Chicago'
        });

        const response = await fetch(`http://localhost:8000/day/${today}`);
        if (response.ok) {
          const data = await response.json();
          
          // Update prediction data
          if (data.predLow && data.predHigh) {
            setPrediction({
              low: data.predLow,
              high: data.predHigh,
              bias: data.bias || 'neutral',
              notes: data.notes || 'No notes available'
            });
            // Set badge based on source/locked
            if (data.source === 'ai') {
              setDataSource('🤖 AI Prediction');
            } else {
              setDataSource('📝 Manual Prediction');
            }
            setLocked(!!data.locked);
          }

          // Update price data
          setKeyTimes(prev => prev.map(item => {
            let price = null;
            switch (item.label.toLowerCase()) {
              case 'open':
                price = data.open;
                break;
              case 'noon':
                price = data.noon;
                break;
              case '2:00':
                price = data.twoPM;
                break;
              case 'close':
                price = data.close;
                break;
            }
            return { ...item, price };
          }));
        } else {
          // No manual data, try AI predictions
          console.log('No manual data found, fetching AI predictions...');
          const aiResponse = await fetch(`http://localhost:8000/ai/predictions/${today}`);
          if (aiResponse.ok) {
            const aiData = await aiResponse.json();
            console.log('AI predictions received:', aiData);
            
            // Extract predicted prices for low/high and round to 2 decimal places
            const prices = aiData.predictions.map((p: any) => Math.round(p.predicted_price * 100) / 100);
            const low = Math.min(...prices);
            const high = Math.max(...prices);
            
            setPrediction({
              low: low,
              high: high,
              bias: 'neutral',
              notes: aiData.market_context || 'AI Prediction'
            });
            setDataSource('🤖 AI Prediction');
            setAiAnalysis(aiData.market_context || null);
            setLocked(true);
            
            // Update price predictions with proper rounding
            setKeyTimes(prev => prev.map(item => {
              const pred = aiData.predictions.find((p: any) => 
                p.checkpoint.toLowerCase() === item.label.toLowerCase() ||
                (p.checkpoint === 'twoPM' && item.label === '2:00')
              );
              return { 
                ...item, 
                price: pred?.predicted_price ? Math.round(pred.predicted_price * 100) / 100 : null 
              };
            }));
          } else {
            setDataSource('❌ No Data Available');
          }
        }
      } catch (error) {
        console.error('Error loading today\'s data:', error);
      }
    };

    loadTodayData();
  }, []);
  const [isUpdatingOptions, setIsUpdatingOptions] = useState(false);
  
  // Generate chart data from actual prediction/price points only
  const chartData = React.useMemo(() => {
    const data = [];
    
    // Add only the actual price points (no interpolation)
    keyTimes.forEach(item => {
      if (item.price !== null) {
        data.push({
          time: item.time,
          actual: item.price
        });
      }
    });
    
    // Sort by time but don't add artificial interpolated points
    return data.sort((a, b) => {
      const timeA = parseFloat(a.time.replace(':', '.'));
      const timeB = parseFloat(b.time.replace(':', '.'));
      return timeA - timeB;
    });
  }, [keyTimes]);
  const optionsSetups: OptionsSetup[] = [{
    type: 'Iron Condor',
    expiration: '0DTE',
    strikes: '633/635/639/641',
    delta: '±15Δ',
    wings: '$2.50',
    targetCredit: '$0.85'
  }, {
    type: 'Iron Butterfly',
    expiration: '1W',
    strikes: '637/637/637',
    delta: '±20Δ',
    wings: '$3.00',
    targetCredit: '$1.25'
  }, {
    type: 'Iron Condor',
    expiration: '1M',
    strikes: '628/633/641/646',
    delta: '±25Δ',
    wings: '$5.00',
    targetCredit: '$2.10'
  }];
  const handlePriceUpdate = async (index: number) => {
    const checkpoint = keyTimes[index];
    const checkpointName = checkpoint.label.toLowerCase() === '2:00' ? 'twoPM' : checkpoint.label.toLowerCase();
    
    // Prompt user for price input
    const priceInput = window.prompt(`Enter ${checkpoint.label} price for SPY:`, '');
    if (!priceInput) return;
    
    const price = parseFloat(priceInput);
    if (isNaN(price) || price <= 0) {
      alert('Please enter a valid price');
      return;
    }

    try {
      // Get current date in CST timezone
      const today = new Date().toLocaleDateString('en-CA', {
        timeZone: 'America/Chicago'
      });

      // Call the backend API
      const response = await fetch(`http://localhost:8000/capture/${today}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          checkpoint: checkpointName,
          price: price
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Update the UI with the captured price
      setKeyTimes(prev => prev.map((item, i) => i === index ? {
        ...item,
        price: price
      } : item));

      console.log(`Price captured: ${checkpoint.label} = $${price}`);
    } catch (error) {
      console.error('Error capturing price:', error);
      alert('Failed to capture price. Please try again.');
    }
  };
  const handleUpdateOptions = async () => {
    setIsUpdatingOptions(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsUpdatingOptions(false);
  };
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
  const rangeHitPercentage = 73;
  const medianAbsError = 1.25;
  return <div className="p-4 space-y-6">
      {/* Prediction Card */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">Today's Prediction</h2>
            <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs rounded-full font-medium">
              {dataSource}
            </span>
            {locked && (
              <span className="ml-2 px-2 py-1 bg-green-600/10 text-green-400 text-xs rounded-full font-medium">
                Locked
              </span>
            )}
          </div>
          {getBiasIcon(prediction.bias)}
        </div>
        
        <div className="flex items-center gap-4 mb-3">
          <div className="text-center">
            <p className="text-xs text-[#A7B3C5] mb-1">Low</p>
            <p className="text-xl font-mono font-bold text-[#DC2626]">${prediction.low}</p>
          </div>
          <div className="flex-1 h-px bg-gradient-to-r from-[#DC2626] via-[#A7B3C5] to-[#16A34A]"></div>
          <div className="text-center">
            <p className="text-xs text-[#A7B3C5] mb-1">High</p>
            <p className="text-xl font-mono font-bold text-[#16A34A]">${prediction.high}</p>
          </div>
        </div>
        
        <p className="text-sm text-[#A7B3C5] bg-[#0B0D12] rounded-lg p-3">
          {prediction.notes}
        </p>
      </motion.div>

      {/* AI Analysis Card - only show if we have AI analysis */}
      {aiAnalysis && (
        <motion.div initial={{
          opacity: 0,
          y: 20
        }} animate={{
          opacity: 1,
          y: 0
        }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="text-sm font-medium text-[#A7B3C5]">AI Market Analysis</h3>
            <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs rounded-full">
              GPT-5 High Reasoning
            </span>
          </div>
          <p className="text-sm text-[#A7B3C5] bg-[#0B0D12] rounded-lg p-3 leading-relaxed">
            {aiAnalysis}
          </p>
        </motion.div>
      )}

      {/* Key Times Grid */}
      <div>
        <h3 className="text-sm font-medium text-[#A7B3C5] mb-3">Key Times (CST)</h3>
        <div className="grid grid-cols-2 gap-3">
          {keyTimes.map((item, index) => <motion.button key={item.time} onClick={() => handlePriceUpdate(index)} whileTap={{
          scale: 0.98
        }} className="bg-[#12161D] rounded-xl p-4 border border-white/8 text-left hover:border-[#006072]/50 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-[#A7B3C5]">{item.label}</span>
                <span className="text-xs font-mono text-[#A7B3C5]">{item.time}</span>
              </div>
              <p className="text-lg font-mono font-bold">
                {item.price ? `$${item.price}` : '---'}
              </p>
            </motion.button>)}
        </div>
      </div>

      {/* Chart Card */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.1
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium">Price Movement</h3>
          <button className="p-1 rounded-lg hover:bg-white/5 transition-colors">
            <RotateCcw className="w-4 h-4 text-[#A7B3C5]" />
          </button>
        </div>
        
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{
              fontSize: 12,
              fill: '#A7B3C5'
            }} />
              <YAxis domain={[
              Math.floor(prediction.low - 2), 
              Math.ceil(prediction.high + 2)
            ]} axisLine={false} tickLine={false} tick={{
              fontSize: 12,
              fill: '#A7B3C5'
            }} />
              <ReferenceArea y1={prediction.low} y2={prediction.high} fill="#006072" fillOpacity={0.1} stroke="#006072" strokeOpacity={0.3} />
              <ReferenceLine y={prediction.low} stroke="#DC2626" strokeDasharray="2 2" />
              <ReferenceLine y={prediction.high} stroke="#16A34A" strokeDasharray="2 2" />
              <Line type="monotone" dataKey="actual" stroke="#E8ECF2" strokeWidth={2} dot={{
              fill: '#E8ECF2',
              strokeWidth: 0,
              r: 3
            }} connectNulls={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Options Suggestions */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-[#A7B3C5]">Options Setups</h3>
          <motion.button onClick={handleUpdateOptions} disabled={isUpdatingOptions} whileTap={{
          scale: 0.95
        }} className="flex items-center gap-2 px-3 py-1 bg-[#006072] text-white text-xs rounded-lg disabled:opacity-50">
            <motion.div animate={isUpdatingOptions ? {
            rotate: 360
          } : {
            rotate: 0
          }} transition={{
            duration: 1,
            repeat: isUpdatingOptions ? Infinity : 0,
            ease: "linear"
          }}>
              <RefreshCw className="w-3 h-3" />
            </motion.div>
            Update
          </motion.button>
        </div>
        
        <div className="space-y-3">
          {optionsSetups.map((setup, index) => <motion.div key={index} initial={{
          opacity: 0,
          x: -20
        }} animate={{
          opacity: 1,
          x: 0
        }} transition={{
          delay: index * 0.1
        }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{setup.type}</span>
                  <span className="px-2 py-1 bg-[#006072] text-white text-xs rounded-full">
                    {setup.expiration}
                  </span>
                </div>
                <span className="text-sm font-mono font-bold text-[#16A34A]">
                  {setup.targetCredit}
                </span>
              </div>
              
              <div className="grid grid-cols-3 gap-4 text-xs">
                <div>
                  <p className="text-[#A7B3C5] mb-1">Strikes</p>
                  <p className="font-mono">{setup.strikes}</p>
                </div>
                <div>
                  <p className="text-[#A7B3C5] mb-1">Delta</p>
                  <p className="font-mono">{setup.delta}</p>
                </div>
                <div>
                  <p className="text-[#A7B3C5] mb-1">Wings</p>
                  <p className="font-mono">{setup.wings}</p>
                </div>
              </div>
            </motion.div>)}
        </div>
      </div>

      {/* Performance Strip */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.2
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <div className="flex items-center justify-between mb-3">
          <div className="text-center">
            <p className="text-xs text-[#A7B3C5] mb-1">Range Hit %</p>
            <p className="text-lg font-mono font-bold text-[#16A34A]">{rangeHitPercentage}%</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-[#A7B3C5] mb-1">Median Abs Error</p>
            <p className="text-lg font-mono font-bold text-[#E8ECF2]">${medianAbsError}</p>
          </div>
        </div>
        
        <div className="bg-[#0B0D12] rounded-lg p-3">
          <p className="text-xs text-[#A7B3C5]">
            💡 <strong>Calibration Tip:</strong> Your ranges are slightly narrow. Consider widening by 10-15% for better hit rate.
          </p>
        </div>
      </motion.div>
    </div>;
}