"""C01-16 PASS04: execute REAL Blender import, native source save, binary FBX and FBX roundtrip.
Input: existing PASS03 welded source OBJ, not replacement primitive geometry.
Invocation: blender -b --factory-startup --python-exit-code 1 --python ci_pass04_native.py -- P16-01
"""
import bpy
import hashlib
import json
import math
import pathlib
import sys
from mathutils import Vector

ASSET = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
if ASSET is None or ASSET not in {"P16-01", "P16-02", "P16-03", "P16-04", "P16-05", "P16-06", "P16-07"}:
    raise SystemExit("Use -- P16-01 ... P16-07")
SOURCE = pathlib.Path(__file__).resolve().parents[1]
obj_file = SOURCE / "OBJ" / (ASSET + ".obj")
detail_file = SOURCE / "DetailsPASS12" / (ASSET + "_detail.obj")
blend_file = SOURCE / "Blender" / (ASSET + ".blend")
fbx_file = SOURCE / "FBX" / (ASSET + ".fbx")
report_dir = SOURCE / "MeshRepairPASS04" / ASSET
report_dir.mkdir(parents=True, exist_ok=True)
blend_file.parent.mkdir(parents=True, exist_ok=True)
fbx_file.parent.mkdir(parents=True, exist_ok=True)

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def mesh_objects():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]

def bounds(meshes):
    world = []
    for ob in meshes:
        world.extend(ob.matrix_world @ v.co for v in ob.data.vertices)
    if not world:
        raise RuntimeError("No mesh vertices")
    return [[min(p[j] for p in world), max(p[j] for p in world)] for j in range(3)]

def inspect(meshes):
    records = []
    for ob in meshes:
        mesh = ob.data
        if len(mesh.vertices) == 0 or len(mesh.polygons) == 0:
            raise RuntimeError("Empty mesh: " + ob.name)
        if len(mesh.uv_layers) < 1:
            raise RuntimeError("No UV0 in " + ob.name)
        use = {}
        for f in mesh.polygons:
            if len(f.vertices) < 3 or f.area < 1e-10:
                raise RuntimeError("Degenerate face: " + ob.name)
            points = list(f.vertices)
            for a, b in zip(points, points[1:] + points[:1]):
                key = tuple(sorted([a, b]))
                use[key] = use.get(key, 0) + 1
        boundary = sum(x == 1 for x in use.values())
        nonmanifold = sum(x > 2 for x in use.values())
        if boundary or nonmanifold:
            raise RuntimeError("Bad edge topology in %s: boundary=%d, nonmanifold=%d" % (ob.name, boundary, nonmanifold))
        records.append(dict(
            object=ob.name, vertices=len(mesh.vertices),
            edges=len(mesh.edges), faces=len(mesh.polygons),
            triangles=sum(len(f.vertices) - 2 for f in mesh.polygons),
            uv0_loops=len(mesh.uv_layers[0].data),
            materials=[m.name if m else "MISSING" for m in mesh.materials],
            boundary=boundary, nonmanifold=nonmanifold,
        ))
    return sorted(records, key=lambda x: x["object"])

if not obj_file.exists():
    raise FileNotFoundError(str(obj_file))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
# Source OBJ and Unity/FBX are Y-up. Convert to Blender Z-up via explicit import axes.
bpy.ops.wm.obj_import(filepath=str(obj_file), forward_axis="NEGATIVE_Z", up_axis="Y", use_split_objects=True, use_split_groups=False)
objects = mesh_objects()
if not objects:
    raise RuntimeError("Source OBJ has no meshes")
expected_parts = {"P16-01": 5, "P16-02": 5, "P16-03": 5, "P16-04": 7, "P16-05": 7, "P16-06": 9, "P16-07": 5}[ASSET]
# Inspect original, untouched PASS03 mesh BEFORE loading extra functional details.
base_objects = list(objects)
if len(objects) != expected_parts:
    raise RuntimeError("Expected %d independent meshes, got %d" % (expected_parts, len(objects)))
