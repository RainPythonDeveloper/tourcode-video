#!/usr/bin/env python3
"""Expand frame sources (src/frames/*.html) into HyperFrames sub-compositions.

Directives inside a source file:
  <!--@css-->                      the shared stylesheet (fonts, VS Code theme vars, the real
                                   webview.css, video overrides, editor-shell styles)
  <!--@ui STATE [PREFIX]-->        the real TourCode DOM from capture/ui-states/STATE.html,
                                   wrapped in .tc-ui, ids/url(#)/aria refs prefixed
  <!--@code FILE PREFIX-->         FILE (capture/assets/FILE) as editor lines with Dark Modern
                                   syntax colors; each line is .ln[data-line=N]
  <!--@icon NAME-->                an inline SVG icon (activity bar, logo, cursor)
  {{LINK}}                         the end-card link text (variables.json)

Output: compositions/frames/<name>.html — one bare <template> fragment.
"""
import html, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src", "frames")
OUT = os.path.join(ROOT, "compositions", "frames")
UI_STATES = os.path.join(ROOT, "capture", "ui-states")
CAP = os.path.join(ROOT, "capture", "assets")
VARS = json.load(open(os.path.join(ROOT, "src", "variables.json")))

# ---------------------------------------------------------------- shared css

FONTS = """
@font-face{font-family:"Inter";src:url("assets/fonts/inter-400.woff2") format("woff2");font-weight:400;font-style:normal;font-display:block}
@font-face{font-family:"Inter";src:url("assets/fonts/inter-500.woff2") format("woff2");font-weight:500;font-style:normal;font-display:block}
@font-face{font-family:"Inter";src:url("assets/fonts/inter-600.woff2") format("woff2");font-weight:600;font-style:normal;font-display:block}
@font-face{font-family:"Inter";src:url("assets/fonts/inter-700.woff2") format("woff2");font-weight:700;font-style:normal;font-display:block}
@font-face{font-family:"JetBrains Mono";src:url("assets/fonts/jetbrains-mono-400.woff2") format("woff2");font-weight:400;font-style:normal;font-display:block}
@font-face{font-family:"JetBrains Mono";src:url("assets/fonts/jetbrains-mono-500.woff2") format("woff2");font-weight:500;font-style:normal;font-display:block}
@font-face{font-family:"JetBrains Mono";src:url("assets/fonts/jetbrains-mono-600.woff2") format("woff2");font-weight:600;font-style:normal;font-display:block}
@font-face{font-family:"JetBrains Mono";src:url("assets/fonts/jetbrains-mono-700.woff2") format("woff2");font-weight:700;font-style:normal;font-display:block}
"""

# theme.css stands in for VS Code Dark Modern; webview.css is the extension's own stylesheet.
# Its document-level rules (body, :root) are kept: every frame shares them.
VIDEO_OVERRIDES = """
/* ---- video overrides: the timeline owns all motion ---- */
:root{--motion:0ms}
/* (transitions/animations removed from the webview.css copy above) */
.tc-ui{color:var(--vscode-foreground);font-family:var(--vscode-font-family);font-size:var(--vscode-font-size);line-height:1.5;text-align:left}
.tc-ui .session{min-height:0}
.tc-ui .step-page-hint, .tc-ui .hint{display:none}
"""

