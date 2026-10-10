"""Sound effects, synthesized. One function per cue name the film registers (film.js → cue()).

Each returns a stereo float32 array. `make(cue)` builds the sound for one cue dict
({name, t, ...}); the same name always gives the same sound unless the cue carries an
index `i` (rising ticks, logo hits) — the brand chime is one fixed sound, used every time.
"""
import numpy as np

from synth import (SR, additive, attack, bell, bp, db, expdec, fade, hp, lp, midi, noise, pan, ramp,
                   reverb, sine, sweep_filter, t_axis, to_stereo)

D_PENTA = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83]  # D major pentatonic from D4


def _whoosh(dur, lo, peak, hi_end, seed=0, pan_from=-0.6, pan_to=0.6, peak_at=0.6, q=0.9):
    n = int(dur * SR)
    x = noise(dur, seed)
    u = np.linspace(0, 1, n)
    fc = np.where(u < peak_at, lo + (peak - lo) * (u / peak_at) ** 1.5,
                  peak + (hi_end - peak) * ((u - peak_at) / (1 - peak_at)))
    y = sweep_filter(x, fc, 'band', 128, q)
    env = np.where(u < peak_at, (u / peak_at) ** 2.2, (1 - (u - peak_at) / (1 - peak_at)) ** 1.6)
    y = y * env
    p = pan_from + (pan_to - pan_from) * u
    a = (p + 1) * np.pi / 4
    st = np.stack([y * np.cos(a), y * np.sin(a)], 1)
    return st / (np.abs(st).max() + 1e-9)


def _blip(f0, f1, dur, tau, harm=0.2):
    t = t_axis(dur)
    f = f1 + (f0 - f1) * np.exp(-t / (dur / 3))
    x = sine(f, dur) + harm * sine(2 * f, dur)
    return x * np.exp(-t / tau) * attack(dur, 0.002)


def _click(seed=0, bright=1.0):
    dur = 0.03
    t = t_axis(dur)
    n = hp(noise(dur, seed), 2500) * np.exp(-t / 0.0015)
    tick = sine(3200 * bright, dur) * np.exp(-t / 0.004) * 0.35
    thock = sine(190, dur) * np.exp(-t / 0.008) * 0.4
    return n * 0.5 + tick + thock


def _add(*xs):
    """Sum signals of different lengths."""
    n = max(len(x) for x in xs)
    out = np.zeros((n,) + xs[0].shape[1:], np.float32)
    for x in xs:
        out[: len(x)] += x
    return out


def _rev(x, mix=0.3, sec=1.8, damp=6000, seed=21):
    y, _ = reverb(x, mix, sec, damp, seed)
    return y


# ---------- the cues ----------
def hook_riser(c):
    dur = c.get('dur', 4.95)
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    x = sweep_filter(np.stack([noise(dur, 1), noise(dur, 2)], 1), 250 + 5500 * u ** 2.2, 'band', 128, 1.1)
    tone = sine(110 * 2 ** (2 * u ** 1.6), dur) * 0.15
    y = (x + tone[:, None]) * (u ** 2.4)[:, None]
    return fade(y / np.abs(y).max(), 0.01, 0.03)


def rush(c):
    i = c.get('i', 0)
    s = _whoosh(0.85, 300, 2600, 700, seed=10 + i, pan_from=-0.8 if i % 2 else 0.8, pan_to=0.8 if i % 2 else -0.8, peak_at=0.55)
    return s


def tape_stop(c):
    dur = 0.75
    t = t_axis(dur)
    f = 30 + 200 * (1 - t / dur) ** 2
    x = lp(sine(f, dur) + 0.4 * sine(2 * f, dur), 900) * (1 - t / dur) ** 1.5
    return to_stereo(x * 0.6)


def thud(c):
    dur = 0.6
    t = t_axis(dur)
    x = sine(38 + 34 * np.exp(-t / 0.05), dur) * np.exp(-t / 0.22)
    x += lp(noise(dur, 3), 300) * np.exp(-t / 0.03) * 0.3
    return to_stereo(np.tanh(x * 1.2))


def cut_soft(c):
    return _whoosh(0.45, 900, 3500, 1500, seed=int(c['t'] * 10), pan_from=-0.3, pan_to=0.3, peak_at=0.35) * 0.6


