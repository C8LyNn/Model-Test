#!/usr/bin/env python3
"""C01-01 / PASS04: native Blender n-gon / triangulation / FBX roundtrip gate.

Usage (real sources, not mock geometry):
  blender -b actual.blend --python-exit-code 13 --python Tools/c01_mesh_repair/triangulation_gate.py -- \
      --asset-id P19-05 --fbx actual.fbx --out report.json --require-explicit-triangles

Never repairs geometry. FAIL is meaningful: inspect the native source and re-export.
A passing result is NOT an independent C01-02 approval or a Unity import.
"""
import argparse
import collections
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

EPS_AREA2 = 1e-12
DOT_MIN = 0.999
POSITION_QUANT = 5


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def point(p):
    return tuple(round(float(v), POSITION_QUANT) for v in p)


def polygon_tessellation(mesh_obj):
    """Inspect Blender's REAL loop triangles and the original source polygon topology."""
    mesh = mesh_obj.data
    mesh.calc_loop_triangles()
    transform = mesh_obj.matrix_world
    out = collections.Counter()
    warnings = []
    nontri = []
    n_verts = 0
    area = 0.0
    neg_tri = 0
    zero_tri = 0
    bad_uv = 0
    face_triangle_area = collections.defaultdict(float)
    face_triangle_counts = collections.Counter()
    for face in mesh.polygons:
        if len(face.vertices) != 3:
            nontri.append({"object": mesh_obj.name, "polygon": face.index, "corners": len(face.vertices)})
        n_verts += len(face.vertices)
    uvs = mesh.uv_layers.active
    for triangle in mesh.loop_triangles:
        face = mesh.polygons[triangle.polygon_index]
        coords = [mesh.vertices[i].co for i in triangle.vertices]
        a, b, c = coords
        cross = (b - a).cross(c - a)
        squared = cross.length_squared
        if not math.isfinite(squared) or squared < EPS_AREA2:
            zero_tri += 1
        else:
            alignment = cross.normalized().dot(face.normal)
            if not math.isfinite(alignment) or alignment < DOT_MIN:
                neg_tri += 1
        face_triangle_area[face.index] += math.sqrt(squared) / 2 if squared >= 0 else 0
        face_triangle_counts[face.index] += 1
        corners = [point(transform @ mesh.vertices[i].co) for i in triangle.vertices]
        out[tuple(sorted(corners))] += 1
        if uvs is None or not all(
            math.isfinite(float(v)) for loop in triangle.loops for v in uvs.data[loop].uv
        ):
            bad_uv += 1
        area += math.sqrt(squared) / 2 if squared >= 0 else 0
    mismatch_area = 0
    for face in mesh.polygons:
        # A triangulated polygon must have exactly N-2 nondegenerate triangles.
        if face_triangle_counts[face.index] != len(face.vertices) - 2:
            warnings.append(f"{mesh_obj.name}:POLY_{face.index}_TRIANGLE_COUNT_WRONG")
        if abs(face_triangle_area[face.index] - face.area) > max(1e-6, face.area * 1e-4):
            mismatch_area += 1
    return {
        "mesh": mesh_obj.name,
        "polygons": len(mesh.polygons),
        "source_ngons": sum(p["corners"] > 4 for p in nontri),
        "non_triangles": len(nontri),
        "max_corners": max((len(p.vertices) for p in mesh.polygons), default=0),
        "nontri_examples": nontri[:20],
        "triangles": len(mesh.loop_triangles),
        "zero_area_triangles": zero_tri,
        "reversed_or_inconsistent_triangulation_normals": neg_tri,
        "triangle_missing_or_invalid_uv0": bad_uv,
        "area_disagreements": mismatch_area,
        "local_surface_area_m2": round(area, 9),
        "warnings": warnings,
        "_triangle_counter": out
    }


