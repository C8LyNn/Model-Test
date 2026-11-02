"""C01-16 PASS19: fail-closed FULL-REVOLUTION P16-06 native FBX rotor clearance.
Read-only Blender 4.x QA. No exports or writes to existing models.
FBX coordinates are imported into Blender Z-up; Y-up Unity rotor is Blender +Z.
A conservative axial-interval + radial-separation proof covers all 360 degrees,
not merely 72 sampled frames. This is producer QA, not C01-02 approval.
"""
import bpy
import hashlib
import json
import math
import pathlib
import sys

from mathutils import Vector

SOURCE = pathlib.Path(__file__).resolve().parents[1]
FBX = SOURCE / "FBX" / "P16-06.fbx"
BLEND = SOURCE / "Blender" / "P16-06.blend"
OUT = SOURCE / "MeshRepairPASS19" / "P16-06-rotor-sweep-fbx.json"
EXPECTED_FBX_SHA256 = "15ca9f7b417721b235243973c8ceaf6747822849c11c69a69b3255fbe4fc827c"
EXPECTED_BLEND_SHA256 = "becb4d8aa083b672472cf0a76e93b132e0d407fa5dcf0e14e18ec21b6679b9d5"
TOL = 1e-5
REQUIRED_CLEARANCE_M = 0.003  # 3mm proof threshold, not artistic preference


def physical_sha(path, signature, expected):
    data = path.read_bytes()
    if not data.startswith(signature):
        raise RuntimeError("NOT_HYDRATED_OR_BAD_BINARY: " + str(path))
    sha = hashlib.sha256(data).hexdigest()
    if sha != expected:
        raise RuntimeError("STALE_OR_DIFFERENT_BINARY %s: %s != %s" % (path, sha, expected))
    return sha, len(data)


def vertices_world(ob):
    return [ob.matrix_world @ v.co for v in ob.data.vertices]


def aabb(vals, index):
    return min(p[index] for p in vals), max(p[index] for p in vals)


def rect_axis_distance(lo, hi, origin):
    if lo > origin:
        return lo - origin
    if hi < origin:
        return origin - hi
    return 0.0


fbx_sha, fbx_bytes = physical_sha(FBX, b"Kaydara FBX Binary", EXPECTED_FBX_SHA256)
blend_sha, blend_bytes = physical_sha(BLEND, b"BLENDER-", EXPECTED_BLEND_SHA256)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(FBX), automatic_bone_orientation=False)
bpy.context.view_layer.update()

meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pivots = [o for o in bpy.context.scene.objects if o.name.startswith("ROTOR_Y_ANIMATABLE")]
rotors = [o for o in meshes if "_ROTOR_" in o.name]
statics = [o for o in meshes if "_STATIC_" in o.name]
if len(meshes) != 23 or len(pivots) != 1 or len(rotors) != 8 or len(statics) != 15:
    raise RuntimeError("HIERARCHY_COUNT_FAIL meshes=%d pivot=%d moving=%d fixed=%d" %
                       (len(meshes), len(pivots), len(rotors), len(statics)))
pivot = pivots[0]
if any(o.parent != pivot for o in rotors):
    raise RuntimeError("PIVOT_PARENTING_FAIL: one or more moving parts detached")
if any(o.parent == pivot for o in statics):
    raise RuntimeError("PIVOT_PARENTING_FAIL: static hardware would rotate")
if any(len(o.data.uv_layers) < 1 for o in meshes):
    raise RuntimeError("MISSING_UV0")

tris = sum(sum(len(poly.vertices) - 2 for poly in o.data.polygons) for o in meshes)
if tris != 388:
    raise RuntimeError("TRIANGLE_REGRESSION: %d != 388" % tris)

pivot_pt = pivot.matrix_world.translation
axis = pivot.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
if axis.length < TOL:
    raise RuntimeError("ZERO_LENGTH_ROTOR_AXIS")
