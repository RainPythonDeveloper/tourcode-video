# Asset inventory — TourCode (no-capture path: user-supplied real product files)

No website was captured. Every asset below is a real TourCode file supplied in ../../assets.
UI states were drawn by the extension's own webview.js + webview.css (tools/snapshot-ui.py)
and saved as static DOM in capture/ui-states/*.html — embed them with theme.css + webview.css.

## Brand
- capture/assets/tourcode-logo.svg — logo: white route line (start dot, S-curve, arrow) on a green #2DA44E circle. End card.
- capture/assets/tourcode-mark.svg — route outline mark (currentColor stroke). Activity-bar icon; the route motif that draws across frames.

## Code (demo project "acme-shop", a small login flow)
- capture/assets/auth.ts — 15 lines: handleLogin (lines 4–10), findUser (12–15).
- capture/assets/password.ts — 7 lines: verifyPassword (1–3), hashPassword (5–7).
- capture/assets/session.ts — 3 lines: startSession.

## UI states (static DOM, real webview code) — capture/ui-states/
- overview.html — Tour map tab (1280 px): eyebrow "● TOUR MAP · 4 STEPS", "How login works", summary, the 4-node map handleLogin → findUser → verifyPassword → startSession, "Start the tour", ROUTE list.
- step1-compact.html — panel under the code, step 1 "The login entry point", STEP 1 OF 4, auth.ts:4–10, progress bar 1/4, short text, low risk line 6, buttons (More, Risks, Explain deeper, What breaks, Edit), sub-tour card "Inside handleLogin", step diagram, suggested questions.
- step1-compact-norisk.html — same with Risks toggled off.
- step1-full.html — step.html as supplied: details open, diagram, Q&A answered, next questions.
- step1-answering.html — the answer to "Why return a result object instead of throwing an error?" streaming in ("Reading src/auth.ts", Stop).
- step1-answered.html — the answered question with "You could ask next" follow-ups (details closed).
- step2-compact.html — step 2 "Looking up the user by email", auth.ts:12–15, risk medium line 13.
- step3-compact.html — step 3 "Verifying the password", password.ts:1–7, risks: High · Security line 6 (red), Low line 2.
- step3-compact-norisk.html — step 3 with Risks off.
- subtour-step.html — sub-tour "Inside handleLogin", STEP 2 OF 5 "The guard before any session", auth.ts:5–8, trail "SUB-TOUR How login works › 1. The login entry point", medium risk.
- sidebar-s0/s1/s2.html — sidebar during the tour at steps 1/2/3 (360 px): progress bar, Tour map button, steps list, sub-tour under step 1, glossary.
- sidebar-subtour.html — sidebar inside the sub-tour with PATH How login works → Inside handleLogin.
- sidebar-home.html — sidebar home: TourCode intro, How to start (/tour command), START HERE pinned "How login works", team group "Authentication" with "Creating a session after login".
- sidebar-home-stale.html — same, the Authentication tour flagged "Out of date: the code changed in 2 of 6 steps · Rebuild".
- sidebar-home-unpinned.html — same, nothing pinned yet.

## Tours (data)
- ../../assets/tours/how-login-works.json — main tour: 4 steps, glossary (handleLogin, passwordHash, verifyPassword, startSession, findUser), risks, suggested questions.
- ../../assets/tours/how-login-works-handle-login-inside.json — sub-tour "Inside handleLogin", 5 steps.
- ../../assets/tours/session-start.json — "Creating a session after login", 6 steps.

## Not supplied (to resolve via /media-use)
- Official logos: VS Code, Cursor, Kiro, Windsurf, Claude Code, Jupyter.
- Music bed and sound effects.
