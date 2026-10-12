#!/usr/bin/env bash
# Re-renders the TourCode teaser v2 from source.
#   ./render.sh            picture + sound with the narration in narration/ (no TTS call)
#   VOICE=kokoro ./render.sh   also regenerates the narration with Kokoro (downloads the model)
# Needs: Node 18+, Python 3.11+, ffmpeg, Chromium for Playwright.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
npm install --no-fund --no-audit
[ -d .venv ] || $PY -m venv .venv
.venv/bin/pip install -q -r requirements.txt
PY=.venv/bin/python

if [ "${VOICE:-}" = kokoro ]; then
  mkdir -p models
  [ -f models/kokoro-v1.0.onnx ] || curl -L -o models/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  [ -f models/voices-v1.0.bin ] || curl -L -o models/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
  $PY audio/patch_kokoro.py models/kokoro-v1.0.onnx models/kokoro-v1.0-timed.onnx
  (cd audio && ../$PY voice_kokoro.py ../models/kokoro-v1.0-timed.onnx ../models/voices-v1.0.bin)
fi

node render/snapshot-ui.mjs          # real UI states from ../../assets/ui via webview.js
$PY render/build-logos.py            # one-tone editor/agent/wiki marks
node render/cues.mjs                 # sound cues registered by the film
mkdir -p audio/build ../checks
(cd audio && ../$PY music.py build/music.wav && ../$PY mix.py build/music.wav build/mix.wav ../../checks/loudness.json)
node render/stills.mjs ../checks/stills   # contact sheet of stills before the full render
node render/capture.mjs ../tourcode-teaser-v2.mp4 audio/build/mix.wav --workers "${WORKERS:-3}"
render/posters-from-mp4.sh ../tourcode-teaser-v2.mp4 ../posters   # poster frames cut from the film
