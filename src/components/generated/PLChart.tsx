import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, ReferenceLine, ReferenceArea, ResponsiveContainer, Tooltip } from 'recharts';
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
      const price = parseFloat(label);
      const pl = payload[0].value;
      const isProfit = pl >= 0;
      
      // Calculate distance from current price and breakevens
      const priceDistance = ((price - data.current_price) / data.current_price * 100);
      const toBreakevenLower = Math.abs(price - data.breakeven_lower);
      const toBreakevenUpper = Math.abs(price - data.breakeven_upper);
      const nearestBreakeven = toBreakevenLower < toBreakevenUpper ? 
        { distance: toBreakevenLower, label: 'Lower BE' } : 
        { distance: toBreakevenUpper, label: 'Upper BE' };
      
      // Determine zone
      const inProfitZone = price >= data.profit_zone_start && price <= data.profit_zone_end;
      const zone = inProfitZone ? 'Profit Zone' : 
                   price < data.breakeven_lower ? 'Loss Zone (Put Side)' : 
                   price > data.breakeven_upper ? 'Loss Zone (Call Side)' : 'Breakeven Zone';
      
      return (
        <div className="bg-[#0B0D12]/95 border border-white/12 rounded-lg p-4 shadow-2xl min-w-[180px] backdrop-blur-sm">
          {/* Price Header */}
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-[#A7B3C5] font-medium">
              Price: ${price.toFixed(2)}
            </p>
            <p className={`text-xs px-2 py-1 rounded-full ${
              Math.abs(priceDistance) < 1 ? 'bg-yellow-500/20 text-yellow-300' :
              Math.abs(priceDistance) < 3 ? 'bg-blue-500/20 text-blue-300' :
              'bg-gray-500/20 text-gray-300'
            }`}>
              {priceDistance >= 0 ? '+' : ''}{priceDistance.toFixed(1)}%
            </p>
          </div>
          
          {/* P&L Display */}
          <div className="mb-3">
            <p className={`text-lg font-mono font-bold ${isProfit ? 'text-[#00D4AA]' : 'text-[#FF6B6B]'}`}>
              {isProfit ? '+' : ''}${pl.toFixed(2)}
            </p>
            <p className="text-xs text-[#A7B3C5]">
              P&L at this price
            </p>
          </div>

          {/* Zone Information */}
          <div className="border-t border-white/8 pt-2">
            <p className={`text-xs font-medium ${
              zone === 'Profit Zone' ? 'text-[#00D4AA]' : 
              zone.includes('Loss') ? 'text-[#FF6B6B]' : 'text-[#F59E0B]'
            }`}>
              {zone}
            </p>
            {nearestBreakeven.distance < 10 && (
              <p className="text-xs text-[#64748B] mt-1">
                ${nearestBreakeven.distance.toFixed(2)} from {nearestBreakeven.label}
              </p>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div 
      className={`relative touch-pan-y rounded-xl overflow-hidden ${
        tenorTheme.urgency === 'high' ? 'ring-2 ring-red-500/30' : 
        tenorTheme.urgency === 'medium' ? 'ring-1 ring-yellow-500/20' : ''
      }`}
      style={{
        background: `linear-gradient(135deg, rgba(${tenorTheme.urgency === 'high' ? '220, 38, 38' : tenorTheme.urgency === 'medium' ? '245, 158, 11' : '16, 185, 129'}, 0.02) 0%, rgba(11, 13, 18, 0.8) 100%)`,
        boxShadow: tenorTheme.glowColor ? `0 0 20px ${tenorTheme.glowColor}33` : undefined
      }}
    >
      {/* Enhanced Header with Live P&L Status */}
      {variant !== 'mini' && (
        <div className="absolute top-3 left-3 right-3 z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
              plStatus.isWinning 
                ? 'bg-[#00D4AA]/20 text-[#00D4AA] border border-[#00D4AA]/30' 
                : 'bg-[#FF6B6B]/20 text-[#FF6B6B] border border-[#FF6B6B]/30'
            }`}>
              <StatusIcon className="w-3 h-3" />
              {plStatus.statusText}
              <span className="font-mono">
                {currentPL >= 0 ? '+' : ''}${currentPL.toFixed(0)}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {tenorTheme.warningText && (
              <div className="flex items-center gap-1 px-2 py-1 bg-red-500/20 text-red-300 rounded-full text-xs font-medium animate-pulse">
                <AlertTriangle className="w-3 h-3" />
                {tenorTheme.warningText}
              </div>
            )}
            
            {variant === 'expanded' && data.time_to_expiry && (
              <div className="flex items-center gap-1 px-2 py-1 bg-[#0B0D12]/60 text-[#A7B3C5] rounded-full text-xs">
                <Clock className="w-3 h-3" />
                {data.time_to_expiry < 24 ? `${data.time_to_expiry.toFixed(0)}h` : `${(data.time_to_expiry/24).toFixed(1)}d`}
              </div>
            )}
          </div>
        </div>
      )}
      
      <ResponsiveContainer width="100%" height={chartHeight}>
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
          
          {/* Profit zone highlighting */}
          <ReferenceArea
            x1={data.profit_zone_start}
            x2={data.profit_zone_end}
            fill="#00D4AA"
            fillOpacity={0.08}
            stroke="none"
          />
          
          {/* Current price line with enhanced styling */}
          {showCurrentPrice && (
            <>
              <ReferenceLine 
                x={data.current_price} 
                stroke="#FFD700"
                strokeWidth={3}
                strokeDasharray="none"
                opacity={0.9}
              />
              {/* Current P&L indicator dot */}
              <ReferenceLine 
                x={data.current_price}
                y={currentPL}
                stroke="none"
              />
            </>
          )}
          
          {/* Enhanced P&L curve */}
          <Line
            type="monotone"
            dataKey="pl"
            stroke={plStatus.isWinning ? '#00D4AA' : '#FF6B6B'}
            strokeWidth={variant === 'mini' ? 2 : 3}
            dot={false}
            activeDot={{ 
              r: variant === 'mini' ? 4 : 6, 
              fill: plStatus.isWinning ? '#00D4AA' : '#FF6B6B',
              stroke: '#E8ECF2',
              strokeWidth: 2,
              style: { touchAction: 'auto' },
              className: 'drop-shadow-lg'
            }}
            connectNulls={false}
          />
          
          <Tooltip content={<CustomTooltip />} />
        </LineChart>
      </ResponsiveContainer>
      
      {/* Enhanced Chart Annotations */}
      <div className="absolute bottom-2 left-2 right-2 flex items-end justify-between">
        <div className="flex flex-col gap-1">
          {variant !== 'mini' && (
            <div className="flex items-center gap-2">
              <div className="text-xs text-[#A7B3C5] bg-[#0B0D12]/80 px-2 py-1 rounded-full">
                Current: ${data.current_price.toFixed(2)}
              </div>
              <div className={`text-xs font-mono font-bold px-2 py-1 rounded-full ${
                plStatus.isWinning 
                  ? 'bg-[#00D4AA]/20 text-[#00D4AA]' 
                  : 'bg-[#FF6B6B]/20 text-[#FF6B6B]'
              }`}>
                {currentPL >= 0 ? '+' : ''}${currentPL.toFixed(0)}
              </div>
            </div>
          )}
          
          {showBreakevens && (
            <div className="text-xs text-[#64748B] bg-[#0B0D12]/80 px-2 py-1 rounded-full">
              BE: ${data.breakeven_lower.toFixed(0)} - ${data.breakeven_upper.toFixed(0)}
            </div>
          )}
        </div>
        
        <div className="flex flex-col items-end gap-1">
          {variant === 'expanded' && (
            <div className="text-xs text-[#16A34A] bg-[#0B0D12]/80 px-2 py-1 rounded-full">
              Max: +${data.max_profit.toFixed(0)}
            </div>
          )}
          
          <div className="flex items-center gap-1">
            <Target className="w-3 h-3 text-[#A7B3C5]" />
            <div className="text-xs text-[#A7B3C5] bg-[#0B0D12]/80 px-2 py-1 rounded-full">
              {data.strategy} • {data.tenor}
            </div>
          </div>
        </div>
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
      variant="mini"
      showBreakevens={false} 
      showCurrentPrice={true}
    />
  );
}

// Enhanced chart variants for different use cases
export function PLChartStandard({ data, showBreakevens = true }: { data: PLData, showBreakevens?: boolean }) {
  return (
    <PLChart 
      data={data} 
      variant="standard"
      showBreakevens={showBreakevens} 
      showCurrentPrice={true}
    />
  );
}

export function PLChartExpanded({ data }: { data: PLData }) {
  return (
    <PLChart 
      data={data} 
      variant="expanded"
      showBreakevens={true} 
      showCurrentPrice={true}
    />
  );
}