axis.normalize()
# Require actual reimported Blender global Z, equivalent to Unity Y.
if abs(axis.dot(Vector((0.0, 0.0, 1.0)))) < 0.99999:
    raise RuntimeError("ROTOR_AXIS_INCORRECT: " + str(list(axis)))
if (abs(pivot_pt.x) > 0.001 or abs(pivot_pt.y) > 0.001
        or abs(pivot_pt.z + 0.20) > 0.001):
    raise RuntimeError("ROTOR_PIVOT_DRIFT: " + str(list(pivot_pt)))

part_data = {}
all_points = []
for ob in meshes:
    points = vertices_world(ob)
    if not points:
        raise RuntimeError("EMPTY_MESH: " + ob.name)
    all_points.extend(points)
    part_data[ob.name] = {
        "height": aabb(points, 2),
        "x": aabb(points, 0),
        "y": aabb(points, 1),
        "radius_max": max(math.hypot(p.x - pivot_pt.x, p.y - pivot_pt.y)
                          for p in points),
    }

total_pairs = 0
axial_separated = 0
radial_separated = 0
minimum_radial_gap = float("inf")
closest_pair = None
for rotor in rotors:
    r = part_data[rotor.name]
    for static in statics:
        s = part_data[static.name]
        total_pairs += 1
        vertical_overlap = min(r["height"][1], s["height"][1]) - max(
            r["height"][0], s["height"][0])
        if vertical_overlap < -TOL:
            axial_separated += 1
            continue
        # Distances computed from the ENTIRE static mesh's projected AABB.
        # Every triangle of that static mesh lies inside this AABB.
        static_rmin = math.hypot(
            rect_axis_distance(*s["x"], pivot_pt.x),
            rect_axis_distance(*s["y"], pivot_pt.y))
        gap = static_rmin - r["radius_max"]
        if gap <= REQUIRED_CLEARANCE_M:
            raise RuntimeError(
                "MOTION_HOLD: %s vs %s, certified radial margin %.8fm"
                % (rotor.name, static.name, gap))
        radial_separated += 1
        if gap < minimum_radial_gap:
            minimum_radial_gap = gap
            closest_pair = [rotor.name, static.name]

# Exact source geometry limits; FP tolerances only.
bounds = [[min(p[k] for p in all_points), max(p[k] for p in all_points)]
          for k in range(3)]
if (max(abs(bounds[0][0] + .14), abs(bounds[0][1] - .14),
        abs(bounds[1][0] + .14), abs(bounds[1][1] - .14),
        abs(bounds[2][0] + .36), abs(bounds[2][1])) > .001):
    raise RuntimeError("WORLD_BOUNDS_DRIFT: " + str(bounds))

OUT.parent.mkdir(parents=True, exist_ok=True)
report = {
    "asset": "P16-06",
    "gate": "REAL_HYDRATED_BLENDER_FBX_ANALYTICAL_360_ROTOR_CLEARANCE",
    "result": "PASS_PRODUCER_MOTION_GEOMETRY_ONLY",
    "blender_version": bpy.app.version_string,
    "blend_sha256": blend_sha,
    "fbx_sha256": fbx_sha,
    "blend_bytes": blend_bytes,
    "fbx_bytes": fbx_bytes,
    "mesh_parts": len(meshes),
    "moving_parts": len(rotors),
    "fixed_parts": len(statics),
    "triangles": tris,
    "pivot_world_xyz_blender": list(pivot_pt),
    "pivot_axis_world_blender": list(axis),
    "pairs_considered": total_pairs,
    "pairs_axially_separated": axial_separated,
    "pairs_radially_separated": radial_separated,
    "conservative_min_radial_gap_m": minimum_radial_gap,
    "minimum_gap_pair": closest_pair,
    "method": "AABB static projected minimum radius vs rotor exact maximum vertex radius, at overlapping height ranges; proves full continuous rotation separation",
    "unity_editor": "NOT_RUN",
    "independent_c01_02": "PENDING",
}
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
print("C01_16_P16_06_GENUINE_FBX_360_SWEEP_PRODUCER_PASS", json.dumps(report))
