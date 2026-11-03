#!/usr/bin/env python3
"""C01-01 PASS03 native source-vs-existing-FBX importer preflight.

Run with REAL production .blend loaded and real binary FBX on disk.
Does not use parametric reconstructions; imported vertex split on UV/sharp is allowed.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy


def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def triangles(objects):
    return sum(sum(max(0,len(f.vertices)-2) for f in o.data.polygons) for o in objects)


def snapshot(objects):
    return {
        "mesh_count":len(objects),
        "triangles":triangles(objects),
        "mesh_names":[o.name for o in objects],
        "uv0_present_on_all_render_meshes":all(bool(o.data.uv_layers) for o in objects if o.data.polygons),
        "materials_used":sorted(set(s.material.name for o in objects for s in o.material_slots if s.material)),
        "world_vertices_bbox_xyz_m":bounds(objects),
        "mesh_local_scales":[{"name":o.name,"scale":[round(float(x),8) for x in o.scale]} for o in objects]
    }


def bounds(objects):
    xyz=[[],[],[]]
    for o in objects:
        for vertex in o.data.vertices:
            p=o.matrix_world @ vertex.co
            for i in range(3):
                xyz[i].append(float(p[i]))
    return [
      [min(vals) if vals else 0 for vals in xyz],
      [max(vals) if vals else 0 for vals in xyz]
    ]


def run(source, fbx, asset_id):
    source_objs=[o for o in bpy.data.objects if o.type=="MESH"]
    if not source_objs:
        raise RuntimeError("No original mesh objects from source .blend")
    old_ptrs={o.as_pointer() for o in bpy.data.objects}
    if fbx.read_bytes()[:18]!=b"Kaydara FBX Binary":
        raise RuntimeError("FBX is not native binary; refuse reader status")
    before=snapshot(source_objs)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    after_objs=[o for o in bpy.data.objects if o.type=="MESH" and o.as_pointer() not in old_ptrs]
    after=snapshot(after_objs)
    errors=[]
    if not after_objs:
        errors.append("FBX_IMPORT_MISSING_MESHES")
    if before["triangles"]!=after["triangles"]:
        errors.append("TRIANGULATION_COUNT_MISMATCH")
    if before["mesh_count"]!=after["mesh_count"]:
        errors.append("MESH_COUNT_CHANGED")
    if before["uv0_present_on_all_render_meshes"] and not after["uv0_present_on_all_render_meshes"]:
        errors.append("UV0_DROPPED_DURING_EXPORT")
    # World-space bounding may differ from import rotation when coordinate-system
    # conventions differ. Report deviations as REVIEW, not topology failure.
    discrepancy=max(abs(a-b) for side_a,side_b in zip(before["world_vertices_bbox_xyz_m"],after["world_vertices_bbox_xyz_m"])
                       for a,b in zip(side_a,side_b))
    review=[]
    if discrepancy > .001:
        review.append("WORLD_BOUNDS_DIFFER_MORE_THAN_1MM_CHECK_AXIS_ROTATION_AND_PIVOTS")
    return {
        "schema":"C01-FBX-SOURCE-COMPARE-1.0","asset_id":asset_id,
        "source_blend":str(source),"source_blend_sha256":sha256(source),
        "existing_export_fbx":str(fbx),"existing_export_fbx_sha256":sha256(fbx),
        "blender_version":bpy.app.version_string,
        "source":before,"fbx_imported_in_blender":after,
        "max_world_bbox_delta_m":round(discrepancy,7),
        "static_import_status":"FAIL" if errors else "PASS",
        "errors":errors,"review_candidates":review,
        "notes":["REAL Blender import of supplied binary FBX executed",
                 "Source FBX provenance/export CI not independently reproduced by this step",
                 "Per-vertex FBX split at UV/hard edge is expected and NOT a topology failure",
                 "Unity import / user preview / C01-02 review NOT RUN"]
    }


def main():
    args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p=argparse.ArgumentParser()
    p.add_argument("--fbx",type=Path,required=True)
    p.add_argument("--asset-id",required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(args)
    source=Path(bpy.data.filepath)
    if not source.is_file() or source.read_bytes()[:7]!=b"BLENDER":
        raise RuntimeError("Real source .blend absent")
    if not a.fbx.is_file():
        raise RuntimeError("Native FBX absent")
    report=run(source,a.fbx,a.asset_id)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("C01_REAL_FBX_IMPORT "+json.dumps({k:report[k] for k in
          ("asset_id","static_import_status","errors","review_candidates")}))
    if report["static_import_status"]!="PASS":
        raise SystemExit(4)


if __name__=="__main__":
    main()
