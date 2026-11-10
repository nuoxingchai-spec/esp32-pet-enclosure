"""Parametric 3D-printable enclosure for an ESP32 desktop pet.

Run in Blender 5.x:
    exec(open(r".../esp32_pet_enclosure.py", encoding="utf-8").read())

Or via BlenderMCP execute_blender_code with the same exec call.

All dimensions are millimetres. The scene is set to metric/mm for display;
STL export uses raw scene units (1 BU = 1 mm) with use_scene_unit=False.
"""

import bpy
import bmesh
import math
import os
import json
from mathutils import Matrix

P = {
    "collection": "ESP32_Pet_Enclosure",
    # ESP32 DevKitC V4 / ESP32-WROOM-32 dev board (including header pins)
    "board_l": 54.4,
    "board_w": 27.9,
    "board_h": 12.0,
    # Side margin around the board. Needs to be large enough for M2.5 bosses.
    "board_clearance": 6.0,
    "wall": 2.0,
    "floor": 2.0,
    "corner_r": 10.0,
    "base_h": 46.0,
    # 1.28" round GC9A01-style display, mounted behind the front wall.
    "display_d": 32.0,
    "display_z": 26.0,
    "display_chamfer": 0.8,
    # USB-C connector at the +X end of the board.
    "usb_w": 9.4,
    "usb_h": 3.6,
    "usb_z": 8.0,
    # Vent slots on the +Y (back) wall.
    "vent_count": 5,
    "vent_w": 2.0,
    "vent_h": 14.0,
    "vent_z": 30.0,
    "vent_pitch": 5.0,
    # Speaker grille on the -X side wall.
    "speaker_count": 5,
    "speaker_d": 2.2,
    "speaker_z": 30.0,
    "speaker_pitch": 4.5,
    # M2.5 self-tapping screws. Pilot hole in the boss, clearance in the lid.
    "screw_d": 2.5,
    "pilot_d": 2.2,
    "boss_d": 5.0,
    "boss_inset": 3.0,
    "boss_gap": 0.2,
    "pilot_depth": 10.0,
    "screw_clear_d": 2.8,
    "counterbore_d": 5.0,
    "counterbore_depth": 1.6,
    # Lid with an inner lip that seats inside the base opening.
    "lid_t": 3.0,
    "lid_overhang": 0.6,
    "lip_t": 1.8,
    "lip_h": 4.0,
    "lid_gap": 0.3,
    "lid_clearance": 0.25,
    "export_dir": os.path.join(os.getcwd(), "exports"),
    "export_stl": True,
}


def _collection(name):
    old = bpy.data.collections.get(name)
    if old is not None:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def _mesh_object(name, bm, col):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def _rounded_points(w, d, r, seg=20):
    r = max(0.05, min(r, w / 2 - 0.01, d / 2 - 0.01))
    hw, hd = w / 2 - r, d / 2 - r
    pts = []
    for cx, cy, a0 in ((hw, hd, 0), (-hw, hd, 90), (-hw, -hd, 180), (hw, -hd, 270)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), 0.0))
    return pts


def _rounded_prism(name, w, d, h, r, z0, col, cap_bottom=True, cap_top=True):
    bm = bmesh.new()
    verts = [bm.verts.new(p) for p in _rounded_points(w, d, r)]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    top_verts = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, h), verts=top_verts)
    bm.normal_update()
    if not cap_top:
        top = [f for f in bm.faces if f.calc_center_median().z > h - 1e-5]
        if top:
            bmesh.ops.delete(bm, geom=top, context="FACES")
    if not cap_bottom:
        bottom = [f for f in bm.faces if abs(f.calc_center_median().z) < 1e-5]
        if bottom:
            bmesh.ops.delete(bm, geom=bottom, context="FACES")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for v in bm.verts:
        v.co.z += z0
    return _mesh_object(name, bm, col)


def _box_cutter(name, size, loc, col):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    mat = Matrix.Translation(loc) @ Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    bmesh.ops.transform(bm, matrix=mat, verts=bm.verts)
    return _mesh_object(name, bm, col)


def _cylinder(name, radius, depth, loc, axis, col, segments=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth,
    )
    if axis == "Y":
        rot = Matrix.Rotation(math.radians(90.0), 4, "X")
    elif axis == "X":
        rot = Matrix.Rotation(math.radians(90.0), 4, "Y")
    else:
        rot = Matrix.Identity(4)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(loc) @ rot, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _mesh_object(name, bm, col)


