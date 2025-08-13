import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../../utils/apiClient';

type AICheckpoint = 'open' | 'noon' | 'twoPM' | 'close';

type AIPrediction = {
  checkpoint: AICheckpoint;
  predicted_price: number;
  confidence: number;
  reasoning: string;
  actual_price?: number | null;
  prediction_error?: number | null;
};

type AIDayPreview = {
  date: string;
  market_context: string; // analysis text
  pre_market_price?: number | null;
  predictions: AIPrediction[];
  sentiment?: {
    direction?: string;
    confidence?: number;
    regime?: string;
    factors?: string[];
  } | null;
};

type DayResponse = {
  id: number;
  date: string;
  predLow: number | null;
  predHigh: number | null;
  source?: string | null;
  locked?: boolean | null;
  volCtx?: string | null;
  notes?: string | null;
};

function formatDateCST(d: Date) {
  return d.toLocaleDateString('en-CA', { timeZone: 'America/Chicago' });
}

export function PredictScreen() {
  const today = useMemo(() => formatDateCST(new Date()), []);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lockedDay, setLockedDay] = useState<DayResponse | null>(null);
  const [aiPreview, setAiPreview] = useState<AIDayPreview | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [lookbackDays, setLookbackDays] = useState<number>(5);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        // 1) Check if day is already created/locked
        try {
          const day: DayResponse = await api.getPrediction(today);
          setLockedDay(day);
        } catch (dayError) {
          setLockedDay(null);
        }

        // 2) Load AI preview for richer info (analysis + per-checkpoint)
        try {
          const ai: AIDayPreview = await api.getAIPredictions(today);
          setAiPreview(ai);
        } catch (aiError) {
          setAiPreview(null);
        }
      } catch (e: any) {
        setError(e?.message ?? 'Failed to load AI predictions');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [today]);

  const createAndLock = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const resp = await fetch(`http://localhost:8000/ai/predict/${today}?lookbackDays=${lookbackDays}`, {
        method: 'POST',
      });
      if (resp.status === 409) {
        // already locked
        const dayResp = await fetch(`http://localhost:8000/day/${today}`);
        if (dayResp.ok) setLockedDay(await dayResp.json());
        return;
      }
      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(`Create failed (${resp.status}): ${txt}`);
      }
      // refresh day
      const dayResp = await fetch(`http://localhost:8000/day/${today}`);
      if (dayResp.ok) setLockedDay(await dayResp.json());
    } catch (e: any) {
      setError(e?.message ?? 'Failed to create & lock');
    } finally {
      setSubmitting(false);
    }
  };

  const locked = Boolean(lockedDay?.locked && lockedDay?.source === 'ai');

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-[#E8ECF2]">AI Prediction</h2>
          <p className="text-sm text-[#A7B3C5]">{today} (CST)</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-[#A7B3C5]">Lookback</label>
          <select
            className="border border-white/8 rounded px-2 py-1 text-sm bg-[#12161D] text-[#E8ECF2]"
            value={lookbackDays}
            onChange={(e) => setLookbackDays(Number(e.target.value))}
            disabled={locked || submitting}
          >
            <option value={3}>3</option>
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
          </select>
          {locked ? (
            <span className="px-2 py-1 bg-green-600/10 text-green-400 text-xs rounded-full font-medium">Locked</span>
          ) : (
            <button
              onClick={createAndLock}
              disabled={submitting}
              className="px-3 py-1 rounded bg-[#006072] text-white text-sm hover:bg-[#006072]/80 disabled:opacity-50"
            >
              {submitting ? 'Creating…' : 'Create & Lock'}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="text-red-400 text-sm bg-red-500/10 rounded-lg p-3 border border-red-500/20">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading ? (
        <div className="text-sm text-[#A7B3C5]">Loading…</div>
      ) : (
        <>
          {/* Analysis */}
          <div className="rounded-lg border border-white/8 bg-[#12161D] p-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-[#E8ECF2]">Analysis</h3>
              {lockedDay?.predLow != null && lockedDay?.predHigh != null && (
                <span className="text-xs text-[#A7B3C5]">
                  Band: {lockedDay.predLow.toFixed(2)} – {lockedDay.predHigh.toFixed(2)}
                </span>
              )}
            </div>
            <p className="text-sm whitespace-pre-wrap text-[#A7B3C5]">
              {aiPreview?.market_context || 'No analysis available.'}
            </p>
            {aiPreview?.sentiment && (
              <div className="mt-3 grid grid-cols-1 gap-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-[#A7B3C5]">Sentiment:</span>
                  <span className="font-medium capitalize text-[#E8ECF2]">{aiPreview.sentiment.direction ?? '—'}</span>
                  {typeof aiPreview.sentiment.confidence === 'number' && (
                    <span className="text-[#A7B3C5]">({Math.round(aiPreview.sentiment.confidence * 100)}%)</span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[#A7B3C5]">Regime:</span>
                  <span className="capitalize text-[#E8ECF2]">{aiPreview.sentiment.regime ?? '—'}</span>
                </div>
                {aiPreview.sentiment.factors && aiPreview.sentiment.factors.length > 0 && (
                  <div>
                    <div className="text-[#A7B3C5]">Factors:</div>
                    <ul className="list-disc pl-5 text-[#A7B3C5]">
                      {aiPreview.sentiment.factors.map((f, i) => (
                        <li key={i}>{f}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Per‑checkpoint table */}
          <div className="rounded-lg border border-white/8 bg-[#12161D]">
            <div className="p-3 border-b border-white/8 font-medium text-[#E8ECF2]">Predictions</div>
            <div className="p-3 overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-left text-[#A7B3C5]">
                  <tr>
                    <th className="py-1 pr-4">Checkpoint</th>
                    <th className="py-1 pr-4">Price</th>
                    <th className="py-1 pr-4">Confidence</th>
                    <th className="py-1 pr-4">Reasoning</th>
                    <th className="py-1">Actual</th>
                  </tr>
                </thead>
                <tbody>
                  {(aiPreview?.predictions || []).map((p) => (
                    <tr key={p.checkpoint} className="align-top">
                      <td className="py-2 pr-4 font-medium capitalize text-[#E8ECF2]">{p.checkpoint}</td>
                      <td className="py-2 pr-4 text-[#E8ECF2] font-mono">${p.predicted_price.toFixed(2)}</td>
                      <td className="py-2 pr-4 text-[#A7B3C5]">{Math.round(p.confidence * 100)}%</td>
                      <td className="py-2 pr-4 max-w-[40ch] whitespace-pre-wrap text-[#A7B3C5]">{p.reasoning}</td>
                      <td className="py-2 text-[#E8ECF2] font-mono">{p.actual_price != null ? `$${p.actual_price.toFixed(2)}` : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}