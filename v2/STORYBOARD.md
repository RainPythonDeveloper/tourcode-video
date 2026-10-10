# TourCode — 60 s launch teaser · storyboard v2

**Key message:** Understand any codebase, one step at a time.
**Format:** 1920×1080, 60 fps, 75.0 s (approved: longer than 60 s, with an export scene added). Dark, precise, generous negative space, one idea per moment.

## Grid

- **112 BPM**, 4/4 → beat 0.536 s, bar 2.143 s. **35 bars = exactly 75.0 s.**
- Every scene cut sits on a bar line; every in-scene event sits on a beat or an 8th.
- The music builds from a near-silent hook to **the drop on bar 10 (0:19.29) = the tour map reveal**.
- Recurring motif: **the route line from the logo**. It leaves the command, connects the files,
  becomes the tour map, becomes a highlighted line's green border, and finally draws the logo.

| # | Scene | Bars | Time | Technique |
|---|-------|------|------|-----------|
| 1 | Hook | 1–3 | 0:00.00–0:06.43 | Kinetic typography in Z-depth |
| 2 | The command | 4–6 | 0:06.43–0:12.86 | Typewriter + slow push-in, grey → green colour shift |
| 3 | The agent studies the code | 7–9 | 0:12.86–0:19.29 | Shape play: nodes and route lines (subway map) |
| 4 | **The reveal: tour map** | 10–13 | 0:19.29–0:27.86 | Match cut on the lines + camera pull-back, on the drop |
| 5 | Step by step | 14–18 | 0:27.86–0:38.57 | Camera dive + travelling green highlight (match cuts between steps) |
| 6 | Go deeper | 19–23 | 0:38.57–0:49.29 | Z-axis fly-through into the sub-tour |
| 7 | For teams | 24–26 | 0:49.29–0:55.71 | Cards lock into place on the beat |
| 8 | **Export (new)** | 27–29 | 0:55.71–1:02.14 | The tour folds into a page and flies out to the team's wiki |
| 9 | Works everywhere | 30–31 | 1:02.14–1:06.43 | Grid snap: logos lock in on the beat |
| 10 | Final frame | 32–35 | 1:06.43–1:15.00 | The route line draws the logo |

---

## 1 · Hook — 0:00.00–0:06.43 (bars 1–3)

- **Idea:** an unfamiliar codebase is overwhelming.
- **Technique:** kinetic typography in Z-depth.
- **Narration:** *"You open a codebase you've never seen. Where do you even start?"*
- **On screen (word by word, in sync with the voice):** "A codebase you've never seen." → "Where do you even start?"
- **Visual:** black #0D1117. Planes of dim code (the demo's own lines, tiled into an endless wall, #9D9D9D at
  low opacity, depth-of-field blur) and file-tree rows drift toward the camera, faster and faster.
  The narration words land one at a time in Inter, white, centre frame, sharp against the blur.
  On "start?" everything freezes and drains to black in one beat.
- **Cut (bar 4):** hard cut on the downbeat to a single blinking caret in empty space.
- **Sound:** sub drone + filtered noise riser across bars 1–3; three airy rush whooshes as the planes pass;
  the riser stops dead on the last beat of bar 3 (tape-stop thud), then half a beat of silence.

## 2 · The command — 0:06.43–0:12.86 (bars 4–6)

- **Idea:** one command.
- **Technique:** typewriter + slow camera push-in; colour shift grey → green on Enter.
- **Narration:** *"Ask your coding agent: slash tour, how does login work."*
- **On screen:** the agent's chat input (a #1F1F1F card, #313131 border, 8 px corners) with the command typed
  character by character in JetBrains Mono: `/tour how does login work` — each character appears as it is spoken.
- **Visual:** the camera pushes in slowly on the input. On Enter (beat 1 of bar 6) `/tour` turns green #3FB950
  with a soft glow, and a thin green route line leaves the end of the command and runs off the right edge.
- **Cut (bar 7):** match cut on the line — the camera follows it into the next scene.
- **Sound:** music enters on bar 4: soft pad + muted pulse on 1 and 3. A soft key click per character;
  a confirm pop + shimmer on Enter; a light swish as the line runs out.

## 3 · The agent studies the code — 0:12.86–0:19.29 (bars 7–9)