def _cone(name, radius_bottom, radius_top, depth, loc, axis, col, segments=64):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius_bottom,
        radius2=radius_top,
        depth=depth,
    )
    if axis == "Y":
        rot = Matrix.Rotation(math.radians(90.0), 4, "X")
    elif axis == "X":
        rot = Matrix.Rotation(math.radians(90.0), 4, "Y")
    else:
        rot = Matrix.Identity(4)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(loc) @ rot, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _mesh_object(name, bm, col)


def _select_only(objs):
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def _apply_modifier(obj, mod):
    _select_only([obj])
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier=mod.name)


def _boolean(target, cutter, operation="DIFFERENCE"):
    mod = target.modifiers.new("Boolean", "BOOLEAN")
    mod.operation = operation
    mod.object = cutter
    if hasattr(mod, "solver"):
        mod.solver = "EXACT"
    if hasattr(mod, "use_self"):
        mod.use_self = True
    _apply_modifier(target, mod)
    bpy.data.objects.remove(cutter, do_unlink=True)


def _join(target, others):
    if not others:
        return target
    _select_only([target, *others])
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.join()
    return target


def _solidify(obj, thickness):
    mod = obj.modifiers.new("Wall", "SOLIDIFY")
    mod.thickness = thickness
    mod.offset = -1.0
    mod.use_rim = True
    mod.use_even_offset = True
    mod.use_quality_normals = True
    _apply_modifier(obj, mod)


