import { test, expect } from '@playwright/test';

test.describe('History Data Bug - Issue #38', () => {
  test('Should show correct data for Mon, Aug 18 - NOT "day incomplete"', async ({ page }) => {
    console.log('Starting test for Issue #38');
    
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // Navigate to History page
    await page.click('text=History');
    
    // Wait for history cards to load - they have rounded-xl class
    await page.waitForSelector('.rounded-xl', { timeout: 10000 });
    
    // Get history entry buttons (not navigation buttons)
    const historyCards = await page.locator('.rounded-xl button.w-full').all();
    console.log('Found ' + historyCards.length + ' history cards');
    
    // Find Mon, Aug 18 entry
    let aug18Entry = null;
    
    for (let card of historyCards) {
      const text = await card.textContent();
      console.log('Checking card: ' + (text || '').substring(0, 80));
      
      if (text && text.includes('Aug') && text.includes('18')) {
        console.log('Found Aug 18 entry\!');
        aug18Entry = card;
        break;
      }
    }
    
    if (aug18Entry) {
      const entryText = await aug18Entry.textContent();
      console.log('Full Aug 18 entry text: ' + entryText);
      
      // Take screenshot
      await aug18Entry.screenshot({ path: 'aug18-entry-before-fix.png' });
      console.log('Screenshot saved: aug18-entry-before-fix.png');
      
      // Check for the bug - "day incomplete" or similar text
      const showsDayIncomplete = 
        entryText.toLowerCase().includes('day incomplete') || 
        entryText.toLowerCase().includes('data missing') ||
        entryText.toLowerCase().includes('waiting for market');
      
      console.log('Shows day incomplete: ' + showsDayIncomplete);
      console.log('EXPECTED: false (should NOT show day incomplete)');
      console.log('ACTUAL: ' + showsDayIncomplete);
      
      // This test should FAIL initially to prove the bug exists
      expect(showsDayIncomplete, 'Mon, Aug 18 should NOT show day incomplete').toBe(false);
    } else {
      console.log('ERROR: Could not find Aug 18 entry');
      console.log('Available dates in history:');
      for (let i = 0; i < Math.min(10, historyCards.length); i++) {
        const text = await historyCards[i].textContent();
        console.log('  Card ' + i + ': ' + (text || '').substring(0, 60));
      }
      throw new Error('Could not find Mon, Aug 18 entry in history');
    }
  });
});
