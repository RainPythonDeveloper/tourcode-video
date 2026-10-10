"""Optional: the same narration with ElevenLabs (eleven_v3), as the brief asked.

NOT RUN in the session that made v2: the cloud environment could not reach api.elevenlabs.io.
It writes the same files as voice_kokoro.py (narration/narration.wav, narration/timeline.json,
data/narration.js), so the film and the mix pick the new voice up unchanged; then re-run the
cues, the mix and the capture (see README.md).

The key is read from ~/.config/elevenlabs/api_key (or ELEVENLABS_API_KEY) and never printed.
Word timings come from the API's character alignment (/with-timestamps).
Usage: python voice_elevenlabs.py VOICE_ID
Note: the free ElevenLabs plan does not allow commercial use and requires attribution.
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

import numpy as np

from voice_kokoro import ROOT, place_segments

SR = 24000


def api_key():
    p = Path.home() / ".config/elevenlabs/api_key"
    return (p.read_text().strip() if p.exists() else os.environ.get("ELEVENLABS_API_KEY", "")).strip()


def words_from_alignment(text, al):
    chars, starts, ends = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur, t0, t1 = [], "", None, None
    for ch, a, b in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                words.append({"word": cur, "start": t0, "end": t1})
            cur, t0 = "", None
            continue
        if t0 is None:
            t0 = a
        cur += ch
        t1 = b
    if cur:
        words.append({"word": cur, "start": t0, "end": t1})
    assert [w["word"] for w in words] == text.split(), "alignment does not match the text"
    return words


def main():
    voice_id = sys.argv[1]
    key = api_key()
    if not key:
        raise SystemExit("no ElevenLabs key in ~/.config/elevenlabs/api_key or ELEVENLABS_API_KEY")
    script = json.loads((ROOT / "narration/script.json").read_text())

    def synth(text, speed):
        body = {"text": text, "model_id": "eleven_v3"}
        if abs(speed - 1.0) > 1e-3:
            body["voice_settings"] = {"speed": speed}
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps?output_format=pcm_24000",
            data=json.dumps(body).encode(), headers={"xi-api-key": key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            res = json.loads(r.read())
        pcm = np.frombuffer(base64.b64decode(res["audio_base64"]), dtype="<i2").astype(np.float32) / 32768
        return pcm, SR, words_from_alignment(text, res["alignment"])

    place_segments(script, synth)


if __name__ == "__main__":
    main()
