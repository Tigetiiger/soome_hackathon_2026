"""timeline.py - the storyboard timing shared by animate_combi.py (Blender) and
compose_overlay.py (Pillow).  Pure Python, no dependencies.  Times are in seconds."""

FPS = 30
N_FRAMES = 480                 # 16 s at 30 fps
LAST_3D_FRAME = 451            # t = 15.0 s: nothing moves afterwards, the closing card reuses it


def t_of(frame: int) -> float:
    return (frame - 1) / FPS


def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease(x: float) -> float:
    """smootherstep: zero velocity and acceleration at both ends."""
    x = clamp01(x)
    return x * x * x * (x * (6 * x - 15) + 10)


def seg(t: float, t0: float, t1: float) -> float:
    return ease((t - t0) / (t1 - t0))


# exploded view: part -> (disassemble start, end, reassemble start, end)
EXPLODE = {
    "lid":        (3.00, 4.20, 13.80, 14.90),
    "cover":      (3.15, 4.35, 13.65, 14.80),
    "side_panel": (3.50, 4.80, 13.30, 14.50),
    "container":  (4.00, 5.50, 12.80, 14.10),
    "door":       (4.70, 6.10, 12.40, 13.50),
    "lift":       (5.40, 6.70, 12.00, 12.90),
}


def explode(part: str, t: float) -> float:
    a, b, c, d = EXPLODE[part]
    return seg(t, a, b) if t < (b + c) / 2 else 1.0 - seg(t, c, d)


# sensors light up one by one
SENSOR_ORDER = ["pressure", "ram", "loadcell", "gps", "tilt", "door", "lid", "oiltemp"]
SENSOR_T0, SENSOR_DT = 7.0, 0.33


def sensor_on(key: str) -> float:
    return SENSOR_T0 + SENSOR_DT * SENSOR_ORDER.index(key)


# the ram strokes once into the container mouth and back
RAM_EXT = (9.70, 11.00)
RAM_RET = (11.25, 12.00)


def ram_progress(t: float) -> float:
    """0 = retracted, 1 = face 25 cm into the container mouth."""
    return seg(t, *RAM_EXT) - seg(t, *RAM_RET)


TITLE = (0.2, 3.1)               # title card window
INTERNALS_CAPTION = (3.35, 14.75)  # "Internal layout: schematic" visible whenever internals show
LABELS_OUT = (12.0, 12.5)        # sensor labels fade; glowing dots remain
MOUTH_GHOST = (9.35, 12.1)
CARD_IN = (15.0, 15.35)          # closing card fade-in

# camera keys: t, target (x, y, z), azimuth deg, elevation deg, distance m
CAM_KEYS = [
    (0.0, (3.25, 0.00, 1.20), 213.0, 14.0, 14.6),
    (3.0, (3.30, 0.00, 1.25), 228.0, 16.0, 14.0),
    (7.0, (4.35, -0.45, 1.55), 238.0, 23.0, 17.2),
    (12.0, (4.25, -0.45, 1.50), 242.0, 24.0, 16.6),
    (15.0, (3.30, 0.00, 1.35), 230.0, 17.0, 14.2),
    (16.0, (3.30, 0.00, 1.35), 230.0, 17.0, 14.2),
]


def _hermite(p0, p1, m0, m1, h, s):
    s2, s3 = s * s, s * s * s
    return ((2 * s3 - 3 * s2 + 1) * p0 + (s3 - 2 * s2 + s) * h * m0
            + (-2 * s3 + 3 * s2) * p1 + (s3 - s2) * h * m1)


def camera_state(t: float):
    """Catmull-Rom through CAM_KEYS (continuous velocity), flat at both ends."""
    ts = [k[0] for k in CAM_KEYS]
    vals = [[*k[1], k[2], k[3], k[4]] for k in CAM_KEYS]
    t = min(max(t, ts[0]), ts[-1])
    i = max(j for j in range(len(ts) - 1) if ts[j] <= t)
    h = ts[i + 1] - ts[i]
    s = (t - ts[i]) / h
    out = []
    for c in range(len(vals[0])):
        def slope(k):
            if k == 0 or k == len(ts) - 1:
                return 0.0
            return (vals[k + 1][c] - vals[k - 1][c]) / (ts[k + 1] - ts[k - 1])
        out.append(_hermite(vals[i][c], vals[i + 1][c], slope(i), slope(i + 1), h, s))
    return (out[0], out[1], out[2]), out[3], out[4], out[5]
