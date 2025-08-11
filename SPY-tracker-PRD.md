PRD — SPY TA Tracker (Mobile Web)

Daily TA → tracked outcomes → IC/IB suggestions for 0DTE / 1W / 1M
Time zone: America/Chicago (CST/CDT)

⸻

1) Purpose & North Star

Enable a <60s morning ritual to record a SPY prediction range and context, auto-log key intraday prices, visualize prediction vs. reality, and propose iron condor/iron butterfly setups for 0DTE / 1-week / 1-month—kept intentionally simple so we can iterate quickly and calibrate over time.

Definition of success (MVP):
	•	Morning entry takes ≤60s on phone.
	•	Dashboard glance yields state-of-day in ≤5s.
	•	Suggestions readable and actionable in ≤10s.
	•	We persist a rolling RangeHit% and Median Abs Error so suggestions can gradually tighten/widen.

⸻

2) Users & Constraints
	•	Primary user: experienced options trader (single user for v1).
	•	Device: mobile-first (phone), works on desktop.
	•	Market: SPY only (no multi-ticker in v1).
	•	No auto-execution; this is a decision aid.

⸻

3) Scope (MVP)

3.1 Morning Prediction (8:00 AM CST)

User inputs:
	•	Predicted Low (number)
	•	Predicted High (number)
	•	Bias: Up / Neutral / Down (segmented)
	•	Vol Context: Low / Medium / High
	•	Day Type: Range / Trend / Reversal
	•	Key Levels (short text)
	•	Notes (short text)
System captures:
	•	Pre-market price (snapshot)
	•	Timestamp (CST)

3.2 Automatic/Manual Intraday Logging

At these checkpoints, store last-trade price:
	•	Open 08:30, Noon 12:00, 2:00 PM, Close 3:00 PM
MVP can log manually (tap-to-log) with a stub price; upgrade to live data fetch on schedule.

3.3 Visualization
	•	Chart predicted band (Low–High) vs. actual intraday points/line.
	•	Badge if the entire session closes inside predicted range.
	•	Show Open/Noon/2/Close values as tiles.

3.4 Suggestions (IC/IB)

For each horizon: 0DTE, 1W, 1M:
	•	Recommend structure (IC vs. IB) from simple rules (below).
	•	Show short legs target deltas, wings, and target credit.
	•	One-line management note (profit target / exit timing).

3.5 Performance & Calibration
	•	RangeHit% (last 20 trading days).
	•	Median Absolute Error to Close (|Close − PredMid|).
	•	Tip: simple, data-driven (e.g., “Widen shorts by +2Δ,” “Favor IB”).
	•	Store realized Day’s Low/High (from data provider) for accuracy scoring.

3.6 History & Metrics
	•	History list of days: prediction, result, hit/miss, error.
	•	Metrics screen: rolling stats and tiny trend badges (improving/worsening).

Out of scope (MVP):
	•	Broker connections, order routing, or auto-trading.
	•	Multi-ticker; complex TA indicators; backtesting engine.
	•	User accounts/teams (single-user only).

⸻

4) Design System (for Design Agent)

Dark default; fast-scan, “decisive” numerics.
	•	Colors
	•	bg-0 #0B0D12, bg-1 #12161D, stroke rgba(255,255,255,.08)
	•	text-high #E8ECF2, text-mid #A7B3C5, accent #006072
	•	success #16A34A, danger #DC2626
	•	Type
	•	Inter/SF; titles 18/24, body 14/20, micro 12/16
	•	Tabular-lining numerals for all price/delta/credit figures
	•	Layout
	•	Spacing: 4, 8, 12, 16, 24
	•	Radius: 12 (cards), 999 (badges)
	•	Bottom nav with safe-area inset
	•	Components
	•	Top bar (title, date badge, refresh)
	•	Prediction card (fields + Save)
	•	Key-times 2×2 tile grid (tap states)
	•	Chart card (band + line, Reset)
	•	Suggestion cards (0DTE/1W/1M)
	•	Performance strip
	•	Bottom nav (Dashboard / Predict / History / Metrics)
	•	Micro-interactions
	•	Save → success toast (2s)
	•	Tile tap → pulse + populate value
	•	Suggestions Update → spinner
	•	Chart touch → crosshair tooltip
	•	Accessibility
	•	Dark-mode contrast AA+
	•	Hit areas ≥44×44px, one-hand thumb reach
	•	Clear focus/active/disabled states

