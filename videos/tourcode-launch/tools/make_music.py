#!/usr/bin/env python3
"""Edit the music bed (HeyGen catalog 9d06052d, 100 BPM, B major) to the film's beat grid.

Bars are 2.4 s. The beat enters on the track's downbeat 19.175 s, placed at film 5.6 s.
One bar is removed from each of the first two 8-bar phrases so that
  phrase B (hats in, track 38.375) lands on the dive into the tour map (film 22.4),
  phrase C (track 57.575) lands on the cut into "Ask and go deeper" (film 39.2),
  the final note (track 76.775) lands on the logo (film 58.4), then a 1.5 s fade to 60.0.
"""
import os, subprocess, numpy as np
SR = 48000
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, ".media", "audio", "bgm", "bgm_001.mp3")
OUT = os.path.join(ROOT, "assets", "audio", "music-bed.wav")
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True, check=True).stdout, dtype=np.float32).reshape(-1, 2)
D = 19.175
SEGS = [(D, D + 6 * 2.4), (D + 7 * 2.4, D + 14 * 2.4), (D + 15 * 2.4, D + 15 * 2.4 + 23.2)]   # → 5.6–20.0, 20.0–36.8, 36.8–60.0
PRE = 0.012      # cut just before each downbeat so the crossfade never smears the kick
XF = 0.024
parts = [x[int((a - PRE) * SR): int((b - PRE) * SR)].copy() for a, b in SEGS]
out = parts[0]
w = np.sin(np.linspace(0, np.pi / 2, int(XF * SR)))[:, None]
for p in parts[1:]:
    n = len(w)
    tail = np.concatenate([p[:0]])
    head_a = out[-n:] * w[::-1]
    # the new part starts XF earlier so its downbeat stays on the grid
    out = np.concatenate([out[:-n], head_a + p[:n] * w, p[n:]])
total = 60.0 - 5.6
out = out[: int(total * SR)]
if len(out) < int(total * SR):
    out = np.concatenate([out, np.zeros((int(total * SR) - len(out), 2), np.float32)])
fi = int(0.01 * SR); out[:fi] *= np.linspace(0, 1, fi)[:, None]
a = int((58.5 - 5.6) * SR); out[a:] *= (np.linspace(1, 0, len(out) - a) ** 2)[:, None]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", OUT],
               input=out.astype(np.float32).tobytes(), check=True)
print(f"wrote {OUT}  {len(out)/SR:.3f}s  (film 5.6–60.0)")