for obj in objects:
    for poly in obj.data.polygons:
        poly.use_smooth = False

# Recreate original PBR/emissive material values from the existing asset palette.
# OBJ MTL stores diffuse Kd only; without this step FBX would silently lose
# emitter intensity. This changes MATERIALS ONLY, never source geometry.
SOURCE_PALETTE = {
    "Steel": (0.32, 0.39, 0.44, 1.0),
    "DarkPanel": (0.075, 0.105, 0.14, 1.0),
    "EmissionWhite": (0.67, 0.91, 1.0, 1.0),
    "EmissionRed": (1.0, 0.12, 0.08, 1.0),
    "EmissionAmber": (1.0, 0.62, 0.08, 1.0),
    "EmissionGreen": (0.14, 1.0, 0.44, 1.0),
}
for ob in objects:
    for mat in ob.data.materials:
        if mat is None:
            raise RuntimeError("Missing original material on " + ob.name)
        base_name = mat.name.split(".")[0]
        rgba = SOURCE_PALETTE.get(base_name)
        if rgba is None:
            raise RuntimeError("Unknown material, refusing implicit replacement: " + mat.name)
        mat.diffuse_color = rgba
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            raise RuntimeError("Missing Principled BSDF: " + mat.name)
        bsdf.inputs["Base Color"].default_value = rgba
        metallic = bsdf.inputs.get("Metallic")
        roughness = bsdf.inputs.get("Roughness")
        if metallic: metallic.default_value = 0.4
        if roughness: roughness.default_value = 0.56
        if base_name.startswith("Emission"):
            emitter = bsdf.inputs.get("Emission Color")
            strength = bsdf.inputs.get("Emission Strength")
            if emitter is None or strength is None:
                raise RuntimeError("Blender does not expose expected emission sockets: " + mat.name)
            emitter.default_value = rgba
            strength.default_value = 1.9

base_pre = inspect(objects)
if sum(x["vertices"] for x in base_pre) != expected_parts * 8:
    raise RuntimeError("PASS03 weld was lost on OBJ import")
if sum(x["triangles"] for x in base_pre) != expected_parts * 12:
    raise RuntimeError("Original triangles changed on import")
if any(x["uv0_loops"] != x["triangles"] * 3 for x in base_pre):
    raise RuntimeError("UV loop count changed on import")

# DETAIL PASS12 — merge real authored OBJ detail submeshes into the SAME asset scene.
# The original 43 PASS03 solids are untouched; this is not a replacement model.
if not detail_file.is_file():
    raise RuntimeError("Missing actual detail geometry: " + str(detail_file))
detail_counts = {"P16-01": 7, "P16-02": 7, "P16-03": 7,
                 "P16-04": 12, "P16-05": 8, "P16-06": 10, "P16-07": 6}
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.obj_import(filepath=str(detail_file), forward_axis="NEGATIVE_Z", up_axis="Y",
                      use_split_objects=True, use_split_groups=False)
objects = mesh_objects()
detail_objects = [o for o in objects if "_DETAIL_" in o.name]
if len(detail_objects) != detail_counts[ASSET]:
    raise RuntimeError("Expected %d detail parts, imported %d" % (detail_counts[ASSET], len(detail_objects)))
if len(objects) != expected_parts + detail_counts[ASSET]:
    raise RuntimeError("Some original parts vanished or duplicate detail parts were created")
for ob in detail_objects:
    for poly in ob.data.polygons:
        poly.use_smooth = False
detail_triangles = {"P16-01":160,"P16-02":160,"P16-03":160,
                    "P16-04":240,"P16-05":196,"P16-06":216,"P16-07":148}
if sum(len(ob.data.polygons) for ob in detail_objects) != detail_triangles[ASSET]:
    raise RuntimeError("Actual detail source triangulation changed")
