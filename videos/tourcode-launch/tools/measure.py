#!/usr/bin/env python3
"""Measure element boxes inside a real UI state, rendered with the film's fonts.

usage: measure.py STATE WIDTH 'css selector' ['css selector' ...]
prints JSON: {selector: [{x,y,w,h,text}...]} relative to the .tc-ui root (top-left).
"""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
import build  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def measure(state, width, selectors):
    css = build.shared_css().replace('url("assets/', f'url("file://{ROOT}/assets/')
    body = build.ui(state, "m")
    script = """
    document.fonts.ready.then(()=>{
      const root=document.querySelector('.tc-ui'); const r0=root.getBoundingClientRect();
      const sels=%s; const out={};
      for(const s of sels){ out[s]=[...root.querySelectorAll(s)].map(e=>{const r=e.getBoundingClientRect();
        return {x:+(r.left-r0.left).toFixed(1),y:+(r.top-r0.top).toFixed(1),w:+r.width.toFixed(1),h:+r.height.toFixed(1),text:(e.textContent||'').trim().slice(0,60)}});}
      out.__height=+r0.height.toFixed(1);
      document.getElementById('out').textContent=JSON.stringify(out);
    });""" % json.dumps(selectors)
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>
<body style="margin:0;background:#1f1f1f"><div style="width:{width}px">{body}</div><pre id="out"></pre><script>{script}</script></body></html>"""
    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False)
    tmp.write(page)
    tmp.close()
    dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
                          "--virtual-time-budget=3000", f"--window-size={width},1400", "--dump-dom",
                          "file://" + tmp.name], capture_output=True, text=True).stdout
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    return json.loads(m.group(1).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))


if __name__ == "__main__":
    st, w, *sels = sys.argv[1:]
    print(json.dumps(measure(st, int(w), sels), indent=1))