def snapshot():
    mesh_objects = sorted(
        (o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: o.name)
    details = [polygon_tessellation(o) for o in mesh_objects]
    counter = collections.Counter()
    for d in details:
        counter.update(d.pop("_triangle_counter"))
    return {
        "mesh_objects": len(mesh_objects),
        "stats": {
            field: sum(x[field] for x in details)
            for field in (
                "polygons", "source_ngons", "non_triangles", "triangles",
                "zero_area_triangles", "reversed_or_inconsistent_triangulation_normals",
                "triangle_missing_or_invalid_uv0", "area_disagreements"
            )
        },
        "objects": details, "_triangle_counter": counter
    }


def compare(asset_id, source, fbx, strict):
    original = snapshot()
    errors = []
    if not original["mesh_objects"]:
        errors.append("NO_SOURCE_MESHES")
    source_counts = original["stats"]
    if strict and source_counts["non_triangles"]:
        errors.append("SOURCE_NOT_EXPLICITLY_TRIANGULATED")
    for k in ("zero_area_triangles", "reversed_or_inconsistent_triangulation_normals",
              "triangle_missing_or_invalid_uv0", "area_disagreements"):
        if source_counts[k]:
            errors.append("SOURCE_" + k.upper())
    if fbx.read_bytes()[:18] != b"Kaydara FBX Binary":
        errors.append("NOT_BINARY_FBX")
        imported = None
    else:
        old_ids = {o.as_pointer() for o in bpy.data.objects}
        bpy.ops.import_scene.fbx(filepath=str(fbx))
        imported_objects = [o for o in bpy.data.objects
                            if o.type == "MESH" and o.as_pointer() not in old_ids]
        # Only imported objects: remove all original source objects before snapshot.
        imported_details = [polygon_tessellation(o) for o in imported_objects]
        imported_counter = collections.Counter()
        for d in imported_details:
            imported_counter.update(d.pop("_triangle_counter"))
        imported = {
            "mesh_objects": len(imported_objects),
            "stats": {k: sum(x[k] for x in imported_details) for k in source_counts},
            "objects": imported_details,
            "_triangle_counter": imported_counter
        }
        if original["mesh_objects"] != imported["mesh_objects"]:
            errors.append("IMPORT_MESH_COUNT_CHANGED")
        if source_counts["triangles"] != imported["stats"]["triangles"]:
            errors.append("IMPORT_TRIANGLE_COUNT_CHANGED")
        if strict and imported["stats"]["non_triangles"]:
            errors.append("IMPORTED_FBX_NOT_EXPLICITLY_TRIANGULATED")
        if original["_triangle_counter"] != imported_counter:
            errors.append("SOURCE_VS_IMPORT_TRIANGLE_POSITIONS_DIFFER")
        for k in ("zero_area_triangles", "reversed_or_inconsistent_triangulation_normals",
                  "triangle_missing_or_invalid_uv0", "area_disagreements"):
            if imported["stats"][k]:
                errors.append("FBX_" + k.upper())
    original.pop("_triangle_counter", None)
    if imported is not None:
        imported.pop("_triangle_counter", None)
    return {
        "schema": "C01-TRIANGULATION-GATE-1.0",
        "asset_id": asset_id,
        "source_blend_sha256": sha256(source),
        "binary_fbx_sha256": sha256(fbx),
        "blender_version": bpy.app.version_string,
        "explicit_triangles_required": strict,
        "source": original,
        "reimported_fbx": imported,
        "result": "FAIL" if errors else "PASS",
        "errors": sorted(set(errors)),
        "unity": "NOT_RUN", "independent_qa": "PENDING",
        "meaning": "Actual source Blender and existing FBX inspected. Not source re-export proof; no geometry edited."
    }


def main():
    tail = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--asset-id", required=True)
    p.add_argument("--fbx", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--require-explicit-triangles", action="store_true")
    args = p.parse_args(tail)
    source = Path(bpy.data.filepath)
    if not source.is_file() or source.read_bytes()[:7] != b"BLENDER":
        raise RuntimeError("Missing actual native .blend")
    if not args.fbx.is_file():
        raise RuntimeError("Missing actual binary FBX")
    r = compare(args.asset_id, source, args.fbx, args.require_explicit_triangles)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n")
    print("C01_TRIANGULATION_GATE " + json.dumps({
        "asset_id": args.asset_id, "result": r["result"],
        "errors": r["errors"],
        "source_non_triangles": r["source"]["stats"]["non_triangles"],
        "import_non_triangles": r["reimported_fbx"]["stats"]["non_triangles"] if r["reimported_fbx"] else None
    }))
    if r["result"] != "PASS":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
