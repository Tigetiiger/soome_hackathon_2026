#!/usr/bin/env bash
# Render the PyVista demo to out/lift_scatter.mp4 (headless EGL, 1920x1080, 30 fps)
set -euo pipefail
cd "$(dirname "$0")"
export VTK_DEFAULT_OPENGL_WINDOW=${VTK_DEFAULT_OPENGL_WINDOW:-vtkEGLRenderWindow}
time ../../.venv/bin/python scatter.py
