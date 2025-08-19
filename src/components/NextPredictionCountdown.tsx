import { useState, useEffect } from 'react';
import { apiClient } from '../utils/apiClient';

interface NextPredictionResponse {
  next_run: string;
  next_run_cst: string;
  time_until: string;
  market_status: string;
  is_weekend: boolean;
  is_holiday: boolean;
}

export function NextPredictionCountdown() {
  const [data, setData] = useState<NextPredictionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNextPrediction = async () => {
    try {
      const response = await apiClient.getNextPredictionTime();
      setData(response);
      setError(null);
    } catch (err) {
      setError('Unable to load prediction time');
      console.error('Failed to fetch next prediction:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchNextPrediction();

    // Update every minute
    const interval = setInterval(() => {
      fetchNextPrediction();
    }, 60 * 1000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="text-slate-500">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="text-red-500">Unable to load prediction time</div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  // Determine the display based on market status
  const getStatusDisplay = () => {
    if (data.is_weekend) {
      return {
        title: 'Market Closed',
        subtitle: 'Weekend',
        message: `Next prediction on Monday at 8:00 AM CST`
      };
    }

    if (data.is_holiday) {
      // Extract holiday name from market_status if available
      const holidayMatch = data.market_status.match(/holiday \((.*?)\)/);
      const holidayName = holidayMatch ? holidayMatch[1] : 'Holiday';
      return {
        title: 'Market Closed',
        subtitle: `Holiday - ${holidayName}`,
        message: `Next prediction: ${data.next_run_cst}`
      };
    }

    if (data.market_status === 'open') {
      return {
        title: 'Market Open',
        subtitle: 'Trading in Progress',
        message: `Next prediction tomorrow at 8:00 AM CST`
      };
    }

    // Default for pre-market or after-hours
    return {
      title: 'Next Prediction',
      subtitle: data.time_until,
      message: data.next_run_cst
    };
  };

  const status = getStatusDisplay();

  return (
    <div className="rounded-lg bg-slate-800/50 p-4 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-slate-300">{status.title}</h3>
          <p className="mt-1 text-lg font-semibold text-white">{status.subtitle}</p>
          <p className="mt-1 text-xs text-slate-400">{status.message}</p>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/10">
          <svg
            className="h-5 w-5 text-emerald-500"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
    </div>
  );
}