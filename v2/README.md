# TourCode — launch teaser v2

**Understand any codebase, one step at a time.**

| File | What it is |
|------|------------|
| `tourcode-teaser-v2.mp4` | The film (v4): 1920×1080, 60 fps, 75.0 s, H.264 High (yuv420p, BT.709) + AAC 256 kb/s, −14 LUFS, 27.5 MB |
| `posters/poster-1-tour-map.png` | Poster frame: the tour map, just after the reveal (0:23) |
| `posters/poster-2-step.png` | Poster frame: step 1, `auth.ts` lines 4–10 lit, the explanation under the code (0:31) |
| `posters/poster-3-final.png` | Poster frame: the final frame (1:14) |
| `STORYBOARD.md` | The approved storyboard: scenes, techniques, narration, sound |
| `checks/` | Contact sheets (stills before the render, the encoded MP4 after it) and the loudness report |
| `source/` | Everything needed to re-render (see below) |

The brief asked for 60 s; on review the export scene was added and the length freed, so the film
is 75 s (35 bars at 112 BPM). v4 (this version): no subtitles and no extra key words, the film's text in
Manrope + Commit Mono, lines appear whole; the rebuilt export scene of v2.1 stays. Earlier renders are in
the git history.

## The story

Every cut sits on a bar line of the music (112 BPM, 2.143 s per bar); the tour map lands on the drop.

| # | Time | Idea | Technique | Narration |
|---|------|------|-----------|-----------|
| 1 | 0:00 | An unfamiliar codebase is overwhelming | Kinetic typography over code flying past in depth | You open a codebase you've never seen. Where do you even start? |
| 2 | 0:06 | One command | Typewriter synced to the voice, push-in, grey → green on Enter | Ask your coding agent: slash tour, how does login work? |
| 3 | 0:13 | The agent finds the route | Shape play: files light up and connect like a subway map | It studies the code, and finds the route through it. |
| 4 | 0:19 | **The tour map (the drop)** | Match cut: the subway stations *are* the map's boxes; pull-back | A tour map: the whole answer. Each box leads to its step. |
| 5 | 0:28 | The exact lines, explained | Box 1 grows to fill the frame and contracts into the green lines; the highlight travels step to step | Step by step, the right file opens. The exact lines light up, explained right under the code. |
| 6 | 0:39 | Go as deep as you need | Ask a question, Risks on, Explain deeper: the camera flies into the lines; the Path | Ask about any step. See what can break. Go deeper, and the Path shows where you are. |
| 7 | 0:49 | For teams | The tour card travels to "Start here"; a changed tour is rebuilt | Pin a tour to Start here, for every newcomer. |
| 8 | 0:56 | Export | The window morphs into the exported page (its parts fly in from the tour); three green routes carry copies to Confluence, Notion and your wiki, each landing as its name is spoken | Export any tour as a page, for Confluence, Notion, or your wiki. |
| 9 | 1:02 | Works everywhere | Editor and agent marks snap in on the beat | Your editor. Your agent. Even your notebooks. |
| 10 | 1:06 | Final frame | The logo's route line draws itself, the green circle blooms | TourCode. Understand any codebase, one step at a time. |

No subtitles. The film's own text is kept to a few lines — the hook, "Ask your coding agent:",
the row labels by the logos and the final line — set in **Manrope**, with the `/tour` command and
the call to action in **Commit Mono**. Each line appears whole, in one quick fade, as its first word
is spoken (word timings from the voice model). The product's own screens keep their own fonts. All TourCode UI in the film is the product's own: the pages in `assets/ui` are drawn
by the extension's `webview.js` with `webview.css` into new states (step 2, step 3, the answer
streaming, risks on, a pinned / out-of-date tour…), and that DOM is embedded in the film with the
same CSS. Code, step titles, diagram labels, the risk note and the glossary definition come from
`assets/code` and `assets/tours`. Only the VS Code window around the panels is built in HTML.

Sound: the music (112 BPM, warm minimal electronic, building to the drop on the tour map) and all
effects are synthesized in code (`source/audio`), no samples. The green highlight has its own short
warm two-note chime (A5 → D6), the same sound every time lines light up. The music ducks about
10 dB under the voice and dips under the signature sounds.

## Checks

- Contact sheet of stills before the full render: `checks/contact-sheet-stills.png`.
- Contact sheet of the encoded MP4: `checks/contact-sheet-mp4.png`.
- Loudness of the final MP4's audio (ffmpeg `ebur128`, `checks/loudness.txt`): integrated **−14.1 LUFS**,
  true peak **−1.1 dBTP**, loudness range 4.7 LU.
- The three render workers' seams (0:25, 0:50) show no jump: frame-to-frame change there is the same as
  around them.
- Colour: an encoded frame matches the browser render within 1/255.
- Voice over the background in the speech band (300 Hz–4 kHz) is 6.6–22 dB on every line.

