#!/usr/bin/env bash
# Render the Manim CE demo (Cairo renderer, CPU) to out/videos/.../CompactorSensors.mp4
set -euo pipefail
cd "$(dirname "$0")"
time ../../.venv/bin/manim render -r 1920,1080 --fps 30 --media_dir out \
  --disable_caching "$@" diagram.py CompactorSensors
