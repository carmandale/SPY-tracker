# Spec Requirements Document

> Spec: Morning Prediction Form UI
> Created: 2025-08-11
> GitHub Issue: #1
> Status: Planning

## Overview

Implement the mobile-first morning prediction form that allows traders to quickly enter their daily SPY predictions and capture pre-market context. This is the foundation of the Core Day Loop, enabling sub-60 second morning entry workflow optimized for mobile use.

## User Stories

### Quick Morning Entry

As an experienced options trader, I want to quickly enter my daily SPY prediction on my phone during my morning commute, so that I can systematically track my technical analysis predictions without disrupting my pre-market routine.

**Workflow:** Open app → Navigate to prediction form → Enter low/high predictions → Select bias and volatility context → Add key levels and notes → Save prediction → Continue with morning routine (total time ≤60 seconds)

## Spec Scope

1. **Mobile-First Form Interface** - Responsive prediction entry form optimized for one-handed mobile use
2. **Input Field Validation** - Zod schema validation for all prediction inputs with real-time feedback
3. **Segmented Controls** - Native mobile-style segmented controls for bias, volatility context, and day type
4. **Pre-market Integration** - Automatic capture of pre-market SPY price when prediction is saved
5. **API Integration** - Save predictions using existing /prediction/{date} endpoint with proper error handling

## Out of Scope

- Historical prediction editing (view-only after submission)
- Multi-ticker support (SPY only for MVP)
- Advanced charting or technical indicators within form
- Automated prediction generation or suggestions

## Expected Deliverable

1. Functional prediction form accessible via mobile navigation that captures all required prediction data
2. Form validation that prevents invalid submissions and provides clear user feedback
3. Successful integration with backend API that persists predictions and captures pre-market pricing data