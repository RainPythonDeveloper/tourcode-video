// Draws every UI state the film needs with TourCode's own webview code
// (assets/ui/webview.js + webview.css + theme.css) and saves the resulting DOM.
//
// Each state starts from one of the real pages in assets/ui and changes only the
// state object the page posts to the webview (step index, risks on/off, the
// question being answered, a stale tour…). The webview draws it exactly as the
// extension would. The film embeds the saved DOM in shadow roots with the same CSS.
//
// Usage: node render/snapshot-ui.mjs   (writes data/ui-states.js, data/webview.css, data/theme.css)
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const ui = path.resolve(root, '../../assets/ui');
const tours = path.resolve(root, '../../assets/tours');
const fonts = path.join(root, 'node_modules/@fontsource');

const mainTour = JSON.parse(fs.readFileSync(path.join(tours, 'how-login-works.json'), 'utf8'));

function readPage(name) {
  const html = fs.readFileSync(path.join(ui, `${name}.html`), 'utf8');
  const m = html.match(/window\.postMessage\((\{[\s\S]*\})\s*,\s*["']\*["']\)/);
  if (!m) throw new Error(`no state in ${name}.html`);
  return { html, json: m[1], state: JSON.parse(m[1]) };
}

const clone = (o) => JSON.parse(JSON.stringify(o));
const faq = (i) => ({ answers: [], suggestions: { kind: 'faq', questions: mainTour.steps[i].suggestedQuestions } });

const QUESTION = 'Why return a result object instead of throwing an error?';
const answered = readPage('step').state.questions;
const fullAnswer = answered.answers[0].answer;
// streaming stages: the answer arrives word by word
const words = fullAnswer.split(' ');
const stages = [3, 9, 16, 24, 33].map((n) => words.slice(0, Math.min(n, words.length)).join(' '));

const states = {
  // the tour map tab
  'map': ['tour-map', (s) => s],
  // explanation panel under the code
  'step1': ['step', (s) => ({ ...s, showDetails: false, showRisks: false, questions: faq(0) })],
  'step2': ['step', (s) => ({ ...s, showDetails: false, showRisks: false, questions: faq(1), session: { ...s.session, stepIndex: 1 } })],
  'step3': ['step', (s) => ({ ...s, showDetails: false, showRisks: false, questions: faq(2), session: { ...s.session, stepIndex: 2 } })],
  ...Object.fromEntries(stages.map((text, i) => [`step1-answering-${i}`, ['step-answering', (s) => ({
    ...s, showDetails: false, showRisks: false,
    questions: { ...s.questions, running: { ...s.questions.running, text } },
  })]])),
  'step1-answered': ['step', (s) => ({ ...s, showDetails: false, showRisks: false })],
  'step1-answered-risks': ['step', (s) => ({ ...s, showDetails: false, showRisks: true })],
  'subtour': ['step-subtour', (s) => s],
  // sidebar
  'sb-tour-0': ['sidebar-tour', (s) => ({ ...s, session: { ...s.session, stepIndex: 0 } })],
  'sb-tour-1': ['sidebar-tour', (s) => s],
  'sb-tour-2': ['sidebar-tour', (s) => ({ ...s, session: { ...s.session, stepIndex: 2 } })],
  'sb-subtour': ['sidebar-subtour', (s) => s],
  'sb-home': ['sidebar-home', (s) => s],
  'sb-home-unpinned': ['sidebar-home', (s) => ({ ...s, tours: s.tours.map((t) => ({ ...t, isPinned: false })) })],
  'sb-home-stale': ['sidebar-home', (s) => ({ ...s, tours: s.tours.map((t) => (t.id === 'session-start' ? { ...t, staleStepCount: 2 } : t)) })],
  'sb-home-unpinned-stale': ['sidebar-home', (s) => ({ ...s, tours: s.tours.map((t) => ({ ...t, isPinned: false, ...(t.id === 'session-start' ? { staleStepCount: 2 } : {}) })) })],
};

const fontCss = [400, 500, 600, 700].map((w) => `
@font-face{font-family:Inter;font-weight:${w};src:url(/fonts/inter/files/inter-latin-${w}-normal.woff2) format('woff2')}
@font-face{font-family:'JetBrains Mono';font-weight:${w};src:url(/fonts/jetbrains-mono/files/jetbrains-mono-latin-${w}-normal.woff2) format('woff2')}`).join('');

const browser = await chromium.launch();
const out = {};
for (const [name, [base, change]] of Object.entries(states)) {
  const page = readPage(base);
  const state = change(clone(page.state));
  const html = page.html
    .replace(page.json, JSON.stringify(state))
    .replace('</head>', `<style>${fontCss}</style></head>`);
  const width = Number(page.html.match(/style="width:(\d+)px"/)[1]);
  const tab = await browser.newPage({ viewport: { width, height: 900 } });
  await tab.route('http://ui.local/**', (route) => {
    const p = decodeURIComponent(new URL(route.request().url()).pathname);
    if (p === '/page.html') return route.fulfill({ body: html, contentType: 'text/html' });
    if (p.startsWith('/fonts/')) return route.fulfill({ path: path.join(fonts, p.slice(7)) });
    return route.fulfill({ path: path.join(ui, p.slice(1)) });
  });
  await tab.goto('http://ui.local/page.html');
  await tab.evaluate(() => document.fonts.ready);
  await tab.waitForTimeout(250);
  out[name] = await tab.evaluate(() => ({
    surface: document.body.dataset.surface,
    width: parseInt(document.body.style.width, 10),
    height: document.getElementById('app').getBoundingClientRect().height,
    html: document.getElementById('app').outerHTML,
  }));
  await tab.screenshot({ path: path.join(root, 'ui-snapshots', `${name}.png`), fullPage: true });
  await tab.close();
  console.log(name.padEnd(24), out[name].surface, out[name].width, Math.round(out[name].height));
}

// the exported page: the same tour as the browser page TourCode makes without the editor
{
  const tab = await browser.newPage({ viewport: { width: 1280, height: 800 }, colorScheme: 'dark' });
  await tab.route('http://ui.local/**', (route) => {
    const p = decodeURIComponent(new URL(route.request().url()).pathname);
    if (p.startsWith('/fonts/')) return route.fulfill({ path: path.join(fonts, p.slice(7)) });
    const html = fs.readFileSync(path.join(tours, 'how-login-works.page.html'), 'utf8')
      .replace('</head>', `<style>${fontCss}</style></head>`);
    return route.fulfill({ body: html, contentType: 'text/html' });
  });
  await tab.goto('http://ui.local/page.html');
  await tab.evaluate(() => document.fonts.ready);
  await tab.waitForTimeout(400);
  await tab.screenshot({ path: path.join(root, 'assets/export-page.png') });
  await tab.close();
  console.log('export page');
}
await browser.close();

fs.writeFileSync(path.join(root, 'data/ui-states.js'), `window.UI_STATES = ${JSON.stringify(out)};\n`);
for (const f of ['webview.css', 'theme.css']) fs.copyFileSync(path.join(ui, f), path.join(root, 'data', f));
// the same CSS, scoped for a shadow root: :root -> :host, body -> .wv-body
const scoped = ['theme.css', 'webview.css']
  .map((f) => fs.readFileSync(path.join(ui, f), 'utf8'))
  .join('\n')
  .replace(/:root\b/g, ':host')
  .replace(/(^|[\s,}])body(?=[\s{[.:,])/g, '$1.wv-body');
fs.writeFileSync(path.join(root, 'data/ui-css.js'), `window.UI_CSS = ${JSON.stringify(scoped)};\n`);
console.log('wrote data/ui-states.js');
