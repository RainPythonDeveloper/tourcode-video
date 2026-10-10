#!/usr/bin/env python3
"""Build every sound of the film into assets/sfx/*.wav (48 kHz stereo, peak-normalised).

Sources: HeyGen sound-effects catalog files (downloaded to .media/sfx-src/<id>.mp3 via
`heygen audio sounds list`), processed here (trim, fades, pitch, tape-stop, reverse reverb),
plus three sounds the catalog did not have, synthesised in the key of the music (B major):
the brand chime, the risk tone and the rebuild swirl.

usage: make_sfx.py SRC_DIR
"""
import json, os, subprocess, sys
import numpy as np

SR = 48000
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "sfx")
SRC = sys.argv[1]
rng = np.random.default_rng(1010)


def load(cid):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SRC, cid + ".mp3"), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def save(name, x, peak_db=-3.0):
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    p = np.max(np.abs(x)) or 1.0
    x = x * (10 ** (peak_db / 20) / p)
    path = os.path.join(OUT, name + ".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", path],
                   input=x.tobytes(), check=True)
    return name, len(x) / SR


def seg(x, a, b=None):
    return x[int(a * SR): (int(b * SR) if b is not None else None)].copy()


def fade(x, fin=0.005, fout=0.05):
    x = x.copy(); n = len(x)
    i = min(int(fin * SR), n); o = min(int(fout * SR), n)
    if i: x[:i] *= np.linspace(0, 1, i)[:, None]
    if o: x[-o:] *= np.linspace(1, 0, o)[:, None] ** 2
    return x


def pitch(x, semis):
    """resample-style pitch shift (duration scales by 2^(-semis/12)), like a varispeed tape"""
    r = 2 ** (semis / 12)
    n = int(len(x) / r)
    t = np.arange(n) * r
    return np.stack([np.interp(t, np.arange(len(x)), x[:, c]) for c in range(2)], 1)


def tape_stop(x, dur):
    """play x with a rate falling 1 → 0 over `dur` seconds (consumes dur/2 s of source)"""
    n = int(dur * SR)
    rate = np.linspace(1, 0, n) ** 1.2
    pos = np.cumsum(rate)
    pos = np.clip(pos, 0, len(x) - 1)
    y = np.stack([np.interp(pos, np.arange(len(x)), x[:, c]) for c in range(2)], 1)
    return y * np.linspace(1, 0.15, n)[:, None]


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); acc = np.zeros(x.shape[1])
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y


def reverb(x, secs=1.6, decay=3.2, wet=0.35):
    x = fade(x, 0.0, 0.25)            # no step where the dry signal ends
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-decay * t)[:, None]
    ir[:, 1] = np.roll(ir[:, 1], 331)
    ir /= np.sqrt((ir ** 2).sum(0))
    y = np.stack([np.convolve(x[:, c], ir[:, c]) for c in range(2)], 1)
    out = np.zeros_like(y); out[: len(x)] += x * (1 - wet); out += y * wet
    return out


def hp(x, fc):
    return x - onepole_lp(x, fc)


# --------------------------------------------------------------- synthesised (catalog misses)

def bell(freq, dur=1.6, decay=2.6, bright=1.0):
    t = np.arange(int(dur * SR)) / SR
    parts = [(1.0, 1.0, 1.0), (2.0, 0.32 * bright, 1.6), (3.01, 0.10 * bright, 2.3), (4.2, 0.04 * bright, 3.0)]
    s = sum(a * np.sin(2 * np.pi * freq * m * t + 0.3 * m) * np.exp(-decay * k * t) for m, a, k in parts)
    atk = np.minimum(1, t / 0.004)
    rel = np.minimum(1, (dur - t) / 0.3)          # each note ends at zero
    return s * atk * rel


def brand_chime():
    # warm two-note mallet: F#4 → B4 (dominant → tonic of the music's B major), 110 ms apart
    a = bell(369.99, 1.7, 2.4, 0.8)
    b = bell(493.88, 1.6, 2.1, 0.8)
    n = len(a) + int(0.11 * SR)
    y = np.zeros((n, 2))
    y[: len(a), 0] += a * 0.85; y[: len(a), 1] += a * 0.75
    o = int(0.11 * SR)
    y[o: o + len(b), 0] += b * 0.8; y[o: o + len(b), 1] += b * 0.95
    y = onepole_lp(y, 5200)
    return reverb(y, 1.4, 3.6, 0.22)


def risk_tone():
    # low, soft, non-alarming: a rounded F#3 with a slow attack and a gentle fall-off
    t = np.arange(int(0.9 * SR)) / SR
    s = np.sin(2 * np.pi * 185.0 * t) + 0.18 * np.sin(2 * np.pi * 370.0 * t) + 0.05 * np.sin(2 * np.pi * 555 * t)
    env = np.minimum(1, t / 0.035) * np.exp(-3.4 * t)
    y = np.stack([s * env, s * env], 1)
    return reverb(onepole_lp(y, 1800), 1.0, 4.5, 0.18)


