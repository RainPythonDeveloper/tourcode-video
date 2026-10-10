// Opens index.html in headless Chromium through a local route (no server needed).
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.json': 'application/json' };

export async function openFilm({ browser } = {}) {
  const own = !browser;
  browser = browser || (await chromium.launch({ args: ['--disable-lcd-text', '--font-render-hinting=none', '--force-color-profile=srgb'] }));
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errors.push(m.text()); });
  await page.route('http://tc.local/**', (route) => {
    const p = decodeURIComponent(new URL(route.request().url()).pathname);
    const file = path.join(root, p === '/' ? 'index.html' : p.slice(1));
    if (!fs.existsSync(file)) return route.fulfill({ status: 404, body: 'not found' });
    return route.fulfill({ path: file, contentType: TYPES[path.extname(file)] || 'application/octet-stream' });
  });
  await page.goto('http://tc.local/index.html');
  await page.waitForFunction(() => window.__ready !== undefined);
  await page.evaluate(() => window.__ready);
  return { browser, page, errors, close: async () => { await page.close(); if (own) await browser.close(); } };
}
