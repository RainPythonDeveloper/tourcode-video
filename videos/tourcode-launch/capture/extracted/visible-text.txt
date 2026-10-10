Make a 60-second product launch video for TourCode, with full sound design, using HyperFrames: start with the /product-launch-video skill; use /media-use for music and sound effects, /hyperframes-audio for the mix, and the embedded-captions skill for captions. If a sound we need is not in the catalog, generate it with the ElevenLabs MCP tool text_to_sound_effects (0.5–5 s each). Ask me before any paid call, and show me the storyboard and the sound list before the first full render.

There are no screen recordings: build every scene in HTML from the real product files in ./assets.

=== ASSETS (the source of truth for how TourCode looks) ===
- assets/ui/*.html: the real TourCode interface. Each page loads the extension's own webview.js and webview.css and draws a real state of the product; theme.css stands in for VS Code's Dark Modern theme. Open them, and reuse their DOM and CSS (embed or copy them) for the UI in the scenes; never invent UI that does not exist.
  - tour-map.html: the tour map (an editor tab), 1280 px wide.
  - step.html: the explanation panel under the code: step 1 with its risk, the full explanation, the step's diagram, a question with its answer and next questions, and the sub-tour card. 1280 px.
  - step-answering.html: the same panel while the agent's answer streams in. 1280 px.
  - step-subtour.html: the panel inside a sub-tour, with the trail back to the main tour. 1280 px.
  - sidebar-tour.html: the sidebar during the tour: progress bar, tour map button, steps, the sub-tour under its step. 360 px.
  - sidebar-subtour.html: the sidebar inside the sub-tour, with the Path from the main tour down to it. 360 px.
  - sidebar-home.html: the sidebar's home: "Start here" (a pinned tour), a team group "Authentication", project tours. 360 px.
- assets/code/src/*.ts: the demo project's code (a small login flow) to show in the editor.
- assets/tours/*.json: the three demo tours (titles, steps, line ranges, explanations, diagrams, risks, glossary, suggested questions). The main one is how-login-works.json; how-login-works-handle-login-inside.json is its sub-tour; session-start.json is a second tour. The *.page.html files are the same tours as the browser page TourCode makes without the editor extension.
- assets/brand/tourcode-logo.svg (white route on a green #2DA44E circle) and tourcode-mark.svg (the route outline).

The editor around the panels does not exist as a file: build it in HTML as VS Code's Dark Modern window — an activity bar with the TourCode route icon, the TourCode sidebar on the left (the sidebar pages), the editor with a tab, line numbers and the demo code in JetBrains Mono, and the explanation panel under the code (the step pages). A step's lines are highlighted with a green background (#3FB950 at 14% opacity) and a 2 px green left border, at the line range the tour JSON gives.

=== PRODUCT ===
TourCode turns any codebase into a guided, step-by-step tour inside the code editor. A developer types to their AI coding agent: /tour how does login work. The agent studies the project and builds a tour; the editor walks through it:
- Tour map: a diagram of the whole answer; each box leads to its step.
- Steps: the right file opens, the exact lines are highlighted in green, a short explanation sits under the code, the full one opens with "More", each step has a small diagram.
- Risks layer: marks lines where something can break.
- Glossary: project terms underlined, definition on hover.
- Ask about a step: one-click suggested questions, the answer streams in.
- Explain deeper / What breaks: a sub-tour from the current step; the Path in the sidebar shows where you are.
- Teams: pin a tour to "Start here", group tours, out-of-date tours are flagged and rebuilt with one click.
- Works in VS Code, Cursor, Kiro and Windsurf, with Claude Code, Cursor or Kiro as the agent. Understands Jupyter notebooks.
Promise: understand any codebase in minutes, not days.
Audience: developers worldwide. Tone: calm, confident, precise, a little magical. No hype, no robots, no stock people.

=== VISUAL IDENTITY ===
Dark editor aesthetic. Background #0D1117 / #181818, cards #1F1F1F with #313131 borders and 8 px corners, text #E6E6E6, secondary #9D9D9D. Brand accent green #3FB950. Sparingly: link blue #4DAAFC, amber #CCA700, risk red #F85149.
Type: Inter (headlines, semibold, tight tracking), JetBrains Mono (code and the /tour command). Small uppercase "eyebrow" labels with a glowing green dot, as in the UI ("● TOUR · 4 STEPS").
Main motif: the logo's route line — a guided path drawn through code. The editor floats in 2.5D space with soft shadows, a subtle green glow on the active element, light grain and a gentle vignette. Code and UI text must always be legible.

=== MOTION ===
Smooth 2.5D camera: slow push-ins on highlighted lines, pull-backs to reveal the tour map, parallax between sidebar, editor and explanation panel. Expo/cubic easing, transitions 400–600 ms, hold readable frames 1.5–2 s.
Signature transition: the green route line draws itself across the frame and leads the camera to the next scene (match-cut on the line). Second: a highlighted line's green bar expands to fill the frame, then contracts into the next scene. "Dive" for the sub-tour: the camera flies through a highlighted line into deeper code with depth-of-field blur. Cut on the music's beat. No shake, no glitch, no flashing.

=== STORYBOARD, ON-SCREEN TEXT AND SOUND (16:9 master, 60 s) ===
0:00–0:05 HOOK. An endless file tree and code blur past in depth. Text: "New codebase. 50,000 lines." → "Where do you even start?" Hard stop on an empty dark editor.
  Sound: low riser + fast data-rush whoosh; a soft tape-stop thud at 0:05, then a beat of near-silence.
0:05–0:10 THE COMMAND. An agent chat panel; the cursor types: /tour how does login work. Push-in; on Enter the text glows green.
  Sound: soft, crisp keyboard clicks synced to each character; a gentle confirm pop + shimmer on Enter. The music starts here (soft pad + light beat).
0:10–0:16 THE AGENT EXPLORES. auth.ts, password.ts and session.ts light up green in the file tree one by one; thin green route lines connect them like a subway map. Text: "Your AI agent studies the code…"
  Sound: light ticks per lit file, rising in pitch; a soft swish each time a route line draws.
0:16–0:23 TOUR MAP. The lines settle into the tour map of tour-map.html (handleLogin → findUser → verifyPassword → startSession). Pull back to the whole map, then dive into the first box. Text: "…and builds a tour."
  Sound: airy whoosh on the pull-back; a soft impact when the map settles; a deeper swoosh on the dive.
0:23–0:33 WALK THROUGH. auth.ts opens with lines 4–10 highlighted; the explanation panel rises (step.html, "● STEP 1 OF 4"). Push-in on the lines; the progress bar advances through steps 2 and 3 with match-cuts to findUser and password.ts. A glossary term is hovered and its definition pops up. Text: "Step by step. Right in your editor."
  Sound: a warm two-note chime when lines highlight (the brand sound — identical every time); a tiny tick per progress segment; a soft pop on the glossary tooltip.
0:33–0:39 RISKS. The "Risks" toggle turns on; the step's risk marker appears on its line with its note (from the tour JSON). Text: "See what can break."
  Sound: toggle click; a low, soft, non-alarming warning tone per marker.
0:39–0:47 ASK AND GO DEEPER. The suggested question "Why return a result object instead of throwing an error?" is clicked; the answer streams in (step-answering.html → step.html). Then "Explain deeper": dive into the sub-tour "Inside handleLogin" (step-subtour.html); the sidebar shows the Path (sidebar-subtour.html). Text: "Ask anything. Go as deep as you need."
  Sound: click; a subtle soft-typing texture while the answer streams; a deep whoosh with reverse reverb on the dive; a light slide for the Path.
0:47–0:53 FOR TEAMS. The sidebar home (sidebar-home.html): the tour sits in "Start here" with a soft green pulse, a team group "Authentication" below; a tour marked "out of date" turns fresh after "Rebuild". Text: "Onboard your team in minutes."
  Sound: a satisfying pin snap; soft slides for the groups; a swirl + success chime on rebuild.
0:53–0:57 WORKS EVERYWHERE. A row of logos: VS Code, Cursor, Kiro, Windsurf, then Claude Code, Cursor, Kiro, and a Jupyter icon (official logos via /media-use). Text: "Your editor. Your agent."
  Sound: one soft percussive hit per logo, on the beat.
0:57–1:00 END CARD. The route line draws the TourCode logo; soft green glow. "TourCode" / "Understand any codebase, one step at a time." / "Try it: [link]".
  Sound: a riser following the line; a shimmering resolve hit on the logo; the music lands on its final note and fades in 1.5 s.

On-screen text: English, sentence case, at most 7 words per line, one message at a time.

=== MUSIC AND MIX ===
Music: minimal modern electronic / lo-fi tech, 100–110 BPM, warm synths, building gently to the end card, no vocals; resolve it from the catalog via /media-use.
Mix: the music bed around −20 LUFS under the sound effects, dipping 3–4 dB under each signature effect; effects short and clean; final master −14 LUFS integrated, true peak −1 dBTP. Captions are burned in, so the video works muted.

=== OPTIONAL VOICEOVER VERSION ===
A second master with a calm, warm English voice (ElevenLabs text_to_speech or HeyGen TTS — ask me first), reading only the on-screen lines; duck the music 6–8 dB under the voice and sync the captions to the voice by transcription.

=== DELIVERABLES (into ./out) ===
1. tourcode-demo-16x9.mp4 — 1920×1080, 60 fps, 60 s (YouTube, Product Hunt, website).
2. tourcode-demo-9x16.mp4 — 1080×1920, 30 s (Shorts, Reels, TikTok): hook → command → tour map → highlighted step → end card, UI centered and zoomed.
3. tourcode-demo-1x1.mp4 — 1080×1080, 30 s (X, LinkedIn).
4. tourcode-teaser-15s.mp4 — command → tour map → end card.
5. tourcode-thumbnail.png — 1280×720: green-highlighted code with the tour map floating above, the words "Take the tour".
6. The sound effects as separate files in ./out/sfx/ with a short list of what each one is.

=== CHECKS BEFORE THE FINAL RENDER ===
Snapshot the key frames and check: the UI matches assets/ui, every line of code is readable, every caption stays on screen at least 1.5 s, green is used only for what matters, no more than two accent colors per frame, sound hits land exactly on the visual events. Fix and re-check, then render all deliverables.