# The FBX exporter MUST see the enriched geometry (and original base geometry).
for ob in detail_objects:
    for mat in ob.data.materials:
        if mat is None:
            raise RuntimeError("Missing authored material on " + ob.name)
        rgba = SOURCE_PALETTE.get(mat.name.split(".")[0])
        if rgba is None:
            raise RuntimeError("Unknown detail material " + mat.name)
        mat.diffuse_color = rgba
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            raise RuntimeError("Missing Principled BSDF on " + mat.name)
        bsdf.inputs["Base Color"].default_value = rgba
        if bsdf.inputs.get("Metallic"): bsdf.inputs["Metallic"].default_value = 0.4
        if bsdf.inputs.get("Roughness"): bsdf.inputs["Roughness"].default_value = 0.56

# DETAIL PASS15: existing-model functional fasteners and support brackets.
# Source meshes are versioned separately to preserve PASS12 immutable evidence.
extra_file = SOURCE / "DetailsPASS15" / (ASSET + "_detail15.obj")
extra_counts = {"P16-01":0, "P16-02":0, "P16-03":0,
                "P16-04":4, "P16-05":2, "P16-06":2, "P16-07":0}
extra_triangles = {"P16-01":0, "P16-02":0, "P16-03":0,
                   "P16-04":48, "P16-05":24, "P16-06":24, "P16-07":0}
if extra_counts[ASSET]:
    if not extra_file.is_file():
        raise RuntimeError("Missing actual PASS15 detail mesh: " + str(extra_file))
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.obj_import(filepath=str(extra_file), forward_axis="NEGATIVE_Z", up_axis="Y",
                          use_split_objects=True, use_split_groups=False)
    objects = mesh_objects()
    extra_objects = [o for o in objects if "_DETAIL15_" in o.name]
    if len(extra_objects) != extra_counts[ASSET]:
        raise RuntimeError("DETAIL15 object count changed: %s" % ASSET)
    if sum(len(o.data.polygons) for o in extra_objects) != extra_triangles[ASSET]:
        raise RuntimeError("DETAIL15 triangle budget changed: %s" % ASSET)
    if any("_ROTOR_" in o.name for o in extra_objects):
        raise RuntimeError("Static mounting detail incorrectly parented to rotor")
    for ob in extra_objects:
        for poly in ob.data.polygons:
            poly.use_smooth = False
        for mat in ob.data.materials:
            if mat is None:
                raise RuntimeError("Missing DETAIL15 material: " + ob.name)
            name = mat.name.split(".")[0]
            rgba = SOURCE_PALETTE.get(name)
            if rgba is None:
                raise RuntimeError("Unexpected DETAIL15 material: " + mat.name)
            mat.diffuse_color = rgba
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf is None:
                raise RuntimeError("No Principled BSDF for " + mat.name)
            bsdf.inputs["Base Color"].default_value = rgba
            if bsdf.inputs.get("Metallic"): bsdf.inputs["Metallic"].default_value = 0.4
            if bsdf.inputs.get("Roughness"): bsdf.inputs["Roughness"].default_value = 0.56
else:
    if extra_file.exists():
        raise RuntimeError("Unexpected PASS15 source in unmodified asset: " + ASSET)

if len(objects) != expected_parts + detail_counts[ASSET] + extra_counts[ASSET]:
    raise RuntimeError("PASS15 merged source object count mismatch")
# FIX: baseline 'pre' MUST represent all authored meshes, not only original
# PASS03 base. Old PASS12 code compared after-FBX details to base-only triangles.
pre = inspect(objects)
if sum(x["triangles"] for x in pre) != expected_parts * 12 + detail_triangles[ASSET] + extra_triangles[ASSET]:
    raise RuntimeError("PASS15 merged source triangle mismatch")
if any(x["uv0_loops"] != x["triangles"] * 3 for x in pre):
    raise RuntimeError("PASS15 source loop UV0 missing")

