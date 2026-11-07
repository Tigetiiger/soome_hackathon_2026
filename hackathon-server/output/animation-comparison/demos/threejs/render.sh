#!/usr/bin/env bash
# Capture the three.js demo to out/fleet_timeseries.mp4 (headless Chromium + SwiftShader, 1920x1080, 30 fps)
set -euo pipefail
cd "$(dirname "$0")"
[ -d node_modules/three ] || npm install
time node capture.mjs "$@"
