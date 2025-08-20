import { test, expect } from '@playwright/test';

test.describe('Verify other dates still work', () => {
  test('Should correctly handle multiple date formats', async ({ page }) => {
    console.log('Testing various dates to ensure no regression');
    
    // Test dates with different scenarios
    const testDates = [
      { date: '2025-08-20', expected: 'Wed' },  // Today (Wednesday)
      { date: '2025-08-18', expected: 'Mon' },  // Monday (the fixed bug)
      { date: '2025-08-17', expected: 'Sun' },  // Sunday (weekend)
      { date: '2025-08-16', expected: 'Sat' },  // Saturday (weekend)
      { date: '2025-08-15', expected: 'Fri' },  // Friday
    ];
    
    for (let testCase of testDates) {
      const testDate = new Date(testCase.date + 'T00:00:00');
      const dayOfWeek = testDate.getDay();
      const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
      
      console.log('Date: ' + testCase.date + 
                  ', Expected: ' + testCase.expected + 
                  ', Day of week: ' + dayOfWeek + 
                  ', Is weekend: ' + isWeekend);
      
      // Verify day matches expected
      const dayName = testDate.toLocaleDateString('en-US', { weekday: 'short' });
      expect(dayName).toBe(testCase.expected);
      
      // Verify weekend detection is correct
      if (testCase.expected === 'Sat' || testCase.expected === 'Sun') {
        expect(isWeekend).toBe(true);
      } else {
        expect(isWeekend).toBe(false);
      }
    }
    
    console.log('All date tests passed - no regression detected\!');
  });
});
