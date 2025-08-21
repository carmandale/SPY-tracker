import { test, expect } from '@playwright/test';

test.describe('SPY Tracker Data Integrity', () => {
  const API_URL = 'https://spy-tracker.onrender.com';
  
  test('No weekend dates should appear in history', async ({ request }) => {
    const response = await request.get(`${API_URL}/history`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    const items = data.items || [];
    
    // Check each date to ensure it's not a weekend
    for (const item of items) {
      const date = new Date(item.date);
      const dayOfWeek = date.getUTCDay();
      
      // Sunday = 0, Saturday = 6
      expect(dayOfWeek).not.toBe(0); // Not Sunday
      expect(dayOfWeek).not.toBe(6); // Not Saturday
    }
  });
  
  test('Today should have predictions if weekday', async ({ request }) => {
    const today = new Date();
    const dayOfWeek = today.getDay();
    
    // Skip test on weekends
    if (dayOfWeek === 0 || dayOfWeek === 6) {
      test.skip();
      return;
    }
    
    const todayStr = today.toISOString().split('T')[0];
    const response = await request.get(`${API_URL}/day/${todayStr}`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    
    // Should have predictions
    expect(data.predLow).not.toBeNull();
    expect(data.predHigh).not.toBeNull();
    expect(data.source).toBeTruthy(); // Should have a source
  });
  
  test('Future prices should be null', async ({ request }) => {
    const now = new Date();
    const currentHourET = now.getUTCHours() - 5; // Rough ET conversion
    
    // Get today's data
    const todayStr = now.toISOString().split('T')[0];
    const response = await request.get(`${API_URL}/day/${todayStr}`);
    
    if (response.ok()) {
      const data = await response.json();
      
      // Check based on current time (rough check)
      if (currentHourET < 16) {
        // Before 4 PM ET, close should be null
        if (currentHourET < 15) {
          expect(data.close).toBeNull();
        }
      }
    }
  });
  
  test('Past prices should be numbers not null', async ({ request }) => {
    // Get history
    const response = await request.get(`${API_URL}/history`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    const items = data.items || [];
    
    // Find entries from earlier this week
    const today = new Date();
    const threeDaysAgo = new Date(today);
    threeDaysAgo.setDate(today.getDate() - 3);
    
    for (const item of items) {
      const itemDate = new Date(item.date);
      
      // If it's a past trading day
      if (itemDate < today && itemDate.getDay() !== 0 && itemDate.getDay() !== 6) {
        // If it's from this week and has predictions
        if (itemDate > threeDaysAgo && item.predLow !== null) {
          // Should have actual prices
          expect(item.open).not.toBeNull();
          expect(item.close).not.toBeNull();
          
          // Prices should be reasonable (SPY is typically 300-700)
          if (item.open !== null) {
            expect(item.open).toBeGreaterThan(300);
            expect(item.open).toBeLessThan(700);
          }
          if (item.close !== null) {
            expect(item.close).toBeGreaterThan(300);
            expect(item.close).toBeLessThan(700);
          }
        }
      }
    }
  });
  
  test('Monday 8/19 should have complete data', async ({ request }) => {
    const response = await request.get(`${API_URL}/day/2025-08-19`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    
    // Should have predictions
    expect(data.predLow).not.toBeNull();
    expect(data.predHigh).not.toBeNull();
    
    // Should have all prices
    expect(data.open).not.toBeNull();
    expect(data.noon).not.toBeNull();
    expect(data.twoPM).not.toBeNull();
    expect(data.close).not.toBeNull();
    
    // Source should indicate recovery or AI
    expect(['ai', 'ai_recovery', 'ai_simulation']).toContain(data.source);
  });
  
  test('Scheduler should be running with correct jobs', async ({ request }) => {
    const response = await request.get(`${API_URL}/scheduler/status`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    
    // Scheduler should be running
    expect(data.scheduler_running).toBe(true);
    
    // Should have 7 jobs
    expect(data.total_jobs).toBe(7);
    
    // Should use Chicago timezone
    expect(data.timezone).toBe('America/Chicago');
    
    // Check for critical jobs
    const jobIds = data.jobs.map((j: any) => j.id);
    expect(jobIds).toContain('ai_predict_0800');
    expect(jobIds).toContain('capture_open');
    expect(jobIds).toContain('capture_noon');
    expect(jobIds).toContain('capture_2pm');
    expect(jobIds).toContain('capture_close');
    
    // All capture jobs should be weekday-only
    for (const job of data.jobs) {
      if (job.id.includes('capture') || job.id.includes('predict')) {
        expect(job.trigger).toContain('day_of_week=\'1-5\'');
      }
    }
  });
  
  test('AI predictions should exist for recent weekdays', async ({ request }) => {
    // Check Tuesday and Wednesday
    const dates = ['2025-08-19', '2025-08-20', '2025-08-21'];
    
    for (const date of dates) {
      const response = await request.get(`${API_URL}/ai/predictions/${date}`);
      
      if (response.ok()) {
        const data = await response.json();
        
        // Should have predictions array
        expect(data.predictions).toBeDefined();
        expect(Array.isArray(data.predictions)).toBe(true);
        
        // Should have 4 predictions (open, noon, twoPM, close)
        expect(data.predictions.length).toBe(4);
        
        // Each prediction should have required fields
        for (const pred of data.predictions) {
          expect(pred.checkpoint).toBeTruthy();
          expect(pred.predicted_price).toBeGreaterThan(0);
          expect(pred.confidence).toBeGreaterThanOrEqual(0);
          expect(pred.confidence).toBeLessThanOrEqual(1);
          expect(pred.reasoning).toBeTruthy();
        }
      }
    }
  });
});