import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, ReferenceLine, ResponsiveContainer, Tooltip } from 'recharts';

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
}

interface PLChartProps {
  data: PLData;
  height?: number;
  showBreakevens?: boolean;
  showCurrentPrice?: boolean;
}

export function PLChart({ 
  data, 
  height = 120, 
  showBreakevens = true, 
  showCurrentPrice = true 
}: PLChartProps) {
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
        <div className="bg-[#0B0D12] border border-white/8 rounded-lg p-2 shadow-lg">
          <p className="text-xs text-[#A7B3C5] mb-1">
            Price: ${label}
          </p>
          <p className={`text-xs font-mono font-medium ${isProfit ? 'text-[#16A34A]' : 'text-[#DC2626]'}`}>
            P&L: {isProfit ? '+' : ''}${pl.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="relative">
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
              r: 3, 
              fill: '#006072',
              stroke: '#E8ECF2',
              strokeWidth: 1
            }}
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