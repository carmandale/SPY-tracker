# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-11-morning-prediction-form-#1/spec.md

> Created: 2025-08-11
> Version: 1.0.0

## Technical Requirements

### Form Components and Validation
- React Hook Form integration with Zod schema validation
- Real-time validation feedback with error messages
- Mobile-optimized input components using shadcn/ui
- Responsive design for mobile-first experience with desktop compatibility
- Proper form state management and submission handling

### Mobile UI Components
- Segmented controls for Bias (Up/Neutral/Down) selection
- Segmented controls for Vol Context (Low/Medium/High) selection  
- Segmented controls for Day Type (Range/Trend/Reversal) selection
- Number inputs for Predicted Low/High with appropriate keyboards on mobile
- Text inputs for Key Levels and Notes with character limits
- Save button with loading states and success feedback

### API Integration Requirements
- Integration with existing `/prediction/{date}` POST endpoint
- Automatic date detection using CST timezone (America/Chicago)
- Pre-market price capture integration when saving predictions
- Error handling for network failures and validation errors
- Success toast notifications with 2-second duration

### Performance Requirements
- Form should be interactive within 500ms of navigation
- Input validation should provide immediate feedback (≤100ms)
- Form submission should complete within 2 seconds on 3G connection
- Bundle size impact should be minimal (target ≤50KB additional)

## Approach Options

**Option A:** Create new dedicated PredictionForm component
- Pros: Clean separation of concerns, reusable component architecture
- Cons: Additional component overhead

**Option B:** Build form directly in existing Predict screen (Selected)
- Pros: Faster implementation, fewer files to manage, direct integration
- Cons: Larger component file, less reusable

**Rationale:** Option B selected for MVP speed and simplicity. The form is specific to the prediction workflow and doesn't need to be reused elsewhere in the current scope.

## External Dependencies

- **@hookform/resolvers** - Zod integration with React Hook Form
- **Justification:** Required for seamless Zod schema validation with React Hook Form

- **react-hook-form** - Form state management (already installed)
- **Justification:** Provides efficient form handling with minimal re-renders

- **zod** - Schema validation (already in tech stack)  
- **Justification:** Type-safe validation matching existing backend patterns

All other dependencies (shadcn/ui, lucide-react, tailwind) are already installed per tech stack specification.

## Implementation Architecture

### Form Schema Structure
```typescript
const PredictionFormSchema = z.object({
  predLow: z.number().min(0).max(1000),
  predHigh: z.number().min(0).max(1000),
  bias: z.enum(['Up', 'Neutral', 'Down']),
  volCtx: z.enum(['Low', 'Medium', 'High']),
  dayType: z.enum(['Range', 'Trend', 'Reversal']),
  keyLevels: z.string().max(200).optional(),
  notes: z.string().max(500).optional()
})
```

### Component Structure
- Main form container with React Hook Form
- Individual input components for each field type
- Validation feedback components
- Submission handling with loading states
- Integration with existing API client patterns

### Timezone Handling
- Use browser's built-in timezone detection
- Format dates for CST/CDT using Intl.DateTimeFormat
- Handle DST transitions properly for market hours