// Font options, shown on real frames of the film: node render/font-preview.mjs OUT_DIR
// Each option only swaps the film's own typography (hook, headline, captions, labels, final frame,
// the /tour command). The product's UI keeps its own fonts.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { openFilm } from './page.mjs';

const out = path.resolve(process.argv[2]);
fs.mkdirSync(out, { recursive: true });
const FS = 'node_modules/@fontsource';
const face = (fam, pkg, weights, italic = []) =>
  weights.map((w) => `@font-face{font-family:'${fam}';font-weight:${w};font-style:normal;src:url(/${FS}/${pkg}/files/${pkg}-latin-${w}-normal.woff2) format('woff2')}`).join('')
  + italic.map((w) => `@font-face{font-family:'${fam}';font-weight:${w};font-style:italic;src:url(/${FS}/${pkg}/files/${pkg}-latin-${w}-italic.woff2) format('woff2')}`).join('');
const geist = face('Geist', 'geist-sans', [400, 500, 600, 700]) + face('Geist Mono', 'geist-mono', [400, 500]);
const instSerif = face('Instrument Serif', 'instrument-serif', [400], [400]);
const GEIST_VARS = { '--display': "'Geist'", '--display-weight': 600, '--display-strong': 600, '--display-tracking': '-0.045em',
  '--caption': "'Geist'", '--caption-weight': 500, '--caption-tracking': '-0.02em', '--code': "'Geist Mono'" };
export const OPTIONS = [
  { id: 'A', name: 'Geist + Geist Mono', faces: geist, vars: GEIST_VARS },
  { id: 'B', name: 'Instrument Serif + Geist Mono', faces: instSerif + face('Instrument Sans', 'instrument-sans', [400, 500, 600]) + face('Geist Mono', 'geist-mono', [400, 500]),
    vars: { '--display': "'Instrument Serif'", '--display-weight': 400, '--display-strong': 400, '--display-tracking': '-0.01em',
      '--caption': "'Instrument Serif'", '--caption-weight': 400, '--caption-tracking': '0em', '--caption-size': '48px', '--code': "'Geist Mono'" } },
  { id: 'C', name: 'Geist + Instrument Serif italic', faces: geist + instSerif,
    vars: { ...GEIST_VARS, '--accent': "'Instrument Serif'", '--accent-style': 'italic', '--accent-weight': 400, '--accent-tracking': '-0.01em' } },
  { id: 'D', name: 'Space Grotesk + JetBrains Mono', faces: face('Space Grotesk', 'space-grotesk', [400, 500, 600, 700]),
    vars: { '--display': "'Space Grotesk'", '--display-weight': 600, '--display-strong': 700, '--display-tracking': '-0.035em',
      '--caption': "'Space Grotesk'", '--caption-weight': 500, '--caption-tracking': '-0.015em', '--code': "'JetBrains Mono'" } },
  { id: 'E', name: 'Bricolage Grotesque + DM Mono', faces: face('Bricolage Grotesque', 'bricolage-grotesque', [500, 600, 700, 800]) + face('DM Sans', 'dm-sans', [400, 500, 600]) + face('DM Mono', 'dm-mono', [400, 500]),
    vars: { '--display': "'Bricolage Grotesque'", '--display-weight': 700, '--display-strong': 800, '--display-tracking': '-0.04em',
      '--caption': "'Bricolage Grotesque'", '--caption-weight': 600, '--caption-tracking': '-0.02em', '--code': "'DM Mono'" } },
  { id: 'F', name: 'Manrope + Commit Mono', faces: face('Manrope', 'manrope', [500, 600, 700, 800]) + face('Commit Mono', 'commit-mono', [400, 500]),
    vars: { '--display': "'Manrope'", '--display-weight': 700, '--display-strong': 800, '--display-tracking': '-0.035em',
      '--caption': "'Manrope'", '--caption-weight': 600, '--caption-tracking': '-0.015em', '--code': "'Commit Mono'" } },
];
const TIMES = [4.75, 10.35, 34.9, 73.5];

if (import.meta.url === `file://${process.argv[1]}`) {
  for (const o of OPTIONS) {
    const css = `<style>${o.faces}:root{${Object.entries(o.vars).map(([k, v]) => `${k}:${v}`).join(';')}}
      .fp-label{position:absolute;z-index:99;left:28px;top:24px;padding:8px 16px;border-radius:10px;background:rgba(255,255,255,.92);color:#0D1117;font:600 26px Inter}
      .fp-tag{position:absolute;z-index:99;left:28px;top:1000px;width:46px;height:46px;border-radius:10px;background:rgba(255,255,255,.92);color:#0D1117;font:700 28px/46px Inter;text-align:center}</style>`;
    const film = await openFilm({ transformHtml: (h) => h.replace('</head>', css + '</head>')
      .replace('<div id="stage">', `<div id="stage"><div class="fp-label">${o.id} · ${o.name}</div><div class="fp-tag">${o.id}</div>`) });
    let t = 0;
    const files = [];
    for (const at of TIMES) {
      for (; t < at; t += 0.25) await film.page.evaluate((x) => window.__seek(x), t);
      await film.page.evaluate((x) => window.__seek(x), at);
      const f = path.join(out, `${o.id}-${at}.png`);
      await film.page.screenshot({ path: f });
      files.push(f);
    }
    if (film.errors.length) console.log(o.id, 'errors', film.errors);
    await film.close();
    // 2×2 sheet per option
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...files.flatMap((f) => ['-i', f]),
      '-filter_complex', '[0][1][2][3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0,scale=1920:1080',
      '-frames:v', '1', path.join(out, `option-${o.id}.png`)]);
    console.log('option', o.id, o.name);
  }
  // overviews: the final frame of every option, and the caption band of every option
  const ids = OPTIONS.map((o) => o.id);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...ids.flatMap((id) => ['-i', path.join(out, `${id}-73.5.png`)]),
    '-filter_complex', `${ids.map((_, i) => `[${i}]scale=960:540[s${i}]`).join(';')};${ids.map((_, i) => `[s${i}]`).join('')}xstack=inputs=6:layout=0_0|960_0|0_540|960_540|0_1080|960_1080`,
    '-frames:v', '1', path.join(out, 'overview-final.png')]);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...ids.flatMap((id) => ['-i', path.join(out, `${id}-34.9.png`)]),
    '-filter_complex', `${ids.map((_, i) => `[${i}]crop=1920:150:0:930[c${i}]`).join(';')};${ids.map((_, i) => `[c${i}]`).join('')}vstack=inputs=6`,
    '-frames:v', '1', path.join(out, 'overview-captions.png')]);
  console.log('overviews written');
}