# DETAIL PASS16: eight small retained screw heads on genuine PASS15 mounting.
# Imported parts are static hardware, not new assets, not parented to P16-06 rotor.
pass16_file = SOURCE / "DetailsPASS16" / (ASSET + "_detail16.obj")
pass16_parts = {"P16-01":0, "P16-02":0, "P16-03":0, "P16-04":4,
                "P16-05":2, "P16-06":2, "P16-07":0}
pass16_triangles = {"P16-01":0, "P16-02":0, "P16-03":0, "P16-04":80,
                    "P16-05":40, "P16-06":40, "P16-07":0}
if pass16_parts[ASSET]:
    if not pass16_file.is_file():
        raise RuntimeError("PASS16 authoring mesh missing: " + str(pass16_file))
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.obj_import(filepath=str(pass16_file), forward_axis="NEGATIVE_Z",
                          up_axis="Y", use_split_objects=True, use_split_groups=False)
    objects = mesh_objects()
    pass16_objects = [ob for ob in objects if "_DETAIL16_" in ob.name]
    if len(pass16_objects) != pass16_parts[ASSET]:
        raise RuntimeError("PASS16 fastener count mismatch")
    if sum(len(o.data.polygons) for o in pass16_objects) != pass16_triangles[ASSET]:
        raise RuntimeError("PASS16 fastener triangle budget mismatch")
    if any("_ROTOR_" in o.name for o in pass16_objects):
        raise RuntimeError("PASS16 STATIC hardware incorrectly classified as rotor")
    for ob in pass16_objects:
        for poly in ob.data.polygons:
            poly.use_smooth = False
        for mat in ob.data.materials:
            if mat is None:
                raise RuntimeError("PASS16 fastener missing Steel material")
            mat_name = mat.name.split(".")[0]
            if mat_name != "Steel" or mat_name not in SOURCE_PALETTE:
                raise RuntimeError("PASS16 unexpected material " + mat.name)
            mat.diffuse_color = SOURCE_PALETTE[mat_name]
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf is None:
                raise RuntimeError("PASS16 material has no Principled BSDF")
            bsdf.inputs["Base Color"].default_value = SOURCE_PALETTE[mat_name]
            if bsdf.inputs.get("Metallic"): bsdf.inputs["Metallic"].default_value = 0.4
            if bsdf.inputs.get("Roughness"): bsdf.inputs["Roughness"].default_value = 0.56
elif pass16_file.exists():
    raise RuntimeError("Unexpected PASS16 source for unchanged asset")

if len(objects) != expected_parts + detail_counts[ASSET] + extra_counts[ASSET] + pass16_parts[ASSET]:
    raise RuntimeError("Merged original + PASS12 + PASS15 + PASS16 object count mismatch")
pre = inspect(objects)
if sum(x["triangles"] for x in pre) != (
        expected_parts * 12 + detail_triangles[ASSET] +
        extra_triangles[ASSET] + pass16_triangles[ASSET]):
    raise RuntimeError("Complete source triangle count mismatch")
if any(x["uv0_loops"] != x["triangles"] * 3 for x in pre):
    raise RuntimeError("PASS16 authored source UV0 loop count mismatch")

