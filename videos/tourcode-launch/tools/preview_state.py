#!/usr/bin/env python3
"""Render a UI state (with the film's fonts + shared CSS) to a PNG for inspection.
usage: preview_state.py STATE WIDTH HEIGHT OUT.png"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import build
ROOT = build.ROOT
st, w, h, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
css = build.shared_css().replace('url("assets/', f'url("file://{ROOT}/assets/')
bg = "#181818" if st.startswith("sidebar") else "#1f1f1f"
page = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body style="margin:0;background:{bg}"><div style="width:{w}px">{build.ui(st, "p")}</div></body></html>'
t = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False); t.write(page); t.close()
subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
  "--allow-file-access-from-files", "--virtual-time-budget=3000", f"--window-size={w},{h}", f"--screenshot={out}", "file://" + t.name], capture_output=True)
print(out)
