import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Target, History, TrendingUp } from 'lucide-react';
type TabType = 'dashboard' | 'predict' | 'history' | 'metrics';
interface BottomNavigationBarProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}
interface NavItem {
  id: TabType;
  label: string;
  icon: React.ComponentType<{
    className?: string;
  }>;
}
const navItems: NavItem[] = [{
  id: 'dashboard',
  label: 'Dashboard',
  icon: BarChart3
}, {
  id: 'predict',
  label: 'Predict',
  icon: Target
}, {
  id: 'history',
  label: 'History',
  icon: History
}, {
  id: 'metrics',
  label: 'Metrics',
  icon: TrendingUp
}];
export function BottomNavigationBar({
  activeTab,
  onTabChange
}: BottomNavigationBarProps) {
  return <nav className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 px-2 py-2 z-50">
      <div className="flex items-center justify-around">
        {navItems.map(item => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        return <motion.button key={item.id} whileTap={{
          scale: 0.95
        }} onClick={() => onTabChange(item.id)} className={`flex flex-col items-center justify-center px-3 py-2 rounded-lg transition-colors touch-manipulation min-w-0 flex-1 ${isActive ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'}`} aria-label={`Navigate to ${item.label}`}>
              <Icon className="w-5 h-5 mb-1" />
              <span className="text-xs font-medium truncate">{item.label}</span>
              
              {isActive && <motion.div layoutId="activeTab" className="absolute inset-0 bg-blue-600 rounded-lg -z-10" initial={false} transition={{
            type: 'spring',
            stiffness: 500,
            damping: 30
          }} />}
            </motion.button>;
      })}
      </div>
    </nav>;
}