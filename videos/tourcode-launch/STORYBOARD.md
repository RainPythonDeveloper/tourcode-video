---
format: 1920x1080
duration: 60s
fps: 60
message: "Understand any codebase in minutes, not days"
arc: Hook → Command → Agent explores → Tour map → Walk-through → Risks → Ask & go deeper → Teams → Works everywhere → End card
audience: developers worldwide
mode: collaborative
music: none
music_host: "HeyGen catalog 9d06052d — subtle modern minimal ambient-electronic, warm pads, light plucks, gentle pulse, 100 BPM, B major (88 s). Enters 0:05.6, edited −2 bars so the final note lands on the logo at 0:58.4, 1.5 s fade."
beat_grid: "100 BPM → 0.6 s per beat; grid = 5.0 + 0.6·k. Every frame cut sits on a beat."
---

# TourCode — 60 s launch film

No voiceover in the main master. The on-screen lines are the captions (burned in, lower band,
one message at a time). Every UI surface is the real TourCode webview DOM
(`capture/ui-states/*.html`, drawn by the extension's own webview.js); only the VS Code window
chrome around it is built in HTML. All frame cuts are `cut` at the storyboard level — the seams
(route-line draw, green-bar expand, dive) are built inside the frames via `handoff_out` / `handoff_in`.

## Frame 1 — Hook: the wall of code

- type: hook
- blueprint: camera-journey (B, cursorless flight)
- duration: 5s
- transition_in: cut
- scene: An endless file tree and code stream past in depth; hard stop on an empty dark editor
- on_screen: "New codebase. 50,000 lines." (0.4–2.4) → "Where do you even start?" (2.6–4.7)
- asset_candidates: capture/assets/auth.ts, capture/assets/password.ts, capture/assets/session.ts (code fragments as blurred depth layers), capture/ui-states/sidebar-home.html (none — tree is generic file names)
- sound: low riser 0.0→5.0 (stops dead at 5.0); data-rush whooshes at 0.3, 1.5, 2.7, 3.6 as layers fly past; tape-stop thud at 5.0; then near-silence to 5.6
- status: animated
- src: compositions/frames/01-hook.html

The viewer's own pain: a huge unfamiliar repo. Columns of file names and code fly toward the
camera in deep Z with depth-of-field blur, accelerating; the two lines land one after another,
centered, Inter 600. At 4.9 s everything decelerates like a tape stopping and the frame snaps to an
empty, dark VS Code window (no files open) — the "where do you even start" silence.

## Frame 2 — The command

- type: product_intro
- blueprint: prompt-type-submit-generate
- duration: 5.4s
- transition_in: cut
- scene: Agent chat panel; the cursor types /tour how does login work; Enter → the text glows green
- on_screen: the command itself, JetBrains Mono — "/tour how does login work"
- asset_candidates: capture/assets/tourcode-mark.svg (activity-bar icon), capture/ui-states/sidebar-home.html (its How-to-start step 2 shows the /tour command style)
- sound: a soft keyclick per character (25 keys, 5.9–8.3, natural rhythm); confirm pop + shimmer on Enter at 8.6; music enters 5.6 (pad), first kick 6.2
- handoff_out: the glowing "/tour" command line — a green route line starts from its end and draws to the right edge at 9.8–10.4
- status: animated
- src: compositions/frames/02-command.html

The empty editor from frame 1 is still there; an agent chat panel slides in on the right
("Claude Code" style input box — generic, no fake branding). Camera pushes in on the input while
the command types. Enter: the command text turns green with a soft bloom. The route line leaves
the command and leads the camera out of frame.

## Frame 3 — The agent explores

- type: feature_showcase
- blueprint: agent-progress-theater
- duration: 6s
- transition_in: cut
- scene: auth.ts, password.ts, session.ts light up green in the file tree one by one; thin green route lines connect them like a subway map
- on_screen: "Your AI agent studies the code…" (11.0–16.0)
- asset_candidates: capture/assets/auth.ts, capture/assets/password.ts, capture/assets/session.ts, capture/assets/tourcode-mark.svg
- handoff_in: the route line enters from the left edge at y=540 and arrives at the file tree's src/ folder
- sound: tick per lit file rising in pitch (11.0 auth.ts, 12.2 password.ts, 13.4 session.ts — +0/+3/+7 semitones); soft swish per route line (11.6, 12.8, 14.0)
- handoff_out: three file nodes and their connecting route lines, centered, which become the tour map's edges
- status: animated
- src: compositions/frames/03-explores.html

A file tree of the demo project (acme-shop: src/auth.ts, src/password.ts, src/session.ts plus
neighbours) floats at a slight angle. The agent "reads": a small "Reading src/auth.ts" status
(same style as the real panel's reading indicator) ticks through files; each of the three files
lights green as it is read, and a thin green line connects it to the previous one — a subway map
forming over the tree.

## Frame 4 — Tour map

- type: feature_showcase
- blueprint: zoom-out-workspace-reveal
- duration: 6.6s
- transition_in: cut
- scene: The route lines settle into the real tour map (handleLogin → findUser → verifyPassword → startSession); pull back to the whole map; dive into the first box
- on_screen: "…and builds a tour." (17.6–21.6)
- asset_candidates: capture/ui-states/overview.html
- handoff_in: the subway-map lines from frame 3 morph into the four-node vertical map
- sound: soft impact as the map settles (17.0); airy whoosh on the pull-back (17.6); deeper swoosh on the dive (22.4)
- handoff_out: the green-bordered "handleLogin(email, password)" node fills the frame at 23.0
- status: animated
- src: compositions/frames/04-tourmap.html

The tour map is the real overview tab (eyebrow "● TOUR MAP · 4 STEPS", "How login works", the
question, summary, the 4-node map, "Start the tour", ROUTE). The camera starts tight on the map
nodes as they settle, pulls back to the whole editor tab, holds, then dives into node 1.

## Frame 5 — Walk through

- type: feature_showcase
- blueprint: device-surface-showcase (floating-window push)
- duration: 10.2s
- transition_in: cut
- scene: auth.ts opens with lines 4–10 highlighted; the explanation panel rises; progress advances through steps 2 and 3 with match-cuts to findUser and password.ts; a glossary term is hovered
- on_screen: "Step by step. Right in your editor." (24.4–28.6)
- asset_candidates: capture/assets/auth.ts, capture/assets/password.ts, capture/ui-states/step1-compact.html, capture/ui-states/step2-compact.html, capture/ui-states/step3-compact-norisk.html, capture/ui-states/sidebar-s0.html, capture/ui-states/sidebar-s1.html, capture/ui-states/sidebar-s2.html
- handoff_in: the green node from frame 4 contracts into the 2 px left border + 14% green band of auth.ts lines 4–10
- sound: brand chime (warm two-note F#→B, identical each time) at 23.6, 26.6, 29.0 as lines highlight; tiny tick per progress segment (26.6, 29.0); soft pop on the glossary tooltip (31.4)
- status: animated
- src: compositions/frames/05-walkthrough.html

Full VS Code Dark Modern window in 2.5D: activity bar (TourCode route icon active), real sidebar
(steps list, progress), editor tab "auth.ts", line numbers, code in JetBrains Mono, the real step
panel under the code. Step 1: lines 4–10 green. Push-in on the lines. Next → step 2: the highlight
match-cuts to lines 12–15 (findUser), sidebar + panel progress advance. Next → step 3: tab switches
to password.ts, lines 1–7. Hover "verifyPassword" (underlined glossary term in the panel text):
the real tooltip with its definition pops up.

## Frame 6 — Risks

- type: feature_showcase
- blueprint: panel-edit-live-sync
- duration: 6s
- transition_in: cut
- scene: The Risks toggle turns on; the step's risk markers appear on their lines with their notes from the tour JSON
- on_screen: "See what can break." (35.6–38.6)
- asset_candidates: capture/ui-states/step3-compact-norisk.html, capture/ui-states/step3-compact.html, capture/assets/password.ts
- sound: toggle click (34.4); low, soft, non-alarming tone per marker (35.0 line 6 high, 35.6 line 2 low)
- status: animated
- src: compositions/frames/06-risks.html

Same window, step 3 (password.ts). The cursor clicks the real "Risks" pill: its switch turns red
(real webview state). In the editor, a risk marker appears in the gutter of line 6 (red, High ·
Security) and line 2 (muted, Low), each with an inline note; in the panel the real risk blocks
appear. Camera pushes toward line 6: "hashPassword just reverses the string…".

## Frame 7 — Ask and go deeper

- type: feature_showcase
- blueprint: camera-journey (A, action roundtrip)
- duration: 7.8s
- transition_in: cut
- scene: The suggested question is clicked, the answer streams in; then "Explain deeper" dives into the sub-tour "Inside handleLogin"; the sidebar shows the Path
- on_screen: "Ask anything." (40.0–42.8) → "Go as deep as you need." (43.6–46.8)
- asset_candidates: capture/ui-states/step1-compact.html, capture/ui-states/step1-answering.html, capture/ui-states/step1-answered.html, capture/ui-states/subtour-step.html, capture/ui-states/sidebar-subtour.html, capture/assets/auth.ts
- handoff_in: the green line band of password.ts expands to fill the frame, then contracts into auth.ts lines 4–10 (step 1)
- sound: click (39.8); soft typing texture while the answer streams (40.4–42.6); deep whoosh with reverse reverb on the dive (43.4→44.6); light slide as the Path appears (44.6)
- status: animated
- src: compositions/frames/07-ask-deeper.html

Back on step 1. Cursor clicks "Why return a result object instead of throwing an error?" — the
real streaming state ("Reading src/auth.ts", text arriving word by word), then the answered state
with follow-ups. Cursor clicks "Explain deeper": the camera flies through highlighted line 6 into
deeper code with depth-of-field blur and lands in the sub-tour — trail "SUB-TOUR How login works ›
1. The login entry point", "STEP 2 OF 5 · The guard before any session", lines 5–8; the sidebar
slides to the real Path (How login works → Inside handleLogin).

## Frame 8 — For teams

- type: benefit_highlight
- blueprint: cursor-ui-demo
- duration: 6s
- transition_in: cut
- scene: Sidebar home: the tour sits in "Start here" with a soft green pulse, a team group "Authentication" below; an out-of-date tour turns fresh after "Rebuild"
- on_screen: "Onboard your team in minutes." (48.2–52.4)
- asset_candidates: capture/ui-states/sidebar-home-unpinned.html, capture/ui-states/sidebar-home.html, capture/ui-states/sidebar-home-stale.html, capture/assets/tourcode-mark.svg
- sound: pin snap (47.6); soft slides for the groups (48.2, 48.8); swirl (50.0) + success chime (50.6) on rebuild
- status: animated
- src: compositions/frames/08-teams.html

The real sidebar home, large and centered (the camera treats the 360 px sidebar as the hero).
"How login works" snaps into START HERE (pinned, green border) with one soft green pulse; the
Authentication team group slides in below with "Creating a session after login" flagged
"Out of date: the code changed in 2 of 6 steps · Rebuild". The cursor clicks Rebuild; a brief
spinner, the flag clears — fresh.

## Frame 9 — Works everywhere

- type: social_proof
- blueprint: fixed-anchor-cycle
- duration: 3.6s
- transition_in: cut
- scene: A row of editor logos, then agent logos and a Jupyter icon, each landing on the beat along the route line
- on_screen: "Your editor. Your agent." (53.6–56.4)
- asset_candidates: official logos via /media-use (VS Code, Cursor, Kiro, Windsurf, Claude Code, Jupyter), capture/assets/tourcode-mark.svg
- sound: one soft percussive hit per logo on the beat grid (eighths: 53.3–55.4)
- handoff_out: the route line running under the logos continues and starts drawing the logo's S-curve
- status: animated
- src: compositions/frames/09-everywhere.html

Two rows, monochrome-ish on dark (logos in their own colors but dimmed to sit calmly): Editors —
VS Code, Cursor, Kiro, Windsurf; Agents — Claude Code, Cursor, Kiro; plus Jupyter ("Understands
Jupyter notebooks"). A thin green route line runs under the rows like a track and lights each logo
as it passes.

## Frame 10 — End card

- type: branding
- blueprint: logo-assemble-lockup
- duration: 3.4s
- transition_in: cut
- scene: The route line draws the TourCode logo; soft green glow; wordmark, tagline and link
- on_screen: "TourCode" / "Understand any codebase, one step at a time." / "Try it: [link]"
- asset_candidates: capture/assets/tourcode-logo.svg, capture/assets/tourcode-mark.svg
- handoff_in: the route line from frame 9 enters and traces start-dot → S-curve → arrow
- sound: riser following the line (56.6→58.4); shimmering resolve hit on the logo (58.4); music lands its final note at 58.4 and fades over 1.5 s
- status: animated
- src: compositions/frames/10-endcard.html

The line traces the logo's route (circle, S-curve, arrow) at 56.6–58.2, the green disc fills
behind it at 58.4 with a soft bloom, then "TourCode" (Inter 600), the tagline and "Try it: [link]"
settle beneath. Hold to 60.0.
