"""Builds data/logos.js: every editor/agent/wiki mark as a one-colour shape.

The film shows the marks in one tone on the dark background (as partner rows on
Linear, Raycast and Vercel pages do). Sources and licences: see README.md.
- simple-icons (CC0-1.0 data): Cursor, Windsurf, Claude, Jupyter, Confluence, Notion
- Visual Studio Code: official logo SVG (code.visualstudio.com/brand) via thesvg, pinned commit;
  the silhouette is the logo's own mask path
- Kiro: official icon PNG from github.com/kirodotdev/Kiro (assets/kiro-icon.png); the white ghost
  is kept as an alpha mask
Usage: python render/build-logos.py
"""
import base64
import io
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(__file__).resolve().parent.parent
logos = root / "assets/logos"
out = {}
for name in ["cursor", "windsurf", "claude", "jupyter", "confluence", "notion"]:
    svg = (logos / f"{name}.svg").read_text()
    d = re.search(r'<path d="([^"]+)"', svg).group(1)
    out[name] = {"viewBox": "0 0 24 24", "paths": [d], "rule": "nonzero"}

vs = (logos / "vscode.svg").read_text()
mask_path = re.search(r'<mask[^>]*>\s*<path[^>]*\sd="([^"]+)"', vs).group(1)
out["vscode"] = {"viewBox": "0 0 100 100", "paths": [mask_path], "rule": "evenodd"}

img = Image.open(logos / "kiro-icon.png").convert("RGBA")
a = np.asarray(img).astype(np.float32) / 255
lum = a[..., :3].min(axis=2)  # the ghost is white; the purple tile and the eyes are not
alpha = np.clip((lum - 0.80) / 0.15, 0, 1) * a[..., 3]
ys, xs = np.where(alpha > 0.5)
pad = 40
crop = alpha[ys.min() - pad: ys.max() + pad, xs.min() - pad: xs.max() + pad]
h, w = crop.shape
rgba = np.zeros((h, w, 4), np.uint8)
rgba[..., :3] = 255
rgba[..., 3] = (crop * 255).astype(np.uint8)
ghost = Image.fromarray(rgba).resize((w // 4, h // 4), Image.LANCZOS)
buf = io.BytesIO()
ghost.save(buf, "PNG", optimize=True)
out["kiro"] = {"png": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), "aspect": w / h}

(root / "data/logos.js").write_text("window.LOGOS = " + json.dumps(out) + ";\n")
print({k: (len(v.get("paths", [""])[0]) if "paths" in v else len(v["png"])) for k, v in out.items()})
