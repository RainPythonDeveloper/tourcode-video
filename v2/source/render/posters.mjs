// Three poster frames (1920×1080 PNG) straight from the film.
//   node render/posters.mjs OUT_DIR
import fs from 'node:fs';
import path from 'node:path';
import { openFilm, root } from './page.mjs';

const out = path.resolve(process.argv[2] || path.join(root, '..', 'posters'));
fs.mkdirSync(out, { recursive: true });
const POSTERS = [
  ['poster-1-tour-map.png', 23.3],   // the tour map, just after the reveal
  ['poster-2-step.png', 31.3],       // step 1: auth.ts lines 4–10 lit, the explanation under the code
  ['poster-3-final.png', 74.6],      // the final frame
];
const film = await openFilm();
// play forward so every tween starts exactly as in the film
let t = 0;
for (const [name, at] of POSTERS) {
  for (; t < at; t += 1 / 60) await film.page.evaluate((x) => window.__seek(x), t);
  await film.page.evaluate((x) => window.__seek(x), at);
  await film.page.screenshot({ path: path.join(out, name) });
  console.log(name, at);
}
await film.close();
