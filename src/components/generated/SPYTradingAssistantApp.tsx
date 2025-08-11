import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HeaderBar } from './HeaderBar';
import { BottomNavigationBar } from './BottomNavigationBar';
import { DashboardScreen } from './DashboardScreen';
import { PredictScreen } from './PredictScreen';
type TabType = 'dashboard' | 'predict' | 'history' | 'metrics';
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
export function SPYTradingAssistantApp() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [spyData, setSPYData] = useState<SPYData>({
    currentPrice: 585.42,
    openPrice: 584.15,
    lastUpdated: new Date()
  });
  const [prediction, setPrediction] = useState<PredictionData | null>(null);
  const [tradeData, setTradeData] = useState<TradeData>({
    dte0: {
      strikes: {
        put: 580,
        call: 590
      },
      delta: 0.15,
      wingWidth: 5,
      targetCredit: 1.25
    },
    week1: {
      strikes: {
        put: 575,
        call: 595
      },
      delta: 0.20,
      wingWidth: 10,
      targetCredit: 2.50
    },
    month1: {
      strikes: {
        put: 565,
        call: 605
      },
      delta: 0.25,
      wingWidth: 15,
      targetCredit: 4.75
    }
  });
  const refreshSPYData = () => {
    // Simulate fetching new SPY data
    setSPYData(prev => ({
      ...prev,
      currentPrice: prev.currentPrice + (Math.random() - 0.5) * 2,
      lastUpdated: new Date()
    }));
  };
  const logPrice = (timeSlot: 'open' | 'noon' | 'twoPM' | 'close') => {
    setSPYData(prev => ({
      ...prev,
      [`${timeSlot}Price`]: prev.currentPrice
    }));
  };
  const resetDay = () => {
    setSPYData(prev => ({
      ...prev,
      noonPrice: undefined,
      twoPMPrice: undefined,
      closePrice: undefined
    }));
    setPrediction(null);
  };
  const savePrediction = (predictionData: PredictionData) => {
    setPrediction(predictionData);
  };
  const renderScreen = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardScreen spyData={spyData} prediction={prediction} tradeData={tradeData} onLogPrice={logPrice} onResetDay={resetDay} />;
      case 'predict':
        return <PredictScreen currentPrice={spyData.currentPrice} onSavePrediction={savePrediction} existingPrediction={prediction} />;
      case 'history':
        return <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-300 mb-2">History</h2>
              <p className="text-gray-500">Historical data coming soon</p>
            </div>
          </div>;
      case 'metrics':
        return <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-300 mb-2">Metrics</h2>
              <p className="text-gray-500">Performance metrics coming soon</p>
            </div>
          </div>;
      default:
        return null;
    }
  };
  return <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      <HeaderBar currentPrice={spyData.currentPrice} lastUpdated={spyData.lastUpdated} onRefresh={refreshSPYData} />
      
      <main className="flex-1 overflow-y-auto pb-20">
        <AnimatePresence mode="wait">
          <motion.div key={activeTab} initial={{
          opacity: 0,
          y: 20
        }} animate={{
          opacity: 1,
          y: 0
        }} exit={{
          opacity: 0,
          y: -20
        }} transition={{
          duration: 0.2
        }} className="h-full">
            {renderScreen()}
          </motion.div>
        </AnimatePresence>
      </main>

      <BottomNavigationBar activeTab={activeTab} onTabChange={setActiveTab} />
    </div>;
}