def key(c):
    seed = int(c['t'] * 1000)
    r = np.random.default_rng(seed)
    return pan(_click(seed, 0.85 + 0.3 * r.random()) * (0.8 + 0.4 * r.random()), r.uniform(-0.2, 0.2))


def enter_pop(c):
    x = _add(_blip(620, 280, 0.25, 0.06, 0.3), _click(7) * 0.6)
    return to_stereo(x)


def shimmer(c):
    out = np.zeros((int(1.4 * SR), 2), np.float32)
    for k, n in enumerate([86, 90, 93, 98]):
        b = bell(midi(n), 1.2, seed=k)
        i = int(k * 0.035 * SR)
        out[i:i + len(b)] += pan(b, -0.5 + k * 0.33)[: len(out) - i]
    return _rev(out, 0.4, 2.0, 9000)


def line_swish(c):
    return _whoosh(0.5, 1500, 6500, 4000, seed=int(c['t'] * 7), pan_from=-0.7, pan_to=0.7, peak_at=0.45, q=1.2) * 0.8


def tick(c):
    i = c.get('i', 0)
    f = midi(86 + [0, 4, 7, 12][i % 4])
    return to_stereo(_blip(f, f, 0.12, 0.035, 0.15))


def swish(c):
    i = c.get('i', 0)
    return _whoosh(0.32, 1800, 5500, 3000, seed=40 + i, pan_from=-0.4, pan_to=0.5, peak_at=0.5, q=1.2) * 0.7


def pop_soft(c):
    i = c.get('i', 0)
    f = midi(D_PENTA[2 + i])
    x = _blip(f * 1.5, f, 0.18, 0.05, 0.25)
    return pan(x, -0.3 + 0.2 * i)


def select(c):
    return to_stereo(_blip(midi(81), midi(81), 0.2, 0.06) * 0.8 + _blip(midi(86), midi(86), 0.2, 0.05) * 0.4)


def impact(c):
    dur = 3.0
    t = t_axis(dur)
    sub = sine(32 + 48 * np.exp(-t / 0.08), dur) * np.exp(-t / 0.7)
    body = lp(noise(dur, 9), 350) * np.exp(-t / 0.12) * 0.5
    air = hp(noise(dur, 10), 4500) * np.exp(-t / 0.5) * 0.12
    x = np.tanh((sub + body) * 1.3) + air
    return _rev(to_stereo(x), 0.35, 3.0, 5000)


def airy_whoosh(c):
    s = _whoosh(1.2, 700, 4200, 1200, seed=60 + int(c['t']), pan_from=0.5, pan_to=-0.5, peak_at=0.4)
    return s * (0.6 if c.get('soft') else 1.0)


def route_tick(c):
    i = c.get('i', 0)
    f = midi(D_PENTA[5 + i])
    return pan(_blip(f, f, 0.15, 0.03, 0.3), -0.45 + 0.3 * i)


def node_ping(c):
    i = c.get('i', 0)
    return pan(bell(midi(D_PENTA[5 + i] + 12), 0.5, seed=70 + i) * 0.8, -0.3 + 0.2 * i)


def click(c):
    return to_stereo(_click(int(c['t'] * 100), 1.1) * 0.9)


def deep_swoosh(c):
    dur = 1.0
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    x = sweep_filter(np.stack([noise(dur, 80), noise(dur, 81)], 1), 2400 * (1 - u) ** 1.5 + 160, 'low', 128)
    x *= (u ** 1.8 * (1 - u) ** 0.3)[:, None]
    tone = sine(320 * (1 - 0.7 * u), dur) * u ** 2 * 0.25
    return (x / np.abs(x).max() + tone[:, None]) * 0.9


_CHIME = None


def chime(c):
    """The brand sound: a short warm two-note chime (A5 → D6), identical every time."""
    global _CHIME
    if _CHIME is None:
        dur = 1.6
        out = np.zeros((int(dur * SR), 2), np.float32)
        for k, (n, g, p) in enumerate([(81, 0.8, -0.15), (86, 1.0, 0.15)]):
            f = midi(n)
            x = additive(f, 1.4, [1, 2, 3, 4.01], [0.9, 0.35, 0.18, 0.1], [1, 0.22, 0.08, 0.03], 200 + k)
            x = lp(x * attack(1.4, 0.006), 5000)
            i = int(k * 0.095 * SR)
            out[i:i + len(x)] += pan(x * g, p)
        _CHIME = _rev(out, 0.28, 1.8, 7000, 31)
    return _CHIME


