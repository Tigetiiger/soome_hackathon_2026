#!/usr/bin/env bash
# Render the ManimGL demo to out/CalibrationSurface.mp4 (1920x1080, 30 fps).
set -euo pipefail
cd "$(dirname "$0")"
ROOT=../..
time "$ROOT/.venv-gl/bin/python" render_headless.py surface.py CalibrationSurface \
  -w --config_file custom_config.yml "$@"
