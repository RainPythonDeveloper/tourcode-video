"""Mix and master: music + narration + sound effects → one stereo track at -14 LUFS, true peak ≤ -1 dBTP.

- The voice is cleaned (high-pass, de-click), levelled and sits on top.
- The music ducks under the voice (about -8 dB, smooth) and dips about -3 dB under the
  signature sounds (the highlight chime, the drop, the final resolve).
- The sound effects are placed at the cues the film registered (data/sfx-cues.json).
- Master: loudness to -14 LUFS integrated, then a look-ahead limiter at -1.2 dBTP
  (4x oversampled peak detection), then measured again.
Usage: python mix.py MUSIC.wav OUT.wav [REPORT.json]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy import ndimage, signal

import sfx
from synth import SR, db, hp, lp, place

ROOT = Path(__file__).resolve().parent.parent

# level of each effect relative to the others (dB)
GAIN = {
    'hook_riser': -13, 'rush': -15, 'tape_stop': -14, 'thud': -6, 'cut_soft': -24, 'key': -21,
    'enter_pop': -12, 'shimmer': -16, 'line_swish': -17, 'tick': -16, 'swish': -20, 'pop_soft': -17,
    'select': -18, 'impact': -5, 'airy_whoosh': -15, 'route_tick': -19, 'node_ping': -21, 'click': -16,
    'deep_swoosh': -11, 'chime': -12.5, 'panel_rise': -21, 'prog_tick': -24, 'tooltip_pop': -17,
    'type_texture': -23, 'toggle': -15, 'warn_tone': -12, 'dive_whoosh': -14, 'path_slide': -17,
    'pin_snap': -12, 'slide': -18, 'swirl': -16, 'rebuild_chime': -15, 'paper_swish': -15, 'land': -14,
    'logo_hit': -18, 'final_riser': -14, 'route_draw': -16, 'resolve': -11, 'cta_tick': -22,
}
SIGNATURE = {'chime', 'impact', 'resolve'}


def lufs(x):
    return pyln.Meter(SR).integrated_loudness(x)


def true_peak_db(x):
    up = signal.resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(np.abs(up).max() + 1e-12)


def envelope(x, attack, release):
    """Peak-ish envelope with separate attack and release (seconds)."""
    a = np.exp(-1 / (attack * SR))
    r = np.exp(-1 / (release * SR))
    rect = np.abs(x)
    # decimate for speed, then upsample
    hop = 64
    v = ndimage.maximum_filter1d(rect, hop)[::hop]
    out = np.zeros_like(v)
    e = 0.0
    a2, r2 = a ** hop, r ** hop
    for i, s in enumerate(v):
        e = a2 * e + (1 - a2) * s if s > e else r2 * e + (1 - r2) * s
        out[i] = e
    return np.interp(np.arange(len(x)) / hop, np.arange(len(out)), out)


def limiter(x, ceiling_db=-1.2, lookahead=0.004, release=0.08):
    ceil = db(ceiling_db)
    up = signal.resample_poly(x, 4, 1, axis=0)
    peak = np.abs(up).max(1).reshape(-1, 4).max(1)[: len(x)]
    need = np.minimum(1.0, ceil / np.maximum(peak, 1e-9))
    L = int(lookahead * SR)
    g = ndimage.minimum_filter1d(need, 2 * L + 1)
    g = ndimage.uniform_filter1d(g, L + 1)
    g = np.minimum(g, ndimage.minimum_filter1d(need, 2 * L + 1))
    # release smoothing (only lets gain recover slowly)
    r = np.exp(-1 / (release * SR))
    hop = 16
    gd = g[::hop]
    out = np.empty_like(gd)
    cur = 1.0
    r2 = r ** hop
    for i, v in enumerate(gd):
        cur = v if v < cur else r2 * cur + (1 - r2) * v
        out[i] = cur
    g2 = np.minimum(np.interp(np.arange(len(g)) / hop, np.arange(len(out)), out), g)
    return x * g2[:, None]


def main(music_path, out_path, report_path=None):
    music, sr = sf.read(music_path, dtype='float32')
    assert sr == SR
    n = len(music)

    # ---- voice ----
    v24, vsr = sf.read(ROOT / 'narration/narration.wav', dtype='float32')
    voice = signal.resample_poly(v24, SR // 8000, vsr // 8000).astype(np.float32)
    # de-click: single-sample spikes far above their neighbourhood
    med = ndimage.median_filter(voice, 9)
    spikes = np.abs(voice - med) > 0.25
    voice[spikes] = med[spikes]
    voice = hp(voice, 75, 2)
    # gentle levelling (slow compressor)
    env = envelope(voice, 0.01, 0.25)
    gain = np.where(env > db(-30), (np.maximum(env, 1e-6) / db(-30)) ** (-0.25), 1.0)
    voice = voice * gain
    voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]
    vst = np.stack([voice, voice], 1)
    vst *= db(-15.5 - lufs(vst))

    # ---- sound effects ----
    cues = json.loads((ROOT / 'data/sfx-cues.json').read_text())['cues']
    fx = np.zeros((n, 2), np.float32)
    sig_fx = np.zeros((n, 2), np.float32)  # signature sounds: ducked less
    sig = np.zeros(n, np.float32)
    for c in cues:
        s = sfx.make(c) * db(GAIN[c['name']])
        place(sig_fx if c['name'] in SIGNATURE else fx, s, c['t'])
        if c['name'] in SIGNATURE:
            i = int(c['t'] * SR)
            k = min(len(s), n - i)
            sig[i:i + k] = np.maximum(sig[i:i + k], np.abs(s[:k]).max(1))

    # ---- music under the voice ----
    music *= db(-21 - lufs(music))
    venv = envelope(voice, 0.04, 0.35)
    duck_v = np.clip(venv / db(-28), 0, 1) ** 0.7  # 0 → 1 as the voice comes in
    senv = envelope(sig, 0.01, 0.3)
    duck_s = np.clip(senv / db(-30), 0, 1)
    g = db(-10.0 * duck_v) * db(-3.0 * duck_s * (1 - duck_v))
    music = music * g[:, None]
    fx = fx * db(-5.0 * duck_v)[:, None] + sig_fx * db(-3.5 * duck_v)[:, None]

    mix = music + vst + fx
    if report_path:  # voice-to-background ratio on every spoken line
        segs = json.loads((ROOT / 'narration/timeline.json').read_text())['segments']
        band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], 'band', output='sos'), x, axis=0)
        bv, bb = band(vst), band(music + fx)
        ratios = []
        for sgm in segs:
            a, b = int(sgm['start'] * SR), int(sgm['end'] * SR)
            rv = np.sqrt((bv[a:b] ** 2).mean()); rb = np.sqrt((bb[a:b] ** 2).mean())
            ratios.append(f"{sgm['id']} {20 * np.log10(rv / rb):.1f}")
        print('voice over background, 300 Hz–4 kHz (dB):', ', '.join(ratios))
    pre = lufs(mix)
    mix *= db(-14 - pre)
    mix = limiter(mix, -1.2)
    # one more pass: the limiter costs a little loudness
    mix *= db(-14 - lufs(mix))
    mix = limiter(mix, -1.2)
    mix[: int(0.003 * SR)] *= np.linspace(0, 1, int(0.003 * SR))[:, None]
    sf.write(out_path, mix, SR, subtype='PCM_24')

    rep = {
        'integrated_lufs': round(lufs(mix), 2),
        'true_peak_dbtp': round(true_peak_db(mix), 2),
        'music_lufs_alone': -21, 'voice_lufs': -15.5,
        'duration_s': round(n / SR, 3),
    }
    print(json.dumps(rep))
    if report_path:
        Path(report_path).write_text(json.dumps(rep, indent=1))


if __name__ == '__main__':
    main(*sys.argv[1:])
