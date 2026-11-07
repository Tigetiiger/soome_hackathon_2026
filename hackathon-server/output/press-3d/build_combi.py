"""build_combi.py - procedural Europress Combi (20 m3) press-container, in metres.

EXTERIOR follows the dimension drawing on page 2 of the Europress Combi brochure
(refs/Europress-Combi-product-brochure_ENG.pdf).  Every exterior number below is tagged
    [D] printed on the drawing / spec table, or
    [M] measured from the to-scale drawing (page rasterised at 400 dpi; 3.927 mm per
        pixel, calibrated on the printed 6520 and 4090 dimensions, which agree to 0.1 %).
See notes/dimensions.md for the full table.

INTERIOR is SCHEMATIC: a standard press-container layout (ram, two double-acting
cylinders, power unit, control box), plausibly sized.  It is NOT Europress CAD.

Axes: +X runs from the front (hook-lift bail, x = 0) to the rear discharge door
(x = 6.52); -Y is the near side seen in the brochure side view (control panel side);
+Z is up, z = 0 is the underside of the rollers.

    .venv-blender/bin/python build_combi.py [--out combi.blend]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy  # noqa: I001  (bpy must be imported before bmesh in the pip module)
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
AC = Path("/home/hackathon/output/animation-comparison")
STYLE = json.loads((AC / "shared" / "style.json").read_text())
C = STYLE["colors"]
FONT_DIR = AC / "assets" / "fonts"

# ----------------------------------------------------------------------------------
# Drawing calibration (side view: columns -> x, rows -> z; top view: rows -> y)
# ----------------------------------------------------------------------------------
MM_PER_PX = 3.927        # [M] 6520 mm / 1660 px and 4090 mm / 1042 px at 400 dpi
COL0 = 82                # [M] column of the front-most point (hook-lift bail)
ROW0 = 827               # [M] row of the underside of the rails
ROW_Y0 = 366.5           # [M] top view: row of the machine centre line
W = 0.030                # [D] "1480 + wheels 30": rollers add 30 mm below the rails


def X(col: float) -> float:
    """Side-view drawing column -> x in metres (front = 0)."""
    return (col - COL0) * MM_PER_PX / 1000.0


def Z(row: float) -> float:
    """Side-view drawing row -> z in metres above the roller underside."""
    return (ROW0 - row) * MM_PER_PX / 1000.0 + W


def Y(row: float) -> float:
    """Top-view drawing row -> y in metres (+Y = far side, up in the top view)."""
    return (ROW_Y0 - row) * MM_PER_PX / 1000.0


L_MAX = 6.520            # [D] overall length, max
L_CONT = 4.090           # [D] container body length
X_CF = X(607)            # [M] 2.062  container front face (start of the 4090 dimension)
X_CR = X_CF + L_CONT     # [D+M] 6.152 container body rear
HW_CONT = 2.350 / 2      # [D] container width 2350
HW_PRESS = 1.720 / 2     # [D] press-section width 1720
HW_MAX = 2.500 / 2       # [D] overall width, max 2500
H_TOP = 2.650 + W        # [D] height "2650 + wheels" (top of the rear door frame)
H_INFEED = 1.480 + W     # [D] infeed height "1480 + wheels 30" (front edge of the lid)
Z_PRESS_TOP = Z(477.5)   # [M] 1.402  top deck of the press section
Z_RAIL_TOP = Z(781)      # [M] 0.211  top of the hook-lift rails
Z_FLOOR = Z(763)         # [M] 0.281  container floor
OPEN_L, OPEN_W = 0.900, 1.500   # [D] infeed aperture net 1500 x 900 (top view: 900 along X, 1500 across)
X_OPEN0 = X_CF - OPEN_L         # [D+M] 1.162 front edge of the infeed opening

# Lid line (side view): front-low to rear-high, hinged at the rear
LID_P0 = (X(165), H_INFEED)      # [M] x 0.326, [D] z 1480 + W
LID_P1 = (X(593), Z(320))        # [M] x 2.007, z 1.991 + W

# ----------------------------------------------------------------------------------
# Schematic internals (NOT from the drawing; plausibly sized, see notes/dimensions.md)
# ----------------------------------------------------------------------------------
RAM_W, RAM_H = 1.500, 0.900      # ram face fills the chamber cross-section (brief)
RAM_Z0 = Z_FLOOR + 0.005
RAM_DEPTH = 0.330
RAM_FACE_RETRACTED = X_OPEN0                 # fully clear of the infeed opening
RAM_ENTRY = 0.250                            # 20-30 cm into the container (Europress)
RAM_FACE_EXTENDED = X_CF + RAM_ENTRY
RAM_STROKE = RAM_FACE_EXTENDED - RAM_FACE_RETRACTED   # ~1.15 m
CYL_Y = 0.420
CYL_Z = RAM_Z0 + 0.42
CYL_BASE_X = 0.300
# Telescopic double-acting cylinders: barrel bore 125 mm (outer 150), three moving
# stages so a ~1.15 m stroke fits between the front wall and the retracted ram.
CYL_STAGES = [  # (name, outer radius, closed front x, length)
    ("barrel", 0.075, 0.770, 0.470),
    ("stage1", 0.0625, 0.790, 0.450),
    ("stage2", 0.050, 0.810, 0.450),
    ("rod", 0.0375, RAM_FACE_RETRACTED - RAM_DEPTH, 0.450),
]

PLATFORM_TOP = 0.300             # schematic SMART Scale platform height
LOADCELL_XY = [(0.15, -0.71), (0.15, 0.71), (6.37, -0.71), (6.37, 0.71)]

# Sensor / label anchors in machine coordinates: key -> (group, (x, y, z))
SENSORS = {
    "pressure": ("press", (0.470, -0.330, 1.330)),
    "ram":      ("ram", (RAM_FACE_RETRACTED + 0.005, -0.40, RAM_Z0 + RAM_H * 0.62)),
    "gps":      ("press", (0.820, -0.735, 1.300)),
    "tilt":     ("press", (0.440, -0.735, 1.120)),
    "door":     ("container", (6.105, -1.205, 1.330)),
    "lid":      ("side_panel", (1.990, -0.885, 1.895)),   # on the near hopper cheek
    "oiltemp":  ("press", (0.750, -0.120, 1.205)),
}


# ----------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------
def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgba(h: str, a: float = 1.0):
    h = h.lstrip("#")
    return (*[srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)], a)


def rrect_xz(x0, x1, z0, z1, r, n=6):
    """Rounded rectangle outline in the XZ plane."""
    pts = []
    for cx, cz, a0 in ((x1 - r, z0 + r, -90), (x1 - r, z1 - r, 0), (x0 + r, z1 - r, 90),
                       (x0 + r, z0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def principled(name, hex_color, rough=0.45, metal=0.0, coat=0.0, aniso=0.0, spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = rgba(hex_color)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.15
    if aniso:
        b.inputs["Anisotropic"].default_value = aniso
    b.inputs["Specular IOR Level"].default_value = spec
    m.diffuse_color = rgba(hex_color)
    return m


def sensor_material(name):
    """Dark sensor body; Emission Strength is keyed by animate_combi.py when it lights up."""
    m = principled(name, "#22282F", rough=0.5)
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Emission Color"].default_value = rgba(C["teal"])
    b.inputs["Emission Strength"].default_value = 0.0
    return m


def fade_emission_material(name, hex_color, strength=2.0):
    """Mix(Transparent, Emission); the mix factor (0 = invisible) is keyed by the animator."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba(hex_color)
    em.inputs["Strength"].default_value = strength
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.name = "fade"
    mix.inputs["Fac"].default_value = 0.0
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def floor_material(name, hex_floor, hex_bg, center, r0, r1):
    """Studio floor that blends into the background colour with distance (no horizon line)."""
    m = principled(name, hex_floor, rough=0.55, spec=0.3)
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = center
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = r0
    mr.inputs["From Max"].default_value = r1
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba(hex_bg)
    em.inputs["Strength"].default_value = 1.0
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Position"], sub.inputs[0])
    nt.links.new(sub.outputs["Vector"], ln.inputs[0])
    nt.links.new(ln.outputs["Value"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], mix.inputs["Fac"])
    nt.links.new(bsdf.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


class Builder:
    def __init__(self):
        self.colls = {}
        self.groups = {}       # name -> (empty, machine-space origin Vector)

    # collections ----------------------------------------------------------------
    def coll(self, name):
        if name not in self.colls:
            c = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(c)
            self.colls[name] = c
        return self.colls[name]

    # groups (animated empties) --------------------------------------------------
    def group(self, name, parent=None, origin=(0, 0, 0)):
        e = bpy.data.objects.new(f"grp_{name}", None)
        e.empty_display_size = 0.3
        self.coll("rig").objects.link(e)
        origin = Vector(origin)
        if parent is not None:
            pe, po = self.groups[parent]
            e.parent = pe
            e.location = origin - po
        else:
            e.location = origin
        self.groups[name] = (e, origin)
        return e

    def attach(self, ob, group):
        if group is None:
            return ob
        e, origin = self.groups[group]
        ob.parent = e
        ob.location = Vector(ob.location) - origin
        return ob

    # primitives -----------------------------------------------------------------
    def _finish(self, bm, name, mat, coll, loc, group):
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        if mat is not None:
            me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        ob.location = loc
        self.coll(coll).objects.link(ob)
        return self.attach(ob, group)

    @staticmethod
    def bevel(ob, width, segments=1):
        mod = ob.modifiers.new("bevel", "BEVEL")
        mod.width = width
        mod.segments = segments
        mod.limit_method = "ANGLE"
        return mod

    def box(self, name, x0, x1, y0, y1, z0, z1, mat, coll="exterior", group=None,
            bevel=0.004, segments=1):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(x1 - x0, y1 - y0, z1 - z0), verts=bm.verts)
        ob = self._finish(bm, name, mat, coll, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), group)
        if bevel:
            self.bevel(ob, min(bevel, 0.3 * min(x1 - x0, y1 - y0, z1 - z0)), segments)
        return ob

    def cyl(self, name, p0, p1, r, mat, coll="exterior", group=None, seg=32, r2=None):
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r, radius2=r if r2 is None else r2, depth=d.length)
        for f in bm.faces:
            f.smooth = abs(f.normal.z) < 0.7
        ob = self._finish(bm, name, mat, coll, (p0 + p1) / 2, group)
        ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        return ob

    def prism_xz(self, name, pts, y0, y1, mat, coll="exterior", group=None, bevel=0.0):
        """Polygon in the XZ plane (machine coords) extruded from y0 to y1."""
        bm = bmesh.new()
        a = [bm.verts.new((x, y0, z)) for x, z in pts]
        b = [bm.verts.new((x, y1, z)) for x, z in pts]
        bm.faces.new(a)
        bm.faces.new(b[::-1])
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = self._finish(bm, name, mat, coll, (0, 0, 0), group)
        if bevel:
            self.bevel(ob, bevel)
        return ob

    def prism_xy(self, name, pts, z0, z1, mat, coll="exterior", group=None, bevel=0.0):
        """Polygon in the XY plane extruded from z0 to z1."""
        bm = bmesh.new()
        a = [bm.verts.new((x, y, z0)) for x, y in pts]
        b = [bm.verts.new((x, y, z1)) for x, y in pts]
        bm.faces.new(a)
        bm.faces.new(b[::-1])
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = self._finish(bm, name, mat, coll, (0, 0, 0), group)
        if bevel:
            self.bevel(ob, bevel)
        return ob

    def sloped_plate(self, name, p0, p1, thick, y0, y1, mat, coll="exterior", group=None,
                     bevel=0.004):
        """Plate whose top surface runs along the XZ line p0 -> p1."""
        (x0, z0), (x1, z1) = p0, p1
        dx, dz = x1 - x0, z1 - z0
        L = math.hypot(dx, dz)
        nx, nz = dz / L * thick, -dx / L * thick       # downward normal * thickness
        pts = [(x0, z0), (x1, z1), (x1 + nx, z1 + nz), (x0 + nx, z0 + nz)]
        return self.prism_xz(name, pts, y0, y1, mat, coll, group, bevel)

    def tube(self, name, pts, r, mat, coll="internals_schematic", group=None):
        cu = bpy.data.curves.new(name, "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = r
        cu.bevel_resolution = 3
        cu.use_fill_caps = True
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = "AUTO"
        cu.materials.append(mat)
        ob = bpy.data.objects.new(name, cu)
        self.coll(coll).objects.link(ob)
        return self.attach(ob, group)

    def text(self, name, body, size, font_file, mat, loc, rot, coll="exterior", group=None,
             extrude=0.0015, align="CENTER"):
        cu = bpy.data.curves.new(name, "FONT")
        cu.body = body
        cu.font = bpy.data.fonts.load(str(FONT_DIR / font_file), check_existing=True)
        cu.size = size
        cu.extrude = extrude
        cu.align_x = align
        cu.align_y = "CENTER"
        cu.materials.append(mat)
        ob = bpy.data.objects.new(name, cu)
        ob.location = loc
        ob.rotation_euler = rot
        self.coll(coll).objects.link(ob)
        return self.attach(ob, group)

    def anchor(self, name, loc, group):
        e = bpy.data.objects.new(name, None)
        e.empty_display_size = 0.05
        e.location = loc
        self.coll("sensors").objects.link(e)
        return self.attach(e, group)


# ----------------------------------------------------------------------------------
# model
# ----------------------------------------------------------------------------------
def build(out: Path) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    B = Builder()
    for c in ("exterior", "internals_schematic", "sensors", "platform", "studio", "rig"):
        B.coll(c)

    M = {
        "blue": principled("paint_europress_blue", "#1F4FA4", rough=0.36, coat=0.35),
        "frame": principled("steel_frame_dark", "#2C3239", rough=0.48, metal=0.65),
        "platform": principled("steel_platform", "#3A4048", rough=0.52, metal=0.7),
        "galv": principled("steel_galvanised", "#9AA2AB", rough=0.38, metal=1.0),
        "barrel": principled("cyl_barrel_brushed", "#8E969F", rough=0.30, metal=1.0, aniso=0.6),
        "rod": principled("cyl_rod_chrome", "#D9DEE3", rough=0.10, metal=1.0, aniso=0.3),
        "ram": principled("ram_paint_grey", "#5C6570", rough=0.42, metal=0.2),
        "liner": principled("chamber_steel", "#3E454E", rough=0.55, metal=0.5),
        "tank": principled("tank_paint", "#36404B", rough=0.45, metal=0.3),
        "motor": principled("motor_paint", "#4A5868", rough=0.40, metal=0.3),
        "alu": principled("valve_block_alu", "#AEB5BD", rough=0.32, metal=1.0),
        "plastic": principled("plastic_matte_panel", "#1A1E23", rough=0.68),
        "plastic_mid": principled("plastic_module_grey", "#5A626C", rough=0.6),
        "rubber": principled("rubber", "#121417", rough=0.85),
        "hose": principled("hose_rubber", "#16191D", rough=0.7),
        "letter": principled("lettering_white", "#EEF2F6", rough=0.4, coat=0.3),
        "estop": principled("estop_red", "#C2302B", rough=0.35),
        "estop_ring": principled("estop_yellow", "#E1B21C", rough=0.4),
        "lamp_g": principled("lamp_green", "#3FA34D", rough=0.3),
        "floor": floor_material("studio_floor", "#141B24", C["bg"], (3.6, 0, 0), 6.0, 20.0),
    }
    S = {k: sensor_material(f"sensor_{k}") for k in list(SENSORS) + ["loadcell"]}
    ram_glow = fade_emission_material("ram_face_glow", C["teal"], 3.0)
    mouth_ghost = fade_emission_material("container_mouth_ghost", C["teal"], 1.6)

    # ---------------- groups (animated empties) ------------------------------------
    B.group("machine")                                   # lifts off the platform
    B.group("press", "machine")                          # static press section
    B.group("side_panel", "press")                       # -Y side panel slides out
    B.group("lid", "press", origin=(LID_P1[0], 0, LID_P1[1]))   # hopper lid lifts
    B.group("cover", "press")                            # top service cover lifts
    B.group("ram", "press")                              # ram strokes along +X
    for side in ("L", "R"):
        for name, *_ in CYL_STAGES[1:]:
            B.group(f"cyl_{side}_{name}", "press")
    B.group("container", "machine")                      # container slides back
    hinge = (X(1688), HW_CONT + 0.035, 0.0)
    B.group("door", "container", origin=hinge)           # rear door swings on +Y hinges

    # ================= PLATFORM (optional SMART Scale; positions per Europress) ======
    P = "platform"
    for sy in (-1, 1):
        B.box(f"platform_rail_{'L' if sy < 0 else 'R'}", 0.05, 6.47, sy * 0.47, sy * 0.59,
              0.135, PLATFORM_TOP, M["platform"], P, bevel=0.006)
    for i, x in enumerate((0.55, 2.2, 4.3, 5.95)):
        B.box(f"platform_cross_{i}", x - 0.06, x + 0.06, -0.47, 0.47, 0.16, 0.28,
              M["platform"], P, bevel=0.005)
    for i, (x, y) in enumerate(LOADCELL_XY):
        sy = 1 if y > 0 else -1
        B.box(f"platform_leg_{i}", x - 0.09, x + 0.09, sy * 0.59, sy * 0.80, 0.135,
              PLATFORM_TOP, M["platform"], P, bevel=0.005)
        B.box(f"platform_foot_top_{i}", x - 0.11, x + 0.11, y - 0.10, y + 0.10, 0.105,
              0.135, M["galv"], P, bevel=0.003)
        B.box(f"platform_base_plate_{i}", x - 0.16, x + 0.16, y - 0.14, y + 0.14, 0.0,
              0.02, M["galv"], P, bevel=0.003)
        B.box(f"platform_base_block_{i}", x - 0.08, x + 0.08, y - 0.08, y + 0.08, 0.02,
              0.05, M["galv"], P, bevel=0.003)
        # load cell (sensor 3): one per corner, per the Europress Scale brochure
        B.cyl(f"sensor_loadcell_{i}", (x, y, 0.05), (x, y, 0.105), 0.055, S["loadcell"],
              "sensors")
        B.anchor(f"anchor_loadcell_{i}", (x, y, 0.08), None)

    # ================= SUBFRAME / ROLLERS (exterior) =================================
    E = "exterior"
    xr_f, xr_r = X(125), X(1665)            # [M] roller centres 0.169 / 6.217
    for sy in (-1, 1):
        s = "L" if sy < 0 else "R"
        B.box(f"hooklift_rail_{s}", xr_f + 0.10, xr_r - 0.10, sy * 0.48, sy * 0.58, W,
              Z_RAIL_TOP, M["frame"], E, "machine", bevel=0.006)
        for x, nm in ((xr_f, "front"), (xr_r, "rear")):
            B.cyl(f"roller_{nm}_{s}", (x, sy * 0.495, 0.075), (x, sy * 0.565, 0.075), 0.075,
                  M["rubber"], E, "machine")
            B.cyl(f"roller_hub_{nm}_{s}", (x, sy * 0.48, 0.075), (x, sy * 0.58, 0.075), 0.03,
                  M["galv"], E, "machine")
            for k, yy in enumerate((0.47, 0.58)):
                B.box(f"roller_cheek_{nm}_{s}_{k}", x - 0.10, x + 0.10, sy * yy,
                      sy * (yy + 0.012), 0.06, Z_RAIL_TOP, M["frame"], E, "machine", bevel=0.004)
    # front cross beam with end blocks (top view: full ~2.49 m width; height not drawn) [M]
    B.box("front_cross_beam", X(126), X(154), -1.245, 1.245, 0.17, 0.37, M["blue"], E,
          "machine", bevel=0.006)
    for sy in (-1, 1):
        B.box(f"front_end_block_{'L' if sy < 0 else 'R'}", X(100), X(130), sy * 1.045,
              sy * 1.245, 0.19, 0.37, M["blue"], E, "machine", bevel=0.006)

    # ================= PRESS SECTION (exterior) =====================================
    G = "press"
    xf0, xf1 = X(106), X(152.5)                 # [M] 0.094 - 0.277 front posts
    for sy in (-1, 1):
        s = "L" if sy < 0 else "R"
        B.box(f"front_post_{s}", xf0, xf1, sy * (HW_PRESS - 0.13), sy * HW_PRESS, W,
              Z_PRESS_TOP, M["blue"], E, G, bevel=0.008)
        # bail lugs
        B.box(f"bail_lug_{s}", 0.07, 0.24, sy * 0.27, sy * 0.31, Z_PRESS_TOP - 0.06,
              Z(430), M["blue"], E, G, bevel=0.006)
    B.box("front_wall", xf1 - 0.03, xf1, -(HW_PRESS - 0.13), HW_PRESS - 0.13, Z_RAIL_TOP,
          Z_PRESS_TOP, M["blue"], E, G, bevel=0.004)
    # hook-lift bail: C-shaped bar, apex at the front-most point x = 0            [M]
    zb, zt = Z(442.5), Z(420)
    B.tube("hooklift_bail", [(0.15, -0.29, zb), (0.04, -0.20, zb + 0.06), (0.0, 0.0, zt),
                             (0.04, 0.20, zb + 0.06), (0.15, 0.29, zb)], 0.026,
           M["frame"], E, G)

    # side panels: plate + ribs. The -Y panel (with the control panel) slides out.
    zb_side, zt_side = Z_RAIL_TOP, Z_PRESS_TOP
    for sy, grp in ((-1, "side_panel"), (1, G)):
        s = "L" if sy < 0 else "R"
        y_out = sy * HW_PRESS
        B.box(f"press_side_plate_{s}", xf1, X_CF, y_out - sy * 0.008, y_out, zb_side,
              zt_side, M["blue"], E, grp, bevel=0.003)
        ribs = [(Z(607.5), Z(572.5), 0.040),   # [M] deep band 0.892 - 1.029
                (Z(714), Z(709), 0.025),       # [M] rib at 0.48
                (Z(786), Z(777.5), 0.020),     # [M] bottom flange
                (zt_side - 0.025, zt_side, 0.025)]
        for i, (z0, z1, d) in enumerate(ribs):
            B.box(f"press_side_rib_{s}_{i}", xf1, X_CF - 0.03, y_out, y_out + sy * d, z0, z1,
                  M["blue"], E, grp, bevel=0.004)
        B.box(f"press_side_flange_{s}", X_CF - 0.035, X_CF, y_out, y_out + sy * 0.03,
              zb_side, zt_side, M["blue"], E, grp, bevel=0.004)
    # control panel (key switch + emergency stop) in the drawing's rounded rectangle [M]
    cp_x0, cp_x1, cp_z0, cp_z1 = X(159), X(325), Z(570), Z(482.5)
    yp = -HW_PRESS
    B.prism_xz("control_panel_frame", rrect_xz(cp_x0, cp_x1, cp_z0, cp_z1 - 0.012, 0.045),
               yp - 0.022, yp, M["plastic"], E, "side_panel", bevel=0.003)
    B.prism_xz("control_panel_face", rrect_xz(cp_x0 + 0.17, cp_x1 - 0.17, cp_z0 + 0.05,
                                               cp_z1 - 0.06, 0.02),
               yp - 0.03, yp - 0.02, M["plastic_mid"], E, "side_panel", bevel=0.002)
    zc = (cp_z0 + cp_z1) / 2
    xc = (cp_x0 + cp_x1) / 2
    B.cyl("estop_ring", (xc + 0.09, yp - 0.03, zc - 0.05), (xc + 0.09, yp - 0.045, zc - 0.05),
          0.045, M["estop_ring"], E, "side_panel")
    B.cyl("estop_button", (xc + 0.09, yp - 0.045, zc - 0.05), (xc + 0.09, yp - 0.085, zc - 0.05),
          0.032, M["estop"], E, "side_panel")
    B.cyl("key_switch", (xc - 0.06, yp - 0.03, zc + 0.05), (xc - 0.06, yp - 0.05, zc + 0.05),
          0.022, M["galv"], E, "side_panel")
    for i, dx in enumerate((-0.09, -0.04, 0.01)):
        B.cyl(f"indicator_lamp_{i}", (xc + dx, yp - 0.03, zc - 0.06),
              (xc + dx, yp - 0.04, zc - 0.06), 0.011, M["lamp_g"], E, "side_panel")

    # top deck (service cover) in front of the infeed opening, with hatch plate     [M]
    B.box("press_top_deck", xf1, X_OPEN0, -HW_PRESS, HW_PRESS, Z_PRESS_TOP - 0.010,
          Z_PRESS_TOP, M["blue"], E, "cover", bevel=0.003)
    B.box("press_top_hatch", X(169), X(266), Y(527), Y(207), Z_PRESS_TOP, Z_PRESS_TOP + 0.008,
          M["blue"], E, "cover", bevel=0.003)
    # rim around the infeed opening (fixed)
    for sy in (-1, 1):
        B.box(f"opening_rim_{'L' if sy < 0 else 'R'}", X_OPEN0, X_CF, sy * OPEN_W / 2,
              sy * HW_PRESS, Z_PRESS_TOP - 0.02, Z_PRESS_TOP, M["blue"], E, G, bevel=0.003)
    # hopper side cheeks under the sloping lid (fixed)                             [M]
    cheek = [(LID_P0[0], Z_PRESS_TOP), (LID_P0[0], LID_P0[1] - 0.026),
             (LID_P1[0], LID_P1[1] - 0.026), (X_CF, LID_P1[1] - 0.026), (X_CF, Z_PRESS_TOP)]
    for sy in (-1, 1):   # the near (-Y) cheek leaves with the side panel
        B.prism_xz(f"hopper_cheek_{'L' if sy < 0 else 'R'}", cheek, sy * (HW_PRESS - 0.008),
                   sy * HW_PRESS, M["blue"], E, "side_panel" if sy < 0 else G, bevel=0.003)
    # sloping hopper lid with front lip, side skirts, handle, rear hinges, gas strut
    B.sloped_plate("hopper_lid", LID_P0, LID_P1, 0.025, -HW_PRESS - 0.02, HW_PRESS + 0.02,
                   M["blue"], E, "lid", bevel=0.004)
    for sy in (-1, 1):
        s = "L" if sy < 0 else "R"
        B.sloped_plate(f"hopper_lid_skirt_{s}", LID_P0, LID_P1, 0.07, sy * (HW_PRESS + 0.02),
                       sy * (HW_PRESS + 0.008), M["blue"], E, "lid", bevel=0.002)
        B.cyl(f"lid_hinge_{s}", (LID_P1[0] - 0.02, sy * 0.55, LID_P1[1] + 0.01),
              (LID_P1[0] - 0.02, sy * 0.70, LID_P1[1] + 0.01), 0.025, M["blue"], E, "lid")
    B.box("hopper_lid_front_lip", LID_P0[0] - 0.012, LID_P0[0] + 0.01, -HW_PRESS - 0.02,
          HW_PRESS + 0.02, LID_P0[1] - 0.07, LID_P0[1], M["blue"], E, "lid", bevel=0.003)
    B.tube("hopper_lid_handle", [(LID_P0[0] + 0.08, -0.25, LID_P0[1] + 0.03),
                                 (LID_P0[0] + 0.05, 0.0, LID_P0[1] + 0.07),
                                 (LID_P0[0] + 0.08, 0.25, LID_P0[1] + 0.03)], 0.014,
           M["galv"], E, "lid")
    B.cyl("lid_gas_strut_body", (1.35, -HW_PRESS - 0.045, 1.62), (1.62, -HW_PRESS - 0.045, 1.80),
          0.014, M["frame"], E, "lid")
    B.cyl("lid_gas_strut_rod", (1.62, -HW_PRESS - 0.045, 1.80), (1.82, -HW_PRESS - 0.045, 1.93),
          0.007, M["rod"], E, "lid")

    # ================= CONTAINER (exterior) =========================================
    K = "container"
    zc0 = Z_RAIL_TOP                         # posts and door reach down to the rails
    zcb = Z(764)                             # [M] 0.277 underside of the container body
    x_post_f1 = X(641)                       # [M] 2.195 front corner post depth
    x_post_r0, x_post_r1 = X(1619), X(1651)  # [M] 6.036 - 6.161 rear frame
    z_post_f = Z(197)                        # [M] 2.474+W front post top
    roof_f, roof_r = (x_post_f1, Z(213)), (x_post_r0, Z(172))   # [M] sloping roof edge
    yi = HW_CONT - 0.02                      # side wall plane (ribs stand 20 mm proud)

    for sy in (-1, 1):
        s = "L" if sy < 0 else "R"
        B.box(f"container_front_post_{s}", X_CF, x_post_f1, sy * (HW_CONT - 0.08),
              sy * HW_CONT, zc0, z_post_f, M["blue"], E, K, bevel=0.008)
        B.box(f"container_rear_post_{s}", x_post_r0, x_post_r1, sy * (HW_CONT - 0.08),
              sy * HW_CONT, zc0, H_TOP, M["blue"], E, K, bevel=0.008)
        side = [(x_post_f1, zcb), (x_post_r0, zcb), roof_r, roof_f]
        B.prism_xz(f"container_side_{s}", side, sy * (yi - 0.006), sy * yi, M["blue"], E, K)
        # top rail along the sloping roof edge, bottom side rail, two horizontal ribs [M]
        B.sloped_plate(f"container_top_rail_{s}", roof_f, roof_r, 0.065, sy * yi,
                       sy * HW_CONT, M["blue"], E, K, bevel=0.004)
        B.box(f"container_bottom_rail_{s}", x_post_f1, x_post_r0, sy * yi, sy * HW_CONT,
              zcb, Z(742), M["blue"], E, K, bevel=0.005)
        for i, (r0, r1) in enumerate(((544, 536), (487, 473))):
            B.box(f"container_rib_{s}_{i}", x_post_f1, x_post_r0, sy * yi,
                  sy * (HW_CONT - 0.004), Z(r0), Z(r1), M["blue"], E, K, bevel=0.004)
    # floor cross members between the body and the hook-lift rails             [M]
    for i, col in enumerate((737, 917, 1097, 1272, 1452)):
        B.box(f"container_crossmember_{i}", X(col) - 0.05, X(col) + 0.05, -yi, yi,
              zc0, zcb, M["frame"], E, K, bevel=0.003)
    # front wall with the chamber mouth (ram enters here)
    mz0, mz1 = Z_FLOOR, RAM_Z0 + RAM_H + 0.08
    mw = OPEN_W / 2 + 0.01
    yfw = HW_CONT - 0.08
    B.box("container_front_wall_L", X_CF, X_CF + 0.03, -yfw, -mw, zc0, z_post_f, M["blue"], E, K, bevel=0)
    B.box("container_front_wall_R", X_CF, X_CF + 0.03, mw, yfw, zc0, z_post_f, M["blue"], E, K, bevel=0)
    B.box("container_front_wall_top", X_CF, X_CF + 0.03, -mw, mw, mz1, z_post_f, M["blue"], E, K, bevel=0)
    B.box("container_front_wall_sill", X_CF, X_CF + 0.03, -mw, mw, zc0, mz0, M["blue"], E, K, bevel=0)
    B.box("container_front_top_beam", X_CF, x_post_f1, -HW_CONT, HW_CONT, z_post_f - 0.10,
          z_post_f, M["blue"], E, K, bevel=0.006)
    B.box("container_floor", X_CF + 0.03, x_post_r0, -yi, yi, zcb - 0.004, Z_FLOOR, M["frame"],
          E, K, bevel=0)
    # roof: sloping plate with longitudinal ribs (top view rows -> y)            [M]
    roof_line_f = (X_CF, roof_f[1] + (roof_r[1] - roof_f[1]) * (X_CF - roof_f[0]) / (roof_r[0] - roof_f[0]))
    B.sloped_plate("container_roof", roof_line_f, (x_post_r1, roof_r[1] + 0.004), 0.008,
                   -yi, yi, M["blue"], E, K, bevel=0)
    for i, row in enumerate((100, 120, 175, 265, 469, 557, 614, 634)):
        y = Y(row)
        B.sloped_plate(f"container_roof_rib_{i}", (roof_line_f[0], roof_line_f[1] + 0.03),
                       (x_post_r0, roof_r[1] + 0.034), 0.03, y - 0.02, y + 0.02, M["blue"], E, K)
    B.box("container_rear_top_beam", x_post_r0, x_post_r1, -HW_CONT, HW_CONT, H_TOP - 0.10,
          H_TOP, M["blue"], E, K, bevel=0.006)
    # plain EUROPRESS lettering on the near side (as in the photo; no logo mark)  [M]
    B.text("lettering_EUROPRESS", "EUROPRESS", 0.33, "IBMPlexSans-SemiBold.ttf", M["letter"],
           ((X(935) + X(1418)) / 2, -(yi + 0.0016), Z(361)), (math.pi / 2, 0, 0), E, K)
    # locking handles: vertical shaft + two lever arms hooking the door           [M]
    yl = -HW_CONT - 0.03
    B.cyl("lock_shaft", (X(1547), yl, Z(690)), (X(1547), yl, Z(250)), 0.018, M["galv"], E, K)
    for i, row in enumerate((255, 675)):
        B.box(f"lock_lever_{i}", X(1540), X(1690), yl - 0.015, yl + 0.015, Z(row) - 0.035,
              Z(row) + 0.035, M["galv"], E, K, bevel=0.006)
        B.box(f"lock_shaft_bracket_{i}", X(1535), X(1560), -HW_CONT, yl + 0.02,
              Z(row + 25) - 0.03, Z(row + 25) + 0.03, M["blue"], E, K, bevel=0.003)

    # rear discharge door (tapered profile from the side view), hinged on +Y     [M]
    D = "door"
    door = [(x_post_r1, zc0), (x_post_r1, H_TOP), (X(1688), H_TOP), (X(1711), Z(182)),
            (X(1711), Z(760)), (X(1688), zc0)]
    B.prism_xz("rear_door", door, -HW_CONT, HW_CONT, M["blue"], E, D, bevel=0.004)
    for sy in (-1, 1):
        B.box(f"rear_door_edge_{'L' if sy < 0 else 'R'}", X(1688), X(1711) + 0.01,
              sy * (HW_CONT - 0.07), sy * HW_CONT, Z(760), Z(182), M["blue"], E, D, bevel=0.005)
    for i, z in enumerate((0.55, 1.40, 2.30)):
        B.cyl(f"door_hinge_{i}", (X(1688), HW_CONT + 0.035, z - 0.09),
              (X(1688), HW_CONT + 0.035, z + 0.09), 0.035, M["blue"], E, D)
        B.box(f"door_hinge_plate_{i}", X(1660), X(1700), HW_CONT - 0.05, HW_CONT + 0.03,
              z - 0.06, z + 0.06, M["blue"], E, D, bevel=0.003)
    for i, row in enumerate((255, 675)):
        B.cyl(f"door_lock_pin_{i}", (X(1678), -HW_CONT + 0.01, Z(row)),
              (X(1678), -HW_CONT - 0.06, Z(row)), 0.022, M["galv"], E, D)
    for i, row in enumerate((640, 735)):
        B.box(f"door_wedge_lock_{i}", X(1690), X(1720), -HW_CONT + 0.25, -HW_CONT + 0.45,
              Z(row) - 0.05, Z(row) + 0.05, M["galv"], E, D, bevel=0.004)
    # rear lifting lug at the centre: the rear-most point (MAX 6520)             [D+M]
    B.box("rear_lug", X(1711), L_MAX, -0.10, 0.10, Z(470), Z(400), M["blue"], E, D, bevel=0.01,
          segments=3)
    B.cyl("rear_lug_pin", (L_MAX - 0.05, -0.13, Z(435)), (L_MAX - 0.05, 0.13, Z(435)), 0.03,
          M["galv"], E, D)

    # ================= INTERNALS (SCHEMATIC, not Europress CAD) ====================
    I = "internals_schematic"
    B.box("chamber_floor", xf1, X_CF, -OPEN_W / 2 - 0.01, OPEN_W / 2 + 0.01, Z_RAIL_TOP,
          Z_FLOOR, M["liner"], I, G, bevel=0)
    B.box("chamber_liner_far", RAM_FACE_RETRACTED - RAM_DEPTH - 0.05, X_CF, OPEN_W / 2 + 0.01,
          OPEN_W / 2 + 0.03, Z_FLOOR, mz1, M["liner"], I, G, bevel=0)
    B.box("ram_guide_far", xf1, X_CF, OPEN_W / 2 - 0.01, OPEN_W / 2 + 0.01, RAM_Z0 + RAM_H + 0.005,
          RAM_Z0 + RAM_H + 0.035, M["frame"], I, G, bevel=0.003)
    # ram block (moves along +X)
    rf, rb = RAM_FACE_RETRACTED, RAM_FACE_RETRACTED - RAM_DEPTH
    B.box("ram_face_plate", rf - 0.035, rf, -RAM_W / 2, RAM_W / 2, RAM_Z0, RAM_Z0 + RAM_H,
          M["ram"], I, "ram", bevel=0.008)
    B.box("ram_body", rb, rf - 0.035, -RAM_W / 2 + 0.03, RAM_W / 2 - 0.03, RAM_Z0 + 0.02,
          RAM_Z0 + RAM_H - 0.02, M["ram"], I, "ram", bevel=0.006)
    for i, zz in enumerate((0.30, 0.60)):
        B.box(f"ram_rib_{i}", rb - 0.02, rf - 0.035, -RAM_W / 2 + 0.03, RAM_W / 2 - 0.03,
              RAM_Z0 + RAM_H * zz - 0.02, RAM_Z0 + RAM_H * zz + 0.02, M["frame"], I, "ram", bevel=0.004)
    B.box("ram_top_plate", rb, rf - 0.035, -RAM_W / 2 + 0.02, RAM_W / 2 - 0.02,
          RAM_Z0 + RAM_H - 0.012, RAM_Z0 + RAM_H, M["ram"], I, "ram", bevel=0.003)
    # thin teal frame around the ram face, faded in by the animator
    gx = rf + 0.004
    t = 0.022
    for nm, (y0, y1, z0, z1) in {
        "top": (-RAM_W / 2, RAM_W / 2, RAM_Z0 + RAM_H - t, RAM_Z0 + RAM_H),
        "bot": (-RAM_W / 2, RAM_W / 2, RAM_Z0, RAM_Z0 + t),
        "left": (-RAM_W / 2, -RAM_W / 2 + t, RAM_Z0, RAM_Z0 + RAM_H),
        "right": (RAM_W / 2 - t, RAM_W / 2, RAM_Z0, RAM_Z0 + RAM_H),
    }.items():
        B.box(f"ram_face_glow_{nm}", gx - 0.003, gx + 0.003, y0, y1, z0, z1, ram_glow, "sensors",
              "ram", bevel=0)
    # ghost outline of the container mouth at its assembled position (for the stroke beat)
    for nm, (y0, y1, z0, z1) in {
        "top": (-mw, mw, mz1 - 0.02, mz1),
        "bot": (-mw, mw, mz0, mz0 + 0.02),
        "left": (-mw, -mw + 0.02, mz0, mz1),
        "right": (mw - 0.02, mw, mz0, mz1),
    }.items():
        B.box(f"mouth_ghost_{nm}", X_CF - 0.004, X_CF + 0.004, y0, y1, z0, z1, mouth_ghost,
              "sensors", G, bevel=0)
    B.anchor("anchor_mouth", (X_CF, -mw, mz0 + 0.02), G)
    B.anchor("anchor_ram_face_low", (RAM_FACE_RETRACTED, -RAM_W / 2, RAM_Z0 + 0.02), "ram")

    # two double-acting (telescopic) cylinders behind the ram
    for side, sy in (("L", -1), ("R", 1)):
        y = sy * CYL_Y
        B.box(f"cyl_{side}_base_clevis", xf1, CYL_BASE_X + 0.03, y - 0.06, y + 0.06,
              CYL_Z - 0.08, CYL_Z + 0.08, M["frame"], I, G, bevel=0.006)
        for name, r, front, length in CYL_STAGES:
            grp = G if name == "barrel" else f"cyl_{side}_{name}"
            mat = M["barrel"] if name in ("barrel", "stage1") else M["rod"]
            p0 = (CYL_BASE_X if name == "barrel" else front - length, y, CYL_Z)
            B.cyl(f"cyl_{side}_{name}", p0, (front, y, CYL_Z), r, mat, I, grp)
            if name != "rod":
                B.cyl(f"cyl_{side}_{name}_gland", (front - 0.03, y, CYL_Z), (front, y, CYL_Z),
                      r + 0.008, M["frame"], I, grp)
        B.box(f"cyl_{side}_rod_eye", rb - 0.05, rb, y - 0.05, y + 0.05, CYL_Z - 0.06,
              CYL_Z + 0.06, M["frame"], I, "ram", bevel=0.006)

    # power unit above the cylinders, in front of the retracted ram
    zs = 0.97
    B.box("power_unit_shelf", xf1, 0.80, -0.62, 0.78, zs - 0.02, zs, M["frame"], I, G, bevel=0.003)
    B.box("oil_tank", 0.32, 0.80, -0.55, 0.35, zs, zs + 0.20, M["tank"], I, G, bevel=0.01, segments=2)
    zt_ = zs + 0.20
    B.cyl("oil_filler_cap", (0.37, 0.28, zt_), (0.37, 0.28, zt_ + 0.05), 0.035, M["frame"], I, G)
    B.box("oil_level_gauge", 0.40, 0.48, -0.556, -0.552, zs + 0.05, zs + 0.15, M["plastic_mid"],
          I, G, bevel=0.002)
    mz = zt_ + 0.105
    B.box("motor_feet", 0.40, 0.66, 0.02, 0.20, zt_, zt_ + 0.03, M["frame"], I, G, bevel=0.003)
    B.cyl("motor_5_5kW", (0.37, 0.11, mz), (0.68, 0.11, mz), 0.103, M["motor"], I, G, seg=40)
    B.cyl("motor_fan_cowl", (0.33, 0.11, mz), (0.37, 0.11, mz), 0.098, M["frame"], I, G, seg=40)
    B.cyl("motor_coupling", (0.68, 0.11, mz), (0.72, 0.11, mz), 0.06, M["frame"], I, G)
    B.cyl("pump", (0.72, 0.11, mz), (0.79, 0.11, mz), 0.05, M["alu"], I, G)
    B.box("motor_terminal_box", 0.47, 0.57, 0.11 - 0.06, 0.11 + 0.06, mz + 0.07, mz + 0.11,
          M["motor"], I, G, bevel=0.006)
    B.box("valve_block", 0.41, 0.59, -0.43, -0.23, zt_, zt_ + 0.11, M["alu"], I, G, bevel=0.004)
    for i, xx in enumerate((0.44, 0.50, 0.56)):
        B.box(f"valve_solenoid_{i}", xx - 0.022, xx + 0.022, -0.43, -0.36, zt_ + 0.11,
              zt_ + 0.16, M["plastic"], I, G, bevel=0.004)
    # hydraulic hoses: valve block -> both ends of each cylinder (static base side)
    # leave the valve block on its -Y face, drop beside the tank, run under the shelf
    j = 0
    for side, sy in (("L", -1), ("R", 1)):
        for k, xx in enumerate((CYL_BASE_X + 0.06, 0.70)):
            x_port = 0.45 + 0.035 * j
            end = Vector((xx, sy * CYL_Y, CYL_Z + 0.07))
            pts = [(x_port, -0.43, zt_ + 0.05), (x_port, -0.60, zt_ + 0.02),
                   (x_port + 0.02, -0.66, zs - 0.10), ((x_port + xx) / 2, (sy * CYL_Y - 0.66) / 2,
                                                      zs - 0.14), end]
            B.tube(f"hose_{side}_{k}", pts, 0.011, M["hose"], I, G)
            j += 1
    # control box behind the panel (open towards -Y; the panel is its door)
    cb_y0, cb_y1 = -HW_PRESS + 0.012, -HW_PRESS + 0.17
    cbx0, cbx1, cbz0, cbz1 = cp_x0 + 0.03, cp_x1 - 0.03, cp_z0 + 0.01, cp_z1 - 0.01
    B.box("control_box_back", cbx0, cbx1, cb_y1 - 0.01, cb_y1, cbz0, cbz1, M["plastic"], I, G, bevel=0.004)
    for nm, (x0, x1, z0, z1) in {
        "top": (cbx0, cbx1, cbz1 - 0.012, cbz1), "bot": (cbx0, cbx1, cbz0, cbz0 + 0.012),
        "front": (cbx0, cbx0 + 0.012, cbz0, cbz1), "rear": (cbx1 - 0.012, cbx1, cbz0, cbz1),
    }.items():
        B.box(f"control_box_{nm}", x0, x1, cb_y0, cb_y1, z0, z1, M["plastic"], I, G, bevel=0.003)
    B.box("control_box_din_rail", cbx0 + 0.04, cbx1 - 0.04, cb_y1 - 0.025, cb_y1 - 0.01,
          cbz0 + 0.115, cbz0 + 0.145, M["galv"], I, G, bevel=0)
    for i in range(5):
        xx = cbx0 + 0.20 + i * 0.055
        B.box(f"control_box_module_{i}", xx - 0.024, xx + 0.024, cb_y1 - 0.09, cb_y1 - 0.01,
              cbz0 + 0.07, cbz0 + 0.19, M["plastic_mid"], I, G, bevel=0.003)
    B.tube("transducer_cable", [Vector(SENSORS["pressure"][1]) + Vector((0, 0, 0.03)),
                                (0.62, -0.50, 1.37), (cbx1 - 0.05, cb_y1 - 0.01, cbz1 - 0.05)],
           0.005, M["hose"], I, G)

    # ================= SENSORS (positions schematic except load cells) ============
    SN = "sensors"
    px, py, pz = SENSORS["pressure"][1]
    B.cyl("sensor_pressure_transducer", (px, py, zt_ + 0.11), (px, py, pz), 0.016,
          S["pressure"], SN, G)
    B.cyl("sensor_pressure_connector", (px, py, pz), (px, py, pz + 0.03), 0.012, M["plastic"], SN, G)
    gx_, gy_, gz_ = SENSORS["gps"][1]
    B.box("sensor_gps_5g_module", gx_ - 0.07, gx_ + 0.07, cb_y1 - 0.05, cb_y1 - 0.01, gz_ - 0.045,
          gz_ + 0.045, S["gps"], SN, G, bevel=0.004)
    B.cyl("sensor_gps_antenna", (gx_ + 0.03, cb_y1 - 0.05, gz_ + 0.02), (gx_ + 0.03, cb_y1 - 0.065, gz_ + 0.02),
          0.022, M["plastic"], SN, G)
    tx, ty, tz = SENSORS["tilt"][1]
    B.box("sensor_tilt_movement", tx - 0.035, tx + 0.035, cb_y1 - 0.045, cb_y1 - 0.01, tz - 0.035,
          tz + 0.035, S["tilt"], SN, G, bevel=0.004)
    dx_, dy_, dz_ = SENSORS["door"][1]
    B.box("sensor_door_interlock", dx_ - 0.035, dx_ + 0.035, -HW_CONT - 0.045, -HW_CONT, dz_ - 0.05,
          dz_ + 0.05, S["door"], SN, K, bevel=0.004)
    B.box("door_interlock_actuator", X(1660), X(1690), -HW_CONT - 0.04, -HW_CONT, dz_ - 0.02,
          dz_ + 0.02, M["galv"], SN, D, bevel=0.003)
    lx, ly, lz = SENSORS["lid"][1]
    B.box("sensor_lid_switch", lx - 0.04, lx + 0.03, -HW_PRESS - 0.035, -HW_PRESS, lz - 0.04,
          lz + 0.03, S["lid"], SN, G, bevel=0.004)
    ox, oy, oz = SENSORS["oiltemp"][1]
    # probe through the tank lid, dipping into the oil
    B.cyl("sensor_oil_temp_probe_head", (ox, oy, zt_), (ox, oy, oz), 0.022, S["oiltemp"], SN, G, seg=6)
    B.cyl("sensor_oil_temp_probe_gland", (ox, oy, oz), (ox, oy, oz + 0.025), 0.011, M["plastic"], SN, G)
    B.cyl("sensor_oil_temp_probe_rod", (ox, oy, zs + 0.03), (ox, oy, zt_), 0.006, M["galv"], SN, G)
    for key, (grp, loc) in SENSORS.items():
        B.anchor(f"anchor_{key}", loc, grp)

    # ================= STUDIO =======================================================
    ST = "studio"
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=80)
    B._finish(bm, "studio_floor", M["floor"], ST, (3.2, 0, 0), None)
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = rgba(C["bg"])
    bg.inputs[1].default_value = 1.0
    target = bpy.data.objects.new("light_target", None)
    target.location = (3.4, 0, 1.0)
    B.coll(ST).objects.link(target)
    press_target = bpy.data.objects.new("light_target_press", None)
    press_target.location = (1.0, -0.3, 1.6)
    B.coll(ST).objects.link(press_target)
    for name, loc, energy, size, color, tgt in (
        ("key", (-4.0, -9.0, 9.0), 5200, 7.0, "#FFF4E8", target),
        ("fill", (9.0, -8.5, 3.5), 1500, 9.0, "#DCE8FF", target),
        ("rim", (8.5, 8.0, 7.5), 2600, 6.0, "#BFD6FF", target),
        ("top", (3.2, 0.0, 10.0), 1800, 10.0, "#FFFFFF", target),
        # soft fill into the opened press section (internals read better)
        ("interior", (-0.8, -5.5, 4.2), 700, 3.0, "#F4F7FF", press_target),
    ):
        light = bpy.data.lights.new(name, "AREA")
        light.energy, light.size = energy, size
        light.color = rgba(color)[:3]
        ob = bpy.data.objects.new(f"light_{name}", light)
        ob.location = loc
        B.coll(ST).objects.link(ob)
        tr = ob.constraints.new("TRACK_TO")
        tr.target = tgt
        tr.track_axis, tr.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"

    # machine stands on the scale platform
    B.groups["machine"][0].location.z = PLATFORM_TOP

    # store key dimensions for the animator / QC
    scene["combi"] = json.dumps({
        "W": W, "X_CF": X_CF, "X_CR": X_CR, "L_MAX": L_MAX, "PLATFORM_TOP": PLATFORM_TOP,
        "RAM_STROKE": RAM_STROKE, "RAM_FACE_RETRACTED": RAM_FACE_RETRACTED,
        "RAM_FACE_EXTENDED": RAM_FACE_EXTENDED, "CYL_STAGES": [s[0] for s in CYL_STAGES],
        "MM_PER_PX": MM_PER_PX, "COL0": COL0, "ROW0": ROW0, "ROW_Y0": ROW_Y0,
    })
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
    n = sum(1 for o in bpy.data.objects if o.type in ("MESH", "CURVE", "FONT"))
    print(f"BUILT {out} objects={n} ram_stroke={RAM_STROKE:.3f} m X_CF={X_CF:.3f} X_CR={X_CR:.3f}")


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "combi.blend"))
    args = ap.parse_args(argv)
    build(Path(args.out))


if __name__ == "__main__":
    main()
