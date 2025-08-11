import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, TrendingUp } from 'lucide-react';
interface HeaderBarProps {
  currentPrice: number;
  lastUpdated: Date;
  onRefresh: () => void;
}
export function HeaderBar({
  currentPrice,
  lastUpdated,
  onRefresh
}: HeaderBarProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };
  return <header className="bg-gray-800 border-b border-gray-700 px-4 py-3 sticky top-0 z-50">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-6 h-6 text-blue-400" />
            <h1 className="text-lg font-bold text-white">SPY Assistant</h1>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-lg font-mono font-bold text-green-400">
              ${currentPrice.toFixed(2)}
            </div>
            <div className="text-xs text-gray-400">
              {formatDate(lastUpdated)} {formatTime(lastUpdated)}
            </div>
          </div>

          <motion.button whileTap={{
          scale: 0.95
        }} onClick={onRefresh} className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors touch-manipulation" aria-label="Refresh SPY price">
            <RefreshCw className="w-5 h-5 text-gray-300" />
          </motion.button>
        </div>
      </div>
    </header>;
}