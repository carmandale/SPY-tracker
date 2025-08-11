import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Target, Calendar, BarChart3, Award, AlertTriangle, Info } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
interface MetricsPeriod {
  value: '7d' | '30d' | '90d' | 'all';
  label: string;
}
interface PerformanceMetric {
  label: string;
  value: string;
  change: number;
  icon: React.ElementType;
  color: string;
}
export function MetricsScreen() {
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d' | 'all'>('30d');
  const periods: MetricsPeriod[] = [{
    value: '7d',
    label: '7D'
  }, {
    value: '30d',
    label: '30D'
  }, {
    value: '90d',
    label: '90D'
  }, {
    value: 'all',
    label: 'All'
  }];
  const performanceMetrics: PerformanceMetric[] = [{
    label: 'Range Hit Rate',
    value: '73%',
    change: +5.2,
    icon: Target,
    color: 'text-[#16A34A]'
  }, {
    label: 'Median Abs Error',
    value: '$1.25',
    change: -0.15,
    icon: TrendingUp,
    color: 'text-[#E8ECF2]'
  }, {
    label: 'Avg Range Width',
    value: '$4.75',
    change: +0.25,
    icon: BarChart3,
    color: 'text-[#006072]'
  }, {
    label: 'Total Predictions',
    value: '47',
    change: +12,
    icon: Calendar,
    color: 'text-[#A7B3C5]'
  }];
  const accuracyTrendData = [{
    date: 'Jan 1',
    accuracy: 65
  }, {
    date: 'Jan 8',
    accuracy: 70
  }, {
    date: 'Jan 15',
    accuracy: 68
  }, {
    date: 'Jan 22',
    accuracy: 75
  }, {
    date: 'Jan 29',
    accuracy: 73
  }, {
    date: 'Feb 5',
    accuracy: 78
  }, {
    date: 'Feb 12',
    accuracy: 76
  }] as any[];
  const errorDistributionData = [{
    range: '0-0.5',
    count: 12
  }, {
    range: '0.5-1',
    count: 18
  }, {
    range: '1-2',
    count: 11
  }, {
    range: '2-3',
    count: 4
  }, {
    range: '3+',
    count: 2
  }] as any[];
  const biasPerformanceData = [{
    name: 'Bullish',
    value: 78,
    color: '#16A34A'
  }, {
    name: 'Bearish',
    value: 71,
    color: '#DC2626'
  }, {
    name: 'Neutral',
    value: 69,
    color: '#A7B3C5'
  }] as any[];
  const dayTypeData = [{
    type: 'Normal',
    predictions: 32,
    accuracy: 75
  }, {
    type: 'FOMC',
    predictions: 8,
    accuracy: 62
  }, {
    type: 'OpEx',
    predictions: 5,
    accuracy: 80
  }, {
    type: 'Earnings',
    predictions: 2,
    accuracy: 50
  }] as any[];
  const calibrationTips = [{
    type: 'success',
    title: 'Strong Performance',
    message: 'Your bullish predictions are highly accurate. Keep leveraging technical analysis.',
    icon: Award
  }, {
    type: 'warning',
    title: 'FOMC Challenges',
    message: 'Consider wider ranges on Fed days. Volatility often exceeds expectations.',
    icon: AlertTriangle
  }, {
    type: 'info',
    title: 'Range Optimization',
    message: 'Your ranges are slightly narrow. Expanding by 10-15% could improve hit rate.',
    icon: Info
  }] as any[];
  const getTipColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'border-[#16A34A] bg-[#16A34A]/10';
      case 'warning':
        return 'border-[#DC2626] bg-[#DC2626]/10';
      default:
        return 'border-[#006072] bg-[#006072]/10';
    }
  };
  const getTipIconColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-[#16A34A]';
      case 'warning':
        return 'text-[#DC2626]';
      default:
        return 'text-[#006072]';
    }
  };
  return <div className="p-4 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-xl font-semibold mb-2">Performance Metrics</h1>
        <p className="text-sm text-[#A7B3C5]">
          Detailed analysis of your prediction accuracy
        </p>
      </div>

      {/* Period Selector */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} className="bg-[#12161D] rounded-xl p-2 border border-white/8">
        <div className="flex items-center justify-center gap-1">
          {periods.map(period => <button key={period.value} onClick={() => setSelectedPeriod(period.value)} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${selectedPeriod === period.value ? 'bg-[#006072] text-white' : 'text-[#A7B3C5] hover:text-[#E8ECF2] hover:bg-white/5'}`}>
              {period.label}
            </button>)}
        </div>
      </motion.div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 gap-3">
        {performanceMetrics.map((metric, index) => {
        const Icon = metric.icon;
        return <motion.div key={metric.label} initial={{
          opacity: 0,
          y: 20
        }} animate={{
          opacity: 1,
          y: 0
        }} transition={{
          delay: index * 0.1
        }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
              <div className="flex items-center justify-between mb-2">
                <Icon className={`w-5 h-5 ${metric.color}`} />
                <span className={`text-xs font-medium ${metric.change > 0 ? 'text-[#16A34A]' : 'text-[#DC2626]'}`}>
                  {metric.change > 0 ? '+' : ''}{metric.change}
                </span>
              </div>
              <p className="text-lg font-mono font-bold mb-1">{metric.value}</p>
              <p className="text-xs text-[#A7B3C5]">{metric.label}</p>
            </motion.div>;
      })}
      </div>

      {/* Accuracy Trend Chart */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.2
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <h3 className="text-lg font-semibold mb-4">Accuracy Trend</h3>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={accuracyTrendData}>
              <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{
              fontSize: 12,
              fill: '#A7B3C5'
            }} />
              <YAxis domain={[60, 85]} axisLine={false} tickLine={false} tick={{
              fontSize: 12,
              fill: '#A7B3C5'
            }} />
              <Line type="monotone" dataKey="accuracy" stroke="#006072" strokeWidth={3} dot={{
              fill: '#006072',
              strokeWidth: 0,
              r: 4
            }} activeDot={{
              r: 6,
              fill: '#006072'
            }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Error Distribution */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.3
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <h3 className="text-lg font-semibold mb-4">Error Distribution</h3>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={errorDistributionData}>
              <XAxis dataKey="range" axisLine={false} tickLine={false} tick={{
              fontSize: 12,
              fill: '#A7B3C5'
            }} />
              <YAxis axisLine={false} tickLine={false} tick={{
              fontSize: 12,
              fill: '#A7B3C5'
            }} />
              <Bar dataKey="count" fill="#006072" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="text-xs text-[#A7B3C5] mt-2 text-center">
          Error ranges in dollars ($)
        </p>
      </motion.div>

      {/* Bias Performance */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.4
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <h3 className="text-lg font-semibold mb-4">Performance by Bias</h3>
        <div className="flex items-center justify-center h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={biasPerformanceData} cx="50%" cy="50%" innerRadius={40} outerRadius={80} paddingAngle={5} dataKey="value">
                {biasPerformanceData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex justify-center gap-4 mt-4">
          {biasPerformanceData.map(item => <div key={item.name} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{
            backgroundColor: item.color
          }} />
              <span className="text-xs text-[#A7B3C5]">
                {item.name}: {item.value}%
              </span>
            </div>)}
        </div>
      </motion.div>

      {/* Day Type Analysis */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.5
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <h3 className="text-lg font-semibold mb-4">Performance by Day Type</h3>
        <div className="space-y-3">
          {dayTypeData.map((day, index) => <div key={day.type} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium w-16">{day.type}</span>
                <div className="flex-1 bg-white/5 rounded-full h-2 overflow-hidden">
                  <motion.div initial={{
                width: 0
              }} animate={{
                width: `${day.accuracy}%`
              }} transition={{
                delay: index * 0.1,
                duration: 0.8
              }} className="h-full bg-[#006072] rounded-full" />
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-mono font-bold">{day.accuracy}%</p>
                <p className="text-xs text-[#A7B3C5]">{day.predictions} pred</p>
              </div>
            </div>)}
        </div>
      </motion.div>

      {/* Calibration Tips */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.6
    }} className="space-y-3">
        <h3 className="text-lg font-semibold">Calibration Tips</h3>
        {calibrationTips.map((tip, index) => {
        const Icon = tip.icon;
        return <motion.div key={index} initial={{
          opacity: 0,
          x: -20
        }} animate={{
          opacity: 1,
          x: 0
        }} transition={{
          delay: 0.6 + index * 0.1
        }} className={`border rounded-xl p-4 ${getTipColor(tip.type)}`}>
              <div className="flex items-start gap-3">
                <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${getTipIconColor(tip.type)}`} />
                <div>
                  <h4 className="font-semibold mb-1">{tip.title}</h4>
                  <p className="text-sm text-[#A7B3C5]">{tip.message}</p>
                </div>
              </div>
            </motion.div>;
      })}
      </motion.div>

      {/* Summary Stats */}
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      delay: 0.7
    }} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <h3 className="text-lg font-semibold mb-4">Summary Statistics</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-[#A7B3C5]">Best Streak:</span>
              <span className="font-mono font-bold">8 hits</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#A7B3C5]">Worst Streak:</span>
              <span className="font-mono font-bold">3 misses</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#A7B3C5]">Best Day:</span>
              <span className="font-mono font-bold">$0.15 error</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-[#A7B3C5]">Avg Range:</span>
              <span className="font-mono font-bold">$4.75</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#A7B3C5]">Max Error:</span>
              <span className="font-mono font-bold">$5.25</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#A7B3C5]">Min Error:</span>
              <span className="font-mono font-bold">$0.05</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>;
}