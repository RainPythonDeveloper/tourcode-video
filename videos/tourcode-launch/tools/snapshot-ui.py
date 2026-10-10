#!/usr/bin/env python3
"""Render real TourCode UI states with the extension's own webview.js and save the DOM.

Each state = one of assets/ui/*.html + a small mutation of the state object it posts
(e.g. another stepIndex, risks off). The webview code draws it; we keep #app's DOM.
"""
import copy, json, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
UI = os.path.join(ROOT, "assets", "ui")
OUT = os.path.join(os.path.dirname(__file__), "..", "capture", "ui-states")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def load(page):
    s = open(os.path.join(UI, page)).read()
    m = re.search(r'window\.postMessage\((\{.*\})\s*,\s*"\*"\)', s, re.S)
    surface = re.search(r'data-surface="(\w+)"', s).group(1)
    width = int(re.search(r'style="width:(\d+)px"', s).group(1))
    return json.loads(m.group(1)), surface, width


def no_questions(d):
    d.pop("questions", None)
    return d


def step(i):
    def f(d):
        d["session"]["stepIndex"] = i
        return d
    return f


def chain(*fs):
    def f(d):
        for g in fs:
            d = g(d)
        return d
    return f


def setk(k, v):
    def f(d):
        d[k] = v
        return d
    return f


def suggest(d):
    q = d["session"]["tour"]["steps"][d["session"]["stepIndex"]]["suggestedQuestions"]
    d["questions"] = {"answers": [], "suggestions": {"kind": "faq", "questions": q}}
    return d


def building(title, reads, origin=None):
    def f(d):
        d["build"] = {"title": title, "reads": reads}
        if origin:
            d["build"]["origin"] = origin
        return d
    return f


def no_tours(d):
    d["tours"] = []
    d["groups"] = []
    return d


def stale(d):
    for t in d["tours"]:
        if t["id"] == "session-start":
            t["staleStepCount"] = 2
    return d


def unpinned(d):
    for t in d["tours"]:
        t["isPinned"] = False
    return d


STATES = {
    "overview": ("tour-map.html", None, None),
    "step1-full": ("step.html", None, None),
    "step1-compact": ("step.html", chain(no_questions, setk("showDetails", False)), None),
    "step1-compact-norisk": ("step.html", chain(no_questions, setk("showDetails", False), setk("showRisks", False)), None),
    "step1-suggest": ("step.html", chain(setk("showDetails", False), suggest), None),
    "step1-answering": ("step-answering.html", None, None),
    "step1-answered": ("step.html", setk("showDetails", False), None),
    "step2-compact": ("step.html", chain(no_questions, setk("showDetails", False), step(1)), None),
    "step3-compact": ("step.html", chain(no_questions, setk("showDetails", False), step(2)), None),
    "step3-compact-norisk": ("step.html", chain(no_questions, setk("showDetails", False), setk("showRisks", False), step(2)), None),
    "subtour-step": ("step-subtour.html", None, None),
    "sidebar-s0": ("sidebar-tour.html", step(0), None),
    "sidebar-s1": ("sidebar-tour.html", None, None),
    "sidebar-s2": ("sidebar-tour.html", step(2), None),
    "step2-compact-norisk": ("step.html", chain(no_questions, setk("showDetails", False), setk("showRisks", False), step(1)), None),
    "sidebar-s0-norisk": ("sidebar-tour.html", chain(step(0), setk("showRisks", False)), None),
    "sidebar-s1-norisk": ("sidebar-tour.html", setk("showRisks", False), None),
    "sidebar-s2-norisk": ("sidebar-tour.html", chain(step(2), setk("showRisks", False)), None),
    "sidebar-empty": ("sidebar-home.html", no_tours, None),
    "sidebar-build-0": ("sidebar-home.html", chain(no_tours, building("How login works", [])), None),
    "sidebar-build-1": ("sidebar-home.html", chain(no_tours, building("How login works", ["src/auth.ts"])), None),
    "sidebar-build-2": ("sidebar-home.html", chain(no_tours, building("How login works", ["src/auth.ts", "src/password.ts"])), None),
    "sidebar-build-3": ("sidebar-home.html", chain(no_tours, building("How login works", ["src/auth.ts", "src/password.ts", "src/session.ts"])), None),
    "step1-building-subtour": ("step.html", chain(no_questions, setk("showDetails", False), building("Inside handleLogin", ["src/auth.ts"], {"tourId": "how-login-works", "stepId": "handle-login"})), None),
    "sidebar-subtour": ("sidebar-subtour.html", None, None),
    "sidebar-home": ("sidebar-home.html", None, None),
    "sidebar-home-stale": ("sidebar-home.html", stale, None),
    "sidebar-home-unpinned": ("sidebar-home.html", unpinned, None),
}

HARNESS = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="file://{ui}/theme.css"><link rel="stylesheet" href="file://{ui}/webview.css"></head>
<body data-surface="{surface}" style="width:{width}px"><div id="app"></div>
<script>window.acquireVsCodeApi=()=>({{postMessage(){{}}}});</script>
<script src="file://{ui}/webview.js"></script>
<script>window.postMessage({state},"*")</script></body></html>"""


def main(names):
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    meta = {}
    for name, (page, mut, _) in STATES.items():
        if names and name not in names:
            continue
        d, surface, width = load(page)
        d = copy.deepcopy(d)
        if mut:
            d = mut(d)
        h = os.path.join(tmp, name + ".html")
        open(h, "w").write(HARNESS.format(ui=UI, surface=surface, width=width, state=json.dumps(d)))
        dom = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
             "--virtual-time-budget=2000", f"--window-size={width},1400", "--dump-dom", "file://" + h],
            capture_output=True, text=True).stdout
        body = re.search(r'<div id="app">.*(?=<script>window\.acquireVsCodeApi)', dom, re.S).group(0)
        open(os.path.join(OUT, name + ".html"), "w").write(body)
        meta[name] = {"page": page, "surface": surface, "width": width}
        print(f"{name:24s} {page:22s} {surface:9s} {width}px  {len(body)} bytes")
    if not names:
        json.dump(meta, open(os.path.join(OUT, "_states.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