SHELL = r"""
/* ---- VS Code Dark Modern window (built in HTML: it does not exist as a file) ---- */
.vsc{position:absolute;width:1688px;height:858px;border-radius:12px;overflow:hidden;background:#1f1f1f;
  border:1px solid #2b2b2b;box-shadow:0 50px 140px rgba(0,0,0,.6),0 14px 40px rgba(0,0,0,.45);
  font-family:"Inter",sans-serif;color:#cccccc}
.vsc-title{position:absolute;left:0;top:0;right:0;height:34px;background:#181818;border-bottom:1px solid #2b2b2b;
  display:flex;align-items:center;justify-content:center;font-size:12.5px;color:#9d9d9d;letter-spacing:.01em}
.vsc-dots{position:absolute;left:14px;top:11px;display:flex;gap:8px}
.vsc-dots i{display:block;width:12px;height:12px;border-radius:50%;background:#3a3a3a}
.vsc-body{position:absolute;left:0;top:34px;right:0;bottom:22px}
.vsc-act{position:absolute;left:0;top:0;bottom:0;width:48px;background:#181818;border-right:1px solid #2b2b2b}
.vsc-act .ai{position:relative;width:48px;height:48px;display:flex;align-items:center;justify-content:center;color:#868686}
.vsc-act .ai svg{width:24px;height:24px}
.vsc-act .ai.on{color:#e6e6e6}
.vsc-act .ai.on::before{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;background:#0078d4}
.vsc-side{position:absolute;left:48px;top:0;bottom:0;width:360px;background:#181818;border-right:1px solid #2b2b2b;overflow:hidden}
.vsc-side-head{height:35px;display:flex;align-items:center;padding:0 20px;font-size:11px;font-weight:400;letter-spacing:.06em;color:#9d9d9d;text-transform:uppercase}
.vsc-side-body{position:absolute;left:0;right:0;top:35px;bottom:0;overflow:hidden}
.vsc-main{position:absolute;left:408px;top:0;right:0;bottom:0;background:#1f1f1f}
.vsc-tabs{position:absolute;left:0;right:0;top:0;height:35px;background:#181818;border-bottom:1px solid #2b2b2b;display:flex}
.vsc-tab{position:relative;height:35px;padding:0 14px 0 12px;display:flex;align-items:center;gap:6px;font-size:13px;color:#9d9d9d;
  background:#181818;border-right:1px solid #2b2b2b}
.vsc-tab.on{background:#1f1f1f;color:#ffffff}
.vsc-tab.on::before{content:"";position:absolute;left:0;right:0;top:0;height:1px;background:#0078d4}
.vsc-tab .ts{font-family:"JetBrains Mono",monospace;font-size:10px;font-weight:700;color:#4d9fdc;letter-spacing:-.02em}
.vsc-crumbs{position:absolute;left:0;right:0;top:35px;height:22px;display:flex;align-items:center;padding-left:16px;font-size:12.5px;color:#9d9d9d;gap:6px}
.vsc-code{position:absolute;left:0;right:0;top:57px;height:340px;overflow:hidden;background:#1f1f1f}
.vsc-panel{position:absolute;left:0;right:0;top:397px;bottom:0;background:#1f1f1f;border-top:1px solid #2b2b2b;overflow:hidden}
.vsc-panel-head{height:35px;display:flex;align-items:center;gap:22px;padding:0 20px;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#9d9d9d}
.vsc-panel-head .on{color:#e6e6e6;position:relative}
.vsc-panel-head .on::after{content:"";position:absolute;left:0;right:0;bottom:-9px;height:1px;background:#e6e6e6}
.vsc-panel-body{position:absolute;left:0;right:0;top:35px;bottom:0;overflow:hidden}
.vsc-status{position:absolute;left:0;right:0;bottom:0;height:22px;background:#181818;border-top:1px solid #2b2b2b;display:flex;align-items:center;
  justify-content:space-between;padding:0 12px;font-size:11.5px;color:#9d9d9d}
.vsc-status span{margin-right:16px}

/* code lines */
.code{position:absolute;left:0;top:6px;right:0;font-family:"JetBrains Mono",monospace;font-size:15px;line-height:22px;font-variant-ligatures:none}
.ln{position:relative;height:22px;white-space:pre;display:flex}
.ln .no{width:64px;flex:none;text-align:right;padding-right:26px;color:#8b949e}
.ln .tx{color:#cccccc;padding-left:18px}
.ln.cur .no{color:#cccccc}
.hl{position:absolute;left:64px;right:0;background:rgba(63,185,80,.14);border-left:2px solid #3fb950}
.tok-k{color:#c586c0}.tok-s{color:#62a8e3}.tok-str{color:#ce9178}.tok-fn{color:#dcdcaa}.tok-v{color:#9cdcfe}
.tok-t{color:#4ec9b0}.tok-c{color:#4fc1ff}.tok-p{color:#cccccc}

/* the real webview pages at their native widths */
.ui-step{position:absolute;left:0;top:0;width:1280px}
.ui-side{position:absolute;left:0;top:0;width:360px}
.ui-side .tc-ui{background:#181818}

/* green field used by the bar-expand / bar-contract seams (transform-only) */
.gfield{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0;background:#233425}
.gedge{position:absolute;left:0;top:0;width:2px;height:1080px;transform-origin:0 0;background:#3fb950}

/* cursor */
.cursor{position:absolute;left:0;top:0;width:26px;height:34px;z-index:50;pointer-events:none}
.cursor svg{width:26px;height:34px;filter:drop-shadow(0 2px 3px rgba(0,0,0,.5))}

/* eyebrow (as in the UI): glowing green dot */
.eb{display:inline-flex;align-items:center;gap:10px;font-family:"Inter",sans-serif;font-weight:600;font-size:18px;letter-spacing:.12em;text-transform:uppercase;color:#3fb950}
.eb::before{content:"";width:9px;height:9px;border-radius:50%;background:#3fb950;box-shadow:0 0 10px 2px rgba(63,185,80,.65)}
"""


