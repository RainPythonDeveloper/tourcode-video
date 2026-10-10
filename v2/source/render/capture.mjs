// Frame-by-frame capture of the paused GSAP timeline at 60 fps, then H.264 + AAC with ffmpeg.
//
//   node render/capture.mjs OUT.mp4 AUDIO.wav [--workers 3] [--from 0] [--to 75]
//
// Each worker renders a contiguous range of frames in its own headless Chromium and pipes
// PNG screenshots into its own ffmpeg (a near-lossless intermediate). Before its first frame,
// a worker plays the timeline forward frame by frame without screenshots, so every tween
// starts from exactly the state it would have in one continuous pass. The chunks are joined
// (lossless RGB) and encoded once to the final H.264 (yuv420p, BT.709) with the mixed audio as AAC.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { openFilm } from './page.mjs';

const args = process.argv.slice(2);
const out = path.resolve(args[0]);
const audio = path.resolve(args[1]);
const opt = (k, d) => { const i = args.indexOf(`--${k}`); return i > 0 ? Number(args[i + 1]) : d; };
const FPS = 60;
const workers = opt('workers', 3);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'tc-capture-'));

const probe = await openFilm();
const duration = await probe.page.evaluate(() => window.__duration);
await probe.close();
const from = Math.round(opt('from', 0) * FPS);
const to = Math.round(opt('to', duration) * FPS);
const total = to - from;
console.log(`frames ${from}–${to} (${total}) with ${workers} workers → ${out}`);

function ffmpeg(argv) {
  const p = spawn('ffmpeg', argv, { stdio: ['pipe', 'ignore', 'pipe'] });
  let err = '';
  p.stderr.on('data', (d) => (err += d));
  const done = new Promise((res, rej) => p.on('close', (c) => (c === 0 ? res() : rej(new Error(err.slice(-2000))))));
  return { p, done };
}

async function worker(w, a, b, browser) {
  const film = await openFilm({ browser });
  const file = path.join(tmp, `chunk-${String(w).padStart(2, '0')}.mkv`);
  // lossless RGB intermediate: the only colour conversion happens once, in the final encode
  const enc = ffmpeg(['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264rgb', '-preset', 'ultrafast', '-qp', '0', file]);
  // pre-roll: play up to the first frame without screenshots
  for (let f = 0; f < a; f++) await film.page.evaluate((t) => window.__seek(t), f / FPS);
  const t0 = Date.now();
  for (let f = a; f < b; f++) {
    await film.page.evaluate((t) => window.__seek(t), f / FPS);
    const png = await film.page.screenshot({ type: 'png' });
    if (!enc.p.stdin.write(png)) await new Promise((r) => enc.p.stdin.once('drain', r));
    if ((f - a) % 300 === 0) console.log(`  w${w} frame ${f} (${(((f - a) / ((Date.now() - t0) / 1000 || 1))).toFixed(1)} fps)`);
  }
  enc.p.stdin.end();
  await enc.done;
  if (film.errors.length) console.log(`  w${w} page errors:`, [...new Set(film.errors)].join('\n'));
  await film.close();
  return file;
}

const browsers = await Promise.all(Array.from({ length: workers }, () =>
  chromium.launch({ args: ['--disable-lcd-text', '--font-render-hinting=none', '--force-color-profile=srgb'] })));
const per = Math.ceil(total / workers);
const t0 = Date.now();
const chunks = await Promise.all(browsers.map((br, w) => worker(w, from + w * per, Math.min(to, from + (w + 1) * per), br)));
await Promise.all(browsers.map((b) => b.close()));
console.log(`captured in ${((Date.now() - t0) / 1000).toFixed(0)} s`);

const list = path.join(tmp, 'list.txt');
fs.writeFileSync(list, chunks.map((c) => `file '${c}'`).join('\n'));
const fin = ffmpeg(['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list,
  '-ss', String(from / FPS), '-t', String(total / FPS), '-i', audio,
  '-map', '0:v', '-map', '1:a',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
  '-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p',
  '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
  '-r', String(FPS), '-g', String(FPS * 2), '-bf', '2',
  '-c:a', 'aac', '-b:a', '256k', '-ar', '48000',
  '-movflags', '+faststart', '-shortest', out]);
await fin.done;
fs.rmSync(tmp, { recursive: true, force: true });
console.log('wrote', out, (fs.statSync(out).size / 1e6).toFixed(1), 'MB');
