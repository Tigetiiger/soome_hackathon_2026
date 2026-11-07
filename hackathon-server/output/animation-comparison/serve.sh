#!/usr/bin/env bash
# Serve the comparison folder so the interactive three.js demo (ES modules + fetch) works.
cd "$(dirname "$0")" && echo "open http://localhost:${1:-8000}/  (gallery)  or  /demos/threejs/index.html" && python3 -m http.server "${1:-8000}" --bind 127.0.0.1
