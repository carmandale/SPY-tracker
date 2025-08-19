/**
 * Fallback data for when API endpoints are unavailable
 * This ensures the app remains functional even during outages
 */

import type { NextPredictionResponse, VersionResponse } from './apiClient';

/**
 * Calculate next 8 AM CST on the next trading day
 */
function getNextTradingDay8AM(): Date {
	const now = new Date();
	const tomorrow = new Date(now);
	tomorrow.setDate(tomorrow.getDate() + 1);
	
	// Set to 8 AM
	tomorrow.setHours(8, 0, 0, 0);
	
	// Skip weekends
	const day = tomorrow.getDay();
	if (day === 0) { // Sunday
		tomorrow.setDate(tomorrow.getDate() + 1);
	} else if (day === 6) { // Saturday
		tomorrow.setDate(tomorrow.getDate() + 2);
	}
	
	return tomorrow;
}

/**
 * Get fallback data for next prediction time
 */
export function getFallbackNextPrediction(): NextPredictionResponse {
	const now = new Date();
	const nextRun = getNextTradingDay8AM();
	const hoursUntil = Math.floor((nextRun.getTime() - now.getTime()) / (1000 * 60 * 60));
	const minutesUntil = Math.floor(((nextRun.getTime() - now.getTime()) % (1000 * 60 * 60)) / (1000 * 60));
	
	// Check if it's weekend
	const day = now.getDay();
	const isWeekend = day === 0 || day === 6;
	
	// Check if market is open (9:30 AM - 4:00 PM ET, which is 8:30 AM - 3:00 PM CST)
	const currentHour = now.getHours();
	const currentMinutes = now.getMinutes();
	const timeInMinutes = currentHour * 60 + currentMinutes;
	const marketOpenTime = 8 * 60 + 30; // 8:30 AM CST
	const marketCloseTime = 15 * 60; // 3:00 PM CST
	const isMarketOpen = !isWeekend && timeInMinutes >= marketOpenTime && timeInMinutes < marketCloseTime;
	
	return {
		next_prediction_time: nextRun.toISOString(),
		hours_until: hoursUntil,
		minutes_until: minutesUntil,
		is_market_open: isMarketOpen,
		current_time: now.toISOString(),
		timezone: 'America/Chicago',
		next_run_date: nextRun.toISOString().split('T')[0],
		is_weekend: isWeekend,
		is_holiday: false, // Can't determine holidays without backend
		holiday_name: null,
		market_status: isMarketOpen ? 'open' : 'closed'
	};
}

/**
 * Get fallback version info
 */
export function getFallbackVersion(): VersionResponse {
	return {
		version: '2.0.0',
		commit: 'unknown',
		environment: 'production',
		deployment_date: new Date().toISOString(),
		build_number: 'fallback'
	};
}

/**
 * Check if we should use fallback data
 * Returns true if we've had multiple recent failures
 */
const failureTracker = new Map<string, number[]>();

export function shouldUseFallback(endpoint: string): boolean {
	const failures = failureTracker.get(endpoint) || [];
	const recentFailures = failures.filter(
		timestamp => Date.now() - timestamp < 60000 // Last minute
	);
	
	// Use fallback if we've had 3+ failures in the last minute
	return recentFailures.length >= 3;
}

/**
 * Track API failure for an endpoint
 */
export function trackFailure(endpoint: string): void {
	const failures = failureTracker.get(endpoint) || [];
	failures.push(Date.now());
	
	// Keep only last 10 failures
	if (failures.length > 10) {
		failures.shift();
	}
	
	failureTracker.set(endpoint, failures);
}

/**
 * Clear failure tracking for an endpoint (on success)
 */
export function clearFailures(endpoint: string): void {
	failureTracker.delete(endpoint);
}

/**
 * Get user-friendly message for fallback mode
 */
export function getFallbackMessage(endpoint: string): string {
	const messages: Record<string, string> = {
		'/api/scheduler/next-prediction': 'Using estimated time. Actual prediction time may vary.',
		'/api/version': 'Version information temporarily unavailable.',
		'/api/changelog': 'Changelog temporarily unavailable.',
		default: 'Some features may be limited while offline.'
	};
	
	return messages[endpoint] || messages.default;
}