def _mesh_health(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    faces = len(bm.faces)
    verts = len(bm.verts)
    bm.free()
    return {
        "verts": verts,
        "faces": faces,
        "non_manifold_edges": non_manifold,
        "boundary_edges": boundary,
    }


def build(overrides=None):
    p = dict(P)
    if overrides:
        p.update(overrides)

    inner_l = p["board_l"] + 2 * p["board_clearance"]
    inner_d = p["board_w"] + 2 * p["board_clearance"]
    outer_l = inner_l + 2 * p["wall"]
    outer_d = inner_d + 2 * p["wall"]
    boss_x = inner_l / 2 - p["boss_inset"]
    boss_y = inner_d / 2 - p["boss_inset"]
    boss_top = p["base_h"] - p["boss_gap"]
    boss_positions = [
        (sx * boss_x, sy * boss_y)
        for sx in (-1.0, 1.0)
        for sy in (-1.0, 1.0)
    ]

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    scene.unit_settings.length_unit = "MILLIMETERS"

    col = _collection(p["collection"])

    # Base: open-top rounded tray, solidified inward.
    base = _rounded_prism(
        "Enclosure_Base", outer_l, outer_d, p["base_h"], p["corner_r"],
        0.0, col, cap_bottom=True, cap_top=False,
    )
    _solidify(base, p["wall"])

    # Display window through the front (-Y) wall.
    display = _cylinder(
        "cut_display", p["display_d"] / 2, p["wall"] + 8.0,
        (0.0, -outer_d / 2, p["display_z"]), "Y", col, segments=64,
    )
    _boolean(base, display)
    if p["display_chamfer"] > 0:
        chamfer = p["display_chamfer"]
        front_y = -outer_d / 2
        countersink = _cone(
            "cut_display_chamfer", p["display_d"] / 2,
            p["display_d"] / 2 + chamfer, chamfer + 0.5,
            (0.0, front_y + (chamfer - 0.5) / 2.0, p["display_z"]),
            "Y", col, segments=64,
        )
        _boolean(base, countersink)

    # USB-C opening through the +X end wall.
    usb = _box_cutter(
        "cut_usb", (p["wall"] + 8.0, p["usb_w"], p["usb_h"]),
        (outer_l / 2, 0.0, p["usb_z"]), col,
    )
    _boolean(base, usb)

    # Vent slots through the back (+Y) wall.
    xs = [(i - (p["vent_count"] - 1) / 2.0) * p["vent_pitch"] for i in range(p["vent_count"])]
    for i, x in enumerate(xs):
        vent = _box_cutter(
            f"cut_vent_{i}", (p["vent_w"], p["wall"] + 8.0, p["vent_h"]),
            (x, outer_d / 2, p["vent_z"]), col,
        )
        _boolean(base, vent)

    # Speaker holes through the -X side wall.
    ys = [(i - (p["speaker_count"] - 1) / 2.0) * p["speaker_pitch"] for i in range(p["speaker_count"])]
    for i, y in enumerate(ys):
        hole = _cylinder(
            f"cut_speaker_{i}", p["speaker_d"] / 2, p["wall"] + 8.0,
            (-outer_l / 2, y, p["speaker_z"]), "X", col, segments=32,
        )
        _boolean(base, hole)

    # Screw bosses, joined to the base, then drilled with pilot holes.
    bosses = []
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        bosses.append(
            _cylinder(
                f"boss_{sx}_{sy}", p["boss_d"] / 2, boss_top - p["floor"] + 0.2,
                (sx * boss_x, sy * boss_y, (p["floor"] + boss_top) / 2), "Z", col,
            )
        )
    _join(base, bosses)
    for i, (x, y) in enumerate(boss_positions):
        pilot = _cylinder(
            f"cut_pilot_{i}", p["pilot_d"] / 2, p["pilot_depth"] + 1.0,
            (x, y, boss_top - p["pilot_depth"] / 2 + 0.5), "Z", col, segments=32,
        )
        _boolean(base, pilot)

    # Lid plate.
    lid_z = p["base_h"] + p["lid_gap"]
    lid = _rounded_prism(
        "Enclosure_Lid",
        outer_l + 2 * p["lid_overhang"], outer_d + 2 * p["lid_overhang"],
        p["lid_t"], p["corner_r"] + p["lid_overhang"], lid_z, col,
        cap_bottom=True, cap_top=True,
    )
    for i, (x, y) in enumerate(boss_positions):
        through = _cylinder(
            f"cut_lid_screw_{i}", p["screw_clear_d"] / 2, p["lid_t"] + 2.0,
            (x, y, lid_z + p["lid_t"] / 2), "Z", col, segments=32,
        )
        _boolean(lid, through)
        counter = _cylinder(
            f"cut_lid_counter_{i}", p["counterbore_d"] / 2,
            p["counterbore_depth"] + 1.0,
            (x, y, lid_z + p["lid_t"] - p["counterbore_depth"] / 2 + 0.5),
            "Z", col, segments=32,
        )
        _boolean(lid, counter)

    # Inner lid lip: thin ring that seats inside the base opening.
    lip_l = inner_l - 2 * p["lid_clearance"]
    lip_d = inner_d - 2 * p["lid_clearance"]
    lip_r = max(1.0, p["corner_r"] - p["wall"] - p["lid_clearance"])
    lip_z = lid_z - p["lip_h"]
    lip = _rounded_prism(
        "Enclosure_Lid_Lip", lip_l, lip_d, p["lip_h"], lip_r,
        lip_z, col, cap_bottom=True, cap_top=True,
    )
    lip_cut = _rounded_prism(
        "cut_lip_inner", lip_l - 2 * p["lip_t"], lip_d - 2 * p["lip_t"],
        p["lip_h"] + 2.0, max(0.5, lip_r - p["lip_t"]),
        lip_z - 1.0, col, cap_bottom=True, cap_top=True,
    )
    _boolean(lip, lip_cut)
    for i, (x, y) in enumerate(boss_positions):
        clearance = _cylinder(
            f"cut_lip_boss_{i}", p["boss_d"] / 2 + 0.3, p["lip_h"] + 2.0,
            (x, y, lip_z + p["lip_h"] / 2), "Z", col, segments=32,
        )
        _boolean(lip, clearance)
    _join(lid, [lip])

    base_health = _mesh_health(base)
    lid_health = _mesh_health(lid)

    result = {
        "base": {
            "dimensions_mm": [round(v, 2) for v in base.dimensions],
            "health": base_health,
        },
        "lid": {
            "dimensions_mm": [round(v, 2) for v in lid.dimensions],
            "health": lid_health,
        },
        "inner_cavity_mm": [round(inner_l, 2), round(inner_d, 2)],
        "outer_mm": [round(outer_l, 2), round(outer_d, 2), round(p["base_h"] + p["lid_gap"] + p["lid_t"], 2)],
        "boss_positions_mm": [[round(x, 2), round(y, 2)] for x, y in boss_positions],
        "exported": [],
    }

    if p["export_stl"]:
        os.makedirs(p["export_dir"], exist_ok=True)
        for obj, filename in ((base, "enclosure_base.stl"), (lid, "enclosure_lid.stl")):
            path = os.path.join(p["export_dir"], filename)
            _select_only([obj])
            bpy.ops.wm.stl_export(
                filepath=path,
                export_selected_objects=True,
                apply_modifiers=True,
                use_scene_unit=False,
                global_scale=1.0,
                ascii_format=False,
            )
            result["exported"].append(path)

    print("ENCLOSURE_RESULT " + json.dumps(result, ensure_ascii=False))
    return result


RESULT = build() if not globals().get("SKIP_AUTO_BUILD", False) else None
