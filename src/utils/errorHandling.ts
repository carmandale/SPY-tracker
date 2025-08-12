/**
 * Error handling utilities for SPY TA Tracker frontend
 */

export interface APIError {
  error: {
    message: string;
    type?: string;
    details?: Record<string, any>;
  };
}

export interface ValidationError {
  field: string;
  message: string;
  type: string;
}

export class SPYTrackerError extends Error {
  public type: string;
  public details?: Record<string, any>;
  public statusCode?: number;

  constructor(message: string, type: string = 'UnknownError', details?: Record<string, any>, statusCode?: number) {
    super(message);
    this.name = 'SPYTrackerError';
    this.type = type;
    this.details = details;
    this.statusCode = statusCode;
  }
}

/**
 * Parse API error response into user-friendly message
 */
export function parseAPIError(error: any): string {
  // Handle network errors
  if (!error.response) {
    if (error.message === 'Network Error') {
      return 'Unable to connect to server. Please check your internet connection.';
    }
    return error.message || 'An unexpected error occurred';
  }

  // Handle API errors with our custom format
  const data = error.response.data;
  if (data?.error) {
    const apiError = data as APIError;
    
    // Handle validation errors specially
    if (apiError.error.type === 'ValidationError' && apiError.error.details?.validation_errors) {
      const errors = apiError.error.details.validation_errors as ValidationError[];
      return `Validation failed: ${errors.map(e => `${e.field}: ${e.message}`).join(', ')}`;
    }
    
    // Add hint if available
    if (apiError.error.details?.hint) {
      return `${apiError.error.message}. ${apiError.error.details.hint}`;
    }
    
    return apiError.error.message;
  }

  // Handle standard HTTP errors
  switch (error.response.status) {
    case 400:
      return 'Invalid request. Please check your input and try again.';
    case 401:
      return 'Authentication required. Please log in.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return 'The requested data was not found.';
    case 409:
      return 'This action conflicts with the current state. The data may be locked.';
    case 422:
      return 'The provided data is invalid. Please check your input.';
    case 500:
      return 'Server error. Please try again later or contact support.';
    case 503:
      return 'Service temporarily unavailable. Please try again in a few moments.';
    default:
      return `Error ${error.response.status}: ${error.response.statusText || 'Unknown error'}`;
  }
}

/**
 * User-friendly error messages for specific scenarios
 */
export const ErrorMessages = {
  PREDICTION_LOCKED: 'This prediction is locked and cannot be modified.',
  MARKET_DATA_UNAVAILABLE: 'Market data is temporarily unavailable. Using cached prices.',
  NO_DATA_FOR_DATE: 'No data available for the selected date.',
  INVALID_DATE_RANGE: 'Please select a valid date range.',
  NETWORK_ERROR: 'Network connection lost. Please check your internet.',
  SAVE_FAILED: 'Failed to save. Please try again.',
  LOAD_FAILED: 'Failed to load data. Please refresh the page.',
  FORM_VALIDATION_FAILED: 'Please correct the highlighted errors before submitting.',
} as const;

/**
 * Toast notification types and utilities
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

export function createToast(
  type: ToastType,
  message: string,
  duration: number = 5000
): Toast {
  return {
    id: `toast-${Date.now()}-${Math.random()}`,
    type,
    message,
    duration,
  };
}

/**
 * Retry logic for failed API calls
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelay: number = 1000
): Promise<T> {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = error;
      
      // Don't retry on client errors (4xx)
      if (error.response?.status >= 400 && error.response?.status < 500) {
        throw error;
      }
      
      // Wait before retrying with exponential backoff
      if (i < maxRetries - 1) {
        const delay = initialDelay * Math.pow(2, i);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError;
}

/**
 * Format error for logging
 */
export function formatErrorForLogging(error: any): Record<string, any> {
  const formatted: Record<string, any> = {
    timestamp: new Date().toISOString(),
    message: error.message || 'Unknown error',
  };

  if (error.response) {
    formatted.response = {
      status: error.response.status,
      statusText: error.response.statusText,
      data: error.response.data,
    };
  }

  if (error.config) {
    formatted.request = {
      method: error.config.method,
      url: error.config.url,
      params: error.config.params,
    };
  }

  if (error.stack) {
    formatted.stack = error.stack;
  }

  return formatted;
}

/**
 * Error boundary fallback component props
 */
export interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: any): boolean {
  return (
    !error.response &&
    (error.message === 'Network Error' ||
     error.code === 'ERR_NETWORK' ||
     error.code === 'ECONNABORTED')
  );
}

/**
 * Check if error is a timeout error
 */
export function isTimeoutError(error: any): boolean {
  return error.code === 'ECONNABORTED' || error.message.includes('timeout');
}