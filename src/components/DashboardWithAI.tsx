import React, { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { api } from '../utils/apiClient';

interface PredictionData {
  low: number;
  high: number;
  bias: string;
  notes: string;
}

interface PriceData {
  time: string;
  price: number | null;
  label: string;
}

export function DashboardWithAI() {
  const [prediction, setPrediction] = useState<PredictionData>({
    low: 0,
    high: 0,
    bias: 'neutral',
    notes: 'Loading data...'
  });
  const [dataSource, setDataSource] = useState<string>('Loading...');
  const [keyTimes, setKeyTimes] = useState<PriceData[]>([
    { time: '8:30', price: null, label: 'Open' },
    { time: '12:00', price: null, label: 'Noon' },
    { time: '14:00', price: null, label: '2:00' },
    { time: '15:00', price: null, label: 'Close' }
  ]);

  useEffect(() => {
    const loadTodayData = async () => {
      try {
        const today = new Date().toLocaleDateString('en-CA', {
          timeZone: 'America/Chicago'
        });

        // Try manual predictions first
        try {
          const data = await api.getPrediction(today);
          
          if (data.predLow && data.predHigh) {
            setPrediction({
              low: data.predLow,
              high: data.predHigh,
              bias: data.bias || 'neutral',
              notes: data.notes || 'No notes available'
            });
            setDataSource('📝 Manual Prediction');
          }

          // Update price data
          setKeyTimes(prev => prev.map(item => {
            let price = null;
            switch (item.label.toLowerCase()) {
              case 'open': price = data.open; break;
              case 'noon': price = data.noon; break;
              case '2:00': price = data.twoPM; break;
              case 'close': price = data.close; break;
            }
            return { ...item, price };
          }));
        } else {
          // If no manual predictions, try AI predictions
          console.log('No manual predictions, fetching AI predictions...');
          const aiResponse = await fetch(`http://localhost:8000/ai/predictions/${today}`);
          if (aiResponse.ok) {
            const aiData = await aiResponse.json();
            console.log('AI predictions received:', aiData);
            
            // Extract predicted prices for low/high
            const prices = aiData.predictions.map((p: any) => p.predicted_price);
            const low = Math.min(...prices);
            const high = Math.max(...prices);
            
            setPrediction({
              low: low,
              high: high,
              bias: 'neutral',
              notes: aiData.market_context || 'AI Prediction'
            });
            setDataSource('🤖 AI Prediction (GPT-4o)');
            
            // Update price predictions
            setKeyTimes(prev => prev.map(item => {
              const pred = aiData.predictions.find((p: any) => 
                p.checkpoint.toLowerCase() === item.label.toLowerCase() ||
                (p.checkpoint === 'twoPM' && item.label === '2:00')
              );
              return { ...item, price: pred?.predicted_price || null };
            }));
          } else {
            setDataSource('❌ No Data Available');
          }
        }
      } catch (error) {
        console.error('Error loading data:', error);
        setDataSource('⚠️ Error Loading Data');
      }
    };

    loadTodayData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="bg-gray-900/50 border-b border-gray-800">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold">SPY TA Tracker</h1>
            <span className="bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded text-xs font-medium">
              {dataSource}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">
              {new Date().toLocaleDateString('en-US', { 
                weekday: 'short', 
                month: 'short', 
                day: 'numeric',
                timeZone: 'America/Chicago'
              })} CST
            </span>
            <RefreshCw 
              className="w-4 h-4 text-gray-400 cursor-pointer hover:text-white" 
              onClick={() => window.location.reload()}
            />
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Today's Prediction */}
        <div className="bg-gray-900/50 rounded-lg border border-gray-800 p-4">
          <h2 className="text-sm text-gray-400 mb-3">Today's Prediction</h2>
          <div className="flex justify-between items-center mb-4">
            <div>
              <div className="text-xs text-gray-500">Low</div>
              <div className="text-2xl font-bold text-red-400">${prediction.low.toFixed(2)}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">High</div>
              <div className="text-2xl font-bold text-green-400">${prediction.high.toFixed(2)}</div>
            </div>
          </div>
          <div className="text-xs text-gray-400">{prediction.notes}</div>
        </div>

        {/* Key Times */}
        <div className="bg-gray-900/50 rounded-lg border border-gray-800 p-4">
          <h2 className="text-sm text-gray-400 mb-3">Key Times (CST)</h2>
          <div className="grid grid-cols-2 gap-3">
            {keyTimes.map((item) => (
              <div key={item.label} className="bg-gray-800/50 rounded p-3">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>{item.label}</span>
                  <span>{item.time}</span>
                </div>
                <div className="text-lg font-semibold">
                  {item.price ? `$${item.price.toFixed(2)}` : '---'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Price Range Indicator */}
        <div className="bg-gray-900/50 rounded-lg border border-gray-800 p-4">
          <h2 className="text-sm text-gray-400 mb-3">Price Movement</h2>
          <div className="relative h-32">
            <div className="absolute inset-0 flex flex-col justify-between text-xs text-gray-500">
              <div>${(prediction.high + 2).toFixed(0)}</div>
              <div>${prediction.high.toFixed(0)}</div>
              <div>${((prediction.high + prediction.low) / 2).toFixed(0)}</div>
              <div>${prediction.low.toFixed(0)}</div>
              <div>${(prediction.low - 2).toFixed(0)}</div>
            </div>
            <div className="ml-12 h-full flex flex-col justify-center">
              <div 
                className="bg-green-500/20 border-t border-b border-green-500/50"
                style={{
                  height: `${((prediction.high - prediction.low) / 10) * 100}%`,
                  marginTop: '20%'
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}