def swirl():
    # rebuild swirl: band-passed noise sweeping up then down, panned in a small circle
    d = 0.62; n = int(d * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    fc = 500 + 2600 * np.sin(np.pi * t / d) ** 1.5
    y = np.zeros(n); lp1 = 0.0; lp2 = 0.0
    for i in range(n):  # state-variable-ish two-pole band-pass following fc
        f = 2 * np.sin(np.pi * fc[i] / SR); q = 0.35
        hp_ = noise[i] - lp2 - q * lp1; lp1 += f * hp_; lp2 += f * lp1; y[i] = lp1
    env = np.sin(np.pi * t / d) ** 1.6
    pan = 0.5 + 0.4 * np.sin(2 * np.pi * 3.2 * t)
    y = y * env
    return np.stack([y * (1 - pan), y * pan], 1)


# --------------------------------------------------------------- keystrokes from a real keyboard recording

def keystrokes(x, count=6):
    m = x.mean(1)
    hop = 128
    e = np.array([np.sum(m[i:i + hop] ** 2) for i in range(0, len(m) - hop, hop)])
    on = [i for i in range(4, len(e) - 40) if e[i] > 6 * e[i - 4: i].mean() + 1e-9 and e[i] == e[i - 2: i + 3].max()]
    picks, last = [], -10 ** 9
    for i in on:
        if i - last > 40:
            picks.append(i); last = i
    picks = sorted(picks, key=lambda i: -e[i])[: count * 3]
    picks = sorted(picks)[::3][:count]
    out = []
    for i in picks:
        s = i * hop - int(0.004 * SR)
        k = x[s: s + int(0.11 * SR)]
        out.append(fade(hp(k, 180), 0.002, 0.04))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    made = {}
    def put(name, x, peak=-3.0):
        n, d = save(name, x, peak); made[n] = round(d, 3)

    # hook: low riser (0–4.6) → tape stop (4.6–5.0), data-rush whooshes, soft thud
    r = load("ce04abf6")
    body = seg(r, 0.4, 5.0)
    put("riser_tape_stop", fade(np.concatenate([fade(body, 0.4, 0.0), tape_stop(seg(r, 5.0), 0.4)]), 0.3, 0.02))
    w1, w2 = load("a4855a82"), load("97f631e2")
    put("rush_whoosh_a", fade(w1, 0.003, 0.15))
    put("rush_whoosh_b", fade(pitch(w2, -2), 0.003, 0.12))
    put("tape_thud", fade(onepole_lp(load("8b1ac2f2"), 900), 0.002, 0.3))
    # command: keystrokes (real keyboard), confirm pop + shimmer (+4 st → B, C#, D#)
    for i, k in enumerate(keystrokes(load("0c447abf"))):
        put(f"key_{i + 1}", k, -6.0)
    put("confirm_pop", fade(load("4558aa13"), 0.002, 0.1))
    put("shimmer", fade(pitch(seg(load("7a885578"), 0.0, 2.6), 4), 0.01, 0.5))
    # agent explores: ticks rising +0/+3/+7, route-line swish
    tick = fade(load("cf8c57bb"), 0.001, 0.05)
    for i, st in enumerate([0, 3, 7]):
        put(f"file_tick_{i + 1}", pitch(tick, st))
    put("line_swish", fade(load("00caa739"), 0.003, 0.2))
    # tour map: soft impact, airy pull-back whoosh, deeper dive swoosh
    put("map_impact", fade(onepole_lp(load("050666a0"), 1400), 0.002, 0.4))
    put("airy_whoosh", fade(seg(load("f6995a68"), 1.2), 0.15, 0.25))
    put("dive_swoosh", fade(load("9e6eacef"), 0.01, 0.25))
    # walk-through: the brand chime (identical every time), progress tick, glossary pop
    put("brand_chime", brand_chime())
    put("progress_tick", fade(load("19bd1766"), 0.001, 0.05))
    put("glossary_pop", fade(load("13175e25"), 0.001, 0.05))
    # risks: toggle click, soft risk tone
    put("toggle_click", fade(load("09a80f87"), 0.001, 0.04))
    put("risk_tone", risk_tone())
    # ask and go deeper: click, streaming typing texture, deep whoosh with reverse reverb, path slide
    put("ui_click", fade(load("c47bc2fb"), 0.001, 0.04))
    put("typing_texture", fade(onepole_lp(hp(seg(load("0c447abf"), 12.0, 13.8), 300), 4200), 0.15, 0.3))
    deep = load("2e34dc51")
    swell = reverb(seg(deep, 0.25, 0.75), 1.2, 3.0, 0.7)[::-1][-int(0.75 * SR):]
    a, b = fade(swell, 0.2, 0.0), fade(seg(deep, 0.45), 0.0, 0.5)
    xf = int(0.08 * SR)                 # equal-power crossfade at the join
    w = np.sin(np.linspace(0, np.pi / 2, xf))[:, None]
    dive = np.concatenate([a[:-xf], a[-xf:] * w[::-1] + b[:xf] * w, b[xf:]])
    put("dive_reverse_whoosh", dive)
    put("path_slide", fade(load("72d0b143"), 0.002, 0.08))
    # teams: pin snap, group slides, swirl + success chime (E6, in key)
    put("pin_snap", fade(load("7e44f651"), 0.001, 0.05))
    put("group_slide", fade(pitch(load("72d0b143"), -3), 0.002, 0.08))
    put("rebuild_swirl", swirl())
    put("success_chime", fade(load("35aab3e8"), 0.002, 0.3))
    # works everywhere: one soft hit per logo, B-major pentatonic upward (source pop is E5)
    pop = fade(load("3f701632"), 0.001, 0.15)
    for i, st in enumerate([-5, -3, -1, 2, 4, 7, 9, 11]):
        put(f"logo_hit_{i + 1}", pitch(pop, st))
    # end card: riser following the line (the hook's drone, last 1.8 s), resolve hit (−4 st → D# + B)
    put("end_riser", fade(seg(r, 3.6, 5.4), 0.2, 0.01))
    put("resolve_hit", fade(seg(pitch(load("ca9b70d3"), -4), 0.4), 0.05, 0.8))
    json.dump(made, open(os.path.join(OUT, "_durations.json"), "w"), indent=1)
    for k, v in made.items():
        print(f"{k:22s} {v:6.3f}s")


if __name__ == "__main__":
    main()
