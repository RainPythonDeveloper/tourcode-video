"""The score: minimal warm electronic at 112 BPM, synthesized from code.

Arrangement (bars of 2.143 s, 35 bars = 75 s):
  1–3   hook: dark drone swell, then a tape stop into near-silence
  4–6   the command: soft pad and a muted pulse on 1 and 3, sparse plucks
  7–9   the agent studies: hats, bass pulse, plucks in 8ths, filter opens, a snare roll, a breath
  10    THE DROP on the tour map: four-on-the-floor, sub bass, open pad, 16th arp with delay
  10–29 groove under the narration (the mix ducks it under the voice)
  30–31 lighter, a riser into the end
  32–35 the final chord, ringing out to silence
Usage: python music.py OUT.wav
"""
import sys

import numpy as np

from synth import (SR, adsr, bell, bp, db, delay, expdec, fade, hp, lp, midi, noise, place, pluck, reverb,
                   sine, supersaw, sweep_filter, t_axis)

BPM = 112
BEAT = 60 / BPM
BAR = 4 * BEAT
TOTAL = 35 * BAR  # 75.0
N = int(TOTAL * SR) + SR


def T(b, beat=1.0):
    return (b - 1) * BAR + (beat - 1) * BEAT


# chord: (pad notes, bass root)
CH = {
    'Bm9': ([50, 54, 57, 61], 35),
    'Gmaj7': ([50, 54, 55, 59], 31),
    'Em9': ([50, 54, 55, 59], 28),
    'Asus': ([50, 52, 57, 59], 33),
    'A': ([49, 52, 57, 59], 33),
    'D': ([50, 54, 57, 64], 38),
    'A/C#': ([49, 52, 57, 59], 37),
    'Dmaj9': ([50, 54, 57, 61, 64], 38),
}
CYCLE = ['D', 'A/C#', 'Bm9', 'Gmaj7']
PROG = {4: 'Bm9', 5: 'Gmaj7', 6: 'Bm9', 7: 'Gmaj7', 8: 'Em9', 9: 'Asus'}
for b in range(10, 30):
    PROG[b] = CYCLE[(b - 10) % 4]
PROG[30] = 'Em9'
PROG[31] = 'Asus'


def bus():
    return np.zeros((N, 2), np.float32)


# ---------- drums ----------
def kick(gain=1.0, tau=0.3, f0=115, f1=44):
    dur = 0.6
    t = t_axis(dur)
    f = f1 + (f0 - f1) * np.exp(-t / 0.045)
    body = sine(f, dur) * np.exp(-t / tau)
    click = hp(noise(0.012, 5), 1800) * np.exp(-t_axis(0.012) / 0.003) * 0.25
    out = body.copy()
    out[:len(click)] += click
    return np.tanh(out * 1.4) * gain * 0.85


def clap(seed=0):
    dur = 0.45
    n = noise(dur, seed)
    env = np.zeros(int(dur * SR))
    for k, o in enumerate([0, 0.011, 0.022]):
        i = int(o * SR)
        env[i:] += np.exp(-np.arange(len(env) - i) / SR / (0.007 if k < 2 else 0.12))
    return bp(n * env, 900, 2600) * 0.9


def hat(open_=False, seed=0):
    dur = 0.35 if open_ else 0.06
    x = hp(noise(dur, seed), 7500, 2) * expdec(dur, 0.12 if open_ else 0.018)
    return x * (0.45 if open_ else 0.6)


def snare_roll(start, end, out):
    t = start
    k = 0
    while t < end:
        u = (t - start) / (end - start)
        step = BEAT / 4 if u < 0.5 else BEAT / 8
        hit = bp(noise(0.12, 100 + k), 300, 6000) * expdec(0.12, 0.035) * (0.08 + 0.5 * u ** 2)
        place(out, hit, t)
        t += step
        k += 1