⸻

5) Functional Requirements

5.1 Data Model (SQLite via SQLModel)

DailyPrediction
	•	date (PK, ISO YYYY-MM-DD)
	•	Inputs @08:00: predLow (float), predHigh (float), bias (enum), volCtx (enum), dayType (enum), keyLevels (str), notes (str)
	•	Snapshots: preMarket, open, noon, twoPM, close (floats, nullable)
	•	Realized: realizedLow, realizedHigh (floats, from provider)
	•	Scores: rangeHit (bool), absErrorToClose (float)
	•	Context (optional): iv30 (float), ivRank (float)

Suggestion (derived, persisted for audit)
	•	date (FK)
	•	horizon ∈ {0DTE,1W,1M}
	•	type ∈ {IC,IB}
	•	shortPut, longPut, shortCall, longCall (floats; nearest strikes)
	•	targetCredit (float), deltaTarget (float), wings (float/int)
	•	note (str) — management summary

Note: For MVP we may not have full option chains; store targets and logic inputs. When an options API is added, we’ll fill exact strikes and credits.

5.2 Business Logic (v1)
	•	Expected Move (EM): EM ≈ S * IV * sqrt(T/365)
	•	For 0DTE use day IV; for 1W/1M use corresponding term IV (stub 18% if missing).
	•	PredMid: (predLow + predHigh)/2
	•	Structure selection:
	•	If bias = Neutral and RangeHit% (last 20) ≥ 65% → IC
	•	Else → IB, center near PredMid; skew 1–2 strikes toward bias if desired
	•	Delta targets (starting points):
	•	IC 0DTE: short legs ~ ±10–15Δ; ensure min credit ≥ $0.30–$0.50 per $1 wing
	•	IC 1W: ±15–20Δ; manage at 25–50% max profit
	•	IC 1M: ±20Δ; manage earlier (30–50%)
	•	IB: center at PredMid (nearest strike); wings ~ 0.5–1.0× EM
	•	Risk filters:
	•	Skip if IVR < 10 and bias = Neutral
	•	Tag macro days (CPI/FOMC/Jobs) to reduce size (manual flag for MVP)
	•	Calibration nudges (daily after close):
	•	If RangeHit% < 55% → widen IC shorts (+2–3Δ) and/or reduce size
	•	If median error consistently positive/negative → nudge next day PredMid by that value as a hint

5.3 Scheduling (APScheduler)

All times America/Chicago:
	•	08:00: prompt user (UI) to enter prediction; snapshot pre-market
	•	08:30: record open
	•	12:00: record noon
	•	14:00: record 2 PM
	•	15:00: record close, fetch realized Low/High, compute scores & tips

⸻

6) API (FastAPI)
	•	POST /prediction/{date}
Body: {predLow, predHigh, bias, volCtx, dayType, keyLevels?, notes?}
Resp: DailyPrediction
	•	GET /day/{date} → current day snapshot (all fields + latest suggestions)
	•	POST /capture/{date}
Body: {checkpoint: "open"|"noon"|"twoPM"|"close", price}
(MVP can accept manual price; scheduled job will call same endpoint)
	•	GET /suggestions/{date} → array of {horizon, type, deltaTarget, wings, targetCredit, note}
	•	GET /metrics → { rangeHit20, medianAbsErr20, ivRank? }
	•	POST /recompute/{date} → recompute suggestions from current state

Errors & empty states:
All endpoints return structured error codes and messages; UI shows toasts and subtle inline hints.

