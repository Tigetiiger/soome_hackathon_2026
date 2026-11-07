#!/usr/bin/env bash
# Render the Europress Combi exploded-view / sensor clip and encode out/combi_exploded_sensors.mp4.
#
#   1. build_combi.py       -> combi.blend            (only if missing)
#   2. animate_combi.py     -> out/anchors.json + combi_animated.blend
#   3. animate_combi.py     -> out/frames3d/fNNNN.png (Cycles CPU + OIDN, WORKERS processes)
#   4. compose_overlay.py   -> out/frames/fNNNN.png   (labels, captions, inset, closing card)
#   5. ffmpeg               -> out/combi_exploded_sensors.mp4 (H.264, CRF 18, yuv420p, faststart)
#   6. compose_overlay.py   -> out/poster.jpg, out/contact_sheet.jpg
#
# Resumable: finished frames are kept and skipped, every frame is written to a temporary
# name and renamed when complete, so after an interruption just run ./render.sh again.
#   FRESH=1 ./render.sh        delete model, anchors and all frames, start over
#   ENCODE_ONLY=1 ./render.sh  composite + encode whatever 3D frames exist (partial clip)
#   OVERLAY=1 ./render.sh      re-composite every overlay frame (after editing the copy/layout)
#   SAMPLES=16 WORKERS=2 ./render.sh   (defaults; threads per worker = nproc / WORKERS)
#   SCALE=50 ./render.sh       quick 960x540 3D pass (use FRESH=1 when changing SCALE)
# Long runs:  nohup setsid ./render.sh > logs/render.log 2>&1 &
set -euo pipefail
cd "$(dirname "$0")"
AC=../animation-comparison
PYB=$AC/.venv-blender/bin/python      # bpy 5.2 (Blender as a Python module)
PYP=$AC/.venv/bin/python              # Pillow + numpy for the 2D overlay
FF=$AC/bin/ffmpeg
SAMPLES=${SAMPLES:-16}; SCALE=${SCALE:-100}; WORKERS=${WORKERS:-2}
THREADS=${THREADS:-$(( $(nproc) / WORKERS ))}
mkdir -p out logs qc

if [ "${FRESH:-0}" = "1" ]; then
  rm -rf out/frames3d out/frames out/anchors.json combi.blend combi_animated.blend
fi

if [ "${ENCODE_ONLY:-0}" != "1" ]; then
  [ -f combi.blend ] || $PYB build_combi.py 2>&1 | grep -E "BUILT|Error" || true
  $PYB animate_combi.py --anchors --save-blend 2>&1 | grep -E "ANCHORS|SAVED|Error" || true
  mkdir -p out/frames3d
  rm -f out/frames3d/*.tmp.png          # leftovers from an interrupted frame
  echo "3D pass: $(ls out/frames3d | wc -l) of 451 frames already rendered;" \
       "${WORKERS} workers x ${THREADS} threads, ${SAMPLES} samples + OIDN"
  start=$(date +%s)
  pids=()
  for w in $(seq 0 $((WORKERS - 1))); do
    $PYB animate_combi.py --render --samples "$SAMPLES" --scale "$SCALE" \
      --worker "$w" --workers "$WORKERS" --threads "$THREADS" > "logs/render_w$w.log" 2>&1 &
    pids+=($!)
  done
  for p in "${pids[@]}"; do wait "$p"; done
  echo "3D pass wall time: $(( $(date +%s) - start )) s"
fi

# frames 452-480 (closing card) reuse 3D frame 451: nothing moves after t = 15 s
OVR=""; [ "${OVERLAY:-0}" = "1" ] && OVR="--overwrite"
$PYP compose_overlay.py --frames $OVR --jobs 16

# ffmpeg's image2 reader stops at the first missing number, so a partial run encodes f0001..fN.
$FF -y -loglevel error -framerate 30 -i out/frames/f%04d.png \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -movflags +faststart \
  out/combi_exploded_sensors.mp4
echo "wrote out/combi_exploded_sensors.mp4 from $(ls out/frames | wc -l) frames"
if [ "$(ls out/frames | wc -l)" -ge 480 ]; then
  $PYP compose_overlay.py --sheet
fi
