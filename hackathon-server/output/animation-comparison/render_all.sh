#!/usr/bin/env bash
# Render every demo sequentially (so the timings in COMPARISON.md are not skewed
# by parallel jobs) and copy the results into media/.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p media logs
run() {  # name, command...
  local name=$1; shift
  local t0=$(date +%s%N)
  if "$@" > "logs/$name.log" 2>&1; then status=ok; else status=FAILED; fi
  local ms=$(( ($(date +%s%N) - t0) / 1000000 ))
  printf '%-10s %-7s %4d.%01ds\n' "$name" "$status" $((ms / 1000)) $(((ms % 1000) / 100)) | tee -a logs/timings.txt
}
: > logs/timings.txt
run manimce  demos/manimce/render.sh
run manimgl  demos/manimgl/render.sh
run pyvista  demos/pyvista/render.sh
run threejs  demos/threejs/render.sh
[ -f demos/blender/render.sh ] && run blender demos/blender/render.sh
cp demos/manimce/out/videos/diagram/1080p30/CompactorSensors.mp4 media/manimce_compactor_diagram.mp4 2>/dev/null
cp demos/manimgl/out/CalibrationSurface.mp4 media/manimgl_calibration_surface.mp4 2>/dev/null
cp demos/pyvista/out/lift_scatter.mp4 media/pyvista_lift_scatter.mp4 2>/dev/null
cp demos/threejs/out/fleet_timeseries.mp4 media/threejs_fleet_timeseries.mp4 2>/dev/null
cp demos/blender/out/blender_calibration_surface.mp4 media/blender_calibration_surface.mp4 2>/dev/null
ls -la media
