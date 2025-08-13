/**
 * Performance monitoring and optimization utilities
 */

/**
 * Measure and log performance of async operations
 */
export async function measurePerformance<T>(
  name: string,
  operation: () => Promise<T>
): Promise<T> {
  const startTime = performance.now();
  
  try {
    const result = await operation();
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    if (duration > 1000) {
      console.warn(`⚠️ Slow operation: ${name} took ${duration.toFixed(2)}ms`);
    } else if (process.env.NODE_ENV === 'development') {
      console.log(`⚡ ${name}: ${duration.toFixed(2)}ms`);
    }
    
    return result;
  } catch (error) {
    const endTime = performance.now();
    const duration = endTime - startTime;
    console.error(`❌ ${name} failed after ${duration.toFixed(2)}ms`, error);
    throw error;
  }
}

/**
 * Debounce function calls to improve performance
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: number;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    
    clearTimeout(timeout);
    timeout = window.setTimeout(later, wait);
  };
}

/**
 * Throttle function calls to limit execution frequency
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      window.setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Lazy load images with Intersection Observer
 */
export function lazyLoadImage(
  imgElement: HTMLImageElement,
  src: string,
  placeholder?: string
): void {
  if (placeholder) {
    imgElement.src = placeholder;
  }
  
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        imgElement.src = src;
        observer.unobserve(imgElement);
      }
    });
  });
  
  imageObserver.observe(imgElement);
}

/**
 * Cache API responses in memory with TTL
 */
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class MemoryCache {
  private cache = new Map<string, CacheEntry<any>>();
  
  set<T>(key: string, data: T, ttl: number = 60000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }
  
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }
    
    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data as T;
  }
  
  clear(): void {
    this.cache.clear();
  }
  
  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;
    
    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return false;
    }
    
    return true;
  }
}

export const apiCache = new MemoryCache();

/**
 * Memoize function results
 */
export function memoize<T extends (...args: any[]) => any>(
  func: T,
  keyGenerator?: (...args: Parameters<T>) => string
): T {
  const cache = new Map<string, ReturnType<T>>();
  
  return ((...args: Parameters<T>) => {
    const key = keyGenerator ? keyGenerator(...args) : JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = func(...args);
    cache.set(key, result);
    
    return result;
  }) as T;
}

/**
 * Request idle callback with fallback
 */
export function requestIdleCallbackShim(
  callback: () => void,
  options?: { timeout?: number }
): number {
  if ('requestIdleCallback' in window) {
    return (window as any).requestIdleCallback(callback, options);
  }
  
  // Fallback to setTimeout
  return window.setTimeout(callback, options?.timeout || 1);
}

/**
 * Cancel idle callback with fallback
 */
export function cancelIdleCallbackShim(id: number): void {
  if ('cancelIdleCallback' in window) {
    (window as any).cancelIdleCallback(id);
  } else {
    window.clearTimeout(id);
  }
}

/**
 * Batch DOM updates using requestAnimationFrame
 */
export function batchDOMUpdates(updates: (() => void)[]): void {
  requestAnimationFrame(() => {
    updates.forEach(update => update());
  });
}

/**
 * Preload critical resources
 */
export function preloadResources(urls: string[]): void {
  urls.forEach(url => {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
  });
}

/**
 * Web Vitals tracking
 */
export interface WebVitals {
  FCP?: number; // First Contentful Paint
  LCP?: number; // Largest Contentful Paint
  FID?: number; // First Input Delay
  CLS?: number; // Cumulative Layout Shift
  TTFB?: number; // Time to First Byte
}

export function trackWebVitals(callback: (vitals: WebVitals) => void): void {
  const vitals: WebVitals = {};
  
  // Track paint timing
  if ('PerformanceObserver' in window) {
    try {
      const paintObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.name === 'first-contentful-paint') {
            vitals.FCP = entry.startTime;
          }
        }
      });
      paintObserver.observe({ entryTypes: ['paint'] });
      
      // Track LCP
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        vitals.LCP = lastEntry.startTime;
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      
      // Track TTFB
      const navTiming = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navTiming) {
        vitals.TTFB = navTiming.responseStart - navTiming.requestStart;
      }
      
      // Report vitals after page load
      window.addEventListener('load', () => {
        setTimeout(() => {
          callback(vitals);
        }, 0);
      });
    } catch (e) {
      console.error('Failed to track web vitals:', e);
    }
  }
}