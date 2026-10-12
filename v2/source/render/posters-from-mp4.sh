#!/usr/bin/env bash
# Poster frames cut from the finished film (exact frame numbers at 60 fps).
# usage: render/posters-from-mp4.sh FILM.mp4 OUT_DIR
set -euo pipefail
mp4=$1; out=$2; mkdir -p "$out"
for p in "poster-1-tour-map 1398" "poster-2-step 1878" "poster-3-final 4476"; do
  set -- $p
  ffmpeg -v error -y -i "$mp4" \
    -vf "select=eq(n\,$2),scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24" \
    -frames:v 1 -update 1 "$out/$1.png"
  echo "$1.png  frame $2 ($(awk "BEGIN{printf \"%.1f\", $2/60}") s)"
done