def panel_rise(c):
    return _whoosh(0.45, 500, 2200, 1800, seed=90, pan_from=0, pan_to=0, peak_at=0.7, q=1.0) * 0.5


def prog_tick(c):
    return to_stereo(_blip(2500, 2500, 0.05, 0.008, 0.0) * 0.6)


def tooltip_pop(c):
    return to_stereo(_blip(1100, 980, 0.12, 0.03, 0.4))


def type_texture(c):
    dur = c.get('dur', 2.0)
    out = np.zeros((int((dur + 0.1) * SR), 2), np.float32)
    r = np.random.default_rng(5)
    t = 0.0
    while t < dur:
        k = _click(int(t * 1000) + 3, 0.9) * (0.35 + 0.25 * r.random())
        i = int(t * SR)
        out[i:i + len(k)] += pan(k, r.uniform(-0.3, 0.3))[: len(out) - i]
        t += 0.045 + 0.06 * r.random()
    return out


def toggle(c):
    a = _click(11, 0.9)
    b = _click(12, 1.2) * 0.7
    out = np.zeros(int(0.12 * SR), np.float32)
    out[: len(a)] += a
    i = int(0.045 * SR)
    out[i:i + len(b)] += b
    return to_stereo(out)


def warn_tone(c):
    """Low, soft, not alarming: a muted two-note figure (D4 → A3) with a slow tremolo."""
    out = np.zeros(int(1.0 * SR), np.float32)
    for k, n in enumerate([62, 57]):
        x = additive(midi(n), 0.8, [1, 2, 3], [0.45, 0.2, 0.1], [1, 0.25, 0.08], 300 + k)
        x = lp(x * attack(0.8, 0.012), 1800)
        i = int(k * 0.16 * SR)
        out[i:i + len(x)] += x * (0.9 if k == 0 else 0.75)
    trem = 1 - 0.18 * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t_axis(1.0)))
    return _rev(to_stereo(out * trem), 0.25, 1.5, 4000)


