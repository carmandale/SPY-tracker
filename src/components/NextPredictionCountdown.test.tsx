import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, act } from '@testing-library/react'

// Mock the entire apiClient module before any imports
vi.mock('../utils/apiClient', () => {
  return {
    apiClient: {
      getNextPredictionTime: vi.fn()
    }
  }
})

import { NextPredictionCountdown } from './NextPredictionCountdown'
import { apiClient } from '../utils/apiClient'

describe('NextPredictionCountdown', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders loading state initially', () => {
    render(<NextPredictionCountdown />)
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('displays countdown during market hours', async () => {
    const mockResponse = {
      next_run: '2025-08-19T08:00:00-05:00',
      next_run_cst: 'Tuesday, August 19 at 08:00 AM CST',
      time_until: '2 hours, 30 minutes',
      market_status: 'closed',
      is_weekend: false,
      is_holiday: false
    }

    vi.mocked(apiClient.getNextPredictionTime).mockResolvedValue(mockResponse)

    await act(async () => {
      render(<NextPredictionCountdown />)
    })

    await waitFor(() => {
      expect(screen.getByText(/next prediction/i)).toBeInTheDocument()
      expect(screen.getByText(/2 hours, 30 minutes/i)).toBeInTheDocument()
    })
  })

  it('displays weekend message on weekends', async () => {
    const mockResponse = {
      next_run: '2025-08-25T08:00:00-05:00',
      next_run_cst: 'Monday, August 25 at 08:00 AM CST',
      time_until: '2 days, 14 hours',
      market_status: 'weekend',
      is_weekend: true,
      is_holiday: false
    }

    vi.mocked(apiClient.getNextPredictionTime).mockResolvedValue(mockResponse)

    await act(async () => {
      render(<NextPredictionCountdown />)
    })

    await waitFor(() => {
      expect(screen.getByText(/market closed/i)).toBeInTheDocument()
      expect(screen.getByText(/monday/i)).toBeInTheDocument()
    })
  })

  it('displays holiday message on holidays', async () => {
    const mockResponse = {
      next_run: '2025-12-26T08:00:00-06:00',
      next_run_cst: 'Friday, December 26 at 08:00 AM CST',
      time_until: '1 day, 17 hours',
      market_status: 'holiday (Christmas)',
      is_weekend: false,
      is_holiday: true
    }

    vi.mocked(apiClient.getNextPredictionTime).mockResolvedValue(mockResponse)

    await act(async () => {
      render(<NextPredictionCountdown />)
    })

    await waitFor(() => {
      expect(screen.getByText(/holiday/i)).toBeInTheDocument()
      expect(screen.getByText(/christmas/i)).toBeInTheDocument()
    })
  })

  it('updates countdown every minute', async () => {
    const mockResponse = {
      next_run: '2025-08-19T08:00:00-05:00',
      next_run_cst: 'Tuesday, August 19 at 08:00 AM CST',
      time_until: '2 hours, 30 minutes',
      market_status: 'closed',
      is_weekend: false,
      is_holiday: false
    }

    vi.mocked(apiClient.getNextPredictionTime).mockResolvedValue(mockResponse)

    await act(async () => {
      render(<NextPredictionCountdown />)
    })

    await waitFor(() => {
      expect(screen.getByText(/2 hours, 30 minutes/i)).toBeInTheDocument()
    })

    // Update the mock for the next call
    vi.mocked(apiClient.getNextPredictionTime).mockResolvedValue({
      ...mockResponse,
      time_until: '2 hours, 29 minutes'
    })

    // Advance timer by 1 minute
    await act(async () => {
      vi.advanceTimersByTime(60 * 1000)
    })

    await waitFor(() => {
      expect(screen.getByText(/2 hours, 29 minutes/i)).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    vi.mocked(apiClient.getNextPredictionTime).mockRejectedValue(
      new Error('Network error')
    )

    await act(async () => {
      render(<NextPredictionCountdown />)
    })

    await waitFor(() => {
      expect(screen.getByText(/unable to load/i)).toBeInTheDocument()
    })
  })

  it('displays market open message during trading hours', async () => {
    const mockResponse = {
      next_run: '2025-08-20T08:00:00-05:00',
      next_run_cst: 'Wednesday, August 20 at 08:00 AM CST',
      time_until: '23 hours, 0 minutes',
      market_status: 'open',
      is_weekend: false,
      is_holiday: false
    }

    vi.mocked(apiClient.getNextPredictionTime).mockResolvedValue(mockResponse)

    await act(async () => {
      render(<NextPredictionCountdown />)
    })

    await waitFor(() => {
      expect(screen.getByText(/market open/i)).toBeInTheDocument()
      expect(screen.getByText(/tomorrow at 8:00 AM/i)).toBeInTheDocument()
    })
  })

  it('cleans up timer on unmount', () => {
    const clearIntervalSpy = vi.spyOn(global, 'clearInterval')
    
    const { unmount } = render(<NextPredictionCountdown />)
    
    unmount()
    
    expect(clearIntervalSpy).toHaveBeenCalled()
  })
})