- **Idea:** the agent reads the code and finds the route through it.
- **Technique:** shape play — files as nodes, joined by route lines like a subway map.
- **Narration:** *"It studies the code, and finds the route through it."*
- **On screen:** the narration's key words ("studies the code", "the route") in the lower third, in sync.
- **Visual:** the project's file tree floats in grey (#9D9D9D). The route line arrives from the left;
  `src/auth.ts`, `src/password.ts`, `src/session.ts` light up green one per beat, and the line connects them
  with rounded 90° turns — the logo's route shape. The function names appear beside each file:
  `handleLogin`, `findUser`, `verifyPassword`, `startSession`.
- **Cut (bar 10):** the four names lift off the tree and become the four boxes of the map (match cut).
- **Sound:** the pulse builds — hats join, the filter opens, a riser through bar 9. A tick per lit file,
  rising in pitch; a soft swish each time a line segment draws.

## 4 · The reveal: tour map — 0:19.29–0:27.86 (bars 10–13) · THE DROP

- **Idea:** the whole answer at a glance.
- **Technique:** match cut on the lines + camera pull-back, landing on the drop.
- **Narration (starts half a bar after the drop, so the hit breathes):**
  *"A tour map: the whole answer. Each box leads to its step."*
- **On screen:** the rebuilt tour-map tab from `assets/ui/tour-map.html`: eyebrow "● TOUR MAP · 4 STEPS",
  title "How login works", the question "how does login work in this project?", and the map
  `handleLogin(email, password)` → `findUser(email)` → `verifyPassword(password, hash)` → `startSession(userId)`
  with edge labels `email`, `user.passwordHash`, `if password ok`. Then the ROUTE list (4 steps with
  `auth.ts:4–10`, `auth.ts:12–15`, `password.ts:1–7`, `session.ts:1–3`).
- **Visual:** on the downbeat of bar 10 the four boxes snap into the vertical map and the edges draw down
  in one stroke; the camera pulls back from the boxes to the whole tab floating in 2.5D with a soft shadow.
  Box 1 keeps its green border and glow; the ROUTE items light in sequence, one per beat.
- **Cut (bar 14):** the camera dives into box 1 — its green outline fills the frame.
- **Sound:** **the drop** — full groove (soft four-on-the-floor kick, warm sub bass, wide pad, plucked arp),
  a deep soft impact + shimmer on the map snap; an airy whoosh on the pull-back; a deeper swoosh on the dive.

## 5 · Step by step — 0:27.86–0:38.57 (bars 14–18)

- **Idea:** the exact lines, highlighted and explained.
- **Technique:** camera dive, then a travelling green highlight with match cuts between steps.
- **Narration:** *"Step by step, the right file opens. The exact lines light up, explained right under the code."*
- **On screen:** the editor rebuilt in 2.5D (VS Code Dark Modern look): TourCode sidebar on the left
  (from `sidebar-tour.html`: "● TOUR · 4 STEPS", progress bar, the steps), the tab `auth.ts`, line numbers,
  the demo code in JetBrains Mono, the explanation panel under the code (from `step.html`:
  "● STEP 1 OF 4 · auth.ts:4–10", "The login entry point", its text).
- **Visual:**
  - Bar 14: box 1's outline contracts into the 2 px green left border of `auth.ts` lines 4–10;
    the 14 % green band wipes down the lines; the panel rises under the code.
  - Bar 16: Next → the highlight slides to lines 12–15 ("Looking up the user by email"), progress advances.
  - Bar 17: match cut on the green bar → `password.ts` lines 1–7 ("Verifying the password").
  - Bar 18: the dotted-underlined term `verifyPassword` in the panel is hovered; its glossary card pops up:
    "Hashes the submitted password and checks whether it equals the stored hash."
  - Camera: slow push-in on the lit lines, gentle parallax between sidebar, code and panel.
- **Sound:** **the highlight chime** — one short, warm two-note chime, identical every time a line range lights
  (3× here); a tiny tick per progress segment; a soft pop on the glossary card.

## 6 · Go deeper — 0:38.57–0:49.29 (bars 19–23)

