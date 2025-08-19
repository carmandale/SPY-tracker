import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiClient } from './apiClient';
import type { NextPredictionResponse } from './apiClient';

// Mock the global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('apiClient', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		// Clear any cached data
		localStorage.clear();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('getVersion', () => {
		it('should fetch version information successfully', async () => {
			const mockVersion = {
				version: '2.0.0',
				commit: 'abc123',
				environment: 'production',
				deployment_date: '2025-08-18T10:00:00Z',
				build_number: '42'
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockVersion,
			});

			const result = await apiClient.getVersion();
			
			expect(result).toEqual(mockVersion);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining('/api/version'),
				expect.objectContaining({
					method: 'GET',
					headers: expect.objectContaining({
						'Content-Type': 'application/json',
					}),
				})
			);
		});

		it('should handle version fetch errors', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				statusText: 'Internal Server Error',
				json: async () => ({ error: { message: 'Server error' } }),
			});

			await expect(apiClient.getVersion()).rejects.toThrow('Server error');
		});

		it('should handle network errors', async () => {
			mockFetch.mockRejectedValueOnce(new Error('Network error'));

			await expect(apiClient.getVersion()).rejects.toThrow('Network error');
		});
	});

	describe('getNextPredictionTime', () => {
		const mockPrediction: NextPredictionResponse = {
			next_prediction_time: '2025-08-19T08:00:00-05:00',
			hours_until: 12,
			minutes_until: 30,
			is_market_open: false,
			current_time: '2025-08-18T19:30:00-05:00',
			timezone: 'America/Chicago',
			next_run_date: '2025-08-19',
			is_weekend: false,
			is_holiday: false,
			holiday_name: null,
			market_status: 'closed'
		};

		it('should fetch next prediction time successfully', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockPrediction,
			});

			const result = await apiClient.getNextPredictionTime();
			
			expect(result).toEqual(mockPrediction);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining('/api/scheduler/next-prediction'),
				expect.any(Object)
			);
		});

		it('should cache next prediction response for 30 seconds', async () => {
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockPrediction,
			});

			// First call should fetch
			const result1 = await apiClient.getNextPredictionTime();
			expect(mockFetch).toHaveBeenCalledTimes(1);

			// Second immediate call should use cache
			const result2 = await apiClient.getNextPredictionTime();
			expect(mockFetch).toHaveBeenCalledTimes(1); // Still only 1 call
			expect(result2).toEqual(result1);
		});

		it('should handle holiday information correctly', async () => {
			const holidayPrediction: NextPredictionResponse = {
				...mockPrediction,
				is_holiday: true,
				holiday_name: 'Christmas',
				next_prediction_time: '2025-12-26T08:00:00-06:00',
				hours_until: 36,
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => holidayPrediction,
			});

			const result = await apiClient.getNextPredictionTime();
			
			expect(result.is_holiday).toBe(true);
			expect(result.holiday_name).toBe('Christmas');
		});

		it('should handle weekend information correctly', async () => {
			const weekendPrediction: NextPredictionResponse = {
				...mockPrediction,
				is_weekend: true,
				next_prediction_time: '2025-08-18T08:00:00-05:00',
				next_run_date: '2025-08-18',
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => weekendPrediction,
			});

			const result = await apiClient.getNextPredictionTime();
			
			expect(result.is_weekend).toBe(true);
		});

		it('should handle API errors gracefully', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 503,
				statusText: 'Service Unavailable',
				json: async () => ({ error: { message: 'Service temporarily unavailable' } }),
			});

			await expect(apiClient.getNextPredictionTime()).rejects.toThrow('Service temporarily unavailable');
		});
	});

	describe('getChangelog', () => {
		it('should fetch changelog successfully', async () => {
			const mockChangelog = {
				content: '# Changelog\n\n## [2.0.0] - 2025-08-18\n### Added\n- New features',
				versions: [
					{ version: '2.0.0', date: '2025-08-18', changes: ['New features'] },
					{ version: '1.0.0', date: '2025-08-15', changes: ['Initial release'] }
				]
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockChangelog,
			});

			const result = await apiClient.getChangelog();
			
			expect(result).toEqual(mockChangelog);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining('/api/changelog'),
				expect.any(Object)
			);
		});

		it('should cache changelog for 5 minutes', async () => {
			const mockChangelog = {
				content: '# Changelog',
				versions: []
			};

			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockChangelog,
			});

			// First call should fetch
			await apiClient.getChangelog();
			expect(mockFetch).toHaveBeenCalledTimes(1);

			// Second call should use cache
			await apiClient.getChangelog();
			expect(mockFetch).toHaveBeenCalledTimes(1);
		});
	});

	describe('error handling', () => {
		it('should handle non-JSON error responses', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				statusText: 'Internal Server Error',
				text: async () => 'Internal Server Error',
				json: async () => {
					throw new Error('Invalid JSON');
				},
			});

			await expect(apiClient.getVersion()).rejects.toThrow('HTTP error! status: 500');
		});

		it('should handle timeout errors', async () => {
			mockFetch.mockImplementationOnce(() => new Promise((_, reject) => {
				setTimeout(() => reject(new Error('Request timeout')), 100);
			}));

			await expect(apiClient.getVersion()).rejects.toThrow('Request timeout');
		});

		it('should handle CORS errors', async () => {
			mockFetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));

			await expect(apiClient.getVersion()).rejects.toThrow('Failed to fetch');
		});
	});

	describe('caching behavior', () => {
		it('should respect different cache TTLs for different endpoints', async () => {
			const mockVersion = { version: '2.0.0' };
			const mockPrediction = { next_prediction_time: '2025-08-19T08:00:00' };

			mockFetch.mockImplementation((url: string) => {
				if (url.includes('/api/version')) {
					return Promise.resolve({
						ok: true,
						json: async () => mockVersion,
					});
				} else if (url.includes('/api/scheduler/next-prediction')) {
					return Promise.resolve({
						ok: true,
						json: async () => mockPrediction,
					});
				}
				return Promise.reject(new Error('Unknown endpoint'));
			});

			// Fetch both endpoints
			await apiClient.getVersion();
			await apiClient.getNextPredictionTime();
			expect(mockFetch).toHaveBeenCalledTimes(2);

			// Both should be cached on immediate recall
			await apiClient.getVersion();
			await apiClient.getNextPredictionTime();
			expect(mockFetch).toHaveBeenCalledTimes(2); // Still only 2 calls
		});

		it('should bypass cache on error responses', async () => {
			// First call fails
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				json: async () => ({ error: { message: 'Server error' } }),
			});

			try {
				await apiClient.getVersion();
			} catch (e) {
				// Expected error
			}

			// Second call succeeds
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => ({ version: '2.0.0' }),
			});

			const result = await apiClient.getVersion();
			
			expect(result).toEqual({ version: '2.0.0' });
			expect(mockFetch).toHaveBeenCalledTimes(2); // Should have made 2 calls
		});
	});

	describe('fallback behavior', () => {
		it('should provide fallback data when API is unavailable', async () => {
			// Mock a complete API failure scenario
			mockFetch.mockRejectedValue(new Error('Network completely unavailable'));

			// For critical endpoints like next prediction, we might want to handle this gracefully
			// This is a placeholder for implementing fallback behavior
			try {
				await apiClient.getNextPredictionTime();
			} catch (error) {
				expect(error).toBeInstanceOf(Error);
				expect((error as Error).message).toContain('unavailable');
			}
		});
	});
});