def shared_css():
    theme = open(os.path.join(CAP, "theme.css")).read()
    web = open(os.path.join(CAP, "webview.css")).read()
    # theme.css's own body/background rules are page-level for the standalone pages: drop them
    theme = re.sub(r"body\s*\{[^}]*\}", "", theme)
    theme = re.sub(r"body\[data-surface[^{]*\{[^}]*\}", "", theme)
    web = re.sub(r"body\[data-surface=\"(overview|step)\"\]\s*\{[^}]*\}", "", web)
    # the timeline owns all motion: drop the UI's own CSS transitions / keyframe animations
    web = re.sub(r"\s*transition:[^;{}]*;", "", web)
    web = re.sub(r"\s*animation:[^;{}]*;", "", web)
    return "\n".join([FONTS, "/* theme.css */", theme, "/* webview.css (TourCode) */", web, VIDEO_OVERRIDES, SHELL])


# ---------------------------------------------------------------- ui includes

def ui(state, prefix):
    s = open(os.path.join(UI_STATES, state + ".html")).read()
    # the real UI keeps its own layering (sticky footer, diagram labels): mark it intentional
    s = s.replace('<div id="app">', f'<div class="tc-ui" data-ui="{state}" data-layout-allow-overlap>', 1)
    ids = set(re.findall(r'\sid="([^"]+)"', s))
    for i in sorted(ids, key=len, reverse=True):
        s = s.replace(f'id="{i}"', f'id="{prefix}-{i}"')
        s = s.replace(f'url(#{i})', f'url(#{prefix}-{i})')
        s = re.sub(rf'(aria-(?:describedby|labelledby|controls)=")({re.escape(i)})(")', rf'\g<1>{prefix}-\2\3', s)
    s = s.replace(' data-autofocus=""', "").replace(" data-autofocus", "")
    if state.startswith("sidebar"):
        # the sidebar's sticky footer (Back / Next) scrolls over the glossary in the real UI
        for tag in ("<dt", "<dd", "<button"):
            s = s.replace(tag, tag + " data-layout-allow-overlap")
    return s


# ---------------------------------------------------------------- code

KW_CTRL = {"import", "from", "export", "return", "if", "await"}
KW_STOR = {"async", "function", "const", "true", "false", "undefined"}
TYPES = {"string", "boolean"}
TOKEN = re.compile(r'("[^"]*")|([A-Za-z_][A-Za-z0-9_]*)|(\s+)|(.)')


