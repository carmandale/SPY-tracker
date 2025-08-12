import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Target, History, TrendingUp } from 'lucide-react';
import { DashboardScreen } from './DashboardScreen';
import { PredictScreen } from './PredictScreen';
import { HistoryScreen } from './HistoryScreen';
import { MetricsScreen } from './MetricsScreen';
type Screen = 'dashboard' | 'predict' | 'history' | 'metrics';
export function SPYTaTrackerApp() {
  const [activeScreen, setActiveScreen] = useState<Screen>('dashboard');
  const getCurrentDate = () => {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      timeZone: 'America/Chicago'
    });
  };
  const navItems = [{
    id: 'dashboard',
    icon: BarChart3,
    label: 'Dashboard'
  }, {
    id: 'predict',
    icon: Target,
    label: 'Predict'
  }, {
    id: 'history',
    icon: History,
    label: 'History'
  }, {
    id: 'metrics',
    icon: TrendingUp,
    label: 'Metrics'
  }] as const;
  const renderScreen = () => {
    switch (activeScreen) {
      case 'dashboard':
        return <DashboardScreen />;
      case 'predict':
        return <PredictScreen />;
      case 'history':
        return <HistoryScreen />;
      case 'metrics':
        return <MetricsScreen />;
      default:
        return <DashboardScreen />;
    }
  };
  return <div className="min-h-screen bg-[#0B0D12] text-[#E8ECF2] flex flex-col">
      {/* Global Header with Navigation */}
      <header className="border-b border-white/8">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-[#006072] rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">S</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold">SPY TA Tracker</h1>
              <p className="text-xs text-[#A7B3C5]">{getCurrentDate()} CST</p>
            </div>
          </div>
        </div>
        
        {/* Top Navigation */}
        <nav className="bg-[#12161D] px-4 pb-2">
          <div className="flex items-center gap-1">
            {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeScreen === item.id;
            return <motion.button key={item.id} onClick={() => setActiveScreen(item.id)} whileTap={{
              scale: 0.95
            }} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors relative ${isActive ? 'text-[#006072] bg-[#006072]/10' : 'text-[#A7B3C5] hover:text-[#E8ECF2]'}`}>
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{item.label}</span>
                  {isActive && <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#006072] rounded-full" />}
                </motion.button>;
          })}
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <motion.div key={activeScreen} initial={{
        opacity: 0,
        x: 20
      }} animate={{
        opacity: 1,
        x: 0
      }} exit={{
        opacity: 0,
        x: -20
      }} transition={{
        duration: 0.2
      }}>
          {renderScreen()}
        </motion.div>
      </main>
    </div>;
}