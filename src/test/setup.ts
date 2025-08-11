import '@testing-library/jest-dom'

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: 'div',
    button: 'button',
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
}))

// Mock Intl.DateTimeFormat for consistent timezone testing
Object.defineProperty(global, 'Intl', {
  value: {
    ...global.Intl,
    DateTimeFormat: vi.fn().mockImplementation(() => ({
      format: vi.fn().mockReturnValue('12:00 PM'),
    })),
  },
})

// Mock Date.toLocaleDateString for consistent date formatting
const originalDateToLocaleDateString = Date.prototype.toLocaleDateString
Date.prototype.toLocaleDateString = vi.fn().mockImplementation(function(...args) {
  // For test consistency, return a fixed date format
  if (args[1]?.timeZone === 'America/Chicago') {
    return 'Sunday, August 11'
  }
  return originalDateToLocaleDateString.apply(this, args as any)
})

// Mock Date.toLocaleTimeString for consistent time formatting  
const originalDateToLocaleTimeString = Date.prototype.toLocaleTimeString
Date.prototype.toLocaleTimeString = vi.fn().mockImplementation(function(...args) {
  // For test consistency, return a fixed time format
  if (args[1]?.timeZone === 'America/Chicago') {
    return '08:00 AM'
  }
  return originalDateToLocaleTimeString.apply(this, args as any)
})