def colorize(line):
    out = []
    toks = TOKEN.findall(line)
    flat = [a or b or c or d for a, b, c, d in toks]
    for idx, (st, ident, ws, ch) in enumerate(toks):
        if st:
            out.append(f'<span class="tok-str">{html.escape(st)}</span>')
        elif ident:
            nxt = next((t for t in flat[idx + 1:] if not t.isspace()), "")
            prev = next((t for t in reversed(flat[:idx]) if not t.isspace()), "")
            if ident in KW_CTRL:
                cls = "tok-k"
            elif ident in KW_STOR:
                cls = "tok-s"
            elif ident in TYPES and prev == ":":
                cls = "tok-t"
            elif ident == "crypto":
                cls = "tok-v"
            elif nxt == "(":
                cls = "tok-fn"
            else:
                cls = "tok-v"
            out.append(f'<span class="{cls}">{ident}</span>')
        elif ws:
            out.append(ws)
        else:
            out.append(f'<span class="tok-p">{html.escape(ch)}</span>')
    return "".join(out)


def code(fname, prefix):
    lines = open(os.path.join(CAP, fname)).read().rstrip("\n").split("\n")
    rows = []
    for n, l in enumerate(lines, 1):
        rows.append(f'<div class="ln" data-line="{n}"><span class="no">{n}</span><span class="tx">{colorize(l)}</span></div>')
    return f'<div class="code" id="{prefix}-{fname.replace(".", "-")}">' + "".join(rows) + "</div>"


# ---------------------------------------------------------------- icons

ICONS = {
    "files": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M14 3H7a1 1 0 0 0-1 1v15a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5"/><path d="M3 7v13a1 1 0 0 0 1 1h11" opacity=".0"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="10" r="6"/><path d="M15.5 14.5 20 19" stroke-linecap="round"/></svg>',
    "scm": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="7" cy="5" r="2"/><circle cx="7" cy="19" r="2"/><circle cx="17" cy="9" r="2"/><path d="M7 7v10M17 11c0 4-6 3-9.5 6.5"/></svg>',
    "run": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M8 5v14l11-7z"/></svg>',
    "ext": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1" transform="rotate(12 17.5 6.5)"/></svg>',
    # tourcode-mark.svg (assets/brand), stroke currentColor
    "tourcode": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="5.5" cy="18.5" r="2.5"/><path d="M8 18.5h6.5a3.5 3.5 0 0 0 0-7h-5a3.5 3.5 0 0 1 0-7H16"/><path d="M15.5 2l3 2.5-3 2.5"/></svg>',
    "cursor": '<svg viewBox="0 0 26 34"><path d="M2 2 L2 26 L8 20.5 L12.5 31 L16.5 29.3 L12.2 19.2 L20.5 19.2 Z" fill="#ffffff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>',
    "branch": '<svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="4.5" cy="3.5" r="1.5"/><circle cx="4.5" cy="12.5" r="1.5"/><circle cx="11.5" cy="5.5" r="1.5"/><path d="M4.5 5v6M11.5 7c0 3-4 2.5-6.2 4.6"/></svg>',
}


def icon(name):
    return ICONS[name]


# ---------------------------------------------------------------- expand

def expand(src, name):
    def rep(m):
        parts = m.group(1).split()
        kind = parts[0]
        if kind == "css":
            return "<style>\n" + shared_css() + "\n</style>"
        if kind == "ui":
            return ui(parts[1], parts[2] if len(parts) > 2 else f"{name}-{parts[1]}")
        if kind == "code":
            return code(parts[1], parts[2] if len(parts) > 2 else name)
        if kind == "icon":
            return icon(parts[1])
        raise SystemExit(f"{name}: unknown directive {kind}")
    out = re.sub(r"<!--@(.*?)-->", rep, src)
    for k, v in VARS.items():
        out = out.replace("{{" + k + "}}", html.escape(v))
    return out


def main(names):
    os.makedirs(OUT, exist_ok=True)
    for f in sorted(os.listdir(SRC)):
        if not f.endswith(".html"):
            continue
        name = f[:-5]
        if names and name not in names:
            continue
        src = open(os.path.join(SRC, f)).read()
        out = expand(src, name)
        if not out.lstrip().startswith("<template"):
            raise SystemExit(f"{f}: must start with <template>")
        open(os.path.join(OUT, f), "w").write(out)
        print(f"built compositions/frames/{f}  ({len(out)//1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1:])
