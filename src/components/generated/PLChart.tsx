import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, ReferenceLine, ReferenceArea, ResponsiveContainer, Tooltip, defs, linearGradient, stop } from 'recharts';
import { TrendingUp, TrendingDown, Clock, AlertTriangle, Target } from 'lucide-react';

interface PLPoint {
  underlying_price: number;
  total_pl: number;
  put_spread_pl: number;
  call_spread_pl: number;
}

interface PLData {
  tenor: string;
  strategy: string;
  points: PLPoint[];
  breakeven_lower: number;
  breakeven_upper: number;
  max_profit: number;
  max_loss: number;
  current_price: number;
  profit_zone_start: number;
  profit_zone_end: number;
  current_pl?: number;
  time_to_expiry?: number; // hours remaining
  winning_probability?: number;
}

interface PLChartProps {
  data: PLData;
  height?: number;
  showBreakevens?: boolean;
  showCurrentPrice?: boolean;
  variant?: 'mini' | 'standard' | 'expanded';
}

export function PLChart({ 
  data, 
  height, 
  showBreakevens = true, 
  showCurrentPrice = true,
  variant = 'standard'
}: PLChartProps) {
  // Dynamic height based on variant and mobile responsiveness
  const chartHeight = useMemo(() => {
    if (height) return height;
    
    const sizes = {
      mini: 200,      // Much larger than before (was 80px)
      standard: 320,  // Professional size (was 120px)  
      expanded: 420   // Full analysis view
    };
    
    const baseHeight = sizes[variant];
    const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
    return isMobile ? baseHeight : Math.min(baseHeight * 1.1, 500);
  }, [height, variant]);

  // Calculate current P&L if not provided
  const currentPL = useMemo(() => {
    if (data.current_pl !== undefined) return data.current_pl;
    
    const currentPoint = data.points.find(p => 
      Math.abs(p.underlying_price - data.current_price) < 0.5
    );
    return currentPoint?.total_pl || 0;
  }, [data]);

  // Determine tenor urgency and styling
  const tenorTheme = useMemo(() => {
    const hoursRemaining = data.time_to_expiry || 24;
    
    switch (data.tenor) {
      case '0DTE':
        return {
          urgency: 'high' as const,
          borderColor: '#DC2626',
          glowColor: hoursRemaining < 4 ? '#DC2626' : undefined,
          warningText: hoursRemaining < 2 ? 'EXPIRING SOON!' : undefined
        };
      case '1W':
        return {
          urgency: 'medium' as const,
          borderColor: '#F59E0B',
          glowColor: undefined,
          warningText: undefined
        };
      case '1M':
        return {
          urgency: 'low' as const,
          borderColor: '#10B981', 
          glowColor: undefined,
          warningText: undefined
        };
      default:
        return {
          urgency: 'medium' as const,
          borderColor: '#64748B',
          glowColor: undefined,
          warningText: undefined
        };
    }
  }, [data.tenor, data.time_to_expiry]);

  // Enhanced profit/loss status
  const plStatus = useMemo(() => {
    const isWinning = currentPL > 0;
    const withinProfitZone = data.current_price >= data.profit_zone_start && 
                            data.current_price <= data.profit_zone_end;
    
    return {
      isWinning,
      withinProfitZone,
      statusColor: isWinning ? '#00D4AA' : '#FF6B6B',
      statusText: isWinning ? 'WINNING' : 'LOSING',
      statusIcon: isWinning ? TrendingUp : TrendingDown,
      urgencyLevel: Math.abs(currentPL / (data.max_profit || 1))
    };
  }, [currentPL, data]);

  const StatusIcon = plStatus.statusIcon;
  const chartData = useMemo(() => {
    return data.points.map(point => ({
      price: point.underlying_price,
      pl: point.total_pl,
      formatted_price: point.underlying_price.toFixed(0),
      formatted_pl: point.total_pl >= 0 ? `+$${point.total_pl.toFixed(2)}` : `-$${Math.abs(point.total_pl).toFixed(2)}`
    }));
  }, [data.points]);

  const { minPrice, maxPrice, minPL, maxPL } = useMemo(() => {
    const prices = data.points.map(p => p.underlying_price);
    const pls = data.points.map(p => p.total_pl);
    
    return {
      minPrice: Math.min(...prices),
      maxPrice: Math.max(...prices),
      minPL: Math.min(...pls),
      maxPL: Math.max(...pls)
    };
  }, [data.points]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const pl = payload[0].value;
      const isProfit = pl >= 0;
      
      return (
        <div className="bg-[#0B0D12] border border-white/8 rounded-lg p-3 shadow-lg min-w-[120px]">
          <p className="text-sm text-[#A7B3C5] mb-1 font-medium">
            Price: ${parseFloat(label).toFixed(0)}
          </p>
          <p className={`text-sm font-mono font-bold ${isProfit ? 'text-[#16A34A]' : 'text-[#DC2626]'}`}>
            P&L: {isProfit ? '+' : ''}${pl.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="relative touch-pan-y">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
          <XAxis 
            dataKey="price"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 10, fill: '#A7B3C5' }}
            domain={[minPrice, maxPrice]}
            type="number"
            scale="linear"
            tickFormatter={(value) => `$${value.toFixed(0)}`}
            interval="preserveStartEnd"
          />
          <YAxis 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 10, fill: '#A7B3C5' }}
            domain={[minPL * 1.1, maxPL * 1.1]}
            tickFormatter={(value) => value >= 0 ? `+$${value.toFixed(0)}` : `-$${Math.abs(value).toFixed(0)}`}
            width={40}
          />
          
          {/* Zero line */}
          <ReferenceLine 
            y={0} 
            stroke="#A7B3C5" 
            strokeDasharray="2 2" 
            strokeWidth={1}
            opacity={0.5}
          />
          
          {/* Breakeven lines */}
          {showBreakevens && (
            <>
              <ReferenceLine 
                x={data.breakeven_lower} 
                stroke="#006072" 
                strokeDasharray="3 3" 
                strokeWidth={1}
                opacity={0.7}
              />
              <ReferenceLine 
                x={data.breakeven_upper} 
                stroke="#006072" 
                strokeDasharray="3 3" 
                strokeWidth={1}
                opacity={0.7}
              />
            </>
          )}
          
          {/* Current price line */}
          {showCurrentPrice && (
            <ReferenceLine 
              x={data.current_price} 
              stroke="#E8ECF2" 
              strokeWidth={2}
              opacity={0.8}
            />
          )}
          
          {/* P&L curve */}
          <Line
            type="monotone"
            dataKey="pl"
            stroke="#006072"
            strokeWidth={2}
            dot={false}
            activeDot={{ 
              r: 4, 
              fill: '#006072',
              stroke: '#E8ECF2',
              strokeWidth: 2,
              style: { touchAction: 'auto' }
            }}
            connectNulls={false}
          />
          
          <Tooltip content={<CustomTooltip />} />
        </LineChart>
      </ResponsiveContainer>
      
      {/* Chart annotations */}
      <div className="absolute top-1 right-1 flex gap-1">
        {showBreakevens && (
          <div className="text-xs text-[#006072] bg-[#0B0D12]/80 px-1 rounded">
            BE: ${data.breakeven_lower.toFixed(0)}-${data.breakeven_upper.toFixed(0)}
          </div>
        )}
      </div>
    </div>
  );
}

interface PLChartMiniProps {
  data: PLData;
}

export function PLChartMini({ data }: PLChartMiniProps) {
  return (
    <PLChart 
      data={data} 
      height={80} 
      showBreakevens={false} 
      showCurrentPrice={true}
    />
  );
}