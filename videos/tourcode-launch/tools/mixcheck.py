#!/usr/bin/env python3
"""Offline reference mix of src/audio_cues.json (clip × volume × volume lane × group gain)
and its loudness: integrated LUFS, true peak, plus music-only and sfx-only stems.
usage: mixcheck.py [GROUP_GAIN] [--write out.wav]"""
import json, os, re, subprocess, sys
import numpy as np
SR = 48000
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
cues = json.load(open(os.path.join(ROOT, "src", "audio_cues.json")))
G = float(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else 1.0
cache = {}
def load(p):
    if p not in cache:
        cache[p] = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, p), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                                                capture_output=True, check=True).stdout, dtype=np.float32).reshape(-1, 2)
    return cache[p]
def lane(points, n):
    t = np.arange(n) / SR
    return np.interp(t, [p["t"] for p in points], [p["v"] for p in points])
L = int(60 * SR)
music = np.zeros((L, 2)); sfx = np.zeros((L, 2))
for c in cues:
    x = load(c["file"])[: int(c["duration"] * SR)] * c["volume"]
    if "automation" in c:
        for ln in c["automation"]["lanes"]:
            if ln["target"] == "volume":
                x = x * lane(ln["points"], len(x))[:, None]
    a = int(c["start"] * SR); b = min(L, a + len(x))
    (music if c["id"] == "music-bed" else sfx)[a:b] += x[: b - a]
mix = (music + sfx) * G
def meas(y, label):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       input=y.astype(np.float32).tobytes(), capture_output=True)
    s = r.stderr.decode()
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", s)[-1]; TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", s)[-1]
    M = [float(v) for v in re.findall(r"M:\s*(-?[\d.]+)", s)]
    print(f"{label:6s} integrated {I} LUFS   true peak {TP} dBTP   max momentary {max(M):.1f}")
meas(mix, "mix"); meas(music * G, "music"); meas(sfx * G, "sfx")
if "--write" in sys.argv:
    out = sys.argv[sys.argv.index("--write") + 1]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", out], input=mix.astype(np.float32).tobytes(), check=True)