def drums():
    b = bus()
    kicks = []
    # 4–6: muted pulse on 1 and 3
    for bb in (4, 5, 6):
        for beat in (1, 3):
            kicks.append((T(bb, beat), 0.5))
    # 7–8: four on the floor, soft; 9: until the breath
    for bb in (7, 8):
        for beat in (1, 2, 3, 4):
            kicks.append((T(bb, beat), 0.62))
    for beat in (1, 2, 3):
        kicks.append((T(9, beat), 0.7))
    # 10–29 and 30, 31 (first half)
    for bb in range(10, 31):
        for beat in (1, 2, 3, 4):
            kicks.append((T(bb, beat), 1.0 if bb < 30 else 0.8))
    kicks += [(T(31, 1), 0.75), (T(31, 2), 0.7)]
    for t, g in kicks:
        place(b, kick(g), t)
    # the drop: a bigger, longer kick
    place(b, kick(1.0, tau=0.55, f0=140, f1=38), T(10))
    # final downbeat
    place(b, kick(0.9, tau=0.8, f0=120, f1=36), T(32))
    # hats
    for bb in range(7, 31):
        for e in range(8):
            t = T(bb) + e * BEAT / 2
            if bb == 9 and e >= 7:
                continue
            if e % 2 == 1:
                place(b, hat(False, bb * 8 + e), t, 0.55 if bb < 10 else 0.7)
            elif bb >= 10:
                place(b, hat(False, bb * 9 + e), t, 0.22)
        if bb >= 10 and bb % 2 == 1:
            place(b, hat(True, bb), T(bb, 4.5), 0.35)
    # claps on 2 and 4 from the drop
    cl = bus()
    for bb in range(10, 31):
        for beat in (2, 4):
            place(cl, clap(bb * 2 + beat), T(bb, beat), 0.55)
    snare_roll(T(9, 1), T(9, 4.5), cl)
    cl, _ = reverb(cl, 0.22, 1.6, 6000, 7)
    b += cl
    return b, [t for t, _ in kicks] + [T(10), T(32)]


# ---------- tonal ----------
def pad_bus():
    b = bus()
    for bb, name in PROG.items():
        notes, _ = CH[name]
        dur = BAR + 0.9
        for i, n in enumerate(notes):
            x = supersaw(midi(n), dur, 5, 12, seed=bb * 10 + i)
            x *= adsr(dur, 0.25 if bb != 10 else 0.02, 0.4, 0.85, 0.85)[:, None]
            place(b, x, T(bb) - 0.02, 0.16)
    # final chord: long and open
    notes, _ = CH['Dmaj9']
    dur = TOTAL - T(32) + 0.5
    for i, n in enumerate(notes + [69, 73]):
        x = supersaw(midi(n), dur, 5, 10, seed=900 + i)
        env = adsr(dur, 0.03, 1.2, 0.7, 4.5)
        place(b, x * env[:, None], T(32), 0.15)
    # cutoff over time: dark → opening → open on the drop → warm under the voice
    pts = [(0, 300), (T(4), 700), (T(6), 900), (T(7), 1000), (T(9, 4), 3000), (T(10), 3600), (T(10, 3), 2400),
           (T(14), 2200), (T(30), 2000), (T(31, 4), 3200), (T(32), 3400), (TOTAL, 1500)]
    tt = np.arange(N) / SR
    curve = np.interp(tt, [p[0] for p in pts], [p[1] for p in pts])
    b = sweep_filter(b, curve, 'low')
    b = hp(b, 120)
    b, _ = reverb(b, 0.38, 3.4, 5000, 11)
    return b


def hook_drone():
    """Bars 1–3: a dark swell that tape-stops at 4.85 s."""
    dur = 6.0
    t = t_axis(dur)
    sw = np.clip(t / 4.6, 0, 1) ** 1.8
    x = np.zeros((len(t), 2), np.float32)
    for i, n in enumerate([35, 47, 54, 61]):
        v = supersaw(midi(n), dur, 5, 18, seed=50 + i)
        x += v * (0.35 if i == 0 else 0.18)
    x = sweep_filter(x, 250 + 2200 * sw, 'low')
    x *= (0.15 + 0.85 * sw)[:, None]
    x += np.stack([sine(midi(35), dur)] * 2, 1) * (0.22 * sw)[:, None]
    # tape stop: playback speed falls from 1 to 0 between 4.85 and 5.6 s
    t0, t1 = 4.85, 5.6
    speed = np.where(t < t0, 1.0, np.clip(1 - (t - t0) / (t1 - t0), 0, 1) ** 1.3)
    pos = np.cumsum(speed) - 1
    warped = np.stack([np.interp(pos, np.arange(len(t)), x[:, c]) for c in range(2)], 1)
    warped *= np.where(t < t1, 1.0, 0.0)[:, None]
    warped = fade(warped, 0.5, 0.01)
    out, _ = reverb(warped, 0.3, 2.5, 4000, 5)
    b = bus()
    place(b, out, 0)
    return b * 0.6


