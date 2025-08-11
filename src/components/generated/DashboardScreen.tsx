import React from 'react';
import { motion } from 'framer-motion';
import { Clock, RotateCcw, RefreshCw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, ReferenceLine, ReferenceArea } from 'recharts';
interface SPYData {
  currentPrice: number;
  openPrice: number;
  noonPrice?: number;
  twoPMPrice?: number;
  closePrice?: number;
  lastUpdated: Date;
}
interface PredictionData {
  predictedLow: number;
  predictedHigh: number;
  bias: 'up' | 'neutral' | 'down';
  volatilityContext: string;
  dayType: string;
  notes: string;
  date: Date;
}
interface TradeData {
  dte0: {
    strikes: {
      put: number;
      call: number;
    };
    delta: number;
    wingWidth: number;
    targetCredit: number;
  };
  week1: {
    strikes: {
      put: number;
      call: number;
    };
    delta: number;
    wingWidth: number;
    targetCredit: number;
  };
  month1: {
    strikes: {
      put: number;
      call: number;
    };
    delta: number;
    wingWidth: number;
    targetCredit: number;
  };
}
interface DashboardScreenProps {
  spyData: SPYData;
  prediction: PredictionData | null;
  tradeData: TradeData;
  onLogPrice: (timeSlot: 'open' | 'noon' | 'twoPM' | 'close') => void;
  onResetDay: () => void;
}
export function DashboardScreen({
  spyData,
  prediction,
  tradeData,
  onLogPrice,
  onResetDay
}: DashboardScreenProps) {
  const priceSlots = [{
    id: 'open',
    label: 'Open',
    time: '9:30 AM',
    price: spyData.openPrice,
    color: 'bg-blue-600'
  }, {
    id: 'noon',
    label: 'Noon',
    time: '12:00 PM',
    price: spyData.noonPrice,
    color: 'bg-yellow-600'
  }, {
    id: 'twoPM',
    label: '2:00 PM',
    time: '2:00 PM',
    price: spyData.twoPMPrice,
    color: 'bg-orange-600'
  }, {
    id: 'close',
    label: 'Close',
    time: '4:00 PM',
    price: spyData.closePrice,
    color: 'bg-red-600'
  }] as any[];
  const chartData = [{
    time: '9:30',
    price: spyData.openPrice
  }, ...(spyData.noonPrice ? [{
    time: '12:00',
    price: spyData.noonPrice
  }] : []), ...(spyData.twoPMPrice ? [{
    time: '14:00',
    price: spyData.twoPMPrice
  }] : []), ...(spyData.closePrice ? [{
    time: '16:00',
    price: spyData.closePrice
  }] : [])];
  const getBiasColor = (bias: string) => {
    switch (bias) {
      case 'up':
        return 'text-green-400';
      case 'down':
        return 'text-red-400';
      default:
        return 'text-blue-400';
    }
  };
  return <div className="p-4 space-y-6">
      {/* Live Price Cards */}
      <section>
        <h2 className="text-lg font-semibold text-gray-200 mb-3">Price Logging</h2>
        <div className="grid grid-cols-2 gap-3">
          {priceSlots.map(slot => <motion.button key={slot.id} whileTap={{
          scale: 0.98
        }} onClick={() => onLogPrice(slot.id as any)} className={`p-4 rounded-xl border border-gray-700 bg-gray-800 hover:bg-gray-750 transition-colors touch-manipulation ${slot.price ? 'ring-2 ring-blue-500' : ''}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-300">{slot.label}</span>
                <Clock className="w-4 h-4 text-gray-400" />
              </div>
              <div className="text-xs text-gray-500 mb-1">{slot.time}</div>
              <div className="text-lg font-mono font-bold text-white">
                {slot.price ? `$${slot.price.toFixed(2)}` : 'Tap to log'}
              </div>
            </motion.button>)}
        </div>
      </section>

      {/* Chart Section */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-200">Intraday Chart</h2>
          <motion.button whileTap={{
          scale: 0.95
        }} onClick={onResetDay} className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors text-sm touch-manipulation">
            <RotateCcw className="w-4 h-4" />
            <span>Reset Day</span>
          </motion.button>
        </div>
        
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                {prediction && <ReferenceArea y1={prediction.predictedLow} y2={prediction.predictedHigh} fill="rgba(59, 130, 246, 0.1)" stroke="none" />}
                {prediction && <>
                    <ReferenceLine y={prediction.predictedLow} stroke="#ef4444" strokeDasharray="3 3" />
                    <ReferenceLine y={prediction.predictedHigh} stroke="#22c55e" strokeDasharray="3 3" />
                  </>}
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{
                fill: '#9ca3af',
                fontSize: 12
              }} />
                <YAxis domain={['dataMin - 2', 'dataMax + 2']} axisLine={false} tickLine={false} tick={{
                fill: '#9ca3af',
                fontSize: 12
              }} />
                <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={{
                fill: '#3b82f6',
                strokeWidth: 2,
                r: 4
              }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          {prediction && <div className="mt-3 text-xs text-gray-400 text-center">
              Predicted Range: ${prediction.predictedLow.toFixed(2)} - ${prediction.predictedHigh.toFixed(2)} 
              <span className={`ml-2 font-medium ${getBiasColor(prediction.bias)}`}>
                ({prediction.bias.toUpperCase()})
              </span>
            </div>}
        </div>
      </section>

      {/* Trade Suggestions */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-200">Trade Suggestions</h2>
          <motion.button whileTap={{
          scale: 0.95
        }} className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 transition-colors text-sm touch-manipulation">
            <RefreshCw className="w-4 h-4" />
            <span>Update</span>
          </motion.button>
        </div>

        <div className="space-y-3">
          {[{
          key: 'dte0',
          label: '0DTE',
          data: tradeData.dte0
        }, {
          key: 'week1',
          label: '1W',
          data: tradeData.week1
        }, {
          key: 'month1',
          label: '1M',
          data: tradeData.month1
        }].map(trade => <div key={trade.key} className="bg-gray-800 rounded-xl p-4 border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-white">{trade.label} Iron Condor</h3>
                <span className="text-sm text-green-400 font-mono">${trade.data.targetCredit.toFixed(2)}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Strikes</div>
                  <div className="font-mono text-white">
                    {trade.data.strikes.put}/{trade.data.strikes.call}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Delta</div>
                  <div className="font-mono text-white">{trade.data.delta.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Wing Width</div>
                  <div className="font-mono text-white">${trade.data.wingWidth}</div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Target Credit</div>
                  <div className="font-mono text-green-400">${trade.data.targetCredit.toFixed(2)}</div>
                </div>
              </div>
            </div>)}
        </div>
      </section>
    </div>;
}