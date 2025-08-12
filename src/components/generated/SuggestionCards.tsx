import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Activity, DollarSign, Target, AlertCircle, BarChart3, Eye, EyeOff } from 'lucide-react';
import { PLChartMini } from './PLChart';

interface Strike {
  put_long: number;
  put_short: number;
  call_short: number;
  call_long: number;
}

interface Suggestion {
  tenor: string;
  strategy: string;
  put_short_strike?: number;
  put_long_strike?: number;
  call_short_strike?: number;
  call_long_strike?: number;
  center_strike?: number;
  wings?: number;
  expected_move?: number;
  max_profit?: number;
  max_loss?: number;
  breakeven_lower?: number;
  breakeven_upper?: number;
  profit_target?: number;
  stop_loss?: number;
  rationale: string;
  note: string;
  management_notes?: string;
}

interface SuggestionCardsProps {
  date?: string;
}

export function SuggestionCards({ date }: SuggestionCardsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [plData, setPLData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCharts, setShowCharts] = useState(false);

  useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        const targetDate = date || new Date().toLocaleDateString('en-CA', {
          timeZone: 'America/Chicago'
        });
        
        const response = await fetch(`http://localhost:8000/suggestions/${targetDate}`);
        if (response.ok) {
          const data = await response.json();
          setSuggestions(data.suggestions || []);
        }
      } catch (error) {
        console.error('Failed to fetch suggestions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSuggestions();
  }, [date]);

  // Fetch P&L data when charts are shown
  useEffect(() => {
    if (!showCharts || suggestions.length === 0) return;

    const fetchPLData = async () => {
      try {
        const targetDate = date || new Date().toLocaleDateString('en-CA', {
          timeZone: 'America/Chicago'
        });
        
        const response = await fetch(`http://localhost:8000/suggestions/${targetDate}/pl-data`);
        if (response.ok) {
          const data = await response.json();
          setPLData(data.pl_data || []);
        }
      } catch (error) {
        console.error('Failed to fetch P&L data:', error);
        setPLData([]);
      }
    };

    fetchPLData();
  }, [showCharts, suggestions, date]);

  const getTenorBadgeColor = (tenor: string) => {
    switch (tenor) {
      case '0DTE': return 'bg-red-500/10 text-red-400';
      case '1W': return 'bg-yellow-500/10 text-yellow-400';
      case '1M': return 'bg-green-500/10 text-green-400';
      default: return 'bg-gray-500/10 text-gray-400';
    }
  };

  const getStrategyIcon = (strategy: string) => {
    return strategy === 'Iron Condor' ? <Activity className="w-4 h-4" /> : <Target className="w-4 h-4" />;
  };

  const formatStrike = (value?: number) => {
    return value ? value.toFixed(0) : '---';
  };

  const formatCurrency = (value?: number) => {
    if (!value) return '$---';
    return `$${value.toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <p className="text-sm text-[#A7B3C5]">Loading suggestions...</p>
      </div>
    );
  }

  if (suggestions.length === 0) {
    return (
      <div className="bg-[#12161D] rounded-xl p-4 border border-white/8">
        <p className="text-sm text-[#A7B3C5]">No suggestions available. Enter predictions to generate suggestions.</p>
      </div>
    );
  }

  // Find P&L data for a specific suggestion
  const findPLData = (suggestion: Suggestion) => {
    return plData.find(pl => 
      pl.tenor === suggestion.tenor && 
      pl.strategy === suggestion.strategy
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-[#A7B3C5]">Option Structure Suggestions</h3>
        <button
          onClick={() => setShowCharts(!showCharts)}
          className="flex items-center gap-1 px-2 py-1 text-xs text-[#A7B3C5] hover:text-[#E8ECF2] transition-colors"
        >
          {showCharts ? <EyeOff className="w-3 h-3" /> : <BarChart3 className="w-3 h-3" />}
          {showCharts ? 'Hide P&L' : 'Show P&L'}
        </button>
      </div>
      
      {suggestions.map((suggestion, index) => (
        <motion.div
          key={`${suggestion.tenor}-${suggestion.strategy}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="bg-[#12161D] rounded-xl p-4 border border-white/8"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {getStrategyIcon(suggestion.strategy)}
              <h4 className="text-sm font-medium text-[#E8ECF2]">{suggestion.strategy}</h4>
              <span className={`px-2 py-1 text-xs rounded-full ${getTenorBadgeColor(suggestion.tenor)}`}>
                {suggestion.tenor}
              </span>
            </div>
            <span className="text-xs text-[#A7B3C5]">
              EM: {formatCurrency(suggestion.expected_move)}
            </span>
          </div>

          {/* Strike Prices */}
          <div className="bg-[#0B0D12] rounded-lg p-3 mb-3">
            {suggestion.strategy === 'Iron Condor' ? (
              <div className="flex justify-between items-center">
                <div className="text-xs text-[#A7B3C5]">
                  <span className="block mb-1">Put Side</span>
                  <span className="font-mono text-[#E8ECF2]">
                    {formatStrike(suggestion.put_long_strike)}/{formatStrike(suggestion.put_short_strike)}
                  </span>
                </div>
                <div className="text-xs text-[#006072]">•</div>
                <div className="text-xs text-[#A7B3C5]">
                  <span className="block mb-1">Call Side</span>
                  <span className="font-mono text-[#E8ECF2]">
                    {formatStrike(suggestion.call_short_strike)}/{formatStrike(suggestion.call_long_strike)}
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-center text-xs text-[#A7B3C5]">
                <span className="block mb-1">Butterfly Structure</span>
                <span className="font-mono text-[#E8ECF2]">
                  {formatStrike(suggestion.put_long_strike)} / {formatStrike(suggestion.center_strike)} / {formatStrike(suggestion.call_long_strike)}
                </span>
              </div>
            )}
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="bg-[#0B0D12] rounded-lg p-2">
              <p className="text-xs text-[#A7B3C5] mb-1">Max Profit</p>
              <p className="text-sm font-mono font-bold text-[#16A34A]">
                {formatCurrency(suggestion.max_profit)}
              </p>
            </div>
            <div className="bg-[#0B0D12] rounded-lg p-2">
              <p className="text-xs text-[#A7B3C5] mb-1">Max Loss</p>
              <p className="text-sm font-mono font-bold text-[#DC2626]">
                {formatCurrency(suggestion.max_loss)}
              </p>
            </div>
            <div className="bg-[#0B0D12] rounded-lg p-2">
              <p className="text-xs text-[#A7B3C5] mb-1">Profit Target</p>
              <p className="text-sm font-mono text-[#E8ECF2]">
                {formatCurrency(suggestion.profit_target)}
              </p>
            </div>
            <div className="bg-[#0B0D12] rounded-lg p-2">
              <p className="text-xs text-[#A7B3C5] mb-1">Stop Loss</p>
              <p className="text-sm font-mono text-[#E8ECF2]">
                {formatCurrency(suggestion.stop_loss)}
              </p>
            </div>
          </div>

          {/* Breakevens */}
          <div className="bg-[#0B0D12] rounded-lg p-2 mb-3">
            <p className="text-xs text-[#A7B3C5] mb-1">Breakeven Points</p>
            <div className="flex justify-between">
              <span className="text-xs font-mono text-[#E8ECF2]">
                Lower: ${formatStrike(suggestion.breakeven_lower)}
              </span>
              <span className="text-xs font-mono text-[#E8ECF2]">
                Upper: ${formatStrike(suggestion.breakeven_upper)}
              </span>
            </div>
          </div>

          {/* P&L Chart */}
          {showCharts && (() => {
            const suggestPLData = findPLData(suggestion);
            return suggestPLData ? (
              <div className="bg-[#0B0D12] rounded-lg p-2 mb-3">
                <div className="flex items-center gap-1 mb-2">
                  <BarChart3 className="w-3 h-3 text-[#006072]" />
                  <span className="text-xs text-[#A7B3C5]">P&L Chart</span>
                </div>
                <PLChartMini data={suggestPLData} />
              </div>
            ) : (
              <div className="bg-[#0B0D12] rounded-lg p-2 mb-3">
                <p className="text-xs text-[#A7B3C5]">Loading P&L chart...</p>
              </div>
            );
          })()}

          {/* Management Notes */}
          {suggestion.management_notes && (
            <div className="flex items-start gap-2">
              <AlertCircle className="w-3 h-3 text-[#006072] mt-0.5 flex-shrink-0" />
              <p className="text-xs text-[#A7B3C5]">
                {suggestion.management_notes}
              </p>
            </div>
          )}
        </motion.div>
      ))}
    </div>
  );
}