def dive_whoosh(c):
    """Reverse-reverb swell into a deep whoosh."""
    hit = np.zeros(int(0.05 * SR), np.float32)
    hit[:] = lp(noise(0.05, 13), 2500) * np.exp(-t_axis(0.05) / 0.01)
    _, wet = reverb(np.concatenate([hit, np.zeros(int(0.9 * SR), np.float32)]), 1.0, 0.9, 3500, 41)
    swell = wet[::-1] / (np.abs(wet).max() + 1e-9)
    down = deep_swoosh(c)
    out = np.zeros((len(swell) + len(down) // 2, 2), np.float32)
    out[: len(swell)] += swell * 0.8
    out[len(swell) - len(down) // 2: len(swell) - len(down) // 2 + len(down)] += down
    return out


def path_slide(c):
    s = _whoosh(0.4, 900, 3200, 3000, seed=95, pan_from=-0.5, pan_to=0.0, peak_at=0.6, q=1.0) * 0.6
    g = sine(np.linspace(midi(74), midi(81), len(s)), len(s) / SR) * np.linspace(0, 1, len(s)) ** 2 * 0.15
    return s + g[:, None]


def pin_snap(c):
    x = _add(_click(14, 1.3), lp(sine(130, 0.08) * np.exp(-t_axis(0.08) / 0.02), 600) * 0.6)
    ping = bell(2400, 0.25, seed=5, warm=False) * 0.25
    out = np.zeros(int(0.3 * SR), np.float32)
    out[: len(x)] += x
    out[: len(ping)] += ping
    return to_stereo(out)


def slide(c):
    return _whoosh(0.5, 600, 2600, 1500, seed=97, pan_from=0.2, pan_to=-0.2, peak_at=0.5) * 0.55


def swirl(c):
    dur = 0.6
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    fc = (500 + 2600 * u) * (1 + 0.35 * np.sin(2 * np.pi * 7 * u * dur))
    y = sweep_filter(noise(dur, 98), fc, 'band', 96, 0.8) * np.sin(np.pi * u) ** 1.2
    p = 0.6 * np.sin(2 * np.pi * 3 * u * dur)
    a = (p + 1) * np.pi / 4
    st = np.stack([y * np.cos(a), y * np.sin(a)], 1)
    return st / np.abs(st).max() * 0.7


def rebuild_chime(c):
    out = np.zeros(int(1.2 * SR), np.float32)
    for k, n in enumerate([86, 90, 93]):
        b = bell(midi(n), 0.9, seed=400 + k)
        i = int(k * 0.07 * SR)
        out[i:i + len(b)] += b[: len(out) - i] * 0.8
    return _rev(to_stereo(out), 0.3, 1.6, 8000)


def paper_swish(c):
    dur = 0.6
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    y = bp(noise(dur, 99), 1800, 7000)
    flutter = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 22 * u * dur + 3 * np.sin(2 * np.pi * 3 * u * dur)))
    y = y * flutter * np.sin(np.pi * u) ** 1.5
    return pan(y / np.abs(y).max(), -0.3) * 0.7


def land(c):
    i = c.get('i', 0)
    t = t_axis(0.2)
    x = sine(70 + 50 * np.exp(-t / 0.02), 0.2) * np.exp(-t / 0.05) * 0.8
    x += bp(noise(0.2, 120 + i), 900, 4000) * np.exp(-t / 0.012) * 0.4
    x += bell(midi(D_PENTA[4 + i] + 12), 0.2, seed=130 + i) * 0.25
    return pan(x, 0.3)


def logo_hit(c):
    i = c.get('i', 0)
    notes = [62, 66, 69, 74, 69, 74, 78, 81, 86, 86]
    f = midi(notes[min(i, len(notes) - 1)])
    x = additive(f, 0.7, [1, 4.0, 9.9], [0.32, 0.06, 0.02], [1, 0.25, 0.08], 500 + i)
    x = x * attack(0.7, 0.002) + bp(noise(0.7, 600 + i), 1500, 5000) * expdec(0.7, 0.006) * 0.3
    return _rev(pan(x, -0.5 + 0.14 * (i % 8)), 0.2, 1.2, 6000)


def final_riser(c):
    dur = c.get('dur', 2.14)
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    x = sweep_filter(np.stack([noise(dur, 140), noise(dur, 141)], 1), 400 + 7000 * u ** 2, 'band', 128, 1.0)
    tone = (sine(midi(57) * 2 ** (u * 1.0), dur) + 0.5 * sine(midi(62) * 2 ** (u * 1.0), dur)) * 0.12
    y = (x * 0.8 + tone[:, None]) * (u ** 2.6)[:, None]
    return fade(y / np.abs(y).max(), 0.01, 0.01)


def route_draw(c):
    dur = 1.1
    u = np.linspace(0, 1, int(dur * SR))
    f = midi(86) * 2 ** u
    x = sine(f, dur) * np.sin(np.pi * u) * 0.25 + hp(noise(dur, 150), 6000) * np.sin(np.pi * u) * 0.08
    return _rev(pan(x, -0.4), 0.4, 1.8, 9000) * 0.8


def resolve(c):
    dur = 4.0
    out = np.zeros(int(dur * SR), np.float32)
    for k, n in enumerate([62, 66, 69, 76, 81]):
        b = bell(midi(n), 3.5, seed=700 + k)
        i = int(k * 0.02 * SR)
        out[i:i + len(b)] += b[: len(out) - i] * (0.6 if k < 3 else 0.4)
    t = t_axis(dur)
    out += sine(midi(38), dur) * np.exp(-t / 0.9) * 0.5
    out += hp(noise(dur, 160), 5000) * np.exp(-t / 0.8) * 0.06
    return _rev(to_stereo(out), 0.4, 3.5, 7000)


def cta_tick(c):
    return to_stereo(_blip(midi(93), midi(93), 0.15, 0.03, 0.2) * 0.5)


def make(c):
    fn = globals().get(c['name'])
    if fn is None:
        raise KeyError(f"no sound for cue {c['name']!r}")
    y = fn(c).astype(np.float32)
    return y / (np.abs(y).max() + 1e-9)  # peak-normalized; the mix sets each level
