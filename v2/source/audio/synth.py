"""Small synthesis toolkit for the teaser's music and sound effects (numpy + scipy).

Everything is generated from code: no samples, no third-party sounds.
Signals are float32 mono arrays at SR unless a function says stereo (shape (n, 2)).
"""
import numpy as np
from scipy import signal

SR = 48000
_rng = np.random.default_rng(1)


def rng(seed):
    return np.random.default_rng(seed)


def t_axis(dur):
    return np.arange(int(round(dur * SR))) / SR


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def db(x):
    return 10 ** (x / 20)


# ---------- oscillators ----------
def sine(f, dur, phase=0.0):
    t = t_axis(dur)
    if np.ndim(f) == 0:
        return np.sin(2 * np.pi * f * t + phase)
    return np.sin(2 * np.pi * np.cumsum(f) / SR + phase)


def _polyblep(phase, dt):
    out = np.zeros_like(phase)
    m = phase < dt
    x = phase[m] / dt[m]
    out[m] = x + x - x * x - 1
    m2 = phase > 1 - dt
    x = (phase[m2] - 1) / dt[m2]
    out[m2] = x * x + x + x + 1
    return out


def saw(f, dur, phase0=0.0):
    n = int(round(dur * SR))
    f = np.full(n, f) if np.ndim(f) == 0 else f[:n]
    dt = f / SR
    phase = (phase0 + np.cumsum(dt)) % 1.0
    return (2 * phase - 1 - _polyblep(phase, dt)).astype(np.float32)


def supersaw(f, dur, voices=5, detune_cents=14, seed=0, stereo=True):
    r = rng(seed)
    offs = np.linspace(-detune_cents, detune_cents, voices)
    L = np.zeros(int(round(dur * SR)), np.float32)
    R = np.zeros_like(L)
    for i, c in enumerate(offs):
        v = saw(f * 2 ** (c / 1200), dur, r.random())
        pan = (i / (voices - 1)) if voices > 1 else 0.5
        L += v * np.cos(pan * np.pi / 2)
        R += v * np.sin(pan * np.pi / 2)
    out = np.stack([L, R], 1) / np.sqrt(voices)
    return out if stereo else out.mean(1)


def noise(dur, seed=0):
    return rng(seed).standard_normal(int(round(dur * SR))).astype(np.float32)


def additive(f, dur, partials, decays, amps=None, phase_seed=0):
    """Sum of sine partials (ratios to f), each with its own exponential decay time."""
    t = t_axis(dur)
    r = rng(phase_seed)
    out = np.zeros_like(t)
    amps = amps or [1.0] * len(partials)
    for p, d, a in zip(partials, decays, amps):
        if f * p >= SR / 2 - 200:
            continue
        out += a * np.sin(2 * np.pi * f * p * t + r.random() * 2 * np.pi) * np.exp(-t / d)
    return out.astype(np.float32)


def pluck(f, dur, bright=1.0, decay=0.9, seed=0):
    """Warm plucked string: harmonics 1/k, higher ones die faster."""
    ks = np.arange(1, 14)
    return additive(f, dur, ks, [decay / (1 + 0.55 * (k - 1) / bright) for k in ks],
                    [1 / k ** 1.15 for k in ks], seed) * attack(dur, 0.003)


def bell(f, dur, seed=0, warm=True):
    """Soft bell: mostly harmonic partials with a touch of inharmonic shimmer."""
    parts = [1, 2, 3, 4.2, 5.4] if warm else [1, 2.76, 5.4, 8.93]
    decs = [dur * 0.55, dur * 0.3, dur * 0.18, dur * 0.12, dur * 0.08]
    amps = [1, 0.35, 0.16, 0.1, 0.05]
    return additive(f, dur, parts, decs, amps, seed) * attack(dur, 0.004)


# ---------- envelopes ----------
def attack(dur, a):
    n = int(round(dur * SR))
    e = np.ones(n, np.float32)
    k = max(1, int(a * SR))
    e[:k] = np.linspace(0, 1, k) ** 1.5
    return e


def adsr(dur, a=0.01, d=0.1, s=0.7, r=0.2):
    n = int(round(dur * SR))
    e = np.full(n, s, np.float32)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na) if na else e[:na]
    e[na:na + nd] = np.linspace(1, s, len(e[na:na + nd]))
    if nr:
        e[-nr:] *= np.linspace(1, 0, min(nr, n)) ** 1.6
    return e


def expdec(dur, tau):
    return np.exp(-t_axis(dur) / tau).astype(np.float32)


