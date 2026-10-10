/* TourCode teaser v2 — one paused GSAP timeline, driven frame by frame by render/capture.mjs.
 *
 * Time is music time: 112 BPM, bar(b, beat) gives seconds. Spoken words come from
 * data/narration.js (word timings from the voice model); every on-screen word uses them.
 * Every sound effect is registered with cue() next to the visual event it belongs to, and
 * render/cues.mjs exports the list for the mix, so picture and sound share one source.
 */
(function () {
  'use strict';
  gsap.config({ force3D: false });

  const BPM = NARRATION.bpm;
  const BEAT = 60 / BPM;
  const BAR = 4 * BEAT;
  const bar = (b, beat = 1) => (b - 1) * BAR + (beat - 1) * BEAT;
  const END = bar(36); // 75.0 s

  const $ = (s, r = document) => r.querySelector(s);
  const el = (tag, cls, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  };
  const SEG = (id) => NARRATION.segments.find((s) => s.id === id);
  const words = (id) => SEG(id).words;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const smooth = (a, b, v) => { const x = clamp((v - a) / (b - a), 0, 1); return x * x * (3 - 2 * x); };

  const tl = gsap.timeline({ paused: true });
  const R = []; // per-frame renderers: (t) => void
  const CUES = [];
  const cue = (name, t, extra = {}) => CUES.push({ name, t: +t.toFixed(4), ...extra });

  // discrete changes (text, classes) picked by time on every frame
  function schedule(list, apply) {
    let last;
    R.push((t) => {
      let v = list[0][1];
      for (const [tt, val] of list) if (tt <= t) v = val;
      if (v !== last) { apply(v); last = v; }
    });
  }

  // ---------- real TourCode UI in a shadow root ----------
  function ui(name, zoom = 1) {
    const st = UI_STATES[name];
    if (!st) throw new Error('no UI state ' + name);
    const host = el('div', 'ui-host');
    const root = host.attachShadow({ mode: 'open' });
    root.innerHTML = `<style>${UI_CSS}
      .wv-body{position:relative}
      .term-tooltip{position:absolute}
      *{transition:none!important;animation:none!important}</style>
      <div class="wv-body" data-surface="${st.surface}" style="width:${st.width}px">${st.html}</div>`;
    host.style.zoom = zoom;
    host.q = (s) => root.querySelector(s);
    host.qa = (s) => [...root.querySelectorAll(s)];
    host.body = root.querySelector('.wv-body');
    host.stateName = name;
    return host;
  }
  const byText = (host, sel, text) => host.qa(sel).find((n) => n.textContent.trim().startsWith(text));
  const rect = (node) => { const r = node.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height, cx: r.left + r.width / 2, cy: r.top + r.height / 2, r: r.right, b: r.bottom }; };

  // camera: put cam point P at screen centre (+ offset) at scale s
  const cam = (P, s, o = {}) => ({
    x: -s * (P.x - 960) + (o.dx || 0), y: -s * (P.y - 540) + (o.dy || 0), scale: s,
    rotationX: o.rx || 0, rotationY: o.ry || 0,
  });

  // ---------- words in sync with the voice ----------
  function wordSpans(container, list, cls = 'w', accent = []) {
    return list.map((w, i) => {
      const s = el('span', cls + (accent.includes(i) ? ' acc' : ''), w.word + (i < list.length - 1 ? ' ' : ''));
      container.appendChild(s);
      return s;
    });
  }
  function wordsIn(spans, list, o = {}) {
    spans.forEach((s, i) => {
      tl.fromTo(s, { opacity: 0, y: o.y ?? 22, filter: `blur(${o.blur ?? 10}px)`, scale: o.scale ?? 1 },
        { opacity: 1, y: 0, filter: 'blur(0px)', scale: 1, duration: o.dur ?? 0.42, ease: o.ease || 'expo.out' },
        list[i].start - (o.lead ?? 0.04));
    });
  }
  // ---------- kinetic key words ----------
  /* Only the important words, set large in Instrument Serif. Each word appears as it is
     spoken: its letters rise out of a mask one by one with a small 3D turn and a blur that
     clears; italic marks the heart of the phrase. A soft shade sits behind words that
     land over the UI. */
  const titles = $('#titles');
  function kinetic({ lines, x = 120, y = null, bottom = null, center = false, out = null, shade = false, parent = titles, lead = 0.06 }) {
    const box = el('div', 'kt' + (center ? ' center' : ''));
    if (!center) box.style.left = x + 'px';
    if (y != null) box.style.top = y + 'px';
    if (bottom != null) box.style.bottom = bottom + 'px';
    const sh = shade ? el('div', 'kt-shade') : null;
    if (sh) parent.appendChild(sh);
    parent.appendChild(box);
    const wordEls = [];
    let first = Infinity;
    for (const L of lines) {
      const line = el('div', 'kl');
      line.style.fontSize = L.size + 'px';
      if (L.gap) line.style.marginTop = L.gap + 'px';
      box.appendChild(line);
      const list = words(L.seg);
      L.words.forEach((wi, k) => {
        const w = list[wi];
        const text = (L.text && L.text[wi]) || w.word;
        const wEl = el('span', 'kw' + (L.it && L.it.includes(wi) ? ' it' : ''));
        const chars = [...text].map((ch) => { const c = el('span', 'kc', ch); wEl.appendChild(c); return c; });
        line.appendChild(wEl);
        if (k < L.words.length - 1) line.appendChild(document.createTextNode(' '));
        const t = w.start - lead;
        first = Math.min(first, t);
        gsap.set(chars, { yPercent: 112, rotationX: -75, opacity: 0, filter: 'blur(12px)' });
        tl.to(chars, { yPercent: 0, rotationX: 0, opacity: 1, filter: 'blur(0px)', duration: 0.95, ease: 'expo.out', stagger: 0.028 }, t);
        wordEls.push(wEl);
      });
    }
    if (sh) {
      tl.to(sh, { opacity: 1, duration: 0.5, ease: 'power2.out' }, first - 0.2);
      if (out != null) tl.to(sh, { opacity: 0, duration: 0.55, ease: 'power2.inOut' }, out + 0.1);
    }
    // the exit moves the words, not their letters, so a letter still settling never fights it
    if (out != null) tl.to(wordEls, { y: -36, opacity: 0, filter: 'blur(10px)', duration: 0.5, ease: 'power3.in', stagger: 0.035 }, out);
    return box;
  }

  // ---------- cursor ----------
  function cursor(node) {
    const c = node;
    gsap.set(c, { x: 0, y: 0, opacity: 0, '--ring': 0, '--ring-s': 0.4 });
    return {
      show(t, p) { tl.set(c, { x: p.x, y: p.y }, t); tl.to(c, { opacity: 1, duration: 0.2 }, t); },
      move(t, p, d = 0.55) { tl.to(c, { x: p.x, y: p.y, duration: d, ease: 'power3.inOut' }, t); },
      click(t, sound = 'click') {
        tl.to(c, { scale: 0.86, duration: 0.07, ease: 'power2.out', transformOrigin: '2px 2px' }, t - 0.04);
        tl.to(c, { scale: 1, duration: 0.18, ease: 'power2.out' }, t + 0.04);
        tl.fromTo(c, { '--ring': 0.9, '--ring-s': 0.4 }, { '--ring': 0, '--ring-s': 1.25, duration: 0.45, ease: 'power2.out', immediateRender: false }, t);
        if (sound) cue(sound, t);
      },
      hide(t) { tl.to(c, { opacity: 0, duration: 0.25 }, t); },
    };
  }

  // ---------- state stacks: one host per UI state, cross-faded ----------
  function stack(container, names, zoom = 1) {
    const hosts = {};
    const scroller = el('div', 'scroller');
    scroller.style.position = 'absolute';
    scroller.style.left = '0'; scroller.style.top = '0';
    container.appendChild(scroller);
    for (const n of names) {
      const h = ui(n, zoom);
      gsap.set(h, { opacity: 0 });
      scroller.appendChild(h);
      hosts[n] = h;
    }
    let current = null;
    return {
      hosts, scroller,
      show(name, t, fade = 0.22) {
        const h = hosts[name];
        if (current && current !== h) {
          const prev = current;
          if (fade > 0) tl.to(prev, { opacity: 0, duration: fade, ease: 'none' }, t);
          else tl.set(prev, { opacity: 0 }, t);
        }
        if (fade > 0) tl.to(h, { opacity: 1, duration: fade, ease: 'none' }, t);
        else tl.set(h, { opacity: 1 }, t);
        current = h;
      },
      init(name) { gsap.set(hosts[name], { opacity: 1 }); current = hosts[name]; },
    };
  }

  // ---------- code editor ----------
  const KW = new Set(['export', 'async', 'function', 'const', 'let']);
  const CTRL = new Set(['import', 'from', 'return', 'if', 'await']);
  const TYPES = new Set(['string', 'boolean', 'Date']);
  const LIT = new Set(['undefined', 'true', 'false']);
  function highlight(line) {
    const out = [];
    const re = /("[^"]*")|([A-Za-z_$][\w$]*)|(\s+)|(.)/g;
    let m, prev = '';
    while ((m = re.exec(line))) {
      const [tok, str, id, ws] = m;
      const esc = tok.replace(/&/g, '&amp;').replace(/</g, '&lt;');
      let cls = 'tk-p';
      if (str) cls = 'tk-s';
      else if (id) {
        const next = line.slice(re.lastIndex).trimStart()[0];
        if (KW.has(id) || LIT.has(id)) cls = 'tk-k';
        else if (CTRL.has(id)) cls = 'tk-c';
        else if (TYPES.has(id)) cls = 'tk-t';
        else if (next === '(') cls = 'tk-f';
        else cls = 'tk-v';
      } else if (ws) cls = '';
      out.push(cls ? `<span class="${cls}">${esc}</span>` : esc);
      if (!ws) prev = tok;
    }
    return out.join('');
  }
  function codeLines(file) {
    const box = el('div', 'lines');
    DEMO.code[file].forEach((src, i) => {
      const ln = el('div', 'ln', `<span class="no">${i + 1}</span>${highlight(src)}`);
      box.appendChild(ln);
    });
    return box;
  }

  // ---------- small svg helpers ----------
  const SVGNS = 'http://www.w3.org/2000/svg';
  function svgEl(tag, attrs, parent) {
    const e = document.createElementNS(SVGNS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function drawPath(p, t, d, ease = 'power2.inOut') {
    const L = p.getTotalLength();
    gsap.set(p, { strokeDasharray: `${L} ${L + 2}`, strokeDashoffset: L, opacity: 0 });
    tl.set(p, { opacity: 1 }, t);
    tl.to(p, { strokeDashoffset: 0, duration: d, ease }, t);
    return L;
  }
  // a route through points with rounded corners (the logo's line)
  function routeD(pts, r = 22) {
    let d = `M ${pts[0][0]} ${pts[0][1]}`;
    for (let i = 1; i < pts.length - 1; i++) {
      const [x0, y0] = pts[i - 1], [x1, y1] = pts[i], [x2, y2] = pts[i + 1];
      const l1 = Math.hypot(x1 - x0, y1 - y0), l2 = Math.hypot(x2 - x1, y2 - y1);
      const rr = Math.min(r, l1 / 2, l2 / 2);
      const ax = x1 - ((x1 - x0) / l1) * rr, ay = y1 - ((y1 - y0) / l1) * rr;
      const bx = x1 + ((x2 - x1) / l2) * rr, by = y1 + ((y2 - y1) / l2) * rr;
      d += ` L ${ax} ${ay} Q ${x1} ${y1} ${bx} ${by}`;
    }
    const last = pts[pts.length - 1];
    return d + ` L ${last[0]} ${last[1]}`;
  }
  function monoMark(key, size) {
    const L = LOGOS[key];
    const m = el('div', 'mono-mark');
    m.style.width = m.style.height = size + 'px';
    if (L.png) {
      m.innerHTML = `<img src="${L.png}" alt="">`;
    } else {
      m.innerHTML = `<svg viewBox="${L.viewBox}" fill-rule="${L.rule}">${L.paths.map((d) => `<path d="${d}" fill-rule="${L.rule}" clip-rule="${L.rule}"/>`).join('')}</svg>`;
    }
    return m;
  }

  // =====================================================================================
  //  BUILD THE DOM (everything that needs measuring)
  // =====================================================================================

  // ---- 1 · hook planes ----
  const field = $('.hook-field');
  const snippets = (() => {
    const c = DEMO.code;
    const all = [...c.auth, '', ...c.password, '', ...c.session];
    const tree = ['acme-shop/', '  .tourcode/tours/', '  src/', '    auth.ts', '    cart.ts', '    catalog.ts', '    db.ts', '    password.ts', '    routes.ts', '    session.ts', '  tests/', '  package.json'];
    const out = [];
    for (let i = 0; i < 14; i++) {
      const a = (i * 5) % all.length;
      out.push(all.slice(a, a + 7 + (i % 4)).map((l) => highlight(l).replace(/tk-k|tk-c/g, 'k').replace(/tk-f/g, 'f').replace(/tk-s/g, 's').replace(/tk-[a-z]/g, 'x')).join('\n'));
    }
    out.push(tree.slice(0, 7).join('\n'), tree.slice(4).join('\n'));
    return out;
  })();
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const planes = [];
  const ZFAR = -4200, ZNEAR = 650, ZR = ZNEAR - ZFAR;
  for (let i = 0; i < 44; i++) {
    const p = el('div', 'plane', snippets[i % snippets.length]);
    field.appendChild(p);
    let x = (rnd() * 2 - 1) * 1500, y = (rnd() * 2 - 1) * 820;
    if (Math.abs(x) < 380 && Math.abs(y) < 260) x += x < 0 ? -420 : 420; // keep the words clear
    planes.push({ node: p, x, y, z0: ZFAR + (i / 44) * ZR, rot: (rnd() * 2 - 1) * 8 });
  }

  // ---- 2 · prompt ----
  const promptSlash = $('#prompt .slash'), promptRest = $('#prompt .rest'), caret = $('#prompt .caret');

  // ---- 3 · explorer ----
  const explorer = $('#explorer');
  explorer.appendChild(el('div', 'ex-title', 'EXPLORER'));
  const ROWS = [
    [0, 'folder', 'acme-shop', true], [1, 'folder', '.tourcode', false], [1, 'folder', 'src', true],
    [2, 'ts', 'auth.ts'], [2, 'ts', 'cart.ts'], [2, 'ts', 'catalog.ts'], [2, 'ts', 'db.ts'],
    [2, 'ts', 'password.ts'], [2, 'ts', 'routes.ts'], [2, 'ts', 'session.ts'],
    [1, 'folder', 'tests', false], [1, 'json', 'package.json'], [1, 'md', 'README.md'],
  ];
  const rowEls = {};
  for (const [d, kind, name, open] of ROWS) {
    const r = el('div', 'row');
    r.style.setProperty('--d', d);
    const chev = kind === 'folder' ? (open ? '⌄' : '›') : '';
    const ico = kind === 'ts' ? '<span class="ico">TS</span>' : kind === 'json' ? '<span class="ico" style="color:#CBCB41">{ }</span>'
      : kind === 'md' ? '<span class="ico" style="color:#519ABA">M↓</span>' : '';
    r.innerHTML = `<span class="lit"></span><span class="txt"><span class="chev">${chev}</span>${ico}${name}</span><span class="read">✓</span>`;
    explorer.appendChild(r);
    rowEls[name] = r;
  }

  // ---- 4 · map ----
  const mapWin = $('#map-window');
  const mapHost = ui('map', 1.25);
  $('.map-body', mapWin).appendChild(mapHost);

  // ---- 5/6 · editor ----
  const editor = $('#editor');
  const act = $('.activity', editor);
  const ICONS = {
    files: '<path d="M6 3h7l5 5v13H6z M13 3v5h5" />',
    search: '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/>',
    git: '<circle cx="6" cy="5" r="2.2"/><circle cx="6" cy="19" r="2.2"/><circle cx="18" cy="9" r="2.2"/><path d="M6 7.2v9.6M18 11.2c0 4-6 3-11 6"/>',
    ext: '<path d="M4 9h6V3H4zM4 20h6v-6H4zM14 20h6v-6h-6zM14 4l4.2 4.2-4.2 4.2-4.2-4.2z"/>',
    tour: '<circle cx="5.5" cy="18.5" r="2.5"/><path d="M8 18.5h6.5a3.5 3.5 0 0 0 0-7h-5a3.5 3.5 0 0 1 0-7H16"/><path d="M15.5 2l3 2.5-3 2.5"/>',
  };
  ['files', 'search', 'git', 'ext', 'tour'].forEach((k, i) => {
    const a = el('div', 'ai' + (k === 'tour' ? ' on' : ''),
      `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="${k === 'tour' ? '#E6E6E6' : '#C5C5C5'}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${ICONS[k]}</svg>`);
    a.style.top = (14 + i * 48) + 'px';
    act.appendChild(a);
  });
  const sb = stack($('#sb-stack'), ['sb-tour-0', 'sb-tour-1', 'sb-tour-2', 'sb-subtour'], 1);
  const panelNames = ['step1', 'step2', 'step3', 'step1-answering-0', 'step1-answering-1', 'step1-answering-2', 'step1-answering-3',
    'step1-answering-4', 'step1-answered', 'step1-answered-risks', 'subtour'];
  const pn = stack($('#panel-stack'), panelNames, 1);
  const codeBox = $('#code');
  const files = { auth: codeLines('auth'), password: codeLines('password'), session: codeLines('session') };
  for (const k in files) { codeBox.appendChild(files[k]); gsap.set(files[k], { opacity: k === 'auth' ? 1 : 0 }); }
  const band = el('div', 'band');
  codeBox.insertBefore(band, codeBox.firstChild);
  const riskDot = el('div', 'risk-dot'); codeBox.appendChild(riskDot);
  const riskNote = el('div', 'risk-note', '<b>Low · Breaks on change</b>&nbsp; this guard relies on that (no await)');
  codeBox.appendChild(riskNote);
  const crumbs = $('#crumbs');
  const tabName = $('#code-tab .name');
  const LH = 24, LTOP = 12;
  const lineY = (n) => LTOP + (n - 1) * LH; // inside .code
  const setBand = (a, b) => ({ top: lineY(a), height: (b - a + 1) * LH });
  gsap.set(band, { ...setBand(4, 10), opacity: 0 });
  const edCursor = cursor($('#cursor-ed'));
  const pathRing = el('div', 'hl-ring'); $('#s5 .cam').appendChild(pathRing);

  // ---- 7 · home ----
  const home = stack($('#home-stack'), ['sb-home-unpinned-stale', 'sb-home-stale', 'sb-home'], 1.6);
  const homeWin = $('#home-window');
  const homeCursor = cursor($('#cursor-home'));

  // ---- 8 · export ----
  const exWin = $('#export-window');
  const ex = stack($('#export-stack'), ['sb-home', 'sb-tour-0'], 1.6);
  ex.init('sb-home');
  const exCursor = cursor($('#cursor-export'));
  // the exported page (assets/tours/how-login-works.page.html), its real DOM and CSS
  const PZ = 1060 / 1280; // 1280×800 → 1060×662.5
  const pageFrame = $('#page-frame');
  const pageHost = el('div', 'ui-host');
  {
    const r = pageHost.attachShadow({ mode: 'open' });
    r.innerHTML = `<style>${PAGE_CSS}.pg-body{width:1280px;height:800px;position:relative;overflow:hidden}.step-list{overflow:visible}.step-list-item{white-space:nowrap}*{transition:none!important}</style><div class="pg-body">${UI_STATES['export-page'].html}</div>`;
    pageHost.q = (q) => r.querySelector(q);
    pageHost.qa = (q) => [...r.querySelectorAll(q)];
  }
  pageHost.style.zoom = PZ;
  pageFrame.insertBefore(pageHost, pageFrame.firstChild);
  const wikiMark = (size) => {
    const m = el('div', 'mono-mark', '<svg viewBox="0 0 24 24" style="fill:none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H11v18H5.5A1.5 1.5 0 0 1 4 19.5z"/><path d="M20 4.5A1.5 1.5 0 0 0 18.5 3H13v18h5.5a1.5 1.5 0 0 0 1.5-1.5z"/></svg>');
    m.style.width = m.style.height = size + 'px';
    return m;
  };
  const DEST = [
    { key: 'confluence', label: 'Confluence', word: 7, x: 1250, y: 112 },
    { key: 'notion', label: 'Notion', word: 8, x: 1335, y: 380 },
    { key: null, label: 'Your wiki', word: 11, x: 1250, y: 648 },
  ];
  const apps = DEST.map((d) => {
    const w = el('div', 'app');
    w.style.left = d.x + 'px'; w.style.top = d.y + 'px';
    const head = el('div', 'app-bar');
    head.append(d.key ? monoMark(d.key, 22) : wikiMark(22), el('span', 'app-name', d.label));
    const body = el('div', 'app-body',
      '<div class="sk"><i style="width:58%"></i><i style="width:90%"></i><i style="width:76%"></i><i style="width:84%"></i><i style="width:44%"></i></div>'
      + '<div class="app-doc"><img src="assets/export-page.png" alt=""></div>'
      + '<div class="app-ok"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="#0D1117" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 8.5l3 3 6-7"/></svg></div>');
    w.append(head, body);
    $('#dest').appendChild(w);
    return w;
  });

  // ---- 9 · rows ----
  const rows = $('#rows');
  const ROWDEF = [
    { label: [0, 2], y: 215, items: [['vscode', 'VS Code'], ['cursor', 'Cursor'], ['kiro', 'Kiro'], ['windsurf', 'Windsurf']] },
    { label: [2, 4], y: 445, items: [['claude', 'Claude Code'], ['cursor', 'Cursor'], ['kiro', 'Kiro']] },
    { label: [4, 7], y: 675, items: [['jupyter', 'Jupyter']] },
  ];
  const rowNodes = ROWDEF.map((r) => {
    const row = el('div', 'lrow');
    row.style.top = r.y + 'px';
    const lab = el('div', 'label');
    row.appendChild(lab);
    const items = r.items.map(([k, name], i) => {
      const it = el('div', 'logo-item');
      it.style.left = (860 + i * 235) + 'px';
      it.appendChild(monoMark(k, 84));
      it.appendChild(el('div', 'name', name));
      row.appendChild(it);
      return it;
    });
    rows.appendChild(row);
    return { row, lab, items };
  });

  // ---- 10 · final ----

  // =====================================================================================
  //  MEASURE, THEN ANIMATE
  // =====================================================================================
  async function build() {
    // load every face the film's typography uses before anything is measured
    const cs = getComputedStyle(document.documentElement);
    const fams = ['--display', '--caption', '--code', '--accent'].map((v) => cs.getPropertyValue(v).trim()).filter((f) => f && f !== 'inherit');
    await Promise.all(fams.flatMap((f) => ['400', '500', '600', '700', 'italic 400'].map((w) => document.fonts.load(`${w} 40px ${f}`).catch(() => null))));
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => (i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
    document.querySelectorAll('.scene').forEach((s) => (s.style.visibility = 'visible'));

    // ---- measurements (all cameras at identity) ----
    promptSlash.textContent = '/tour'; promptRest.textContent = ' how does login work';
    const promptEnd = rect(caret);
    promptSlash.textContent = ''; promptRest.textContent = '';

    const mapNodes = mapHost.qa('.overview-node').map(rect);
    const mapEdges = mapHost.qa('.overview-edge');
    const mapEdgeBox = rect(mapHost.q('.overview-edges'));
    const mapNode1 = mapNodes[0];
    const mapNodesBox = {
      x: Math.min(...mapNodes.map((r) => r.x)), y: mapNodes[0].y,
      r: Math.max(...mapNodes.map((r) => r.r)), b: mapNodes[3].b,
    };
    const mapCenter = { x: (mapNodesBox.x + mapNodesBox.r) / 2, y: (mapNodesBox.y + mapNodesBox.b) / 2 };
    const rowRect = (n) => rect(rowEls[n]);
    const codeR = rect(codeBox);
    const lineCam = (n) => ({ x: codeR.x + 300, y: codeR.y + lineY(n) + LH / 2 });
    const panelR = rect($('#panel-stack'));
    const sbR = rect($('#sb-stack'));
    const H = (n) => pn.hosts[n];
    const line6End = rect(files.auth.children[5].lastElementChild).r - codeR.x;
    const nextBtn = rect(H('step1').q('.step-page-controls .button-primary'));
    const chip = rect(H('step1').q('.ask-suggestion'));
    const askTop = rect(H('step1').q('.ask')).y;
    const risksBtnA = rect(H('step1-answered').q('.risks-toggle'));
    const deeperBtn = rect(byText(H('step1-answered-risks'), '.step-page-toggles button', 'Explain deeper'));
    const termEl = H('step3').q('.step-page-lead .term');
    const term = rect(termEl);
    const step3Body = rect(H('step3').body);
    const pathBox = rect(sb.hosts['sb-subtour'].q('.path'));
    const pathSection = pathBox;
    const home0 = home.hosts['sb-home-unpinned-stale'], home1 = home.hosts['sb-home-stale'], home2 = home.hosts['sb-home'];
    const cardA = byText(home0, '.tour-card', 'How login works');
    const cardB = byText(home1, '.tour-card', 'How login works');
    const toursTitle = rect(byText(home0, '.section-title', 'Tours in this project'));
    const homeStackR = rect($('#home-stack'));
    const cardAR = rect(cardA), cardBR = rect(cardB);
    const rebuildBtn = rect(home1.q('.tour-card-stale .link-button'));
    const exportLink = byText(ex.hosts['sb-tour-0'], '.link-button', 'Export');
    const exportR = rect(exportLink);
    // flip sources (the tour sidebar) and targets (the page at its final size)
    const tourHost = ex.hosts['sb-tour-0'];
    const fontPx = (n, zoom) => parseFloat(getComputedStyle(n).fontSize) * zoom;
    const srcOf = (n) => ({ ...rect(n), font: fontPx(n, 1.6) });
    const flipSrc = {
      title: srcOf(tourHost.q('.tour-title')),
      map: srcOf(tourHost.q('.overview-button')),
      steps: tourHost.qa('.steps-item .step .step-title').slice(0, 4).map(srcOf),
    };
    Object.assign(pageFrame.style, { left: '760px', top: '196px', width: '1060px', height: '662.5px' });
    const pageFinal = new Map();
    for (const n of [pageHost.q('.header-title'), ...pageHost.qa('.step-list-item')]) {
      const r = rect(n);
      const cs = getComputedStyle(n);
      pageFinal.set(n, { lx: r.x - 760 - 1, ly: r.y - 196 - 1, h: r.h, w: r.w, font: parseFloat(cs.fontSize) * PZ,
        padL: parseFloat(cs.paddingLeft) * PZ, padT: parseFloat(cs.paddingTop) * PZ });
    }
    Object.assign(pageFrame.style, { left: '1150px', top: '160px', width: '578px', height: '690px' });
    const logo = $('#logo');
    const rPath = $('.r-path', logo), rHead = $('.r-head', logo), rDot = $('.r-dot', logo);

    // =================================================================================
    // 1 · HOOK  0:00 – bar 4
    // =================================================================================
    // speed of the flight: slow → fast → tape stop
    const vel = (t) => (t < 4.75 ? 140 + 2300 * Math.pow(t / 4.75, 2.2) : t < 5.55 ? 2440 * Math.pow(1 - (t - 4.75) / 0.8, 2) : 0);
    const DIST = []; { let d = 0; for (let i = 0; i <= 7000; i++) { DIST.push(d); d += vel(i / 1000) / 1000; } }
    const dist = (t) => DIST[clamp(Math.round(t * 1000), 0, 7000)];
    const FOCUS = -700;
    R.push((t) => {
      if (t > bar(4) + 0.1) return;
      const D = dist(t);
      const dim = 1 - smooth(5.0, 5.9, t);
      for (const p of planes) {
        let z = p.z0 + D;
        z = ((z - ZFAR) % ZR + ZR) % ZR + ZFAR;
        const op = smooth(ZFAR, ZFAR + 1500, z) * (1 - smooth(300, ZNEAR, z)) * 0.85 * dim;
        const blur = Math.min(9, Math.abs(z - FOCUS) / 260);
        p.node.style.transform = `translate3d(${p.x}px, ${p.y}px, ${z}px) rotateY(${p.rot}deg)`;
        p.node.style.opacity = op.toFixed(3);
        p.node.style.filter = `blur(${blur.toFixed(2)}px)`;
      }
    });
    $('#s1').style.perspective = '1100px';
    kinetic({ center: true, y: 330, out: 3.22, lines: [
      { seg: 's1a', words: [2, 3], text: { 2: 'A' }, size: 132 },
      { seg: 's1a', words: [4, 5, 6], it: [4, 5, 6], size: 132 },
    ] });
    const hookQ = kinetic({ center: true, y: 300, out: 5.98, lines: [
      { seg: 's1b', words: [0, 1, 2], size: 176 },
      { seg: 's1b', words: [3, 4], it: [3, 4], size: 176 },
    ] });
    tl.to(hookQ, { scale: 0.965, duration: 1.1, ease: 'sine.inOut' }, 4.9);
    tl.fromTo('#s1 .cam', { scale: 1 }, { scale: 1.05, duration: 5.6, ease: 'none' }, 0);
    cue('hook_riser', 0.0, { dur: 4.95 });
    [1.05, 2.35, 3.4, 4.25].forEach((t, i) => cue('rush', t, { i }));
    cue('tape_stop', 4.85);
    cue('thud', 5.55);

    // =================================================================================
    // 2 · THE COMMAND  bar 4 – bar 7
    // =================================================================================
    const s2 = bar(4);
    gsap.set('#prompt', { opacity: 0, y: 30, scale: 0.97 });
    tl.to('#prompt', { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: 'expo.out' }, s2 + 0.05);
    kinetic({ center: true, y: 268, out: bar(6) + 0.5, lines: [
      { seg: 's2', words: [0, 1, 2, 3], it: [2, 3], text: { 3: 'agent.' }, size: 104 },
    ] });
    cue('cut_soft', s2);
    // typing: "/tour" on "slash tour", then each word across its own spoken time
    const sw = words('s2');
    const typed = [];
    const push = (txt, a, b, target) => { const n = txt.length; for (let i = 0; i < n; i++) typed.push({ t: a + ((b - a) * i) / Math.max(1, n), ch: txt[i], target }); };
    push('/', sw[4].start, sw[4].start + 0.05, 'slash');
    push('tour', sw[5].start, sw[5].end - 0.05, 'slash');
    push(' how', sw[6].start - 0.05, sw[6].end, 'rest');
    push(' does', sw[7].start - 0.03, sw[7].end, 'rest');
    push(' login', sw[8].start - 0.03, sw[8].end, 'rest');
    push(' work', sw[9].start - 0.03, sw[9].end - 0.08, 'rest');
    typed.forEach((k) => { if (k.ch !== ' ') cue('key', k.t); });
    const typeStart = typed[0].t, typeEnd = typed[typed.length - 1].t;
    const ENTER = bar(6);
    R.push((t) => {
      if (t < s2 - 0.1 || t > bar(7) + 0.1) return;
      let a = '', b = '';
      for (const k of typed) { if (k.t <= t) { if (k.target === 'slash') a += k.ch; else b += k.ch; } }
      promptSlash.textContent = a; promptRest.textContent = b;
      const typing = t >= typeStart - 0.3 && t <= typeEnd + 0.25;
      const on = t >= ENTER ? 0 : typing ? 1 : (Math.floor((t - s2) / BEAT) % 2 === 0 ? 1 : 0);
      caret.style.opacity = on;
    });
    tl.fromTo('#s2 .cam', cam({ x: 960, y: 540 }, 1), { ...cam({ x: 960, y: 540 }, 1.1), duration: ENTER - s2, ease: 'sine.inOut' }, s2);
    // Enter: the command turns green
    tl.to('#prompt .prompt-text', { color: '#3FB950', textShadow: '0 0 28px rgba(63,185,80,.55)', duration: 0.28, ease: 'power2.out' }, ENTER);
    tl.to('#prompt .slash', { color: '#3FB950', duration: 0.28 }, ENTER);
    tl.to('#prompt', { borderColor: 'rgba(63,185,80,.55)', boxShadow: '0 30px 90px rgba(0,0,0,.5), 0 0 60px rgba(63,185,80,.18)', duration: 0.35 }, ENTER);
    cue('enter_pop', ENTER); cue('shimmer', ENTER + 0.03);
    // the route line leaves the command and leads the camera to the next scene
    const r2 = $('#cmd-route');
    const y2 = promptEnd.cy;
    const startX = promptEnd.r + 28;
    const dot2 = svgEl('circle', { cx: startX, cy: y2, r: 8 }, r2);
    const glow2 = svgEl('path', { d: `M ${startX + 8} ${y2} L 3400 ${y2}`, class: 'glow' }, r2);
    const line2 = svgEl('path', { d: `M ${startX + 8} ${y2} L 3400 ${y2}` }, r2);
    gsap.set(dot2, { opacity: 0, scale: 0, svgOrigin: `${startX} ${y2}` });
    tl.to(dot2, { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(2)' }, ENTER + 0.25);
    drawPath(line2, ENTER + 0.4, 1.75, 'power2.in');
    drawPath(glow2, ENTER + 0.4, 1.75, 'power2.in');
    cue('line_swish', ENTER + 0.45);
    tl.to('#s2 .cam', { x: '-=1250', duration: bar(7) - (ENTER + 0.75), ease: 'power2.in' }, ENTER + 0.75);
    tl.to('#prompt', { opacity: 0.25, duration: 0.8 }, ENTER + 1.0);

    // =================================================================================
    // 3 · THE AGENT STUDIES THE CODE  bar 7 – bar 10
    // =================================================================================
    const s3 = bar(7);
    // the map space: identical to the tour map's first framing in scene 4
    const MAP0 = cam(mapCenter, 1.48, { dx: 340, dy: -10 });
    const mapspace = $('#mapspace');
    gsap.set(mapspace, { x: MAP0.x, y: MAP0.y, scale: MAP0.scale });
    const toScreen = (P) => ({ x: 960 + MAP0.x + MAP0.scale * (P.x - 960), y: 540 + MAP0.y + MAP0.scale * (P.y - 540) });
    // node clones at the map nodes' exact places
    const nodeHTML = mapHost.qa('.overview-node').map((n) => n.outerHTML);
    const stations = nodeHTML.map((h, i) => {
      const host = el('div', 'ui-host station');
      const root = host.attachShadow({ mode: 'open' });
      root.innerHTML = `<style>${UI_CSS}*{transition:none!important}</style><div class="wv-body" data-surface="overview" style="width:auto;padding:0;margin:0;background:transparent">${h}</div>`;
      host.style.left = mapNodes[i].x + 'px'; host.style.top = mapNodes[i].y + 'px';
      mapspace.appendChild(host);
      const btn = root.querySelector('.overview-node');
      btn.classList.remove('is-current'); btn.classList.add('is-ahead');
      host.btn = btn;
      return host;
    });
    schedule([[0, false], [bar(9, 2), true]], (on) => {
      stations[0].btn.classList.toggle('is-current', on);
      stations[0].btn.classList.toggle('is-ahead', !on);
    });
    // the route through the stations (centre line), in map space
    const msvg = svgEl('svg', { viewBox: '0 0 1920 1080' }, mapspace);
    const spine = svgEl('path', {
      d: `M ${mapNodes[0].cx} ${mapNodes[0].b} L ${mapNodes[3].cx} ${mapNodes[3].y}`,
      fill: 'none', stroke: '#3FB950', 'stroke-width': 2, 'stroke-linecap': 'round',
    }, msvg);
    mapspace.insertBefore(msvg, mapspace.firstChild);
    gsap.set(explorer, { opacity: 0, x: -40 });
    tl.to(explorer, { opacity: 1, x: 0, duration: 0.6, ease: 'expo.out' }, s3);
    const r3 = $('#s3-route');
    const srcRow = rowRect('src');
    const entry = svgEl('path', { d: routeD([[-60, y2], [100, y2], [100, srcRow.cy], [150, srcRow.cy]], 26) }, r3);
    drawPath(entry, s3, 0.55, 'expo.out');
    cue('line_swish', s3 + 0.02);
    // files light up, one per beat
    const lit = [['auth.ts', bar(7, 3)], ['password.ts', bar(7, 4)], ['session.ts', bar(8, 1)]];
    lit.forEach(([n, t], i) => {
      const r = rowEls[n];
      tl.to($('.lit', r), { opacity: 1, duration: 0.25, ease: 'power2.out' }, t);
      tl.to($('.txt', r), { color: '#FFFFFF', duration: 0.25 }, t);
      tl.fromTo($('.read', r), { opacity: 0, x: -6 }, { opacity: 1, x: 0, duration: 0.3, ease: 'back.out(2)' }, t + 0.12);
      cue('tick', t, { i });
    });
    // connectors from each file to its function, then the stations
    const links = [['auth.ts', 0, bar(8, 1) - 0.1], ['auth.ts', 1, bar(8, 2) - 0.1], ['password.ts', 2, bar(8, 3) - 0.1], ['session.ts', 3, bar(8, 4) - 0.1]];
    links.forEach(([file, ni, t], i) => {
      const fr = rowRect(file);
      const sp = toScreen({ x: mapNodes[ni].x, y: mapNodes[ni].cy });
      const lane = 690 + i * 22;
      const p = svgEl('path', { d: routeD([[622, fr.cy], [lane, fr.cy], [lane, sp.y], [sp.x - 6, sp.y]], 22), style: 'stroke-width:2.5;opacity:.85' }, r3);
      drawPath(p, t, 0.42, 'power2.inOut');
      cue('swish', t + 0.05, { i });
      const st = stations[ni];
      gsap.set(st, { opacity: 0, scale: 0.85, transformOrigin: '0% 50%' });
      tl.to(st, { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(1.8)' }, t + 0.36);
      cue('pop_soft', t + 0.38, { i });
    });
    // the route connects the stations, top to bottom
    drawPath(spine, bar(8, 4) + 0.45, 1.0, 'power2.inOut');
    cue('line_swish', bar(8, 4) + 0.5);
    tl.add(() => {}, bar(9));
    cue('select', bar(9, 2));
    tl.to(r3, { opacity: 0.35, duration: 1.2 }, bar(9, 1));
    tl.to(explorer, { opacity: 0.35, x: -30, duration: 1.6, ease: 'sine.inOut' }, bar(9, 1));
    kinetic({ x: 120, bottom: 118, out: bar(9, 4), lines: [
      { seg: 's3', words: [5, 6, 7], it: [6, 7], text: { 5: 'Finds', 7: 'route.' }, size: 136 },
    ] });

    // =================================================================================
    // 4 · THE REVEAL — TOUR MAP  bar 10 (the drop) – bar 14
    // =================================================================================
    const s4 = bar(10);
    const PULL = 21.95; // the camera holds on the map while the line is spoken, then pulls back
    const m4 = $('#s4 .cam');
    gsap.set(m4, MAP0);
    // the panel and everything but the nodes assemble around them
    const mapParts = [mapHost.q('.overview-header'), mapHost.q('.overview-summary'), mapHost.q('.overview-start'), mapHost.q('.section')];
    gsap.set(mapParts, { opacity: 0, y: 16 });
    gsap.set(mapWin, { backgroundColor: 'rgba(31,31,31,0)', borderColor: 'rgba(49,49,49,0)', boxShadow: '0 40px 120px rgba(0,0,0,0)' });
    gsap.set($('.tabstrip', mapWin), { opacity: 0 });
    gsap.set(mapHost.q('.overview'), { backgroundColor: 'transparent', borderColor: 'transparent' });
    const mapBodyBg = mapHost.body;
    gsap.set(mapBodyBg, { backgroundColor: 'rgba(31,31,31,0)' });
    const edgeLabels = mapHost.qa('.overview-edge-label');
    gsap.set(edgeLabels, { opacity: 0 });
    mapEdges.forEach((p, i) => drawPath(p, s4 + 0.05 + i * 0.12, 0.35, 'power2.out'));
    tl.to(edgeLabels, { opacity: 1, duration: 0.4, stagger: 0.12 }, s4 + 0.25);
    // green route overlay (continuity from scene 3), fades as the real edges settle
    const ov = svgEl('svg', { viewBox: '0 0 1920 1080', style: 'position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible' });
    m4.appendChild(ov);
    const spine4 = svgEl('path', { d: `M ${mapNodes[0].cx} ${mapNodes[0].b} L ${mapNodes[3].cx} ${mapNodes[3].y}`, fill: 'none', stroke: '#3FB950', 'stroke-width': 2 }, ov);
    tl.to(spine4, { opacity: 0, duration: 0.6 }, s4 + 0.25);
    cue('impact', s4);
    const glow = $('#reveal-glow');
    tl.fromTo(glow, { opacity: 0, scale: 0.6 }, { opacity: 0.75, scale: 1, duration: 0.35, ease: 'expo.out' }, s4);
    tl.to(glow, { opacity: 0.22, duration: 2.2, ease: 'sine.inOut' }, s4 + 0.4);
    tl.fromTo(mapHost.qa('.overview-node'), { scale: 1.06 }, { scale: 1, duration: 0.6, ease: 'expo.out', stagger: 0.05 }, s4);
    // pull back to the whole tab
    tl.to(m4, { scale: MAP0.scale * 1.025, x: MAP0.x * 1.025, y: MAP0.y * 1.025, duration: PULL - s4, ease: 'sine.inOut' }, s4);
    kinetic({ x: 120, y: 318, out: PULL - 0.15, lines: [
      { seg: 's4a', words: [0, 1, 2], text: { 2: 'map.' }, size: 150 },
      { seg: 's4a', words: [3, 4, 5], it: [3, 4, 5], text: { 3: 'The' }, size: 116, gap: 14 },
    ] });
    const MAPFULL = cam({ x: 960, y: 650 }, 0.88, { dy: -40, rx: 5 });
    tl.to(m4, { ...MAPFULL, duration: 1.6, ease: 'expo.inOut' }, PULL);
    cue('airy_whoosh', PULL);
    tl.to(mapWin, { backgroundColor: 'rgba(31,31,31,1)', borderColor: 'rgba(49,49,49,1)', boxShadow: '0 40px 120px rgba(0,0,0,.55)', duration: 0.9 }, PULL + 0.05);
    tl.to(mapBodyBg, { backgroundColor: 'rgba(31,31,31,1)', duration: 0.9 }, PULL + 0.05);
    tl.to(mapHost.q('.overview'), { borderColor: '#313131', duration: 0.9 }, PULL + 0.3);
    tl.to($('.tabstrip', mapWin), { opacity: 1, duration: 0.6 }, PULL + 0.2);
    tl.to(mapParts, { opacity: 1, y: 0, duration: 0.7, stagger: 0.12, ease: 'expo.out' }, PULL + 0.3);
    const routeItems = mapHost.qa('.route-item');
    gsap.set(routeItems, { opacity: 0, y: 10 });
    tl.to(routeItems, { opacity: 1, y: 0, duration: 0.5, stagger: BEAT / 4, ease: 'expo.out' }, bar(11, 4));
    routeItems.forEach((_, i) => cue('route_tick', bar(11, 4) + i * BEAT / 4, { i }));

    // "Each box leads to its step": box n and route item n glow together, one per beat
    const nodesEls = mapHost.qa('.overview-node');
    const steps = mapHost.qa('.route-step');
    words('s4b').length;
    for (let i = 0; i < 4; i++) {
      const t = bar(12, 1) + i * BEAT;
      if (i > 0) {
        tl.to(nodesEls[i], { borderColor: '#3FB950', boxShadow: '0 0 0 3px rgba(63,185,80,0.14)', duration: 0.18 }, t);
        tl.to(nodesEls[i], { borderColor: '#313131', boxShadow: '0 0 0 0px rgba(63,185,80,0)', duration: 0.5 }, t + 0.45);
      }
      tl.to(steps[i], { backgroundColor: 'rgba(63,185,80,0.14)', duration: 0.18 }, t);
      if (i > 0) tl.to(steps[i], { backgroundColor: 'rgba(63,185,80,0)', duration: 0.5 }, t + 0.45);
      cue('node_ping', t, { i });
    }

    // dive into box 1
    const mapCursor = el('div', 'cursor'); m4.appendChild(mapCursor);
    const mc = cursor(mapCursor);
    mc.show(bar(13, 1), { x: mapNode1.r + 120, y: mapNode1.b + 120 });
    mc.move(bar(13, 1) + 0.05, { x: mapNode1.cx - 30, y: mapNode1.cy + 2 }, 0.75);
    mc.click(bar(13, 3));
    mc.hide(bar(13, 3) + 0.2);
    const DIVE = bar(13, 3) + 0.08;
    tl.to(m4, { ...cam({ x: mapNode1.cx, y: mapNode1.cy }, 5.5), duration: bar(14) - DIVE, ease: 'expo.in' }, DIVE);
    tl.to(mapHost, { filter: 'blur(3px)', duration: 0.5, ease: 'power2.in' }, bar(14) - 0.5);
    cue('deep_swoosh', DIVE);

    const xfer = $('#xfer');
    const XF0 = bar(14) - 0.32;

    // =================================================================================
    // 5 · STEP BY STEP  bar 14 – bar 19
    // =================================================================================
    const s5 = bar(14);
    const c5 = $('#s5 .cam');
    sb.init('sb-tour-0');
    pn.init('step1');
    gsap.set($('#panel-stack'), { opacity: 0, y: 70 });
    gsap.set($('.panel-title', editor), { opacity: 0 });
    gsap.set(files.auth.children, { opacity: 0 });
    const S5A = cam(lineCam(7), 1.55, { dx: 0, dy: 0 });
    gsap.set(c5, S5A);
    tl.set(band, { opacity: 1 }, s5 + 0.55);
    schedule([[0, false], [s5 + 0.55, true]], (on) => codeBox.classList.toggle('focus', on));
    cue('chime', s5 + 0.08);
    // the file opens around the lit lines
    [...files.auth.children].forEach((ln, i) => {
      const d = Math.abs(i + 1 - 7);
      tl.to(ln, { opacity: 1, duration: 0.35, ease: 'power1.out' }, s5 + 0.35 + d * 0.06);
    });
    gsap.set(editor, { backgroundColor: '#1F1F1F' });
    // pull back to the whole editor, the explanation rises under the code
    const S5B = cam({ x: 990, y: 500 }, 1.03, { ry: -6, rx: 3 });
    tl.to(c5, { ...S5B, duration: 2.2, ease: 'expo.inOut' }, bar(14, 3));
    cue('airy_whoosh', bar(14, 3) + 0.1, { soft: 1 });
    tl.to($('.panel-title', editor), { opacity: 1, duration: 0.4 }, bar(15, 2));
    tl.to($('#panel-stack'), { opacity: 1, y: 0, duration: 0.8, ease: 'expo.out' }, bar(15, 2));
    cue('panel_rise', bar(15, 2));
    kinetic({ x: 120, bottom: 110, shade: true, out: words('s5b')[0].start - 0.75, lines: [
      { seg: 's5a', words: [0, 1, 2], it: [1, 2], text: { 2: 'step.' }, size: 150 },
    ] });
    kinetic({ x: 120, bottom: 104, shade: true, out: bar(18, 1) - 0.25, lines: [
      { seg: 's5b', words: [0, 1, 2], text: { 2: 'lines,' }, size: 128 },
      { seg: 's5b', words: [5], it: [5], text: { 5: 'explained.' }, size: 128 },
    ] });
    // step 2: Next → lines 12–15
    edCursor.show(bar(15, 4), { x: nextBtn.cx + 140, y: nextBtn.cy + 160 });
    edCursor.move(bar(15, 4) + 0.02, { x: nextBtn.cx - 4, y: nextBtn.cy + 2 }, 0.45);
    const N2 = bar(16, 1);
    edCursor.click(N2);
    tl.to(band, { ...setBand(12, 15), duration: 0.45, ease: 'expo.inOut' }, N2 + 0.02);
    pn.show('step2', N2 + 0.05, 0.25);
    sb.show('sb-tour-1', N2 + 0.05, 0.25);
    cue('chime', N2 + 0.3);
    cue('prog_tick', N2 + 0.1);
    tl.to(c5, { ...cam({ x: 1130, y: 480 }, 1.18, { ry: -4, rx: 3 }), duration: 1.6, ease: 'expo.inOut' }, N2 - 0.3);
    // step 3: Next → password.ts lines 1–7 (match cut on the green bar)
    const N3 = bar(17, 1);
    edCursor.move(N3 - 0.5, { x: nextBtn.cx - 2, y: nextBtn.cy + 3 }, 0.3);
    edCursor.click(N3);
    tl.to(files.auth, { opacity: 0, y: -18, duration: 0.22, ease: 'power2.in' }, N3 + 0.02);
    gsap.set(files.password, { opacity: 0, y: 18 });
    tl.to(files.password, { opacity: 1, y: 0, duration: 0.32, ease: 'power2.out' }, N3 + 0.22);
    [...files.password.children].forEach((ln) => ln.classList.add('on'));
    tl.to(band, { ...setBand(1, 7), duration: 0.42, ease: 'expo.inOut' }, N3 + 0.02);
    pn.show('step3', N3 + 0.05, 0.25);
    sb.show('sb-tour-2', N3 + 0.05, 0.25);
    cue('chime', N3 + 0.3);
    cue('prog_tick', N3 + 0.1);
    // glossary: hover verifyPassword in the explanation
    const tip = el('div', 'term-tooltip is-shown', DEMO.tour.glossary.find((g) => g.term === 'verifyPassword').definition);
    H('step3').body.appendChild(tip);
    tip.style.left = (term.x - step3Body.x) + 'px';
    tip.style.top = (term.b - step3Body.y + 8) + 'px';
    gsap.set(tip, { opacity: 0, y: -4 });
    const HOV = bar(18, 1) + 0.3;
    edCursor.move(bar(18, 1) - 0.35, { x: term.x + term.w * 0.55, y: term.cy + 4 }, 0.6);
    tl.to(tip, { opacity: 1, y: 0, duration: 0.22, ease: 'power2.out' }, HOV);
    cue('tooltip_pop', HOV);
    tl.to(c5, { ...cam({ x: term.x + 260, y: term.cy + 20 }, 1.75, { ry: -3, rx: 2 }), duration: 1.8, ease: 'expo.inOut' }, bar(18, 1) - 0.3);

    // =================================================================================
    // 6 · GO DEEPER  bar 19 – bar 24   (same editor)
    // =================================================================================
    const s6 = bar(19);
    // hard cut on the downbeat: back on step 1, framed on the questions
    tl.set(tip, { opacity: 0 }, s6);
    tl.set(files.password, { opacity: 0 }, s6);
    tl.set(files.auth, { opacity: 1, y: 0 }, s6);
    tl.set([...files.auth.children], { opacity: 1 }, s6);
    tl.set(band, setBand(4, 10), s6);
    pn.show('step1', s6, 0);
    sb.show('sb-tour-0', s6, 0);
    const SCR1 = Math.round(askTop - panelR.y - 14); // the panel scrolls to its questions
    tl.set(pn.scroller, { y: -SCR1 }, s6);
    const chipCam = { x: chip.cx + 330, y: panelR.y + 125 };
    tl.set(c5, cam(chipCam, 1.5, { ry: -3, rx: 2 }), s6);
    tl.set($('#cursor-ed'), { x: chip.cx + 160, y: chip.cy - SCR1 + 120 }, s6);
    cue('cut_soft', s6);
    edCursor.move(s6 + 0.05, { x: chip.x + 60, y: chip.cy - SCR1 + 3 }, 0.32);
    const ASK = words('s6a')[0].start + 0.02;
    edCursor.click(ASK);
    // the answer streams in
    const stream = [0, 1, 2, 3, 4].map((i) => ASK + 0.3 + i * 0.42);
    stream.forEach((t, i) => pn.show(`step1-answering-${i}`, t, 0));
    pn.show('step1-answered', ASK + 0.3 + 5 * 0.42, 0.18);
    cue('type_texture', ASK + 0.3, { dur: 2.1 });
    tl.to(c5, { ...cam({ x: chip.cx + 360, y: panelR.y + 150 }, 1.44, { ry: -3, rx: 2 }), duration: 2.4, ease: 'sine.inOut' }, ASK + 0.2);
    edCursor.move(ASK + 0.3, { x: chip.r + 240, y: chip.cy - SCR1 + 150 }, 0.8);
    kinetic({ x: 120, bottom: 112, shade: true, out: words('s6b')[0].start - 0.95, lines: [
      { seg: 's6a', words: [0, 1, 2, 3], it: [2, 3], size: 132 },
    ] });
    // risks
    const RISK = bar(21, 1);
    tl.to(pn.scroller, { y: 0, duration: 0.6, ease: 'expo.inOut' }, RISK - 0.85);
    tl.to(c5, { ...cam({ x: 1000, y: 360 }, 1.3, { ry: -4, rx: 3 }), duration: 0.8, ease: 'expo.inOut' }, RISK - 0.85);
    edCursor.move(RISK - 0.6, { x: risksBtnA.x + 22, y: risksBtnA.cy + 3 }, 0.5);
    edCursor.click(RISK, 'toggle');
    pn.show('step1-answered-risks', RISK + 0.02, 0.15);
    gsap.set(riskDot, { top: lineY(6) });
    gsap.set(riskNote, { top: lineY(6) + 1, left: line6End + 28 });
    tl.to(riskDot, { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(3)' }, RISK + 0.15);
    tl.fromTo(riskNote, { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: 0.4, ease: 'expo.out', immediateRender: false }, RISK + 0.25);
    cue('warn_tone', RISK + 0.15);
    kinetic({ x: 120, bottom: 112, shade: true, out: words('s6c')[0].start - 0.45, lines: [
      { seg: 's6b', words: [0, 1, 2, 3], it: [1, 2, 3], size: 132 },
    ] });
    // explain deeper → dive into the sub-tour
    const DEEP = bar(22, 1);
    edCursor.move(DEEP - 0.75, { x: deeperBtn.x + 34, y: deeperBtn.cy + 3 }, 0.5);
    edCursor.click(DEEP);
    edCursor.hide(DEEP + 0.15);
    tl.to(c5, { ...cam(lineCam(6), 5.2, { ry: 0, rx: 0 }), duration: 0.62, ease: 'expo.in' }, DEEP + 0.04);
    tl.to(editor, { filter: 'blur(14px)', duration: 0.45, ease: 'power2.in' }, DEEP + 0.2);
    cue('dive_whoosh', DEEP);
    const SWAP = DEEP + 0.66;
    tl.set([riskDot, riskNote], { opacity: 0 }, SWAP);
    tl.set(band, { ...setBand(5, 8), opacity: 0 }, SWAP);
    pn.show('subtour', SWAP, 0);
    sb.show('sb-subtour', SWAP, 0);
    tl.set(c5, cam(lineCam(6), 3.2), SWAP);
    tl.to(editor, { filter: 'blur(0px)', duration: 0.5, ease: 'power2.out' }, SWAP);
    tl.to(c5, { ...cam({ x: 1150, y: 470 }, 1.12, { ry: -5, rx: 3 }), duration: 1.0, ease: 'expo.out' }, SWAP);
    tl.to(band, { opacity: 1, duration: 0.2 }, SWAP + 0.3);
    cue('chime', SWAP + 0.3);
    kinetic({ x: 120, bottom: 112, shade: true, out: words('s6c')[3].start - 0.32, lines: [
      { seg: 's6c', words: [0, 1], it: [1], text: { 1: 'deeper.' }, size: 150 },
    ] });
    kinetic({ x: 120, bottom: 112, shade: true, out: bar(24) - 0.55, lines: [
      { seg: 's6c', words: [3, 4], it: [4], text: { 3: 'The', 4: 'Path.' }, size: 150 },
    ] });
    // the Path shows where you are
    const PATH = bar(23, 1);
    tl.to(c5, { ...cam({ x: pathSection.cx + 120, y: pathSection.cy + 30 }, 1.85, { ry: -4, rx: 2 }), duration: 1.0, ease: 'expo.inOut' }, PATH - 0.6);
    gsap.set(pathRing, { left: pathSection.x - 10, top: pathSection.y - 8, width: pathSection.w + 20, height: pathSection.h + 16 });
    tl.to(pathRing, { opacity: 1, duration: 0.3 }, PATH + 0.1);
    tl.to(pathRing, { opacity: 0.55, duration: 1.2, ease: 'sine.inOut' }, PATH + 0.5);
    cue('path_slide', PATH + 0.1);
    // discrete editor state: lit line numbers, tab and breadcrumbs
    schedule([[0, [4, 10]], [N2 + 0.2, [12, 15]], [s6, [4, 10]], [SWAP, [5, 8]]], ([a, b]) => {
      [...files.auth.children].forEach((ln, i) => ln.classList.toggle('on', i + 1 >= a && i + 1 <= b));
    });
    [...files.password.children].forEach((ln) => ln.classList.add('on'));
    schedule([[0, 'auth.ts'], [N3 + 0.2, 'password.ts'], [s6, 'auth.ts']], (v) => (tabName.textContent = v));
    schedule([[0, 'src  ›  auth.ts  ›  handleLogin'], [N2 + 0.2, 'src  ›  auth.ts  ›  findUser'],
      [N3 + 0.2, 'src  ›  password.ts  ›  verifyPassword'], [s6, 'src  ›  auth.ts  ›  handleLogin']], (v) => (crumbs.textContent = v));
    // =================================================================================
    // 7 · FOR TEAMS  bar 24 – bar 27
    // =================================================================================
    const s7 = bar(24);
    home.init('sb-home-unpinned-stale');
    const scroll7 = toursTitle.y - homeStackR.y - 24;
    gsap.set(home.scroller, { y: -scroll7 });
    gsap.set(homeWin, { opacity: 0, y: 40 });
    tl.to(homeWin, { opacity: 1, y: 0, duration: 0.7, ease: 'expo.out' }, s7);
    const c7 = $('#s7 .cam');
    tl.fromTo(c7, cam({ x: 960, y: 500 }, 1.0, { ry: 6 }), { ...cam({ x: 960, y: 480 }, 1.08, { ry: -4 }), duration: BAR * 3, ease: 'sine.inOut' }, s7);
    cue('cut_soft', s7);
    // stack coords → window/cam coords: stack sits inside the window under the view title
    const homeOff = (r) => ({ x: r.x, y: r.y - scroll7 });
    const A = homeOff(cardAR), B = homeOff(cardBR);
    const PIN = words('s7')[4].start - 0.02; // "Start"
    // flyer: the card itself travels from the project list up to Start here
    const flyer = el('div', 'flyer');
    const fh = el('div', 'ui-host');
    const fr = fh.attachShadow({ mode: 'open' });
    fr.innerHTML = `<style>${UI_CSS}*{transition:none!important}</style><div class="wv-body" data-surface="sidebar" style="width:${cardBR.w / 1.6}px;padding:0;margin:0;background:transparent">${cardB.outerHTML}</div>`;
    fh.style.zoom = 1.6;
    flyer.appendChild(fh);
    $('#s7 .cam').insertBefore(flyer, $('#cursor-home'));
    gsap.set(flyer, { x: A.x, y: A.y, opacity: 0 });
    homeCursor.show(s7 + 0.4, { x: A.x + cardAR.w * 0.7, y: A.y + 140 });
    const pinA = cardA.querySelector('.tour-card-pin');
    const pinR = pinA ? rect(pinA) : { cx: cardAR.r - 30, cy: cardAR.y + 24 };
    homeCursor.move(s7 + 0.45, { x: pinR.cx - 2, y: pinR.cy - scroll7 + 2 }, 0.6);
    homeCursor.click(PIN, 'pin_snap');
    tl.set(flyer, { opacity: 1 }, PIN + 0.02);
    tl.set([cardA, cardB], { visibility: 'hidden' }, PIN + 0.02);
    home.show('sb-home-stale', PIN + 0.05, 0.4);
    tl.to(flyer, { x: B.x, y: B.y, duration: 0.7, ease: 'expo.inOut' }, PIN + 0.05);
    cue('slide', PIN + 0.1);
    tl.set(cardB, { visibility: 'visible' }, PIN + 0.76);
    tl.set(flyer, { opacity: 0 }, PIN + 0.77);
    tl.to(cardB, { boxShadow: '0 0 0 3px rgba(63,185,80,0.35), 0 0 36px rgba(63,185,80,0.3)', duration: 0.35 }, PIN + 0.78);
    tl.to(cardB, { boxShadow: '0 0 0 3px rgba(63,185,80,0), 0 0 36px rgba(63,185,80,0)', duration: 1.2, ease: 'sine.inOut' }, PIN + 1.2);
    homeCursor.move(PIN + 0.6, { x: cardBR.r - 60, y: cardBR.cy - scroll7 + 90 }, 0.5);
    // a changed tour is rebuilt with one click
    const REB = bar(25, 4);
    homeCursor.move(REB - 0.6, { x: rebuildBtn.r - 2, y: rebuildBtn.b - scroll7 - 4 }, 0.5);
    homeCursor.click(REB);
    const spin = home1.q('.tour-card-stale .link-button svg');
    if (spin) tl.to(spin, { rotation: 360, transformOrigin: '50% 50%', duration: 0.5, ease: 'power2.inOut' }, REB);
    cue('swirl', REB + 0.02);
    home.show('sb-home', REB + 0.5, 0.3);
    cue('rebuild_chime', REB + 0.55);
    homeCursor.hide(bar(26, 3));
    kinetic({ x: 120, y: 318, out: bar(27) - 0.55, lines: [
      { seg: 's7', words: [4, 5], text: { 5: 'here,' }, size: 156 },
      { seg: 's7', words: [6, 7, 8], it: [6, 7, 8], size: 104, gap: 10 },
    ] });

    // =================================================================================
    // 8 · EXPORT  bar 27 – bar 30
    // One tour becomes one page, and the page travels the route to where the team reads.
    // =================================================================================
    const s8 = bar(27);
    const c8 = $('#s8 .cam');
    const S7END = cam({ x: 960, y: 480 }, 1.08, { ry: -4 });
    gsap.set(c8, S7END); // continues scene 7's last frame exactly
    // drill into the tour: the home view slides out, the tour slides in (same window)
    const exHome = ex.hosts['sb-home'], exTour = ex.hosts['sb-tour-0'];
    gsap.set(exHome, { y: -scroll7 });
    tl.to(exHome, { x: -70, opacity: 0, duration: 0.22, ease: 'power2.in' }, s8 + 0.02);
    tl.fromTo(exTour, { x: 70, opacity: 0 }, { x: 0, opacity: 1, duration: 0.45, ease: 'expo.out', immediateRender: false }, s8 + 0.2);
    cue('slide', s8 + 0.02);
    tl.to(c8, { ...cam({ x: 960, y: 505 }, 1.0, { ry: -2 }), duration: 1.3, ease: 'expo.inOut' }, s8 + 0.1);
    const EP = { x: exportR.r - 2, y: exportR.b - 4 };
    const EXP = words('s8')[0].start;
    exCursor.show(s8 + 0.25, { x: EP.x + 150, y: EP.y - 170 });
    exCursor.move(s8 + 0.3, { x: EP.x, y: EP.y }, EXP - s8 - 0.38);
    exCursor.click(EXP);
    exCursor.hide(EXP + 0.25);
    tl.to(exportLink, { color: '#3FB950', duration: 0.12 }, EXP);
    // the window becomes the page: frame morphs, the tour's own parts fly into the page's layout
    const M0 = EXP + 0.1, MD = 0.75;
    const WIN = { left: 1150, top: 160, width: 578, height: 690 };
    const PAGE = { left: 760, top: 196, width: 1060, height: 662.5 };
    gsap.set(pageFrame, { ...WIN, opacity: 0 });
    tl.set(pageFrame, { opacity: 1 }, M0);
    tl.to(exWin, { opacity: 0, duration: 0.16 }, M0 + 0.04);
    tl.to(pageFrame, { ...PAGE, duration: MD, ease: 'expo.inOut' }, M0);
    cue('paper_swish', M0);
    const pg = (q) => pageHost.q(q);
    const pgItems = pageHost.qa('.step-list-item');
    const flips = [
      [pg('.header-title'), flipSrc.title],
      [pgItems[0], flipSrc.map],
      ...pgItems.slice(1).map((n, i) => [n, flipSrc.steps[i]]),
    ];
    flips.forEach(([node, src], i) => {
      const fin = pageFinal.get(node);
      const s0 = src.font / fin.font; // start at the sidebar's text size
      const t0 = { x: src.x - fin.padL * s0 - (WIN.left + 1 + fin.lx), y: src.y - fin.padT * s0 - (WIN.top + 1 + fin.ly) };
      gsap.set(node, { transformOrigin: '0 0', opacity: 0 });
      tl.fromTo(node, { x: t0.x / PZ, y: t0.y / PZ, scale: s0 },
        { x: 0, y: 0, scale: 1, duration: MD, ease: 'expo.inOut', immediateRender: false }, M0 + i * 0.03);
      tl.to(node, { opacity: 1, duration: 0.1 }, M0 + i * 0.03);
    });
    const rest = [pg('.header-counter'), pg('.step-list-title'), pg('.overview-question'), pg('.overview-summary')];
    gsap.set(rest, { opacity: 0, y: 14 });
    tl.to(rest, { opacity: 1, y: 0, duration: 0.5, ease: 'expo.out', stagger: 0.06 }, M0 + 0.42);
    const chips = pageHost.qa('.overview-node');
    gsap.set(chips, { opacity: 0, scale: 0.8, transformOrigin: '50% 50%' });
    chips.forEach((c, i) => {
      tl.to(c, { opacity: 1, scale: 1, duration: 0.4, ease: 'back.out(2.2)' }, M0 + 0.62 + i * 0.07);
      cue('route_tick', M0 + 0.62 + i * 0.07, { i });
    });
    const tail = [...pageHost.qa('.overview-edge'), pg('.primary-button')];
    gsap.set(tail, { opacity: 0, x: -10 });
    tl.to(tail, { opacity: 1, x: 0, duration: 0.4, ease: 'expo.out', stagger: 0.05 }, M0 + 0.82);
    tl.to($('.sweep', pageFrame), { xPercent: 260, duration: 0.8, ease: 'power2.inOut' }, M0 + 0.7);
    // the page steps aside and becomes the hub of three routes
    const H0 = M0 + 1.1;
    const HUB = { x: 575 - (PAGE.left + PAGE.width / 2), y: 485 - (PAGE.top + PAGE.height / 2), scale: 0.58 };
    tl.to(pageFrame, { ...HUB, transformOrigin: '50% 50%', duration: 0.62, ease: 'expo.inOut' }, H0);
    cue('airy_whoosh', H0, { soft: 1 });
    const hubRight = { x: PAGE.left + PAGE.width / 2 + HUB.x + (PAGE.width / 2) * HUB.scale, y: PAGE.top + PAGE.height / 2 + HUB.y };
    const r8 = $('#s8-route');
    const packets = $('#packets');
    const flowPaths = [];
    DEST.forEach((d, i) => {
      const w = words('s8')[d.word];
      const T = w.start; // the page lands as the name is spoken
      const app = apps[i];
      const ey = d.y + 125;
      const turn = i === 1 ? 1105 : 1060;
      const pts = i === 1
        ? [[hubRight.x + 4, hubRight.y], [turn, hubRight.y], [turn, ey], [d.x, ey]]
        : [[hubRight.x + 4, hubRight.y], [turn, hubRight.y], [turn, ey], [d.x, ey]];
      const D = routeD(pts, 26);
      const glow = svgEl('path', { d: D, class: 'glow', style: 'stroke-width:7;opacity:.12' }, r8);
      const line = svgEl('path', { d: D, style: 'stroke-width:2.5' }, r8);
      const flow = svgEl('path', { d: D, style: 'stroke-width:2.5;stroke:#9BE9A8;stroke-dasharray:3 17;opacity:0' }, r8);
      flowPaths.push(flow);
      drawPath(line, T - 0.62, 0.45, 'power2.inOut');
      drawPath(glow, T - 0.62, 0.45, 'power2.inOut');
      cue('swish', T - 0.6, { i });
      gsap.set(app, { opacity: 0, x: 40, scale: 0.94, filter: 'blur(8px)', transformOrigin: '0% 50%' });
      tl.to(app, { opacity: 1, x: 0, scale: 1, filter: 'blur(0px)', duration: 0.55, ease: 'expo.out' }, T - 0.6);
      // a copy of the page rides the route
      const pk = el('div', 'packet', '<img src="assets/export-page.png" alt="">');
      packets.appendChild(pk);
      const L = line.getTotalLength();
      const a = T - 0.4, b = T - 0.02;
      R.push((t) => {
        if (t < a - 0.05 || t > b + 0.12) { pk.style.opacity = 0; return; }
        const u = clamp((t - a) / (b - a), 0, 1);
        const e = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
        const P = line.getPointAtLength(e * L);
        const sc = 0.55 + 0.45 * Math.sin(Math.PI * Math.min(1, u * 1.1));
        pk.style.transform = `translate(${P.x.toFixed(1)}px, ${P.y.toFixed(1)}px) scale(${sc.toFixed(3)})`;
        pk.style.opacity = (t > b ? 1 - (t - b) / 0.12 : Math.min(1, (t - a + 0.05) / 0.1)).toFixed(3);
      });
      // landing: ring, the page appears inside, a check
      const ring = el('div', 'ring');
      packets.appendChild(ring);
      gsap.set(ring, { x: d.x, y: ey });
      tl.fromTo(ring, { opacity: 0.95, scale: 0.6 }, { opacity: 0, scale: 4.2, duration: 0.7, ease: 'expo.out', immediateRender: false }, T);
      tl.to($('.sk', app), { opacity: 0, duration: 0.2 }, T);
      tl.fromTo($('.app-doc', app), { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: 0.45, ease: 'expo.out', immediateRender: false }, T);
      tl.fromTo($('.app-ok', app), { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(2.5)', immediateRender: false }, T + 0.12);
      tl.fromTo(app, { boxShadow: '0 30px 80px rgba(0,0,0,.5), 0 0 0 1px rgba(63,185,80,0)' },
        { boxShadow: '0 30px 80px rgba(0,0,0,.5), 0 0 0 1px rgba(63,185,80,.9)', duration: 0.18, immediateRender: false }, T);
      tl.to(app, { boxShadow: '0 30px 80px rgba(0,0,0,.5), 0 0 0 1px rgba(63,185,80,0)', duration: 0.9, ease: 'sine.inOut' }, T + 0.3);
      cue('land', T, { i });
    });
    // once everyone has it, the routes keep flowing
    const FLOW = words('s8')[11].start + 0.45;
    flowPaths.forEach((f, i) => {
      tl.to(f, { opacity: 0.55, duration: 0.4 }, FLOW + i * 0.08);
      tl.fromTo(f, { strokeDashoffset: 0 }, { strokeDashoffset: -120, duration: bar(30) - FLOW, ease: 'none', immediateRender: false }, FLOW);
    });
    tl.to(c8, { ...cam({ x: 990, y: 500 }, 1.05, { ry: 3 }), duration: bar(30) - 0.45 - (s8 + 1.4), ease: 'sine.inOut' }, s8 + 1.4);
    kinetic({ x: 120, y: 372, out: EXP + 0.98, lines: [
      { seg: 's8', words: [0], it: [0], text: { 0: 'Export.' }, size: 200 },
    ] });
    // push through to the next scene
    tl.to(c8, { scale: '+=0.1', opacity: 0, duration: 0.42, ease: 'power2.in' }, bar(30) - 0.42);

    // =================================================================================
    // 9 · WORKS EVERYWHERE  bar 30 – bar 32
    // =================================================================================
    const s9 = bar(30);
    cue('cut_soft', s9);
    rowNodes.forEach((r, ri) => {
      const LAB = [[0, 1], [2, 3], [4, 5, 6]][ri];
      kinetic({ parent: r.lab, x: 0, y: 8, lines: [{ seg: 's9', words: LAB, it: ri === 2 ? [6] : [], size: 96 }] });
      const t0 = words('s9')[LAB[LAB.length - 1]].start;
      r.items.forEach((it, i) => {
        const t = t0 + 0.06 + i * (BEAT / 2);
        tl.fromTo(it, { opacity: 0, y: 26, scale: 0.9, filter: 'blur(8px)' }, { opacity: 1, y: 0, scale: 1, filter: 'blur(0px)', duration: 0.45, ease: 'expo.out' }, t);
        cue('logo_hit', t, { i: ri * 4 + i });
      });
    });
    tl.fromTo('#s9 .cam', cam({ x: 960, y: 540 }, 1.0), { ...cam({ x: 960, y: 540 }, 1.035), duration: BAR * 2, ease: 'none' }, s9);
    tl.to('#rows', { opacity: 0, y: -20, duration: 0.4, ease: 'power2.in' }, bar(32) - 0.42);
    cue('final_riser', bar(31, 1), { dur: BAR });

    // =================================================================================
    // 10 · FINAL FRAME  bar 32 – bar 36
    // =================================================================================
    const s10 = bar(32);
    const disc = $('.logo-disc', logo);
    gsap.set(disc, { scale: 0, svgOrigin: '32 32' });
    drawPath(rDot, s10, 0.3, 'power2.out');
    drawPath(rPath, s10 + 0.18, 0.75, 'power2.inOut');
    drawPath(rHead, s10 + 0.86, 0.22, 'power2.out');
    tl.to(disc, { scale: 1, duration: 0.55, ease: 'back.out(1.6)' }, s10 + 0.98);
    gsap.set(logo, { filter: 'drop-shadow(0 0 0px rgba(45,164,78,0))' });
    tl.to(logo, { filter: 'drop-shadow(0 0 60px rgba(45,164,78,0.45))', duration: 0.9 }, s10 + 1.1);
    cue('route_draw', s10);
    cue('resolve', s10 + 1.0);
    const wm = $('#wordmark');
    gsap.set(wm, { opacity: 0, x: -26, filter: 'blur(10px)' });
    tl.to(wm, { opacity: 1, x: 0, filter: 'blur(0px)', duration: 0.7, ease: 'expo.out' }, words('s10a')[0].start - 0.08);
    const tagList = words('s10b');
    kinetic({ center: true, y: 568, lines: [{ seg: 's10b', words: [0, 1, 2, 3, 4, 5, 6, 7], it: [3, 4, 5, 6, 7], size: 92 }] });
    tl.fromTo('#cta', { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.7, ease: 'expo.out' }, tagList[tagList.length - 1].end + 0.35);
    cue('cta_tick', tagList[tagList.length - 1].end + 0.38);
    tl.fromTo('#s10 .cam', cam({ x: 960, y: 540 }, 1.0), { ...cam({ x: 960, y: 540 }, 1.025), duration: END - s10, ease: 'sine.out' }, s10);

    // ---------- the green bar: grows from box 1 to fill the frame, contracts into lines 4–10 ----------
    const XF1 = bar(14), XF2 = s5 + 0.55, NS = 16;
    const samples = [];
    for (let i = 0; i <= NS; i++) { const t = XF0 + ((XF1 - XF0) * i) / NS; tl.time(t); samples.push(rect(nodesEls[0])); }
    tl.time(s5 + 0.56); const bandScreen = rect(band);
    tl.time(0);
    const FULL = { x: -4, y: -4, w: 1928, h: 1088 };
    const mix = (a, b, k) => ({ x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k, w: a.w + (b.w - a.w) * k, h: a.h + (b.h - a.h) * k });
    const xb = $('b', xfer);
    R.push((t) => {
      if (t < XF0 || t >= XF2) { xfer.style.visibility = 'hidden'; return; }
      let g, rad, op = 1, edge = 0;
      if (t < XF1) {
        const u = (t - XF0) / (XF1 - XF0), f = u * NS, i = Math.min(NS - 1, Math.floor(f));
        const node = mix(samples[i], samples[i + 1], f - i);
        const k = Math.pow(u, 2.4);
        g = mix(node, FULL, k); rad = (node.h / 2) * (1 - k); op = Math.min(1, u * 3.5); edge = 1 - k;
      } else {
        const u = (t - XF1) / (XF2 - XF1), k = 1 - Math.pow(2, -10 * u);
        g = mix(FULL, bandScreen, k); rad = 0;
      }
      xfer.style.visibility = 'visible';
      Object.assign(xfer.style, { left: g.x + 'px', top: g.y + 'px', width: g.w + 'px', height: g.h + 'px', borderRadius: rad + 'px', opacity: op });
      xb.style.opacity = edge;
    });

    // ---------- scene visibility, scrim ----------
    const SC = [['#s1', 0, bar(4)], ['#s2', bar(4), bar(7)], ['#s3', bar(7), bar(10)], ['#s4', bar(10), bar(14)],
      ['#s5', bar(14), bar(24)], ['#s7', bar(24), bar(27)], ['#s8', bar(27), bar(30)], ['#s9', bar(30), bar(32)], ['#s10', bar(32), END + 1]]
      .map(([s, a, b]) => [$(s), a, b]);
    R.push((t) => {
      for (const [n, a, b] of SC) n.style.visibility = t >= a && t < b ? 'visible' : 'hidden';
    });
    tl.set({}, {}, END);

    window.SFX_CUES = CUES.sort((a, b) => a.t - b.t);
    window.__duration = END;
    window.__seek = (t) => { tl.time(t, false); for (const r of R) r(t); };
    window.__seek(0);
  }

  window.__ready = build();
})();
