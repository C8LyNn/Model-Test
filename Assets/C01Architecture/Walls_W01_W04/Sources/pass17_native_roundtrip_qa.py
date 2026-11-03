"""C01-11 PASS17: real Blender 4.x QA-only .blend open, FBX import, geometry/UV parity.

Do not mutate production source or count static checks as Unity approval.
"""
import bpy
import json
import hashlib
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "QA_Candidates" / "PASS17_SourceRecovery"
OUT = QA / "QA" / "PASS17_REAL_BLENDER_ROUNDTRIP.json"
EXPECTED = {"W01": (12, 8), "W02": (572, 288),
            "W03": (20, 12), "W04": (28, 16)}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot(objects):
    mesh_objects = [obj for obj in objects if obj.type == "MESH"]
    if len(mesh_objects) != 1:
        raise RuntimeError("Expected one physical mesh, found " + str(len(mesh_objects)))
    obj = mesh_objects[0]
    mesh = obj.data
    mesh.calc_loop_triangles()
    if len(mesh.uv_layers) < 1 or len(obj.material_slots) < 1:
        raise RuntimeError("UV0 or material slots missing")
    if obj.scale != obj.scale.__class__((1,1,1)):
        raise RuntimeError("Source/import object has unexpected local scale")
    world = obj.matrix_world
    positions = {tuple(round(c,5) for c in world @ vert.co) for vert in mesh.vertices}
    uv = mesh.uv_layers.active.data
    attribute_pairs = set()
    for polygon in mesh.polygons:
        for li in polygon.loop_indices:
            idx = mesh.loops[li].vertex_index
            xyz = tuple(round(c,5) for c in world @ mesh.vertices[idx].co)
            tex = tuple(round(t,5) for t in uv[li].uv)
            attribute_pairs.add((xyz,tex))
    return {"triangles": len(mesh.loop_triangles),
            "vertices": len(mesh.vertices),
            "unique_positions": positions,
            "position_uv_pairs": attribute_pairs,
            "material_slots": len(obj.material_slots),
            "uv_layers": len(mesh.uv_layers)}

results=[]
errors=[]
OUT.parent.mkdir(parents=True,exist_ok=True)
for mid,(triangles,verts) in EXPECTED.items():
    blend = next(iter((QA / "Blender").glob(mid + "_*.blend")),None)
    fbx = next(iter((QA / "FBX").glob(mid + "_*.fbx")),None)
    try:
        if blend is None or fbx is None:
            raise FileNotFoundError(mid + ": physical .blend or .fbx missing")
        if blend.read_bytes()[:7] != b"BLENDER":
            raise RuntimeError(mid + ": invalid Blender native source")
        if fbx.read_bytes()[:20] != b"Kaydara FBX Binary  ":
            raise RuntimeError(mid + ": invalid real binary FBX")
        bpy.ops.wm.open_mainfile(filepath=str(blend))
        source = snapshot(list(bpy.data.objects))
        if source["triangles"] != triangles or source["vertices"] != verts:
            raise RuntimeError(mid + ": source mesh detail loss " + str(source))
        ids_before = {obj.as_pointer() for obj in bpy.data.objects}
        bpy.ops.import_scene.fbx(filepath=str(fbx))
        imported = [obj for obj in bpy.data.objects if obj.as_pointer() not in ids_before]
        after = snapshot(imported)
        if after["triangles"] != triangles:
            raise RuntimeError(mid + ": FBX reimport triangles differ: " + str(after["triangles"]))
        if source["unique_positions"] != after["unique_positions"]:
            raise RuntimeError(mid + ": FBX reimport vertex positions differ")
        if source["position_uv_pairs"] != after["position_uv_pairs"]:
            raise RuntimeError(mid + ": FBX reimport vertex UV0 pairs differ")
        results.append({"id":mid,"result":"PASS",
                        "source_blend_sha256":digest(blend),
                        "blender_fbx_sha256":digest(fbx),
                        "source_triangles":source["triangles"],
                        "reimport_triangles":after["triangles"],
                        "source_vertices":source["vertices"],
                        "import_vertices":after["vertices"],
                        "source_uv0_pairs":len(source["position_uv_pairs"]),
                        "import_uv0_pairs":len(after["position_uv_pairs"]),
                        "material_slots_source":source["material_slots"],
                        "material_slots_import":after["material_slots"]})
        print("PASS actual Blender reopen/import",mid,source["triangles"])
    except Exception as e:
        errors.append(mid+": "+str(e))
        results.append({"id":mid,"result":"FAIL","reason":str(e)})
        print("FAIL actual Blender roundtrip",mid,str(e))

OUT.write_text(json.dumps({"schema":"C01-11-PASS17-NATIVE-ROUNDTRIP",
    "engine":bpy.app.version_string, "result":"FAIL" if errors else "PASS",
    "results":results,"errors":errors,"unity6_urp":"NOT RUN",
    "independent_C01_02":"PENDING"},indent=2)+"\n")
if errors:
    raise SystemExit("Native Blender roundtrip failed: " + "; ".join(errors))
