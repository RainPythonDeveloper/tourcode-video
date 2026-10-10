---
version: alpha
name: TourCode — Frame (video / frame layer)
description: >
  Dark-editor launch film for TourCode. Base preset code-editorial (developer-facing,
  JetBrains Mono code voice) remapped by hand onto the TourCode identity from the brief:
  VS Code Dark Modern grounds, one green accent (#3FB950) that marks only what matters,
  Inter semibold headlines with tight tracking, JetBrains Mono for code and /tour.
  The real product UI (webview.css) is embedded as-is; this spec styles everything around it.
unit: the frame — 1920×1080 primary; 1080×1920 and 1080×1080 cut-downs
principle: the product is the hero · green means "this matters" · every line of code stays readable

colors:
  canvas: "#0D1117"        # deepest ground (space the editor floats in)
  ground: "#181818"        # sidebar / editor chrome
  editor: "#1F1F1F"        # editor + panel surface, cards
  border: "#313131"        # hairlines, card borders
  ink: "#E6E6E6"           # primary text
  muted: "#9D9D9D"         # secondary text, line numbers
  accent: "#3FB950"        # brand green — highlighted lines, route line, eyebrow dot, active state
  accent-deep: "#2DA44E"   # logo disc
  accent-soft: "rgba(63,185,80,0.14)"  # step line highlight background
  link: "#4DAAFC"          # sparingly: links, the Next button family
  warn: "#CCA700"          # sparingly: medium risk
  risk: "#F85149"          # sparingly: high risk marker

borders: { hairline: "1px solid #313131", step: "2px solid #3FB950 (left edge of highlighted lines)" }
shadows:
  float: "0 40px 120px rgba(0,0,0,0.55), 0 12px 32px rgba(0,0,0,0.45)"
  glow: "0 0 24px rgba(63,185,80,0.35)"

typography:
  headline:   { fontFamily: "Inter", px: 72, weight: 600, lineHeight: 1.05, tracking: "-0.03em" }
  subhead:    { fontFamily: "Inter", px: 44, weight: 600, lineHeight: 1.1, tracking: "-0.02em" }
  tagline:    { fontFamily: "Inter", px: 34, weight: 500, lineHeight: 1.3, tracking: "-0.01em" }
  eyebrow:    { fontFamily: "Inter", px: 18, weight: 600, tracking: "0.12em", upper: true, mark: "● glowing green dot" }
  code:       { fontFamily: "JetBrains Mono", px: 22, weight: 400, lineHeight: 1.6 }
  command:    { fontFamily: "JetBrains Mono", px: 40, weight: 500 }
  ui:         { note: "Embedded product UI keeps its own webview.css sizes (13 px base) and is scaled as a whole by the camera; never restyle it." }

spacing:
  safe: "96px"         # 16:9 title-safe inset
  radius: "8px"
  radius-window: "12px"
  gap: "24px"

components:
  editor-window:
    description: "VS Code Dark Modern window built in HTML: title bar (#181818) with three muted dots, activity bar (48 px, #181818) with the TourCode route icon active (green), sidebar 360 px (real sidebar states), editor tab strip + tab, gutter line numbers (#6E7681 → muted), code in JetBrains Mono, explanation panel under the code (real step states). Radius 12 px, hairline border, float shadow."
  step-highlight:
    description: "Lines of the current step: background accent-soft (#3FB950 @14%), 2 px #3FB950 left border, exact line range from the tour JSON."
  eyebrow:
    description: "Small uppercase label with a glowing green dot, as in the UI: ● TOUR · 4 STEPS."
  route-line:
    description: "The logo's route — start dot, S-curve, arrow — as a 3–4 px green stroke with a soft glow. Draws itself (stroke-dashoffset) and carries the camera between scenes."
  headline-card:
    description: "On-screen message: Inter 600, sentence case, ≤7 words per line, one message at a time, ink on canvas; never over code that must be read."
  caption-band:
    description: "Burned-in caption sits in the lower band (y 900–1000 at 1080p) on a #0D1117 @80% pill with hairline border; never covers highlighted code."
---

# TourCode — Frame (video / frame layer)

## Brand adaptation (READ FIRST — the frontmatter is the source of truth)

Started from the **code-editorial** preset (developer-facing, mono code voice) and rewritten by hand:
the automatic remix mapped the accent to amber and the ground to light, which contradicts the brief.
The frontmatter above is normative. Colors, fonts and the embedded UI come from the user's brief and
the real TourCode files in `../../assets`.

## Overview

A calm, precise, slightly magical film about a developer tool. The frame is a dark space
(#0D1117) in which a VS Code Dark Modern window floats in 2.5D, lit softly, with light grain and
a gentle vignette. The product UI is the hero and is never invented: sidebar, tour map and the
explanation panel are the real webview DOM. Green #3FB950 is the only voltage — it marks the lines
the tour explains, the route line, the active step, the eyebrow dot. Blue, amber and red appear only
where the real UI uses them (Next button, medium / high risk), never as decoration.

## The Frame

- 16:9 master at 1920×1080. Keep headlines inside a 96 px safe inset.
- The editor window fills 80–90% of the width at rest; the camera pushes in to 1.6–2.4× on code lines
  so that code renders at ≥ 22 px effective size.
- One message on screen at a time. Text never sits on top of code that is being read.

## Colors

Canvas #0D1117 → chrome #181818 → surfaces #1F1F1F → hairlines #313131. Ink #E6E6E6, muted #9D9D9D.
At most two accent colors per frame (green + one of blue / amber / red when the real UI shows it).

## Typography

Inter 600 for headlines (tight −0.03em), Inter 500 for taglines, JetBrains Mono for code and the
`/tour` command. Eyebrows: Inter 600 uppercase 0.12em with a glowing green dot.

## Depth & Surface

2.5D: perspective 1800–2400 px on a stage; the window tilts at most 8–12° on rotateY / rotateX and
returns to flat when code must be read. Layers (sidebar, editor, panel) can separate by 20–60 px in Z
for parallax. Soft float shadow; a subtle green glow (shadow glow) only on the active element.

## Shapes

8 px radius on cards (the UI's own --radius), 12 px on the window, 999 px pills only where the UI has them.

## Components

See frontmatter. The embedded UI keeps webview.css exactly; transitions inside it are disabled
(`--motion: 0ms`) so the timeline owns all motion.

## Frame Treatments

- Grain: 3–4% monochrome noise overlay, static per frame.
- Vignette: radial darkening to ~35% at the corners.
- Glow: green bloom only around the route line and the active highlight.

## Composition Rules

- The product is centered or slightly right of center; headlines sit left-top or bottom-center.
- Captions/headlines and code never overlap.
- Motion: expo/cubic easing, transitions 0.4–0.6 s, readable holds 1.5–2 s. No shake, glitch, flash.

## Aspect-Ratio Behavior

- 9:16 (1080×1920): UI centered and zoomed — crop to the editor column, sidebar hidden or stacked;
  headline in the top third.
- 1:1 (1080×1080): editor area only, panel below; headline top.

## Approved Real Entities

TourCode; VS Code, Cursor, Kiro, Windsurf (editors); Claude Code, Cursor, Kiro (agents); Jupyter.
Demo project "acme-shop" and its files auth.ts, password.ts, session.ts.

## Numerals & Claims (hard rule)

Only claims from the brief: "50,000 lines" (hook framing), "minutes, not days". No invented stats.

## Pre-Render Self-Audit

UI matches assets/ui · every line of code readable · each text ≥ 1.5 s on screen · green only on
what matters · ≤ 2 accent colors per frame · sound hits on visual events.

## Known Gaps

The editor chrome around the panels is built in HTML (it does not exist as a file in assets).
