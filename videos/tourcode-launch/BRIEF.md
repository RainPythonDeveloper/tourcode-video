---
workflow: product-launch-video
flow: automation
storyboard: yes
message: "Understand any codebase in minutes, not days"
destination: youtube
aspect: 1920x1080
language: en
audience: developers worldwide
length: 60s
angle: product-demo
narration: no
vo_mode: restructured
---

## Intent

A 60-second launch film for TourCode: a tool that turns any codebase into a guided,
step-by-step tour inside the code editor. A developer types `/tour how does login work`
to their AI coding agent; the agent studies the project and builds a tour that the editor
walks through. Tone: calm, confident, precise, a little magical. No hype, no robots, no
stock people. Full sound design, no voiceover in the main master; burned-in captions so it
works muted. Source brief verbatim: `../../prompt.md`.

## Assets

- ../../assets/ui/*.html — the real TourCode webview pages (webview.js + webview.css + theme.css). Every UI in the film is rendered from these, never invented.
  - tour-map.html — tour map editor tab (1280 px) → frames 04, 05
  - step.html — explanation panel, step 1 with risk, details, diagram, Q&A, sub-tour card (1280 px) → frames 05, 06, 07
  - step-answering.html — the panel while the answer streams (1280 px) → frame 07
  - step-subtour.html — the panel inside the sub-tour "Inside handleLogin" (1280 px) → frame 07
  - sidebar-tour.html — sidebar during the tour (360 px) → frame 05
  - sidebar-subtour.html — sidebar inside the sub-tour, with the Path (360 px) → frame 07
  - sidebar-home.html — sidebar home: Start here, team group "Authentication" (360 px) → frame 08
- ../../assets/code/src/{auth,password,session}.ts — the demo project's code, shown in the editor.
- ../../assets/tours/*.json — the three demo tours (line ranges, risks, glossary, questions).
- ../../assets/brand/tourcode-logo.svg — white route on green #2DA44E circle; end card.
- ../../assets/brand/tourcode-mark.svg — route outline; activity bar icon, route motif.

## Customizations

- Storyboard and on-screen text are fixed by the brief (9 beats, 0:00–1:00); on-screen text in English, sentence case, ≤7 words per line, one message at a time.
- Editor chrome built in HTML as VS Code Dark Modern: activity bar with TourCode route icon, TourCode sidebar on the left, editor tab, line numbers, code in JetBrains Mono, explanation panel under the code. Step lines: #3FB950 at 14% background + 2 px green left border, at the tour JSON's line range.
- Motion: smooth 2.5D camera (push-ins, pull-backs, parallax), expo/cubic easing, 400–600 ms transitions, readable holds 1.5–2 s. Signature transition: the green route line draws across the frame and leads to the next scene (match-cut on the line). Second: a highlighted line's green bar expands to fill the frame then contracts into the next scene. "Dive" for the sub-tour with depth-of-field blur. Cut on the beat. No shake, glitch or flashing.
- Sound design per beat (see prompt.md); signature brand chime identical every time lines highlight.
- Music: minimal modern electronic / lo-fi tech, 100–110 BPM, warm synths, building gently to the end card, no vocals; from the catalog via /media-use.
- Mix: bed ≈ −20 LUFS under SFX, dipping 3–4 dB under each signature effect; master −14 LUFS integrated, −1 dBTP.
- Captions burned in (embedded-captions skill).
- SFX not in the catalog → ElevenLabs text_to_sound_effects (0.5–5 s each). Ask the user before any paid call.
- Optional second master with a calm, warm English voice reading only the on-screen lines (ask first); music ducked 6–8 dB under voice; captions synced by transcription.

## Notes

- Deliverables into ../../out: tourcode-demo-16x9.mp4 (1920×1080, 60 fps, 60 s), tourcode-demo-9x16.mp4 (1080×1920, 30 s), tourcode-demo-1x1.mp4 (1080×1080, 30 s), tourcode-teaser-15s.mp4, tourcode-thumbnail.png (1280×720, "Take the tour"), ../../out/sfx/ + list.
- Show the storyboard and the sound list before the first full render.
- Pre-render checks: UI matches assets/ui, every code line readable, every caption ≥1.5 s, green only for what matters, ≤2 accent colors per frame, sound hits land on visual events.
- Visual identity: bg #0D1117 / #181818, cards #1F1F1F, borders #313131, 8 px radius, text #E6E6E6, secondary #9D9D9D, accent #3FB950; sparingly #4DAAFC, #CCA700, #F85149. Inter (semibold, tight) + JetBrains Mono. Eyebrows with a glowing green dot.
