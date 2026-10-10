"""Narration with Kokoro-82M (Apache-2.0) and word-level timings.

Reads narration/script.json, synthesizes every segment, places it on the beat grid
(bar/beat from the script, pushed later if the previous line is still speaking),
and writes narration/narration.wav plus narration/timeline.json with the absolute
start and end of every word. The composition and the mix both read timeline.json.

Usage: python voice_kokoro.py MODEL_TIMED.onnx VOICES.bin
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parent.parent
SR = 24000
MAX_SPEEDUP = 1.08
PUNCT = set(".,:;?!—…\"'“”")


def words_from_timings(text, timings, tokenizer):
    """Assign the spoken phoneme groups (split at spaces) to the words of the text.

    Connected speech does not always keep one group per word: espeak splits
    "TourCode" in two and joins "at a" into one. A small dynamic programme maps
    contiguous groups to words so the phoneme counts match best; a group shared
    by several words is split in time by their phoneme counts."""
    strip = "".join(PUNCT)
    groups, cur = [], []
    for t in timings:
        if t.phoneme == " ":
            if cur:
                groups.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        groups.append(cur)
    merged = []
    for g in groups:
        if merged and all(t.phoneme in PUNCT for t in g):
            merged[-1].extend(g)
        else:
            merged.append(g)
    groups = [[t for t in g if t.phoneme not in PUNCT] or g for g in merged]
    words = text.split()
    wlen = [max(1, len(tokenizer.phonemize(w.strip(strip) or w, "en-us").replace(" ", "").strip(strip))) for w in words]
    glen = [len(g) for g in groups]
    W, G = len(words), len(groups)
    INF = float("inf")
    cost = [[INF] * (G + 1) for _ in range(W + 1)]
    back = [[None] * (G + 1) for _ in range(W + 1)]
    cost[0][0] = 0
    for i in range(W + 1):
        for j in range(G + 1):
            if cost[i][j] == INF:
                continue
            for k in (1, 2, 3):  # one word spoken as k groups
                if i + 1 <= W and j + k <= G:
                    c = cost[i][j] + abs(wlen[i] - sum(glen[j:j + k])) + (k - 1) * 0.5
                    if c < cost[i + 1][j + k]:
                        cost[i + 1][j + k], back[i + 1][j + k] = c, (i, j)
            for m in (2, 3):  # m words run together into one group
                if i + m <= W and j + 1 <= G:
                    c = cost[i][j] + abs(sum(wlen[i:i + m]) - glen[j]) + (m - 1) * 0.5
                    if c < cost[i + m][j + 1]:
                        cost[i + m][j + 1], back[i + m][j + 1] = c, (i, j)
    if cost[W][G] == INF:
        raise SystemExit(f"cannot align {text!r}")
    spans, i, j = [], W, G
    while (i, j) != (0, 0):
        pi, pj = back[i][j]
        spans.append((pi, i, pj, j))
        i, j = pi, pj
    out = []
    for wi, wj, gi, gj in reversed(spans):
        ts = [t for g in groups[gi:gj] for t in g]
        t0, t1 = ts[0].start, ts[-1].end
        if wj - wi == 1:
            out.append({"word": words[wi], "start": t0, "end": t1})
        else:
            total = sum(wlen[wi:wj])
            acc = t0
            for w in range(wi, wj):
                d = (t1 - t0) * wlen[w] / total
                out.append({"word": words[w], "start": acc, "end": acc + d})
                acc += d
    return out


def place_segments(script, synth):
    """Synthesize every segment with synth(text, speed) -> (audio, sr, words) and place it on the beat grid.

    A segment starts on its bar/beat, or on the next 8th after the previous line plus a breath.
    If it would run past its scene, it is sped up by at most 8 % (MAX_SPEEDUP); if it still
    runs long, a warning says to cut words. Writes narration/narration.wav, narration/timeline.json
    and data/narration.js.
    """
    beat = 60.0 / script["bpm"]
    bar = 4 * beat
    timeline, clips = [], []
    prev_end = 0.0
    sr_out = None
    for seg in script["segments"]:
        b, bt = seg["at"]
        want = (b - 1) * bar + (bt - 1) * beat
        scene_end = (script["scenes"][str(seg["scene"])][1] - 1) * bar
        speed = seg.get("speed", script["speed"])
        while True:
            audio, sr, words = synth(seg["text"], speed)
            sr_out = sr
            start = want
            if start < prev_end + 0.25:
                eighth = beat / 2
                start = np.ceil((prev_end + 0.25) / eighth) * eighth
            dur = len(audio) / sr
            if start + dur <= scene_end - 0.15 or speed >= script["speed"] * MAX_SPEEDUP - 1e-6:
                break
            speed = min(script["speed"] * MAX_SPEEDUP, speed + 0.02)
        if start + dur > scene_end - 0.15:
            print(f"WARNING {seg['id']} runs past its scene by {start + dur - scene_end:.2f}s — cut words")
        clips.append((start, audio))
        prev_end = start + dur
        timeline.append({
            "id": seg["id"], "scene": seg["scene"], "text": seg["text"], "speed": round(speed, 3),
            "start": round(start, 4), "end": round(start + dur, 4),
            "words": [{"word": w["word"], "start": round(start + w["start"], 4), "end": round(start + w["end"], 4)}
                      for w in words],
        })
        print(f"{seg['id']:5} {start:6.2f}–{start + dur:6.2f}  x{speed:.2f}  {seg['text']}")
    total = max(s + len(a) / sr_out for s, a in clips) + 0.5
    mix = np.zeros(int(total * sr_out), dtype=np.float32)
    for s, a in clips:
        i = int(round(s * sr_out))
        mix[i:i + len(a)] += a
    sf.write(ROOT / "narration/narration.wav", mix, sr_out, subtype="PCM_24")
    data = {"bpm": script["bpm"], "segments": timeline}
    (ROOT / "narration/timeline.json").write_text(json.dumps(data, indent=1))
    (ROOT / "data/narration.js").write_text("window.NARRATION = " + json.dumps(data) + ";\n")


def main():
    model, voices = sys.argv[1], sys.argv[2]
    script = json.loads((ROOT / "narration/script.json").read_text())
    k = Kokoro(model, voices)

    def synth(text, speed):
        audio, sr, timings = k.create_timed(text, voice=script["voice"], speed=speed, lang="en-us")
        assert sr == SR
        return audio, sr, words_from_timings(text, timings, k.tokenizer)

    place_segments(script, synth)


if __name__ == "__main__":
    main()
