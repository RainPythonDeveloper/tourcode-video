// Stills and a contact sheet: node render/stills.mjs [out-dir] [t1 t2 …]
// With no times, takes one still every 1.5 s. The film is played forward frame by frame, as the capture does.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { openFilm, root } from './page.mjs';

const out = path.resolve(process.argv[2] || path.join(root, '..', 'checks', 'stills'));
fs.mkdirSync(out, { recursive: true });
const film = await openFilm();
const dur = await film.page.evaluate(() => window.__duration);
let times = process.argv.slice(3).map(Number);
if (!times.length) for (let t = 0.75; t < dur; t += 1.5) times.push(+t.toFixed(3));
times.sort((a, b) => a - b);
const files = [];
// play forward frame by frame, exactly as the capture does, so the stills show what the film shows
let now = 0;
for (const t of times) {
  for (; now < t; now += 1 / 60) await film.page.evaluate((x) => window.__seek(x), now);
  await film.page.evaluate((x) => window.__seek(x), t);
  const f = path.join(out, `t${t.toFixed(2).padStart(6, '0')}.png`);
  await film.page.screenshot({ path: f });
  files.push(f);
}
if (film.errors.length) console.log('PAGE ERRORS:\n' + [...new Set(film.errors)].join('\n'));
await film.close();
if (files.length > 1) {
  const cols = 5;
  const list = path.join(out, 'list.txt');
  fs.writeFileSync(list, files.map((f) => `file '${f}'`).join('\n'));
  const sheet = path.join(out, 'contact-sheet.png');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list,
    '-vf', `scale=384:216,drawtext=text='%{metadata\\:t}':x=4:y=4:fontsize=1:fontcolor=white@0,tile=${cols}x${Math.ceil(files.length / cols)}:padding=4:color=0x202020`,
    '-frames:v', '1', sheet]);
  console.log('sheet', sheet);
}
console.log(files.length, 'stills in', out);
