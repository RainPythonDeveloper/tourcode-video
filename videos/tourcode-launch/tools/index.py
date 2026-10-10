#!/usr/bin/env python3
"""Assemble index.html: frames from STORYBOARD.md (durations + order), the caption layer,
the grain/vignette finish, and every audio clip from src/audio_cues.json (if present).

usage: index.py [--format 1920x1080] [--out index.html]
"""
import argparse, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def frames():
    sb = open(os.path.join(ROOT, "STORYBOARD.md")).read()
    out = []
    for m in re.finditer(r"^## Frame (\d+) — (.+?)\n(.*?)(?=^## Frame |\Z)", sb, re.S | re.M):
        n = int(m.group(1))
        dur = float(re.search(r"^- duration:\s*([\d.]+)s", m.group(3), re.M).group(1))
        out.append((n, dur))
    return out


def frame_files():
    d = os.path.join(ROOT, "compositions", "frames")
    return {int(f[:2]): f[:-5] for f in os.listdir(d) if f.endswith(".html") and f[:2].isdigit()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="index.html")
    a = ap.parse_args()
    files = frame_files()
    t = 0.0
    hosts = []
    for n, dur in frames():
        if n in files:
            cid = files[n]
            hosts.append(f'''      <div id="el-{cid}" class="scene" data-composition-id="{cid}" data-composition-src="compositions/frames/{cid}.html"
        data-start="{t:.3f}" data-duration="{dur:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>''')
        t += dur
    total = round(t, 3)
    layers = []
    if os.path.exists(os.path.join(ROOT, "compositions", "captions.html")):
        layers.append(f'''      <div id="el-captions" class="scene" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{total}" data-track-index="5" data-track-kind="captions" data-width="1920" data-height="1080"></div>''')
    layers.append(f'''      <div id="el-finish" class="scene" data-composition-id="finish" data-composition-src="compositions/finish.html"
        data-start="0" data-duration="{total}" data-track-index="6" data-track-kind="graphics" data-width="1920" data-height="1080"></div>''')
    audio = []
    cues_path = os.path.join(ROOT, "src", "audio_cues.json")
    if os.path.exists(cues_path):
        import html as H
        cues = json.load(open(cues_path))
        mix = json.load(open(os.path.join(ROOT, "src", "mix.json")))
        chain = H.escape(json.dumps(mix["chain"]), quote=True)
        audio.append(f'''      <hf-audio-group id="master" data-label="Master" data-volume="1" data-fx-chain="{chain}"></hf-audio-group>''')
        # overlapping sounds go on separate lanes (music keeps its own)
        ends = {}
        for c in sorted(cues, key=lambda c: c["start"]):
            if c["id"] == "music-bed":
                continue
            lane = next(t for t in range(10, 40) if ends.get(t, -1) <= c["start"] + 1e-6)
            c["track"] = lane
            ends[lane] = c["start"] + c["duration"]
        for c in cues:
            extra = ""
            if "automation" in c:
                extra = f' data-automation="{H.escape(json.dumps(c["automation"]), quote=True)}"'
            audio.append(f'''      <audio id="a-{c['id']}" src="{c['file']}" data-start="{c['start']:.3f}" data-duration="{c['duration']:.3f}" data-track-index="{c.get('track', 10)}" data-volume="{c['volume']}" data-audio-group="{c['group']}"{extra}></audio>''')
    html = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #0d1117; }}
      .scene {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}
{chr(10).join(layers)}
{chr(10).join(audio)}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
    open(os.path.join(ROOT, a.out), "w").write(html)
    print(f"wrote {a.out}: {len(hosts)} frames, {len(audio)} audio clips, total {total}s")


if __name__ == "__main__":
    main()
