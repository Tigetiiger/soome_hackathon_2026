"""animate_combi.py - animate the Combi model (combi.blend from build_combi.py), project the
sensor label anchors to screen space, and render the 3D pass with Cycles on the CPU.

Labels, captions and the pressure-curve inset are NOT rendered here: compose_overlay.py
draws them on top of the 3D frames (crisp text, and the copy can change without
re-rendering 90 minutes of path tracing).  This script writes the per-frame screen
positions of every anchor to out/anchors.json for that purpose.

    python animate_combi.py --anchors                      # out/anchors.json (fast)
    python animate_combi.py --render [--samples 16] [--scale 100]
                            [--worker 0 --workers 2 --threads 18] [--overwrite]
    python animate_combi.py --qc                           # QC stills into qc/
    python animate_combi.py --save-blend                   # combi_animated.blend

The frame loop is resumable: existing frames are skipped, each frame is rendered to a
temporary name and renamed when complete.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy  # noqa: I001
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import timeline as TL  # noqa: E402

AC = Path("/home/hackathon/output/animation-comparison")
STYLE = json.loads((AC / "shared" / "style.json").read_text())
OUT = HERE / "out"
QC = HERE / "qc"

# exploded-view travel (metres / degrees)
LID_LIFT, COVER_LIFT = 1.15, 0.75
SIDE_OUT = 2.40
CONTAINER_BACK = 2.30
DOOR_SWING_DEG, DOOR_BACK = 95.0, 0.60
MACHINE_LIFT = 0.60


def load(blend: Path):
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    scene = bpy.context.scene
    dims = json.loads(scene["combi"])
    return scene, dims


def grp(name):
    return bpy.data.objects[f"grp_{name}"]


def add_camera(scene):
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 35
    cam_data.sensor_width = 36
    cam_data.clip_start, cam_data.clip_end = 0.1, 300
    cam = bpy.data.objects.new("cam", cam_data)
    target = bpy.data.objects.new("cam_target", None)
    rig = bpy.data.collections["rig"]
    rig.objects.link(cam)
    rig.objects.link(target)
    tr = cam.constraints.new("TRACK_TO")
    tr.target = target
    tr.track_axis, tr.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    scene.camera = cam
    return cam, target


def place_camera(cam, target, tgt, az, el, dist):
    tgt = Vector(tgt)
    a, e = math.radians(az), math.radians(el)
    cam.location = tgt + dist * Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a),
                                        math.sin(e)))
    target.location = tgt


def key(obj, path, frame):
    obj.keyframe_insert(path, frame=frame)


def sensor_strength(key_name: str, t: float) -> float:
    t_on = TL.sensor_on(key_name)
    if t < t_on:
        return 0.0
    if t < t_on + 0.25:                       # flash in
        return 12.0 * TL.ease((t - t_on) / 0.25)
    if t < TL.LABELS_OUT[0]:
        return 12.0 - 6.0 * TL.ease((t - t_on - 0.25) / 0.5)
    return 6.0 - 2.5 * TL.seg(t, *TL.LABELS_OUT)  # stays as a small glowing dot


def fade_window(t, win, ramp=0.3):
    a, b = win
    return TL.clamp01((t - a) / ramp) * (1.0 - TL.clamp01((t - (b - ramp)) / ramp))


def animate(scene, dims):
    scene.render.fps = TL.FPS
    scene.frame_start, scene.frame_end = 1, TL.N_FRAMES
    # every frame is keyed with its exact eased value, so interpolate linearly between them
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    cam, target = add_camera(scene)

    g = {n: grp(n) for n in ("machine", "lid", "cover", "side_panel", "container", "door", "ram")}
    rest = {n: g[n].location.copy() for n in g}
    stages = {}
    for side in ("L", "R"):
        for name in dims["CYL_STAGES"][1:]:
            o = grp(f"cyl_{side}_{name}")
            stages[o.name] = (o, o.location.copy(), {"stage1": 1 / 3, "stage2": 2 / 3, "rod": 1.0}[name])
    stroke = dims["RAM_STROKE"]

    # the ram has no sensor body: it is highlighted by the ram_face_glow frame instead
    sensor_mats = {k: bpy.data.materials[f"sensor_{k}"] for k in TL.SENSOR_ORDER
                   if f"sensor_{k}" in bpy.data.materials}
    emis = {k: next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Emission Strength"]
            for k, m in sensor_mats.items()}
    ram_glow = bpy.data.materials["ram_face_glow"].node_tree.nodes["fade"].inputs["Fac"]
    ghost = bpy.data.materials["container_mouth_ghost"].node_tree.nodes["fade"].inputs["Fac"]

    for f in range(1, TL.N_FRAMES + 1):
        t = TL.t_of(f)
        tgt, az, el, dist = TL.camera_state(t)
        place_camera(cam, target, tgt, az, el, dist)
        key(cam, "location", f)
        key(target, "location", f)

        g["lid"].location = rest["lid"] + Vector((0, 0, LID_LIFT * TL.explode("lid", t)))
        g["cover"].location = rest["cover"] + Vector((0, 0, COVER_LIFT * TL.explode("cover", t)))
        g["side_panel"].location = rest["side_panel"] + Vector((0, -SIDE_OUT * TL.explode("side_panel", t), 0))
        g["container"].location = rest["container"] + Vector((CONTAINER_BACK * TL.explode("container", t), 0, 0))
        pd = TL.explode("door", t)
        g["door"].location = rest["door"] + Vector((DOOR_BACK * pd, 0, 0))
        g["door"].rotation_euler = (0, 0, math.radians(DOOR_SWING_DEG) * pd)
        g["machine"].location = rest["machine"] + Vector((0, 0, MACHINE_LIFT * TL.explode("lift", t)))
        e = stroke * TL.ram_progress(t)
        g["ram"].location = rest["ram"] + Vector((e, 0, 0))
        for o, r, frac in stages.values():
            o.location = r + Vector((e * frac, 0, 0))
            key(o, "location", f)
        for n in ("lid", "cover", "side_panel", "container", "door", "machine", "ram"):
            key(g[n], "location", f)
        key(g["door"], "rotation_euler", f)

        for k, inp in emis.items():
            inp.default_value = sensor_strength(k, t)
            inp.keyframe_insert("default_value", frame=f)
        ram_glow.default_value = fade_window(t, (TL.sensor_on("ram"), TL.LABELS_OUT[1]))
        ram_glow.keyframe_insert("default_value", frame=f)
        ghost.default_value = 0.85 * fade_window(t, TL.MOUTH_GHOST)
        ghost.keyframe_insert("default_value", frame=f)

    return cam


def configure_render(scene, samples, scale, threads=0, res=(1920, 1080)):
    scene.render.engine = "CYCLES"
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = scale
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    c = scene.cycles
    c.device = "CPU"
    c.samples = samples
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.02
    c.use_denoising = True
    c.denoiser = "OPENIMAGEDENOISE"
    c.max_bounces = 6
    c.diffuse_bounces, c.glossy_bounces = 2, 3
    c.transmission_bounces, c.volume_bounces, c.transparent_max_bounces = 0, 0, 8
    c.caustics_reflective = c.caustics_refractive = False
    c.blur_glossy = 1.0
    scene.render.use_persistent_data = True
    if threads:
        scene.render.threads_mode = "FIXED"
        scene.render.threads = threads


# ---------------------------------------------------------------------------------
# screen-space anchors for the overlay
# ---------------------------------------------------------------------------------
def anchor_objects():
    return sorted([o for o in bpy.data.objects if o.name.startswith("anchor_")], key=lambda o: o.name)


def project_anchors(scene, cam, res):
    w, h = res
    dg = bpy.context.evaluated_depsgraph_get()
    cam_pos = cam.matrix_world.translation
    out = {}
    for a in anchor_objects():
        p = a.matrix_world.translation
        v = world_to_camera_view(scene, cam, p)
        d = p - cam_pos
        dist = d.length
        hit, loc, _n, _i, obj, _m = scene.ray_cast(dg, cam_pos, d.normalized(), distance=dist)
        visible = ((not hit) or (loc - cam_pos).length > dist - 0.04 or obj.name.startswith("sensor_")
                   # a load-cell puck peeks out beside its own foot plate / leg
                   or (a.name.startswith("anchor_loadcell") and obj.name.startswith("platform_")
                       and (loc - p).length < 0.35))
        out[a.name[len("anchor_"):]] = [round(v.x * w, 1), round((1 - v.y) * h, 1), round(v.z, 3),
                                        int(visible)]
    return out


def export_anchors(scene, cam, path: Path):
    res = (STYLE["width"], STYLE["height"])
    data = {}
    for f in range(1, TL.N_FRAMES + 1):
        scene.frame_set(f)
        data[f] = project_anchors(scene, cam, res)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"width": res[0], "height": res[1], "frames": data}))
    print(f"ANCHORS {path} frames={len(data)} anchors={len(data[1])}")


# ---------------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------------
def render_frames(scene, args):
    out = OUT / "frames3d"
    out.mkdir(parents=True, exist_ok=True)
    frames = [f for f in range(1, TL.LAST_3D_FRAME + 1) if (f - 1) % args.workers == args.worker]
    if args.frames:
        frames = frames[:args.frames]
    t0 = time.time()
    done = 0
    for f in frames:
        final = out / f"f{f:04d}.png"
        if final.exists() and not args.overwrite:
            continue
        scene.frame_set(f)
        tmp = out / f"f{f:04d}.tmp.png"
        scene.render.filepath = str(tmp)
        bpy.ops.render.render(write_still=True)
        tmp.replace(final)
        done += 1
        print(f"FRAME {f} {time.time() - t0:.1f}s ({(time.time() - t0) / done:.1f}s/frame)", flush=True)


def qc_stills(scene, cam, dims, samples):
    QC.mkdir(parents=True, exist_ok=True)
    configure_render(scene, samples, 50)
    anchors = {}
    stills = [("01_assembled", 61), ("02_exploded", 215), ("02b_sensors_hold", 330)]
    for name, f in stills:
        scene.frame_set(f)
        scene.render.filepath = str(QC / f"{name}_3d.png")
        bpy.ops.render.render(write_still=True)
        anchors[name] = {"frame": f, "scale": 0.5, "points": project_anchors(scene, cam, (960, 540))}
        print("QC", name, flush=True)

    # sensor close-up: second camera near the press section, exploded state
    f = 330
    scene.frame_set(f)
    cdata = bpy.data.cameras.new("cam_closeup")
    cdata.lens = 35
    close = bpy.data.objects.new("cam_closeup", cdata)
    bpy.data.collections["rig"].objects.link(close)
    tgt = bpy.data.objects.new("cam_closeup_target", None)
    bpy.data.collections["rig"].objects.link(tgt)
    tr = close.constraints.new("TRACK_TO")
    tr.target = tgt
    tr.track_axis, tr.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    z0 = dims["PLATFORM_TOP"] + MACHINE_LIFT
    place_camera(close, tgt, (1.0, -0.45, z0 + 1.05), 242.0, 24.0, 4.6)
    scene.camera = close
    scene.frame_set(f)
    scene.render.filepath = str(QC / "03_sensor_closeup_3d.png")
    bpy.ops.render.render(write_still=True)
    anchors["03_sensor_closeup"] = {"frame": f, "scale": 0.5, "points": project_anchors(scene, close, (960, 540))}
    print("QC closeup", flush=True)

    # orthographic side + top views registered pixel-for-pixel to the drawing crops
    scene.frame_set(1)
    plat = bpy.data.collections["platform"]
    plat.hide_render = True
    m = grp("machine")
    m.animation_data_clear()
    m.location.z = 0.0
    floor = bpy.data.objects["studio_floor"]
    floor.hide_render = True
    mm = dims["MM_PER_PX"] / 1000.0
    odata = bpy.data.cameras.new("cam_ortho")
    odata.type = "ORTHO"
    odata.sensor_fit = "HORIZONTAL"
    odata.ortho_scale = 1920 * mm
    odata.clip_start, odata.clip_end = 0.1, 100
    ortho = bpy.data.objects.new("cam_ortho", odata)
    bpy.data.collections["rig"].objects.link(ortho)
    scene.camera = ortho
    W = dims["W"]
    cx = (960 - dims["COL0"]) * mm
    # side: crop is 1920 x 860, centre row 430; looking along +Y from the near (-Y) side
    configure_render(scene, samples, 100, res=(1920, 860))
    ortho.location = (cx, -20.0, (dims["ROW0"] - 430) * mm + W)
    ortho.rotation_euler = (math.radians(90), 0, 0)
    scene.render.filepath = str(QC / "04_side_ortho_3d.png")
    bpy.ops.render.render(write_still=True)
    # top: crop is 1920 x 700, centre row 350; looking down, image up = +Y; lid removed
    # as in the drawing's top view (which shows the open infeed with its 1500 x 900 dims)
    for o in bpy.data.objects:
        if o.parent and o.parent.name == "grp_lid":
            o.hide_render = True
    configure_render(scene, samples, 100, res=(1920, 700))
    ortho.location = (cx, (dims["ROW_Y0"] - 350) * mm, 20.0)
    ortho.rotation_euler = (0, 0, 0)
    scene.render.filepath = str(QC / "05_top_ortho_3d.png")
    bpy.ops.render.render(write_still=True)
    (QC / "anchors_qc.json").write_text(json.dumps(anchors))
    print("QC ortho done", flush=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--blend", default=str(HERE / "combi.blend"))
    ap.add_argument("--anchors", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--qc", action="store_true")
    ap.add_argument("--save-blend", action="store_true")
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--scale", type=int, default=100)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--frames", type=int, default=0)
    ap.add_argument("--still", default="", help="comma-separated frames to render to qc/still_FFFF.png")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args(argv)

    scene, dims = load(Path(args.blend))
    cam = animate(scene, dims)
    configure_render(scene, args.samples, args.scale, args.threads)
    if args.save_blend:
        scene.frame_set(1)
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "combi_animated.blend"), compress=True)
        print("SAVED combi_animated.blend")
    if args.anchors:
        export_anchors(scene, cam, OUT / "anchors.json")
    if args.still:
        QC.mkdir(exist_ok=True)
        anchors = {}
        for f in [int(v) for v in args.still.split(",")]:
            scene.frame_set(f)
            scene.render.filepath = str(QC / f"still_{f:04d}.png")
            t0 = time.time()
            bpy.ops.render.render(write_still=True)
            res = (scene.render.resolution_x * scene.render.resolution_percentage // 100,
                   scene.render.resolution_y * scene.render.resolution_percentage // 100)
            anchors[f] = project_anchors(scene, cam, res)
            print(f"STILL {f} {time.time() - t0:.1f}s", flush=True)
        (QC / "anchors_stills.json").write_text(json.dumps(anchors))
    if args.render:
        render_frames(scene, args)
    if args.qc:
        qc_stills(scene, cam, dims, args.samples)


if __name__ == "__main__":
    main()
