You're a world-class motion designer and this is your resume video. Make a 60-second product launch teaser about TourCode: a developer types /tour and a question to their AI coding agent, and TourCode turns the codebase into a guided, step-by-step tour right inside the code editor — first a map of the answer, then the exact lines highlighted and explained, one step at a time. It is for software developers worldwide: engineers joining an unfamiliar codebase, tech leads onboarding a team, data scientists reading someone else's notebooks. It will be posted on X, LinkedIn, YouTube and Product Hunt.

Make it dynamic and confident. Open with a striking hook, build through a sequence of distinct techniques (kinetic typography, shape play, camera moves, colour shifts, match cuts), cut everything to the music, and land on a clean, memorable final frame.

Brief

- Goal: a developer watching thinks "next time I open a repo I don't know, I want this" and goes to try TourCode.
- Key message: Understand any codebase, one step at a time.
- Tone: calm and premium, confident, a little magical. Precise like a good engineer; no hype words.
- References:
  - ./assets/ui/*.html — the real TourCode interface (open each page in a browser: it draws a real state of the product with the extension's own CSS and JS). Take the look of the product from them: the green-highlighted code lines with a green left border, the explanation panel under the code, the tour map diagram, the eyebrow labels with a glowing green dot, the sidebar with steps and the Path. Restyle and animate them freely, but keep them recognizable.
  - ./assets/tours/how-login-works.json and ./assets/code/src/*.ts — the demo tour and its code (a small login flow: handleLogin → findUser → verifyPassword → startSession). Use these for any code, step titles and diagram labels on screen.
  - The launch films of Linear, Raycast and Vercel — take their restraint: dark, precise, generous negative space, one idea per moment.
- Facts (put no other claims on screen):
  - The command is /tour followed by a question, typed to the AI coding agent.
  - A tour opens with a tour map: a diagram of the whole answer, each box leading to its step.
  - Each step opens the right file, highlights the exact lines and explains them under the code; "More" opens the full explanation; steps have their own diagrams.
  - Risks: a layer that marks the lines where something can break.
  - Glossary: the project's terms are underlined and explained on hover.
  - Ask about any step; suggested questions are one click away.
  - "Explain deeper" and "What breaks" build a sub-tour from the current step; the Path shows where you are.
  - Teams pin tours to "Start here" for newcomers and sort tours into groups; tours whose code changed are flagged and rebuilt with one click.
  - Works in VS Code, Cursor, Kiro and Windsurf, with Claude Code, Cursor or Kiro as the agent. Understands Jupyter notebooks.

Story
Write the storyboard before you build anything: 8 scenes, each with one idea, one visual technique and one narration line. Follow this order, then show me the storyboard and wait for my OK:
1. Hook: an unfamiliar codebase is overwhelming — where do you even start?
2. The command: /tour how does login work.
3. The agent studies the code: files light up and connect into a route.
4. The reveal: the tour map assembles (the big moment).
5. Step by step: the right lines light up green and get explained.
6. Go deeper: ask about a step, see the risks, dive into a sub-tour, the Path shows where you are.
7. For teams: "Start here" for newcomers; works in your editor with your agent.
8. Final frame.
Final frame: the TourCode logo (./assets/brand/tourcode-logo.svg — its route line is the brand motif, let it draw itself), the line "Understand any codebase, one step at a time." and the call to action "Try it: github.com/RainPythonDeveloper/tourcode".

Narration
ElevenLabs eleven_v3, voice: a warm, calm, confident narrator, neutral American English, unhurried. The API key is in ~/.config/elevenlabs/api_key; never print it. Use the character timestamps so each on-screen word appears as it is spoken. If the voice runs long, speed it up by at most 8%, then cut words, not scenes.

Music and sound
Synthesize the music and effects in code, at 110-118 BPM: minimal modern electronic, warm synths, a soft pulse that builds to the tour map reveal. Every cut lands on a beat, and the tour map reveal hits on the drop. Add sound effects on cuts, reveals and the final frame; give the green line highlight its own short, warm chime and use it every time. Duck the music under the voice and master to -14 LUFS.

Look

- Format: 1920x1080 at 60 fps.
- Colours: background #0D1117 and #181818; surfaces #1F1F1F with #313131 borders and 8 px corners; text #E6E6E6, secondary #9D9D9D; brand green #3FB950 (highlighted code lines: #3FB950 at 14% opacity with a 2 px solid #3FB950 left border); logo circle #2DA44E. Use only sparingly: blue #4DAAFC, amber #CCA700, red #F85149.
- Fonts: Inter for headlines and narration words, JetBrains Mono for code and the /tour command (both under the SIL Open Font License).
- Logo and brand assets: ./assets/brand/tourcode-logo.svg (white route on a green circle) and ./assets/brand/tourcode-mark.svg (the route outline).
- Screens or footage to show: none recorded; rebuild the product's screens from ./assets/ui/*.html.
- Other images and icons: find real assets online whose licence allows this use (for the editor and agent logos: VS Code, Cursor, Kiro, Windsurf, Claude Code), and list each source and licence in the README.
- Keep the frame clean: no HUD or decorative overlays like corner brackets, title labels, counters or timecodes.
- It must work muted: key words appear on screen in sync with the voice.

Build and deliver
Build it as one HTML page with a paused GSAP timeline, capture the frames with Playwright and encode with ffmpeg (H.264 and AAC). Check contact sheets of stills before the full render, and of the encoded MP4 after it, and measure the loudness of the mix. Put the MP4, three poster frames, the re-renderable source and a README with the story, re-render steps and licences in ~/HardWork/tourcode-video/v2, without overwriting anything already there. Tell me if any service's plan limits commercial use, like the free ElevenLabs plan.

Before you start, ask me about any [ ] still left blank.