def ramp(n, a, b, curve=1.0):
    x = np.linspace(0, 1, n) ** curve
    return (a + (b - a) * x).astype(np.float32)


# ---------- filters ----------
def _sos(kind, fc, order=2, q=None):
    nyq = SR / 2
    if kind == 'band':
        lo, hi = fc
        return signal.butter(order, [max(20, lo) / nyq, min(hi, nyq * 0.95) / nyq], 'bandpass', output='sos')
    return signal.butter(order, min(fc, nyq * 0.95) / nyq, kind, output='sos')


def lp(x, fc, order=2):
    return signal.sosfilt(_sos('low', fc, order), x, axis=0).astype(np.float32)


def hp(x, fc, order=2):
    return signal.sosfilt(_sos('high', fc, order), x, axis=0).astype(np.float32)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(_sos('band', (lo, hi), order), x, axis=0).astype(np.float32)


def sweep_filter(x, fc_curve, kind='low', block=256, q_bw=0.6):
    """Time-varying filter: a new biquad every block, with the state carried over."""
    n = len(x)
    out = np.zeros_like(x)
    zi = None
    for i in range(0, n, block):
        fc = float(fc_curve[min(i, len(fc_curve) - 1)])
        if kind == 'band':
            sos = _sos('band', (fc * (1 - q_bw / 2), fc * (1 + q_bw / 2)), 1)
        else:
            sos = _sos(kind, fc, 2)
        seg = x[i:i + block]
        if zi is None:
            zi = np.zeros((sos.shape[0], 2) + seg.shape[1:])
        y, zi = signal.sosfilt(sos, seg, axis=0, zi=zi)
        out[i:i + block] = y
    return out


# ---------- space ----------
_IR_CACHE = {}


def reverb_ir(seconds=2.6, damp=5500, seed=3, predelay=0.012):
    key = (seconds, damp, seed, predelay)
    if key in _IR_CACHE:
        return _IR_CACHE[key]
    n = int(seconds * SR)
    t = np.arange(n) / SR
    r = rng(seed)
    env = np.exp(-t * 6.9 / seconds)
    ir = np.stack([r.standard_normal(n) * env, r.standard_normal(n) * env], 1)
    # darker tail: low-pass that closes over time (crossfade bright → dark)
    dark = lp(ir, damp * 0.35)
    bright = lp(ir, damp)
    w = np.clip(t / seconds * 2.2, 0, 1)[:, None]
    ir = bright * (1 - w) + dark * w
    pd = int(predelay * SR)
    ir = np.concatenate([np.zeros((pd, 2)), ir])
    ir /= np.sqrt((ir ** 2).sum(0)).max()
    _IR_CACHE[key] = ir.astype(np.float32)
    return _IR_CACHE[key]


def reverb(x, mix=0.25, seconds=2.6, damp=5500, seed=3):
    st = to_stereo(x)
    ir = reverb_ir(seconds, damp, seed)
    wet = np.stack([signal.fftconvolve(st[:, c], ir[:, c])[:len(st)] for c in range(2)], 1)
    return (st * (1 - mix) + wet * mix).astype(np.float32), wet[: len(st)].astype(np.float32)


def delay(x, time, feedback=0.35, taps=5, pingpong=True, damp=4000):
    st = to_stereo(x)
    out = st.copy()
    d = int(time * SR)
    g = 1.0
    src = st
    for k in range(1, taps + 1):
        g *= feedback
        src = lp(src, damp)
        shifted = np.zeros_like(st)
        shifted[d * k:] = src[: len(st) - d * k]
        if pingpong:
            ch = k % 2
            shifted[:, 1 - ch] *= 0.25
        out += shifted * g
    return out


# ---------- utilities ----------
def to_stereo(x):
    return x if x.ndim == 2 else np.stack([x, x], 1)


def pan(x, p):
    """p in [-1, 1]."""
    a = (p + 1) * np.pi / 4
    m = x if x.ndim == 1 else x.mean(1)
    return np.stack([m * np.cos(a), m * np.sin(a)], 1).astype(np.float32)


def place(bus, x, t, gain=1.0):
    """Add x into bus starting at time t (seconds)."""
    x = to_stereo(x) * gain
    i = int(round(t * SR))
    if i >= len(bus):
        return
    if i < 0:
        x = x[-i:]
        i = 0
    n = min(len(x), len(bus) - i)
    bus[i:i + n] += x[:n]


def normalize(x, peak=0.9):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


def fade(x, fin=0.002, fout=0.02):
    x = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim == 2 else np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)[:, None] if x.ndim == 2 else np.linspace(1, 0, b)
    return x
