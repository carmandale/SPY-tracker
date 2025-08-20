# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-20-fix-frontend-data-issues-#36/spec.md

> Created: 2025-08-20
> Version: 1.0.0

## Technical Requirements

### Issue 1: Historical Data Shows as "Incomplete"

**Problem Analysis:**
- Monday, August 18, 2025 shows as "incomplete" on the History page despite being a past trading day
- The logic for determining completion status may not be correctly checking all required data points

**Technical Requirements:**
- Investigate the `HistoryView` component logic for determining completion status
- Check if actual price data (open, noon, 2PM, close) exists in the database for 2025-08-18
- Verify the API endpoint that fetches historical data is returning complete information
- Fix the completion status logic to properly identify past vs. current trading days

**Files to Review:**
- `src/components/HistoryView.tsx` - History page component
- `src/hooks/usePredictions.ts` - Data fetching hook
- `backend/app/routers/predictions.py` - API endpoints for historical data

### Issue 2: Manifest.json Warning

**Problem Analysis:**
- Browser console shows: "Parsing application manifest: The manifest is not valid JSON data"
- This indicates the manifest.json file has syntax errors or invalid structure

**Technical Requirements:**
- Validate the manifest.json file syntax
- Ensure all required PWA fields are present and properly formatted
- Fix any JSON syntax errors
- Test PWA installation functionality after fix

**Files to Review:**
- `public/manifest.json` - PWA manifest file
- `index.html` - Manifest link tag

### Issue 3: CSS Resource 403 Error

**Problem Analysis:**
- Console shows: "Failed to load resource: the server responded with a status of 403 () (css2, line 0)"
- Likely a Google Fonts URL issue or external resource loading problem

**Technical Requirements:**
- Identify which CSS resource is failing (check network tab)
- Fix the resource URL or remove if unnecessary
- Ensure all external resources use proper protocols (https)
- Consider self-hosting fonts if external CDN is problematic

**Files to Review:**
- `index.html` - External CSS links
- `src/index.css` - CSS imports
- Any component files with external font imports

## Approach Options

**Option A: Fix Each Issue Independently**
- Pros: Clear separation of concerns, easier to test each fix
- Cons: May miss related issues

**Option B: Comprehensive Frontend Audit and Fix** (Selected)
- Pros: Can identify and fix related issues, ensures consistency
- Cons: Slightly more time-consuming

**Rationale:** Option B is selected because these issues are all frontend-related and may have common root causes. A comprehensive approach ensures we catch any related problems.

## Implementation Strategy

1. **Data Completion Logic Fix:**
   - Add proper date comparison to distinguish past vs. current trading days
   - Ensure the completion check verifies all required data points
   - Add logging to help debug data availability issues

2. **Manifest.json Fix:**
   - Use a JSON validator to identify syntax errors
   - Ensure all required PWA fields are present
   - Add proper icon definitions and theme colors

3. **CSS Resource Fix:**
   - Replace any http:// URLs with https://
   - Consider using modern Google Fonts API syntax
   - Add fallback fonts in case external resources fail

## External Dependencies

No new external dependencies are required for these fixes. All issues can be resolved with existing tools and libraries.