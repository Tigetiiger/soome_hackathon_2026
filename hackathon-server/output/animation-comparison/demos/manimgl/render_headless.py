"""Run ManimGL without a display: force moderngl's standalone context onto EGL
(Mesa llvmpipe here, or a real GPU when available) and pyglet into headless mode."""
import os
import sys

os.environ.setdefault("PYGLET_HEADLESS", "1")
import moderngl  # noqa: E402

_create = moderngl.create_standalone_context
moderngl.create_standalone_context = lambda *a, **k: _create(*a, **{"backend": "egl", **k})

from manimlib.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.argv = ["manimgl", *sys.argv[1:]]
    main()
