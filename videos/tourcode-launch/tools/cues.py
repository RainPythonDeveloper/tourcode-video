#!/usr/bin/env python3
"""Every sound of the film, on the film's clock (seconds). Writes src/audio_cues.json.

Each cue lands on its visual event (see STORYBOARD.md). The music bed dips ~3.5 dB under the
signature effects through a volume lane (clip-local time).
"""
import json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DUR = json.load(open(os.path.join(ROOT, "assets", "sfx", "_durations.json")))
cues = []


def add(name, start, vol, dur=None, cid=None):
    d = dur if dur is not None else DUR[name]
    cues.append({"id": cid or f"{name}-{len([c for c in cues if c['file'].endswith(name + '.wav')]) + 1}",
                 "file": f"assets/sfx/{name}.wav", "start": round(start, 3), "duration": round(min(d, 60.0 - start), 3),
                 "volume": vol, "group": "master", "track": 10})


# 01 hook — riser into a tape stop, data-rush whooshes accelerating, soft thud at the hard stop
add("riser_tape_stop", 0.0, 0.62)
for t, v, n in [(0.2, 0.26, "a"), (1.4, 0.32, "b"), (2.4, 0.38, "a"), (3.2, 0.44, "b"), (3.85, 0.5, "a")]:
    add(f"rush_whoosh_{n}", t, v, dur=min(DUR[f"rush_whoosh_{n}"], 4.62 - t))
add("tape_thud", 5.0, 0.6)
# 02 command — one key per character (space bar = key_6), Enter, confirm pop + shimmer
KT = [0.95, 1.03, 1.12, 1.20, 1.28, 1.40, 1.50, 1.58, 1.66, 1.78, 1.88, 1.95, 2.03, 2.12, 2.24, 2.36, 2.44, 2.52, 2.60, 2.69, 2.82, 2.94, 3.02, 3.11, 3.20]
CMD = "/tour how does login work"
order = [1, 2, 3, 4, 5, 2, 4, 1, 3, 5, 2, 1, 4, 3, 5, 1, 2]
k = 0
for i, (t, ch) in enumerate(zip(KT, CMD)):
    if ch == " ":
        add("key_6", 5.0 + t, 0.34)
    else:
        add(f"key_{order[k % len(order)]}", 5.0 + t, 0.30 + 0.06 * ((i * 7) % 3) / 2)
        k += 1
add("key_3", 8.58, 0.42, cid="enter-key")
add("confirm_pop", 8.6, 0.55)
add("shimmer", 8.62, 0.34)
add("line_swish", 9.82, 0.22)                    # the route line leaves the command
# 03 the agent explores — ticks rising in pitch per lit file, a swish per route line
add("file_tick_1", 11.0, 0.5); add("file_tick_2", 12.2, 0.5); add("file_tick_3", 13.4, 0.5)
for t in (11.6, 12.8, 14.0):
    add("line_swish", t, 0.28)
# 04 tour map — soft impact as it settles, airy whoosh on the pull-back, deeper swoosh on the dive
add("map_impact", 16.42, 0.55)
add("airy_whoosh", 17.4, 0.42)
add("dive_swoosh", 21.85, 0.55)
# 05 walk-through — the brand chime each time lines highlight, a tick per progress segment, glossary pop
for t in (23.6, 26.6, 29.0):
    add("brand_chime", t, 0.5)
for t in (26.6, 29.0):
    add("progress_tick", t, 0.38)
add("glossary_pop", 31.4, 0.42)
# 06 risks — toggle click, soft warning tone per marker; the band expands into frame 07
add("toggle_click", 34.38, 0.55)
add("risk_tone", 35.0, 0.5); add("risk_tone", 35.6, 0.34)
add("rush_whoosh_a", 38.45, 0.22)
# 07 ask and go deeper — chime as lines highlight, click, streaming texture, reverse-reverb dive, path slide
add("brand_chime", 39.8, 0.5)
add("ui_click", 40.4, 0.5)
add("typing_texture", 40.95, 0.2, dur=1.6)
add("ui_click", 43.4, 0.5)
add("dive_reverse_whoosh", 43.45, 0.5)
add("path_slide", 44.6, 0.45)
add("line_swish", 46.95, 0.26)                   # the route line crosses into frame 08
# 08 teams — pin snap, group slides, rebuild: click + swirl, success chime
add("pin_snap", 47.6, 0.6)
add("group_slide", 48.2, 0.34); add("group_slide", 48.8, 0.34)
add("ui_click", 49.98, 0.42)
add("rebuild_swirl", 50.0, 0.42)
add("success_chime", 50.6, 0.36)
# 09 works everywhere — one soft hit per logo, on the beat grid (eighths)
for i, t in enumerate([53.3, 53.6, 53.9, 54.2, 54.5, 54.8, 55.1, 55.4]):
    add(f"logo_hit_{i + 1}", t, 0.42)
add("line_swish", 55.78, 0.24)                   # the route carries the dot to the logo
# 10 end card — riser following the line, shimmering resolve hit on the logo
add("end_riser", 56.6, 0.4)
add("resolve_hit", 57.55, 0.5)

# the music bed: enters on the beat at 5.6, dips ~3.5 dB under each signature effect
DIPS = [16.95, 22.35, 23.6, 26.6, 29.0, 35.0, 39.8, 43.4, 50.0]
DIP = 0.67
pts = [{"t": 0, "v": 1}]
for d in DIPS:
    a = d - 5.6
    pts += [{"t": round(a - 0.08, 3), "v": 1}, {"t": round(a, 3), "v": DIP}, {"t": round(a + 0.55, 3), "v": DIP}, {"t": round(a + 1.0, 3), "v": 1}]
music = {"id": "music-bed", "file": "assets/audio/music-bed.wav", "start": 5.6, "duration": 54.4, "volume": 0.63, "group": "master",
         "track": 9, "automation": {"version": 1, "lanes": [{"target": "volume", "points": pts}]}}
json.dump([music] + cues, open(os.path.join(ROOT, "src", "audio_cues.json"), "w"), indent=1)
print(f"{len(cues)} sfx cues + music bed → src/audio_cues.json")
