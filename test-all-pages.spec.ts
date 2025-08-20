import { test, expect } from '@playwright/test';

test.describe('SPY Tracker Production Tests', () => {
  const baseURL = 'https://spy-tracker.onrender.com';

  test('Dashboard loads and displays data', async ({ page }) => {
    // Go to dashboard
    await page.goto(baseURL);
    
    // Wait for page to load
    await page.waitForSelector('h1:has-text("SPY TA Tracker")', { timeout: 10000 });
    
    // Check for prediction data
    const predictionCard = await page.locator('text=/Predicted Range|No predictions yet/').first();
    await expect(predictionCard).toBeVisible();
    
    // Check for price tiles
    const priceTiles = await page.locator('.grid').first();
    await expect(priceTiles).toBeVisible();
    
    // Verify no console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.waitForTimeout(2000);
    
    if (errors.length > 0) {
      console.error('Console errors found:', errors);
    }
    
    expect(errors.length).toBe(0);
  });

  test('Predict page loads without errors', async ({ page }) => {
    await page.goto(`${baseURL}/predict`);
    
    // Wait for predict form to load
    await page.waitForSelector('h1:has-text("Morning Prediction")', { timeout: 10000 });
    
    // Check for form fields
    await expect(page.locator('input[placeholder*="Low"]')).toBeVisible();
    await expect(page.locator('input[placeholder*="High"]')).toBeVisible();
    
    // Check for bias buttons
    await expect(page.locator('text="Bearish"')).toBeVisible();
    await expect(page.locator('text="Neutral"')).toBeVisible();
    await expect(page.locator('text="Bullish"')).toBeVisible();
  });

  test('History page loads and displays data', async ({ page }) => {
    await page.goto(`${baseURL}/history`);
    
    // Wait for history page to load
    await page.waitForSelector('h1:has-text("Prediction History")', { timeout: 10000 });
    
    // Check for history entries or empty state
    const historyContent = await page.locator('text=/predictions found|No history yet/').first();
    await expect(historyContent).toBeVisible();
    
    // If there are predictions, check the table/list loads
    const hasPredictions = await page.locator('text=/predictions found/').count();
    if (hasPredictions > 0) {
      // Wait for data to load
      await page.waitForSelector('[class*="border"]', { timeout: 5000 });
    }
  });

  test('Metrics page loads and displays statistics', async ({ page }) => {
    await page.goto(`${baseURL}/metrics`);
    
    // Wait for metrics page to load
    await page.waitForSelector('h1:has-text("Performance Metrics")', { timeout: 10000 });
    
    // Check for metric cards
    const rangeHitCard = await page.locator('text=/Range Hit %|20-Day Range Hit/').first();
    await expect(rangeHitCard).toBeVisible();
    
    const errorCard = await page.locator('text=/Median Error|20-Day Median Error/').first();
    await expect(errorCard).toBeVisible();
  });

  test('AI predictions endpoint returns data', async ({ request }) => {
    const response = await request.get(`${baseURL}/ai/predictions/2025-08-19`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('date');
    expect(data).toHaveProperty('predictions');
    expect(Array.isArray(data.predictions)).toBeTruthy();
  });

  test('Day endpoint returns current data', async ({ request }) => {
    const today = new Date().toISOString().split('T')[0];
    const response = await request.get(`${baseURL}/day/${today}`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('date');
  });

  test('Metrics endpoint returns statistics', async ({ request }) => {
    const response = await request.get(`${baseURL}/metrics`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('rangeHit20');
    expect(data).toHaveProperty('medianAbsErr20');
  });

  test('Health check passes', async ({ request }) => {
    const response = await request.get(`${baseURL}/healthz`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('ok');
  });
});