def bass_bus(kick_times):
    b = bus()
    for bb, name in PROG.items():
        if bb < 7:
            continue
        _, root = CH[name]
        f = midi(root + (12 if root < 30 else 0))
        steps = 8
        for e in range(steps):
            t = T(bb) + e * BEAT / 2
            if bb == 9 and e >= 7:
                continue
            if bb == 31 and e >= 4:
                continue
            dur = BEAT / 2 * 0.95
            env = adsr(dur, 0.006, 0.08, 0.75, 0.05)
            x = sine(f, dur) + 0.25 * sine(2 * f, dur)
            vel = 0.55 if bb < 10 else (0.9 if e % 2 else 0.7)
            place(b, x * env, t, vel)
    # final sub
    dur = TOTAL - T(32)
    x = sine(midi(26), dur) * adsr(dur, 0.01, 0.5, 0.6, 4.0)
    place(b, x, T(32), 0.9)
    b = np.tanh(b * 1.3) / 1.3
    b = lp(b, 260, 4)
    # a quiet mid layer so the bass line reads on small speakers
    mid = bus()
    for bb, name in PROG.items():
        if bb < 10 or bb > 31:
            continue
        _, root = CH[name]
        f = midi(root + 24)
        x = supersaw(f, BAR, 3, 6, seed=700 + bb, stereo=False)
        place(mid, x * adsr(BAR, 0.01, 0.3, 0.5, 0.2), T(bb), 0.05)
    b += lp(mid, 900)
    return b


def arp_bus():
    b = bus()
    pattern = [0, 2, 4, 5, 3, 1, 2, 4, 0, 2, 4, 5, 3, 4, 2, 1]
    for bb, name in PROG.items():
        notes, _ = CH[name]
        tones = sorted([n + 12 for n in notes] + [n + 24 for n in notes[:2]])
        if bb < 7:
            hits = [(e * 4, 0.5) for e in range(4)]  # quarters
        elif bb < 10:
            hits = [(e * 2, 0.55 + 0.1 * (e % 2 == 0)) for e in range(8)]  # 8ths
        else:
            hits = [(e, 0.75 if e % 4 == 0 else 0.5) for e in range(16)]  # 16ths
        for step, vel in hits:
            if bb == 9 and step >= 14:
                continue
            if bb == 31 and step >= 8:
                continue
            n = tones[pattern[step % 16] % len(tones)]
            t = T(bb) + step * BEAT / 4
            x = pluck(midi(n), 0.7, bright=1.2 if bb >= 10 else 0.8, decay=0.55, seed=bb * 16 + step)
            place(b, x, t, vel * 0.22)
    b = hp(b, 220)
    b = lp(b, 6500)
    b = delay(b, BEAT * 0.75, 0.32, 4, True, 3500)
    b, _ = reverb(b, 0.25, 2.2, 6000, 13)
    return b


def sparkle_bus():
    """Bells on the drop and on the final chord."""
    b = bus()
    for i, n in enumerate([74, 78, 81, 86]):
        place(b, bell(midi(n), 2.5, seed=i), T(10) + i * BEAT / 4, 0.18)
    for i, n in enumerate([74, 78, 81, 85, 88]):
        place(b, bell(midi(n), 4.0, seed=20 + i), T(32) + 0.9 + i * BEAT / 2, 0.16)
    b, _ = reverb(b, 0.45, 3.8, 7000, 17)
    return b


def sidechain(kick_times, depth_db=4.5, tau=0.16):
    g = np.ones(N, np.float32)
    for t in kick_times:
        i = int(t * SR)
        n = min(int(0.5 * SR), N - i)
        if n <= 0:
            continue
        g[i:i + n] = np.minimum(g[i:i + n], 1 - (1 - db(-depth_db)) * np.exp(-np.arange(n) / SR / tau))
    return g[:, None]


def main(out):
    import soundfile as sf
    dr, kick_times = drums()
    sc = sidechain([t for t in kick_times if t >= T(7)])
    pad = pad_bus() * sc
    bass = bass_bus(kick_times) * sidechain([t for t in kick_times if t >= T(7)], 7, 0.12)
    arp = arp_bus() * sc
    hook = hook_drone()
    sp = sparkle_bus()
    mix = dr * db(-8) + pad * db(1.5) + bass * db(-8.5) + arp * db(-1) + hook * db(-1) + sp * db(-4)
    # silence between the tape stop and the command (bar 4), and the ring-out to 1:15
    tt = np.arange(N) / SR
    mix *= np.clip((TOTAL - tt) / 2.5, 0, 1)[:, None]
    mix = mix[: int(TOTAL * SR)]
    mix = mix / np.abs(mix).max() * 0.8
    sf.write(out, mix, SR, subtype='FLOAT')
    for name, x in [('drums', dr), ('pad', pad), ('bass', bass), ('arp', arp), ('hook', hook)]:
        print(f'{name:6} rms {20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9):6.1f} dB')
    print('wrote', out, f'{len(mix) / SR:.2f}s')


if __name__ == '__main__':
    main(sys.argv[1])
