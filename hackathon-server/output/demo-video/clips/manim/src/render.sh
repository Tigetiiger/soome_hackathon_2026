#!/usr/bin/env bash
# Render the three demo-video Manim clips in parallel and copy them to clips/manim/*.mp4
# Usage: ./render.sh            (final 1920x1080 @ 30 fps)
#        ./render.sh preview    (fast 480p check)
set -euo pipefail
cd "$(dirname "$0")"
MANIM=/home/hackathon/output/animation-comparison/.venv/bin/manim
FFMPEG=/home/hackathon/output/animation-comparison/bin/ffmpeg
if [[ "${1:-}" == "preview" ]]; then RES=854,480; MEDIA=out_preview; else RES=1920,1080; MEDIA=out; fi
declare -A SCENE=([problem]=Problem [solution]=Solution [impact]=Impact)
declare -A FRAMES=([problem]=450 [solution]=390 [impact]=750)
pids=()
for f in problem solution impact; do
  "$MANIM" render -r "$RES" --fps 30 --media_dir "$MEDIA" --disable_caching "$f.py" "${SCENE[$f]}" > "$MEDIA.$f.log" 2>&1 &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done
[[ "${1:-}" == "preview" ]] && exit 0
for f in problem solution impact; do
  src=$(ls "$MEDIA"/videos/"$f"/1080p30/"${SCENE[$f]}".mp4)
  n=${FRAMES[$f]}
  # exact length: clone last frame if short, cut if long; H.264 yuv420p, no audio
  "$FFMPEG" -y -loglevel error -i "$src" -an -vf "tpad=stop_mode=clone:stop=60" -frames:v "$n" \
    -c:v libx264 -pix_fmt yuv420p -crf 16 -preset slow -r 30 -movflags +faststart "../$f.mp4"
done
