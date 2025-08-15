/**
 * Optimized API client with caching and error handling
 */
import { apiCache, measurePerformance } from './performance';
import { parseAPIError, retryWithBackoff } from './errorHandling';

function resolveApiBaseUrl(): string {
  // Prefer injected env var when valid and complete
  const raw = (import.meta as unknown as { env?: Record<string, unknown> }).env?.VITE_API_URL as string | undefined;
  const origin = typeof window !== 'undefined' ? window.location.origin : '';

  // Empty, '/', or clearly invalid → same-origin
  if (!raw || raw === '/' || raw === '"/"') return origin;

  try {
    // Support absolute or relative base; URL() with base origin normalizes
    const u = new URL(raw, origin);
    // Guard against values like 'https://' (scheme only → no host)
    if (!u.hostname) return origin;
    return u.origin;
  } catch {
    return origin;
  }
}

const API_BASE_URL = resolveApiBaseUrl();

export interface RequestOptions {
  cache?: boolean;
  cacheTTL?: number;
  retry?: boolean;
  maxRetries?: number;
  method?: string;
  body?: string;
  headers?: Record<string, string>;
}

// Simple API response shapes used by the client
type JsonObject = Record<string, unknown>;

export interface DayResponse {
  date: string;
  predLow?: number | null;
  predHigh?: number | null;
  open?: number | null;
  noon?: number | null;
  twoPM?: number | null;
  close?: number | null;
  source?: string | null;
  locked?: boolean | null;
  notes?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

type SuggestionsResponse = JsonObject;
type MetricsResponse = JsonObject;
type HistoryResponse = JsonObject;
type MarketDataResponse = JsonObject;
type MarketStatusResponse = { market_open: boolean } & JsonObject;
type AIPredictionsResponse = JsonObject;

/**
 * Make an optimized API request with caching and error handling
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    cache = true,
    cacheTTL = 60000, // 1 minute default
    retry = true,
    maxRetries = 3,
    ...fetchOptions
  } = options;

  const url = new URL(endpoint, API_BASE_URL).toString();
  const cacheKey = `${fetchOptions.method || 'GET'}:${url}:${JSON.stringify(fetchOptions.body)}`;

  // Check cache for GET requests
  if (cache && (!fetchOptions.method || fetchOptions.method === 'GET')) {
    const cached = apiCache.get<T>(cacheKey);
    if (cached !== null) {
      console.log(`📦 Cache hit: ${endpoint}`);
      return cached;
    }
  }

  // Make the request with performance monitoring
  const makeRequest = async () => {
    const response = await fetch(url, {
      ...fetchOptions,
      headers: {
        'Content-Type': 'application/json',
        ...fetchOptions.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw {
        response: {
          status: response.status,
          statusText: response.statusText,
          data: error,
        },
      };
    }

    const data = await response.json();

    // Cache successful GET requests
    if (cache && (!fetchOptions.method || fetchOptions.method === 'GET')) {
      apiCache.set(cacheKey, data, cacheTTL);
    }

    return data as T;
  };

  // Wrap in performance monitoring and retry logic
  return measurePerformance(
    `API: ${fetchOptions.method || 'GET'} ${endpoint}`,
    async () => {
      if (retry && (!fetchOptions.method || fetchOptions.method === 'GET')) {
        return retryWithBackoff(makeRequest, maxRetries);
      }
      return makeRequest();
    }
  );
}

/**
 * Prefetch and cache multiple endpoints
 */
export async function prefetchEndpoints(endpoints: string[]): Promise<void> {
  const promises = endpoints.map(endpoint =>
    apiRequest(endpoint, { cache: true }).catch(err => {
      console.warn(`Failed to prefetch ${endpoint}:`, parseAPIError(err));
    })
  );
  
  await Promise.all(promises);
}

/**
 * API methods for SPY Tracker
 */
export const api = {
  // Predictions
  async getPrediction(date: string) {
    return apiRequest<DayResponse>(`/day/${date}`);
  },

  async createPrediction(date: string, data: JsonObject) {
    return apiRequest<JsonObject>(`/prediction/${date}`, {
      method: 'POST',
      body: JSON.stringify(data),
      cache: false,
    });
  },

  // Price logging
  async logPrice(checkpoint: string, data: { date: string; price: number }) {
    return apiRequest<JsonObject>(`/capture/${data.date}`, {
      method: 'POST',
      body: JSON.stringify({ checkpoint, price: data.price }),
      cache: false,
    });
  },

  // Suggestions
  async getSuggestions(date: string) {
    return apiRequest<SuggestionsResponse>(`/suggestions/${date}`, {
      cacheTTL: 300000, // Cache for 5 minutes
    });
  },

  async getSuggestionsPLData(date: string) {
    return apiRequest<JsonObject>(`/suggestions/${date}/pl-data`, {
      cacheTTL: 180000, // Cache for 3 minutes
    });
  },

  // Metrics
  async getMetrics() {
    return apiRequest<MetricsResponse>('/metrics', {
      cacheTTL: 120000, // Cache for 2 minutes
    });
  },

  // History
  async getHistory(limit = 20, offset = 0) {
    return apiRequest<HistoryResponse>(`/history?limit=${limit}&offset=${offset}`, {
      cacheTTL: 180000, // Cache for 3 minutes
    });
  },

  // Market data
  async getMarketData(symbol = 'SPY') {
    return apiRequest<MarketDataResponse>(`/market-data/${symbol}`, {
      cacheTTL: 30000, // Cache for 30 seconds
    });
  },

  async getMarketStatus() {
    return apiRequest<MarketStatusResponse>('/market-status', {
      cacheTTL: 30000, // Cache for 30 seconds
    });
  },

  // AI Predictions
  async getAIPredictions(date: string) {
    return apiRequest<AIPredictionsResponse>(`/ai/predictions/${date}`, {
      cacheTTL: 300000, // Cache for 5 minutes
    });
  },

  async createAIPrediction(date: string, lookbackDays?: number) {
    return apiRequest<JsonObject>(`/ai/predict/${date}`, {
      method: 'POST',
      body: lookbackDays ? JSON.stringify({ lookbackDays }) : undefined,
      cache: false,
    });
  },

  async getAIAccuracy() {
    return apiRequest<JsonObject>('/ai/accuracy', {
      cacheTTL: 300000, // Cache for 5 minutes
    });
  },

  // Clear cache
  clearCache() {
    apiCache.clear();
    console.log('🧹 API cache cleared');
  },
};

/**
 * Prefetch critical data on app load
 */
export async function prefetchCriticalData(): Promise<void> {
  const today = new Date().toISOString().split('T')[0];
  
  await prefetchEndpoints([
    `/day/${today}`,
    `/suggestions/${today}`,
    '/metrics',
    '/market-status',
  ]);
  
  console.log('🚀 Critical data prefetched');
}