if ASSET == "P16-06":
    # Unity local Y=-0.20 maps to Blender local Z=-0.20 after Y-up OBJ import.
    pivot = bpy.data.objects.new("ROTOR_Y_ANIMATABLE", None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = (0, 0, -0.20)
    bpy.context.view_layer.update()
    rotors = [ob for ob in objects if "_ROTOR_" in ob.name]
    if len(rotors) != 8:
        raise RuntimeError("P16-06: expected original 4 rotor solids plus 4 moving hub bolts, got %d" % len(rotors))
    for ob in rotors:
        old_world = ob.matrix_world.copy()
        ob.parent = pivot
        ob.matrix_world = old_world
    bpy.context.view_layer.update()
    if any(ob.parent != pivot for ob in rotors):
        raise RuntimeError("P16-06: rotor parent not preserved")

original_bounds = bounds(objects)
bpy.ops.wm.save_as_mainfile(filepath=str(blend_file))
if not blend_file.exists() or not blend_file.read_bytes().startswith(b"BLENDER-"):
    raise RuntimeError("Did not generate real native .blend file")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.fbx(filepath=str(fbx_file), use_selection=True,
    axis_forward="-Z", axis_up="Y", apply_unit_scale=True,
    global_scale=1.0, add_leaf_bones=False, bake_space_transform=False)
if not fbx_file.exists() or not fbx_file.read_bytes().startswith(b"Kaydara FBX Binary"):
    raise RuntimeError("Real binary Autodesk FBX not generated")
pre_fbx_bytes = fbx_file.stat().st_size

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(fbx_file), automatic_bone_orientation=False)
imported = mesh_objects()
post = inspect(imported)
# Verify the moving-rotor hierarchy AFTER genuine binary FBX re-import.
# A 360-degree animation is still a separate engine/editor test (NOT RUN).
if ASSET == "P16-06":
    pivot_after = [o for o in bpy.context.scene.objects if o.name.startswith("ROTOR_Y_ANIMATABLE")]
    moving_after = [o for o in imported if "_ROTOR_" in o.name]
    if len(pivot_after) != 1 or len(moving_after) != 8:
        raise RuntimeError("FBX lost the one rotor pivot or four rotor solids plus four attached rotating fasteners")
    if any(o.parent != pivot_after[0] for o in moving_after):
        raise RuntimeError("FBX imported rotor solids without their parent pivot")

if len(imported) != expected_parts + detail_counts[ASSET] + extra_counts[ASSET] + pass16_parts[ASSET]:
    raise RuntimeError("Binary FBX roundtrip changed mesh part count")
if sum(x["triangles"] for x in post) != sum(x["triangles"] for x in pre):
    raise RuntimeError("FBX roundtrip changed triangle count")
if any(not x["materials"] or "MISSING" in x["materials"] for x in post):
    raise RuntimeError("Missing material on FBX reimport")

after_bounds = bounds(imported)
max_error = max(abs(original_bounds[i][j] - after_bounds[i][j]) for i in range(3) for j in range(2))
if max_error > 0.001:
    raise RuntimeError("FBX imported bounds drifted %.8f m" % max_error)

report = {
    "asset": ASSET, "gate": "REAL_BLENDER_BINARY_FBX_ROUNDTRIP",
    "result": "PASS", "blender_version": bpy.app.version_string,
    "original_obj_sha256": sha256(obj_file), "detail_obj_sha256": sha256(detail_file),
    "detail_parts": detail_counts[ASSET], "detail_triangles": detail_triangles[ASSET],
    "detail15_sha256": sha256(extra_file) if extra_counts[ASSET] else None,
    "detail15_parts": extra_counts[ASSET], "detail15_triangles": extra_triangles[ASSET],
    "detail16_obj_sha256": sha256(pass16_file) if pass16_parts[ASSET] else None,
    "detail16_parts": pass16_parts[ASSET], "detail16_triangles": pass16_triangles[ASSET],
    "blend_sha256": sha256(blend_file),
    "binary_fbx_sha256": sha256(fbx_file), "fbx_bytes": pre_fbx_bytes,
    "parts_before": pre, "parts_after": post,
    "bounds_blender_before_xyz": original_bounds,
    "bounds_blender_after_fbx_reimport_xyz": after_bounds,
    "max_bounds_delta_m": max_error,
    "rotor_separate": ASSET == "P16-06",
    "unity_6_urp": "NOT_RUN", "independent_C01_02_QA": "BLOCKED",
}
(report_dir / "blender_binary_fbx_roundtrip.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("C01_16_PASS04_REAL_BLENDER_FBX_PASS", ASSET, report["binary_fbx_sha256"])