- **Idea:** go as deep as you need.
- **Technique:** a Z-axis fly-through — the camera moves *into* the code.
- **Narration:** *"Ask about any step."* (bar 19) · *"See what can break."* (bar 21) · *"Go deeper, and the Path shows where you are."* (bar 22)
- **Visual:**
  - Bars 19–20: back on step 1. The suggested question chip "Why return a result object instead of throwing an error?"
    is clicked; the answer streams in under it (`step-answering.html` → `step.html`).
  - Bar 21: the "Risks" switch turns on; the risk marker appears on line 6 with its note
    (Low · Breaks on change: "verifyPassword returns a boolean synchronously; this guard relies on that…").
  - Bar 22: "Explain deeper" — the camera flies through the highlighted lines (depth-of-field blur) and lands
    in the sub-tour "Inside handleLogin" (`step-subtour.html`, "● STEP 2 OF 5"), "The guard before any session",
    `auth.ts` lines 5–8 lit green.
  - Bar 23: the sidebar shows the Path (`sidebar-subtour.html`): "How login works ← step 1" → "● Inside handleLogin".
- **Sound:** a click on the chip; a soft typing texture while the answer streams; a toggle click and a low,
  soft, non-alarming tone for the risk marker; a deep whoosh with reverse reverb on the dive; the highlight chime
  as the sub-tour lines light; a light slide as the Path appears.

## 7 · For teams — 0:49.29–0:55.71 (bars 24–26)

- **Idea:** a tour every newcomer starts from.
- **Technique:** cards lock into place on the beat.
- **Narration:** *"Pin a tour to Start here, for every newcomer."*
- **Visual:** the sidebar home (`sidebar-home.html`) large and centred: the tour "How login works" drops into
  **START HERE** and pins (green pin, soft pulse); the team group "Authentication" slides in below; a tour flagged
  as changed is rebuilt with one click and turns fresh.
- **Sound:** a pin snap; a soft slide for the group; a swirl + light chime on rebuild.

## 8 · Export — 0:55.71–1:02.14 (bars 27–29) · new

- **Idea:** the tour leaves the editor and lives where the team reads.
- **Technique:** the tour folds into a single page, which flies out and docks into the team's wiki.
- **Narration:** *"Export any tour as a page, for Confluence, Notion, or your wiki."*
- **Visual:** the sidebar's "Export" link is clicked; the tour's steps, map and code collapse into one page
  (the look of the exported page, `assets/tours/how-login-works.page.html`); the page flies to the right and
  docks between the Confluence and Notion marks, landing as a wiki page.
- **Sound:** a click; a paper-like swish as the page folds; a soft landing thump.

## 9 · Works everywhere — 1:02.14–1:06.43 (bars 30–31)

- **Narration:** *"Your editor. Your agent. Even your notebooks."*
- **Visual:** a clean row of editor marks snaps in, one per beat — VS Code, Cursor, Kiro, Windsurf — then the
  agents — Claude Code, Cursor, Kiro — then the Jupyter mark. Monochrome on dark, equal optical size.
- **Sound:** one soft percussive hit per logo, on the beat; a riser under the last bar.

## 10 · Final frame — 1:06.43–1:15.00 (bars 32–35)

- **Narration:** *"TourCode."* (bar 32) · *"Understand any codebase, one step at a time."* (bar 33)
- **Visual:** everything clears to #0D1117. On the downbeat of bar 32 the route line from the logo
  draws itself (start dot → curves → arrowhead), then the #2DA44E circle blooms behind it — the full
  `tourcode-logo.svg`. "TourCode" sets beside it, then the line
  **"Understand any codebase, one step at a time."** appears word by word with the voice, then
  **"Try it: github.com/RainPythonDeveloper/tourcode"** in JetBrains Mono. Hold still for the last ~3 s.
- **Sound:** the riser resolves into a warm, shimmering hit as the line completes; the music lands on its
  final chord and rings out to silence at 1:15.

---

## Narration script (eleven_v3 was the brief; see the README for the voice actually used)

1. You open a codebase you've never seen. Where do you even start?
2. Ask your coding agent: slash tour, how does login work?
3. It studies the code, and finds the route through it.
4. A tour map: the whole answer. Each box leads to its step.
5. Step by step, the right file opens. The exact lines light up, explained right under the code.
6. Ask about any step. See what can break. Go deeper, and the Path shows where you are.
7. Pin a tour to Start here, for every newcomer.
8. Export any tour as a page, for Confluence, Notion, or your wiki.
9. Your editor. Your agent. Even your notebooks.
10. TourCode. Understand any codebase, one step at a time.

Each sentence is generated separately and placed on its beat (`source/narration/script.json`); the
word timings come from the voice model and drive every on-screen word.

## Poster frames

1. The tour map at the moment of the reveal (≈0:22).
2. Step 1 with `auth.ts` lines 4–10 lit green and the panel under the code (≈0:30).
3. The final frame: logo, line, call to action (≈1:13).