## Re-render

Needs Node 18+, Python 3.11+, ffmpeg and Chromium for Playwright.

```bash
cd source
./render.sh                 # picture + sound, with the narration already in source/narration
VOICE=kokoro ./render.sh    # also regenerates the narration with Kokoro (downloads ~350 MB)
```

What it runs, step by step:

1. `node render/snapshot-ui.mjs` — draws every UI state with the real `webview.js` and saves the DOM to `data/ui-states.js`.
2. `python render/build-logos.py` — the one-tone editor/agent/wiki marks → `data/logos.js`.
3. `node render/cues.mjs` — exports the sound cues the film registers next to each visual event → `data/sfx-cues.json`.
4. `python audio/music.py` and `python audio/mix.py` — score, effects, ducking, master to −14 LUFS / −1 dBTP.
5. `node render/stills.mjs ../checks/stills` — stills every 1.5 s and a contact sheet.
6. `node render/capture.mjs OUT.mp4 MIX.wav` — headless Chromium seeks the paused GSAP timeline frame by
   frame at 60 fps (3 parallel workers, lossless RGB intermediates), then one H.264 + AAC encode.
7. `node render/posters.mjs ../posters` — the three poster frames.

To edit: `index.html` + `film.css` + `film.js` are the film (one page, one paused GSAP timeline; open
`index.html` through any local web server and call `__seek(seconds)` in the console). The narration
text and its beats are in `narration/script.json`.

**Narration with ElevenLabs instead.** `audio/voice_elevenlabs.py VOICE_ID` writes the same files
(eleven_v3, word timings from the character alignment), then run `./render.sh`. It was not run for
v2 (see below), so treat it as untested.

## Voice: why Kokoro and not ElevenLabs

The brief asked for ElevenLabs eleven_v3. The cloud machine that made this film could not reach
`api.elevenlabs.io` (blocked by the environment's network policy), so, as agreed, the voice was
generated locally with **Kokoro-82M** (voice `af_heart`, American English, warm and calm), an open
model under Apache-2.0 that allows commercial use. Its phoneme durations give exact word timings.
No line needed speeding up; nothing was cut.

## Licences and sources

| Asset | Source | Licence / terms |
|-------|--------|-----------------|
| TourCode UI, logo, demo code and tours | `assets/` in this repository | Yours |
| Manrope (the film's text, wordmark) | `@fontsource/manrope` 5 (Mikhail Sharanda) | SIL Open Font License 1.1 |
| Commit Mono (the `/tour` command, call to action) | `@fontsource/commit-mono` 5 (Eigil Nikolajsen) | SIL Open Font License 1.1 |
| Inter (editor window chrome) | `@fontsource/inter` 5 (Rasmus Andersson) | SIL Open Font License 1.1 |
| JetBrains Mono (code in the editor) | `@fontsource/jetbrains-mono` 5 (JetBrains) | SIL Open Font License 1.1 |
| GSAP 3.13.0 | npm `gsap` | GSAP Standard "no charge" license — free, including commercial use |
| Playwright, Chromium | npm `playwright` | Apache-2.0 (render tool, not in the film) |
| Voice model Kokoro-82M, voice `af_heart` | hexgrad/Kokoro-82M via `kokoro-onnx` (thewh1teagle, model files from its GitHub release) | Apache-2.0 (model), MIT (`kokoro-onnx`); espeak-ng phonemizer (GPL-3.0) used as a build tool |
| Music and sound effects | Synthesized in `source/audio` for this film | Original, no third-party samples |
| Cursor, Windsurf, Claude, Jupyter, Confluence, Notion marks | `simple-icons` 15 (npm) | Icon data CC0-1.0; the marks are trademarks of Anysphere, Cognition (Windsurf), Anthropic, Project Jupyter, Atlassian and Notion Labs |
| Visual Studio Code logo | Microsoft's official logo (code.visualstudio.com/brand) via `glincker/thesvg@e5957fa` `public/icons/visual-studio-code/default.svg` | Listed MIT by thesvg; trademark of Microsoft — use per the VS Code brand guidelines |
| Kiro icon | `github.com/kirodotdev/Kiro`, `assets/kiro-icon.png` (official repository) | No licence file; trademark of Amazon Web Services |

The editor and agent marks are shown in one tone, only to say that TourCode works with those
products (nominative use). Check each brand's guidelines before paid promotion.

## Commercial use

- **ElevenLabs:** not used in this version. If you switch to it, the free plan does not allow
  commercial use and requires attribution; a paid plan (Starter or higher) includes a commercial licence.
- **Kokoro (the voice used), GSAP, the fonts (all SIL OFL) and the synthesized audio:** commercial use allowed.
- **Logos:** trademarks of their owners (see above).
