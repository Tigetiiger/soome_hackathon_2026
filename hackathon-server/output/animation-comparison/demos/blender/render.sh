#!/usr/bin/env bash
# Render the Blender demo with Cycles on CPU and encode out/blender_calibration_surface.mp4.
# Defaults: 1920x1080, 16 samples + OIDN denoise (~12 s/frame on 16 CPU cores, ~45 s on 4).
#
# Resumable: frames already in out/frames/ are kept and skipped, so after an
# interruption just run ./render.sh again to continue where it stopped.
#   FRESH=1 ./render.sh        delete existing frames and start over
#   ENCODE_ONLY=1 ./render.sh  just encode the frames rendered so far (partial clip)
#   SCALE=50 ./render.sh       quick 960x540 preview (use FRESH=1 when changing SCALE)
set -euo pipefail
cd "$(dirname "$0")"
SCALE=${SCALE:-100}; SAMPLES=${SAMPLES:-16}
[ "${FRESH:-0}" = "1" ] && rm -rf out/frames
mkdir -p out/frames
rm -f out/frames/*.tmp.png   # leftovers from an interrupted frame
if [ "${ENCODE_ONLY:-0}" != "1" ]; then
  echo "resuming with $(ls out/frames | wc -l) of 240 frames already rendered"
  time ../../.venv-blender/bin/python surface.py --scale "$SCALE" --samples "$SAMPLES" 2>&1 | grep -E '^FRAME|Error' || true
fi
# ffmpeg's image2 reader stops at the first missing number, so a partial run encodes f0001..fN.
../../bin/ffmpeg -y -loglevel error -framerate 30 -i out/frames/f%04d.png \
  -vf "scale=1920:1080:flags=lanczos" -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow \
  -movflags +faststart out/blender_calibration_surface.mp4
echo "wrote out/blender_calibration_surface.mp4 from $(ls out/frames | wc -l) frames"