⸻

7) Front-End (Bootstrap + Chart.js)
	•	Pages/Routes
	•	/ Dashboard (today card stack + suggestions)
	•	/predict Morning form
	•	/history Table (date, predicted band, hit/miss, error)
	•	/metrics Rolling stats & tips
	•	State
	•	MVP: localStorage hydration + API when available
	•	Date badge shows today; all stamps labeled CST
	•	Chart
	•	Dashed Pred Low/High lines + Actual line
	•	Ticks: 8:30, 9:30, 10:30, 11:30, 12:00, 13:00, 14:00, 15:00
	•	Reset Day button (clears local state)

⸻

8) Non-Functional Requirements
	•	Performance: first load < 2s on LTE; JS bundle < 200KB gzipped (MVP target).
	•	Reliability: scheduler tolerant to app restarts; idempotent captures.
	•	Security/Privacy: no PII; single-user; use HTTPS; CORS restricted.
	•	Observability: server logs for jobs and API; simple counter metrics (captures per checkpoint, suggestion renders).
	•	Accessibility: WCAG AA contrast; keyboard focus and roles on desktop.

⸻

9) Milestones

M0 – Clickable UI Prototype (Done when):
	•	Mobile pages and components render; local-only mock prices; chart draws; suggestions stubbed.

M1 – Core Day Loop (Backend):
	•	SQLite models, FastAPI endpoints, APScheduler with CST
	•	Manual + scheduled price capture; EOD scoring
	•	Suggestions computed from rules above

M2 – Data Provider & Metrics:
	•	Live SPY price adapter (yfinance → provider interface)
	•	Realized Low/High at close
	•	Metrics & history screens complete

M3 – Calibration & Polish:
	•	RangeHit%/MAE-based nudges
	•	Macro-day tags
	•	Refined copy, toasts, and empty/error states

⸻

10) Acceptance Criteria (MVP)
	•	I can enter a prediction at 08:00 and see pre-market on the card.
	•	The app logs or allows me to log Open/Noon/2/Close and shows them on tiles and chart.
	•	The chart shows my predicted band vs. actual line.
	•	I get three suggestion cards (0DTE / 1W / 1M) with type, delta targets, wings, target credit and a one-line plan.
	•	The History page lists prior days with hit/miss and abs error.
	•	The Metrics page shows RangeHit% (20) and Median Abs Error (20) and a calibration tip.
	•	Times displayed are CST/CDT correct; numerics are tabular.

⸻

11) Risks & Mitigations
	•	Market data gaps → cache last good price; allow manual override.
	•	Time zone drift (DST) → use America/Chicago everywhere; test transition dates.
	•	Overfitting rules → keep nudges small and transparent; expose metrics.

⸻

12) Future (Not in MVP)
	•	Options-chain integration for exact strikes/credits.
	•	Broker ticket pre-fill strings (no auto-trade).
	•	Multi-ticker (SPX, QQQ), tagging of event days, richer analytics, backtests.

⸻

13) Handoff Notes (Design ↔ Engineering)
	•	Design agent uses this PRD plus the MagicPath-style prompt (we drafted) to deliver Figma with tokens, components, and states.
	•	Engineering agent builds to this PRD; endpoints and jobs match section 6 and 5.3; suggestion logic matches 5.2; UI contract matches 7 and 4.

⸻

14) Copy Blocks (UX microtext)
	•	Save toast: “Prediction saved for {date}.”
	•	Empty suggestions: “Enter Pred Low/High to generate suggestions.”
	•	Calibration examples:
	•	“RangeHit% low. Widen IC shorts by +2Δ.”
	•	“Narrow predicted band → favor IB.”

⸻

If you want, I’ll now:
	1.	Convert this PRD into the single master MagicPath prompt (verbatim block) for the design agent, and
	2.	Generate a starter FastAPI repo with models, endpoints, scheduler, and a Bootstrap front-end that mirrors the Figma.