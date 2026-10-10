// Exports the sound cues the film registers (window.SFX_CUES) to data/sfx-cues.json for the mix.
import fs from 'node:fs';
import path from 'node:path';
import { openFilm, root } from './page.mjs';

const film = await openFilm();
const data = await film.page.evaluate(() => ({ duration: window.__duration, cues: window.SFX_CUES }));
await film.close();
fs.writeFileSync(path.join(root, 'data/sfx-cues.json'), JSON.stringify(data, null, 1));
const counts = {};
for (const c of data.cues) counts[c.name] = (counts[c.name] || 0) + 1;
console.log(data.cues.length, 'cues,', data.duration.toFixed(2), 's');
console.log(counts);
