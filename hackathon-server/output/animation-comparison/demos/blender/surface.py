"""Blender (bpy) demo: the ManimGL calibration surface, rendered photorealistically.

Same function as demos/manimgl (shared/mockdata.mass_surface), same palette and
fonts, but path-traced with Cycles: shape keys morph the surface between
material densities while the camera orbits. Titles are Blender text objects
parented to the camera, so the whole frame comes out of Blender.

    python surface.py [--engine CYCLES|BLENDER_EEVEE] [--samples 16]
                      [--scale 100] [--frames N] [--still FRAME]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "shared"))
from mockdata import mass_surface  # noqa: E402

STYLE = json.loads((ROOT / "shared" / "style.json").read_text())
C = STYLE["colors"]
FPS = STYLE["fps"]
DURATION_S = 8.0
GRID_N = 90
SIZE = 6.0       # world units for the unit square (fill × pressure)
Z_SCALE = 1.0    # world units per tonne
FONT_DIR = ROOT / "assets" / "fonts"


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgba(h: str, a: float = 1.0) -> tuple[float, float, float, float]:
    h = h.lstrip("#")
    return (*[srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)], a)


def reset_scene() -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, int(DURATION_S * FPS)
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = rgba(C["bg"])
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    return scene


def heights(d: float) -> np.ndarray:
    u = np.linspace(0, 1, GRID_N)
    fill, pressure = np.meshgrid(u, u, indexing="ij")
    return mass_surface(fill, pressure, d) * Z_SCALE


def build_surface() -> bpy.types.Object:
    u = np.linspace(0, 1, GRID_N)
    verts = [(SIZE * a - SIZE / 2, SIZE * b - SIZE / 2, 0.0) for a in u for b in u]
    faces = [(i * GRID_N + j, (i + 1) * GRID_N + j, (i + 1) * GRID_N + j + 1, i * GRID_N + j + 1)
             for i in range(GRID_N - 1) for j in range(GRID_N - 1)]
    mesh = bpy.data.meshes.new("surface")
    mesh.from_pydata(verts, [], faces)
    uv = mesh.uv_layers.new(name="grid")
    for loop in mesh.loops:
        x, y, _ = verts[loop.vertex_index]
        uv.data[loop.index].uv = ((x + SIZE / 2) / SIZE, (y + SIZE / 2) / SIZE)
    mesh.shade_smooth()
    obj = bpy.data.objects.new("surface", mesh)
    bpy.context.collection.objects.link(obj)

    obj.shape_key_add(name="flat")
    for name, d in (("film", 0.15), ("cardboard", 0.95), ("mixed", 0.55)):
        key = obj.shape_key_add(name=name, from_mix=False)
        z = heights(d).ravel()
        for k, v in enumerate(key.data):
            v.co.z = float(z[k])
    obj.data.materials.append(surface_material())
    return obj


def surface_material() -> bpy.types.Material:
    mat = bpy.data.materials.new("surface")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.32
    bsdf.inputs["Coat Weight"].default_value = 0.35

    geo = nodes.new("ShaderNodeNewGeometry")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    norm = nodes.new("ShaderNodeMath")
    norm.operation = "DIVIDE"
    norm.inputs[1].default_value = 3.2 * Z_SCALE
    ramp = nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].color, els[1].color = rgba(C["violet"]), rgba(C["amber"])
    mid = els.new(0.5)
    mid.color = rgba(C["teal"])
    links.new(geo.outputs["Position"], sep.inputs[0])
    links.new(sep.outputs["Z"], norm.inputs[0])
    links.new(norm.outputs[0], ramp.inputs["Fac"])

    # Grid lines from the UV map: darken where pingpong(uv * 10) is near 0.
    uvn = nodes.new("ShaderNodeUVMap")
    uvn.uv_map = "grid"
    sep_uv = nodes.new("ShaderNodeSeparateXYZ")
    links.new(uvn.outputs["UV"], sep_uv.inputs[0])
    line_mask = None
    for axis in ("X", "Y"):
        mul = nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 10
        frac = nodes.new("ShaderNodeMath"); frac.operation = "PINGPONG"; frac.inputs[1].default_value = 0.5
        thr = nodes.new("ShaderNodeMath"); thr.operation = "LESS_THAN"; thr.inputs[1].default_value = 0.025
        links.new(sep_uv.outputs[axis], mul.inputs[0])
        links.new(mul.outputs[0], frac.inputs[0])
        links.new(frac.outputs[0], thr.inputs[0])
        if line_mask is None:
            line_mask = thr
        else:
            mx = nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
            links.new(line_mask.outputs[0], mx.inputs[0])
            links.new(thr.outputs[0], mx.inputs[1])
            line_mask = mx
    fac_scale = nodes.new("ShaderNodeMath"); fac_scale.operation = "MULTIPLY"
    fac_scale.inputs[1].default_value = 0.45
    links.new(line_mask.outputs[0], fac_scale.inputs[0])
    mix = nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["B"].default_value = rgba(C["bg"])
    links.new(fac_scale.outputs[0], mix.inputs["Factor"])
    links.new(ramp.outputs["Color"], mix.inputs["A"])
    links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    return mat


def emission_material(name: str, hex_color: str, strength: float = 1.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.remove(nodes["Principled BSDF"])
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba(hex_color)
    em.inputs["Strength"].default_value = strength
    mat.node_tree.links.new(em.outputs[0], nodes["Material Output"].inputs["Surface"])
    return mat


def add_floor_and_axes() -> None:
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.002))
    floor = bpy.context.active_object
    mat = bpy.data.materials.new("floor")
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba(C["bg"])
    b.inputs["Roughness"].default_value = 0.75
    floor.data.materials.append(mat)

    line_mat = emission_material("grid", C["grid"], 1.0)
    for k in range(9):
        a = -SIZE / 2 + SIZE * k / 8
        for (x0, y0, x1, y1) in ((a, -SIZE / 2, a, SIZE / 2), (-SIZE / 2, a, SIZE / 2, a)):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=SIZE, vertices=8,
                                                location=((x0 + x1) / 2, (y0 + y1) / 2, 0.004))
            cyl = bpy.context.active_object
            cyl.rotation_euler = (0, math.pi / 2, 0) if y0 == y1 else (math.pi / 2, 0, 0)
            cyl.data.materials.append(line_mat)

    axis_mat = emission_material("axis", C["muted"], 1.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=3.6 * Z_SCALE, vertices=12,
                                        location=(-SIZE / 2, SIZE / 2, 1.8 * Z_SCALE))
    bpy.context.active_object.data.materials.append(axis_mat)


def add_text(body: str, font: str, size: float, color: str, parent=None, loc=(0, 0, 0),
             align: str = "LEFT") -> bpy.types.Object:
    curve = bpy.data.curves.new(type="FONT", name=body[:16])
    curve.body = body
    curve.font = bpy.data.fonts.load(str(FONT_DIR / font), check_existing=True)
    curve.size = size
    curve.align_x = align
    obj = bpy.data.objects.new(body[:16], curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(emission_material(f"txt_{color}", color, 1.0))
    obj.location = loc
    if parent is not None:
        obj.parent = parent
    return obj


def add_camera_rig(scene: bpy.types.Scene, res_label: str) -> bpy.types.Object:
    rig = bpy.data.objects.new("rig", None)
    bpy.context.collection.objects.link(rig)
    rig.location = (0.2, 0.0, 0.9)
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 40
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.parent = rig
    cam.location = (0, -15.5, 7.4)
    track = cam.constraints.new("TRACK_TO")
    track.target = rig
    track.track_axis, track.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    scene.camera = cam

    rig.rotation_euler = (0, 0, math.radians(-38))
    rig.keyframe_insert("rotation_euler", frame=scene.frame_start)
    rig.rotation_euler = (0, 0, math.radians(22))
    rig.keyframe_insert("rotation_euler", frame=scene.frame_end)

    # HUD: text objects in the camera's local frame, 10 units in front of the lens.
    hud = bpy.data.objects.new("hud", None)
    bpy.context.collection.objects.link(hud)
    hud.parent = cam
    hud.location = (0, 0, -1)
    hud.scale = (0.1, 0.1, 0.1)  # 1 unit in front of the lens: nothing can occlude it
    w = 10 * 36 / cam_data.lens / 2           # half-width of the view at distance 10
    h = w * 9 / 16
    add_text("Virtual-scale calibration surface", "IBMPlexSans-SemiBold.ttf", 0.42, C["ink"],
             hud, (-w + 0.5, h - 0.85, 0))
    add_text("estimated payload  m̂(fill, pressure; ρ)  in tonnes  ·  path-traced",
             "IBMPlexSans-Light.ttf", 0.22, C["muted"], hud, (-w + 0.5, h - 1.25, 0))
    add_text(f"Blender 5.2 Cycles (CPU)  ·  {res_label}  ·  30 fps", "IBMPlexMono-Regular.ttf", 0.16,
             C["muted"], hud, (w - 0.45, -h + 0.4, 0), align="RIGHT")
    return cam


def add_lights() -> None:
    for name, loc, energy, size, color in (
        ("key", (-6, -7, 9), 900, 6, "#FFF3E6"),
        ("rim", (5, 9, 6), 350, 4, "#B8D4FF"),
        ("fill", (6, -8, 2), 160, 8, "#FFFFFF"),
    ):
        light = bpy.data.lights.new(name, "AREA")
        light.energy, light.size = energy, size
        light.color = rgba(color)[:3]
        obj = bpy.data.objects.new(name, light)
        obj.location = loc
        bpy.context.collection.objects.link(obj)
        tr = obj.constraints.new("TRACK_TO")
        tr.target = bpy.data.objects["surface"]
        tr.track_axis, tr.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"


def smoothstep(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def morph_weights(s: float) -> dict[str, float]:
    """Shape-key weights at time s (seconds): flat → film → cardboard → mixed."""
    grow = smoothstep((s - 0.4) / 1.6)
    to_card = smoothstep((s - 2.6) / 2.0)
    to_mixed = smoothstep((s - 5.4) / 1.8)
    return {
        "film": grow * (1 - to_card),
        "cardboard": to_card * (1 - to_mixed),
        "mixed": to_mixed,
    }


def animate_morph(obj: bpy.types.Object, scene: bpy.types.Scene) -> None:
    """Key every frame explicitly: version-proof and gives exact smoothstep easing."""
    keys = obj.data.shape_keys.key_blocks
    for fr in range(scene.frame_start, scene.frame_end + 1):
        for name, v in morph_weights((fr - 1) / FPS).items():
            keys[name].value = v
            keys[name].keyframe_insert("value", frame=fr)


def configure_render(scene: bpy.types.Scene, engine: str, samples: int, scale: int) -> None:
    scene.render.engine = engine
    scene.render.resolution_x, scene.render.resolution_y = STYLE["width"], STYLE["height"]
    scene.render.resolution_percentage = scale
    scene.render.image_settings.file_format = "PNG"
    if engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = samples
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.use_denoising = True
        scene.cycles.max_bounces = 4
        scene.render.use_persistent_data = True
    else:
        scene.eevee.taa_render_samples = samples


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="CYCLES")
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--scale", type=int, default=100)
    ap.add_argument("--frames", type=int, default=0, help="render only the first N frames")
    ap.add_argument("--still", type=int, default=0, help="render one frame number")
    ap.add_argument("--overwrite", action="store_true",
                    help="re-render frames that already exist (default: skip them, i.e. resume)")
    args = ap.parse_args()

    scene = reset_scene()
    surf = build_surface()
    add_floor_and_axes()
    add_lights()
    w, h = STYLE["width"] * args.scale // 100, STYLE["height"] * args.scale // 100
    add_camera_rig(scene, f"{w}×{h}")
    animate_morph(surf, scene)
    configure_render(scene, args.engine, args.samples, args.scale)

    out = HERE / "out" / "frames"
    out.mkdir(parents=True, exist_ok=True)
    frames = [args.still] if args.still else range(
        scene.frame_start, (scene.frame_start + args.frames) if args.frames else scene.frame_end + 1)
    t0 = time.time()
    for fr in frames:
        final = out / f"f{fr:04d}.png"
        if final.exists() and not args.overwrite:  # resume: keep frames from an earlier run
            continue
        scene.frame_set(fr)
        # Render to a temp name and rename, so an interrupted run never leaves a
        # half-written PNG that a later resume would mistake for a finished frame.
        tmp = out / f"f{fr:04d}.tmp.png"
        scene.render.filepath = str(tmp)
        bpy.ops.render.render(write_still=True)
        tmp.replace(final)
        print(f"FRAME {fr} {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
