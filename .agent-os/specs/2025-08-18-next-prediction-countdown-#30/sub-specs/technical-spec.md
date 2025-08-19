# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-18-next-prediction-countdown-#30/spec.md

> Created: 2025-08-18
> Version: 1.0.0

## Technical Requirements

### Countdown Timer Implementation
- **Real-time updates**: Timer must update every second using React useEffect with 1-second interval
- **CST/CDT timezone handling**: Calculate countdown based on America/Chicago timezone
- **Next prediction calculation**: Determine next 8:00 AM CST weekday (Mon-Fri) from current time
- **Visual format**: Display format "Xh Ym" or "Ym Xs" based on time remaining
- **Mobile optimization**: Touch-friendly display that works on small screens

### Version Display Requirements  
- **Backend version endpoint**: Create `/api/version` endpoint returning current version from package.json
- **Frontend version display**: Show version in header or footer with production/development indicator
- **Live deployment status**: Show "🟢 Live" for production or "🟡 Dev" for development
- **Render.com integration**: Detect production environment via environment variables

### Scheduler Integration Requirements
- **Next run time calculation**: Use APScheduler's next_run_time to calculate accurate countdown
- **Timezone consistency**: Ensure all timing calculations use America/Chicago timezone
- **Weekday-only logic**: Skip weekends and calculate next business day prediction
- **Fallback handling**: Graceful degradation if scheduler data unavailable

## Approach Options

**Option A: Client-side countdown with static schedule** 
- Pros: Simple implementation, no API dependency, fast loading
- Cons: Less accurate, doesn't account for scheduler changes or holidays

**Option B: Hybrid approach with API validation** (Selected)
- Pros: Accurate timing, validates against actual scheduler, good performance
- Cons: Slightly more complex implementation

**Option C: Full server-side countdown with WebSocket updates**
- Pros: Most accurate, real-time server updates
- Cons: Overengineered for this use case, adds complexity

**Rationale:** Option B provides the best balance of accuracy and simplicity. The countdown calculates client-side for performance but validates against the actual scheduler configuration via API.

## External Dependencies

- **React hooks**: useState, useEffect for timer state management
- **date-fns**: For timezone-aware date calculations and formatting  
- **Lucide React icons**: Clock icon for countdown display
- **Existing API client**: Extend current apiClient.ts for version endpoint

### Justification for Dependencies
- **date-fns**: Already used in project, provides reliable timezone handling for CST/CDT
- **Lucide React**: Consistent with existing icon system, no additional bundle size
- **React hooks**: Native React functionality, no external dependency

## Implementation Details

### Frontend Components
```typescript
// New component: NextPredictionCountdown.tsx
interface CountdownState {
  hours: number;
  minutes: number;
  seconds: number;
  nextPredictionTime: Date | null;
}

// Enhanced header component integration
// Add version display to existing SPYTaTrackerApp.tsx header
```

### Backend API Endpoint
```python
# New endpoint in main.py or separate version router
@app.get("/api/version")
def get_version():
    return {
        "version": "2.1.0",  # From package.json
        "environment": "production",  # From ENV var
        "deployed_at": "2025-08-18T10:30:00Z",
        "scheduler_next_run": scheduler.get_job("ai_predict_0800").next_run_time
    }
```

### Scheduler Integration  
```python
# Extend scheduler router to provide next run times
@router.get("/scheduler/next-prediction")
def get_next_prediction_time():
    # Return next AI prediction job run time
    # Handle timezone conversion to user's preference
```

### Changelog Integration Process
1. Update version number in package.json from 2.0.0 to 2.1.0
2. Add new section to CHANGELOG.md following existing format  
3. Include feature description and issue reference
4. Update deployment tracking section with new version

## Performance Considerations

- **Timer efficiency**: Use single setInterval per component, clear on unmount
- **API caching**: Cache version info for 5 minutes to reduce server load
- **Bundle impact**: Minimal - reuses existing dependencies and patterns
- **Mobile performance**: Lightweight countdown display, no heavy animations