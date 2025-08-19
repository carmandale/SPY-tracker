import { test, expect } from '@playwright/test';

test.describe('SPY Tracker Production Site', () => {
  test('Dashboard loads and displays predictions', async ({ page }) => {
    console.log('🧪 Testing https://spy-tracker.onrender.com ...');
    
    // Navigate to the site
    await page.goto('https://spy-tracker.onrender.com', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Wait for the dashboard to load
    await page.waitForTimeout(3000);
    
    // Take a screenshot for debugging
    await page.screenshot({ path: 'dashboard-screenshot.png', fullPage: true });
    
    // Check if the page has content (not blank)
    const bodyText = await page.textContent('body');
    console.log('Body contains text:', bodyText?.length > 100 ? 'YES' : 'NO');
    
    // Check for the prediction card
    const predictionCard = await page.locator('text=/Today.*Prediction/i').count();
    console.log('Prediction card found:', predictionCard > 0 ? 'YES' : 'NO');
    
    // Check for prediction values
    const hasLowValue = await page.locator('text=/637\\.\\d+/').count();
    const hasHighValue = await page.locator('text=/644\\.\\d+/').count();
    console.log('Low value (637.x) displayed:', hasLowValue > 0 ? 'YES' : 'NO');
    console.log('High value (644.x) displayed:', hasHighValue > 0 ? 'YES' : 'NO');
    
    // Check for AI badge
    const hasAIBadge = await page.locator('text=/AI Prediction/i').count();
    console.log('AI Prediction badge displayed:', hasAIBadge > 0 ? 'YES' : 'NO');
    
    // Check console for errors
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Wait a bit to collect any console errors
    await page.waitForTimeout(2000);
    
    if (consoleErrors.length > 0) {
      console.error('❌ Console errors found:', consoleErrors);
    } else {
      console.log('✅ No console errors');
    }
    
    // Final assertions
    expect(bodyText?.length).toBeGreaterThan(100); // Page has content
    expect(predictionCard).toBeGreaterThan(0); // Prediction card exists
    expect(hasLowValue || hasHighValue).toBeTruthy(); // At least one value shown
    
    console.log('\n📊 FINAL RESULT:');
    console.log('  - Page loads: YES');
    console.log('  - Has content: ', bodyText?.length > 100 ? 'YES' : 'NO');
    console.log('  - Shows predictions: ', (hasLowValue || hasHighValue) ? 'YES' : 'NO');
    console.log('  - Dashboard functional: ', predictionCard > 0 ? 'YES' : 'NO');
  });
});