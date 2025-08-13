/**
 * Optimized API client with caching and error handling
 */
import { apiCache, measurePerformance } from './performance';
import { parseAPIError, retryWithBackoff } from './errorHandling';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface RequestOptions {
  cache?: boolean;
  cacheTTL?: number;
  retry?: boolean;
  maxRetries?: number;
  method?: string;
  body?: string;
  headers?: Record<string, string>;
}

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

  const url = `${API_BASE_URL}${endpoint}`;
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
    return apiRequest<any>(`/day/${date}`);
  },

  async createPrediction(date: string, data: any) {
    return apiRequest<any>(`/prediction/${date}`, {
      method: 'POST',
      body: JSON.stringify(data),
      cache: false,
    });
  },

  // Price logging
  async logPrice(checkpoint: string, data: any) {
    return apiRequest<any>(`/capture/${data.date}`, {
      method: 'POST',
      body: JSON.stringify({ checkpoint, price: data.price }),
      cache: false,
    });
  },

  // Suggestions
  async getSuggestions(date: string) {
    return apiRequest<any>(`/suggestions/${date}`, {
      cacheTTL: 300000, // Cache for 5 minutes
    });
  },

  async getSuggestionsPLData(date: string) {
    return apiRequest<any>(`/suggestions/${date}/pl-data`, {
      cacheTTL: 180000, // Cache for 3 minutes
    });
  },

  // Metrics
  async getMetrics() {
    return apiRequest<any>('/metrics', {
      cacheTTL: 120000, // Cache for 2 minutes
    });
  },

  // History
  async getHistory(limit = 20, offset = 0) {
    return apiRequest<any>(`/history?limit=${limit}&offset=${offset}`, {
      cacheTTL: 180000, // Cache for 3 minutes
    });
  },

  // Market data
  async getMarketData(symbol = 'SPY') {
    return apiRequest<any>(`/market-data/${symbol}`, {
      cacheTTL: 30000, // Cache for 30 seconds
    });
  },

  async getMarketStatus() {
    return apiRequest<any>('/market-status', {
      cacheTTL: 30000, // Cache for 30 seconds
    });
  },

  // AI Predictions
  async getAIPredictions(date: string) {
    return apiRequest<any>(`/ai/predictions/${date}`, {
      cacheTTL: 300000, // Cache for 5 minutes
    });
  },

  async createAIPrediction(date: string, lookbackDays?: number) {
    return apiRequest<any>(`/ai/predict/${date}`, {
      method: 'POST',
      body: lookbackDays ? JSON.stringify({ lookbackDays }) : undefined,
      cache: false,
    });
  },

  async getAIAccuracy() {
    return apiRequest<any>('/ai/accuracy', {
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