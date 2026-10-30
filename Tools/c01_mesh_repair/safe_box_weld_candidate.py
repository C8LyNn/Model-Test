#!/usr/bin/env python3
"""C01-01 PASS03: conservative *opt-in* repair on copies of exact split-quad boxes only.

NOT a general Merge by Distance tool. It hard-aborts if any object differs from
24V/30E/12F/6 islands of a triangulated rectangular solid, UV/hard-edge/material
invariants are not preserved, or repairing would involve distinct object meshes.

Original producer .blend is read-only; output is stored under --output-dir.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh


def load_auditor():
    path=Path(__file__).with_name("topology_audit.py")
    spec=importlib.util.spec_from_file_location("c01_pass03_topo",path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def bmesh_invariants(bm):
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    uv=bm.loops.layers.uv.active
    uvs=sorted((round(float(loop[uv].uv.x),6),round(float(loop[uv].uv.y),6))
               for face in bm.faces for loop in face.loops) if uv else []
    return dict(
        triangles=sum(max(0,len(f.verts)-2) for f in bm.faces),
        area=sum(float(f.calc_area()) for f in bm.faces),
        face_normals=sorted(tuple(round(float(x),5) for x in face.normal) for face in bm.faces),
        materials=sorted(int(f.material_index) for f in bm.faces),
        uv_count=len(uvs),uvs=uvs,
        min_xyz=[min((v.co[i] for v in bm.verts),default=0) for i in range(3)],
        max_xyz=[max((v.co[i] for v in bm.verts),default=0) for i in range(3)])


def ensure_box_candidate(bm, obj, mod):
    """Accept only 6 independent planar faces of same rectangular prism."""
    if (len(bm.verts),len(bm.edges),len(bm.faces))!=(24,30,12):
        raise RuntimeError(obj.name+": expected 24V/30E/12F detached triangulated box")
    if [len(c) for c in []]:  # no implicit generic merge permission
        raise RuntimeError("unreachable")
    if mod._components(bm)!=[4]*6:
        raise RuntimeError(obj.name+": expected exactly six disjoint quad islands")
    if not obj.data.uv_layers.active:
        raise RuntimeError(obj.name+": UV0 missing, preserve seams instead of welding blindly")
    if any(poly.use_smooth for poly in obj.data.polygons):
        raise RuntimeError(obj.name+": smooth/hard edge profile ambiguous, manual review")
    coords={}
    for v in bm.verts:
        key=mod._rounded_key(v.co,6)
        coords[key]=coords.get(key,0)+1
    if len(coords)!=8 or any(n!=3 for n in coords.values()):
        raise RuntimeError(obj.name+": expected eight 3x-coincident box corners")
    mins=[min(p[i] for p in coords) for i in range(3)]
    maxs=[max(p[i] for p in coords) for i in range(3)]
    if any(maxs[i]-mins[i]<1e-4 for i in range(3)):
        raise RuntimeError(obj.name+": zero/thin geometry or invalid cuboid")
    if any(any(abs(p[i]-mins[i])>1e-6 and abs(p[i]-maxs[i])>1e-6 for i in range(3)) for p in coords):
        raise RuntimeError(obj.name+": non-cuboid vertex set; manual repair necessary")
    for f in bm.faces:
        if len(f.verts)!=3 or f.calc_area()<=1e-12:
            raise RuntimeError(obj.name+": unexpected face or degeneracy")
        # Every triangle sits on exactly one of the six planes of a box.
        if sum(all(abs(v.co[i]-plane)<=1e-6 for v in f.verts)
               for i in range(3) for plane in (mins[i],maxs[i]))!=1:
            raise RuntimeError(obj.name+": triangle not on one cuboid side")


def weld_object(obj, mod):
    original_matrix=[list(row) for row in obj.matrix_world]
    names=[m.name if m else None for m in obj.data.materials]
    bm=bmesh.new()
    try:
        bm.from_mesh(obj.data)
        ensure_box_candidate(bm,obj,mod)
        pre=bmesh_invariants(bm)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bm.normal_update()
        post=bmesh_invariants(bm)
        if (len(bm.verts),len(bm.edges),len(bm.faces))!=(8,18,12):
            raise RuntimeError(obj.name+": post geometry !=8V/18E/12F")
        if any(e.is_boundary or not e.is_manifold or not e.is_contiguous for e in bm.edges):
            raise RuntimeError(obj.name+": post has nonmanifold/boundary/inconsistent winding")
        if any(f.calc_area()<1e-12 for f in bm.faces):
            raise RuntimeError(obj.name+": post has degenerate faces")
        for prop in ("triangles","face_normals","materials","uvs"):
            if pre[prop]!=post[prop]:
                raise RuntimeError(obj.name+": loop/shading invariant changed: "+prop)
        for axis in range(3):
            if abs(pre["min_xyz"][axis]-post["min_xyz"][axis])>1e-6 or abs(pre["max_xyz"][axis]-post["max_xyz"][axis])>1e-6:
                raise RuntimeError(obj.name+": geometry bounds changed")
        if abs(pre["area"]-post["area"])>1e-6:
            raise RuntimeError(obj.name+": surface area changed")
        bm.to_mesh(obj.data)
        obj.data.update()
        if [m.name if m else None for m in obj.data.materials]!=names:
            raise RuntimeError(obj.name+": material list changed")
        if any(abs(obj.matrix_world[i][j]-original_matrix[i][j])>1e-8 for i in range(4) for j in range(4)):
            raise RuntimeError(obj.name+": pivot / transform changed")
        return dict(mesh=obj.name,before={"vertices":24,"edges":30,"faces":12,"tris":pre["triangles"]},
                    after={"vertices":8,"edges":18,"faces":12,"tris":post["triangles"]},
                    retained_UV_loops=len(pre["uvs"]),original_area=pre["area"],repaired_area=post["area"])
    finally:
        bm.free()


def main():
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    ap=argparse.ArgumentParser()
    ap.add_argument("--asset-id",choices=["P17-04","P17-05"],required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args(argv)
    source=Path(bpy.data.filepath)
    if not source.is_file() or source.read_bytes()[:7]!=b"BLENDER":
        raise RuntimeError("Missing actual hydrated Blender source")
    mod=load_auditor()
    objects=sorted((o for o in bpy.data.objects if o.type=="MESH"),key=lambda o:o.name)
    expected={"P17-04":29,"P17-05":20}[a.asset_id]
    if len(objects)!=expected:
        raise RuntimeError("Unexpected object count; expected %d actual %d"%(expected,len(objects)))
    a.output_dir.mkdir(parents=True,exist_ok=True)
    before=mod.audit(a.asset_id,"BEFORE")
    original_parts=[o.name for o in objects]
    changes=[]
    for o in objects:
        changes.append(weld_object(o,mod))
    destination=a.output_dir/(a.asset_id+"_REPAIRED.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(destination))
    after=mod.audit(a.asset_id,"AFTER")
    if [o.name for o in sorted((o for o in bpy.data.objects if o.type=="MESH"),key=lambda o:o.name)]!=original_parts:
        raise RuntimeError("Object name/child structure changed")
    if any(sum(x["mesh_issues"][k] for x in after["object_data"]) for k in
           ("zero_length_edges","degenerate_faces","loose_vertices","loose_edges",
            "boundary_edges","nonmanifold_overconnected_edges",
            "inconsistent_winding_edges","colocated_vertex_candidates")):
        raise RuntimeError("Repaired mesh still has topology defects")
    before_file=a.output_dir/"mesh_topology_before.json"
    after_file=a.output_dir/"mesh_topology_after.json"
    before_file.write_text(json.dumps(before,indent=2)+"\n")
    after_file.write_text(json.dumps(after,indent=2)+"\n")
    fbx=a.output_dir/(a.asset_id+"_REPAIRED.fbx")
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=False,
        object_types={"EMPTY","MESH"},apply_unit_scale=True,
        axis_forward="-Z",axis_up="Y",path_mode="AUTO",add_leaf_bones=False)
    if fbx.read_bytes()[:18]!=b"Kaydara FBX Binary":
        raise RuntimeError("Export is not binary FBX")
    expected_triangles=sum(x["counts"]["triangles"] for x in after["object_data"])
    # Fresh Blender scene: actual binary FBX importer, not an assumed export result.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    imported=[o for o in bpy.data.objects if o.type=="MESH"]
    actual_triangles=sum(sum(max(0,len(p.vertices)-2) for p in o.data.polygons) for o in imported)
    has_uv=all(o.data.uv_layers for o in imported)
    fbx_status="PASS" if actual_triangles==expected_triangles and len(imported)==expected and has_uv else "FAIL"
    data=dict(asset_id=a.asset_id,source_original=str(source),source_original_sha256=before["source_sha256"],
        repaired_blend=str(destination),repaired_blend_sha256=sha(destination),
        repaired_fbx=str(fbx),repaired_fbx_sha256=sha(fbx),
        changed_meshes=len(changes),modifications=changes,
        preserved_object_count=len(imported),expected_triangles=expected_triangles,
        imported_triangles=actual_triangles,imported_mesh_count=len(imported),
        imported_uv0_every_mesh=has_uv,fbx_import_topology_static=fbx_status,
        qa_independent="NOT_RUN",qa_unity="NOT_RUN",release="PROPOSED_COPY_NOT_MERGED")
    (a.output_dir/"REPAIR_AND_FBX_ROUNDTRIP.json").write_text(json.dumps(data,indent=2)+"\n")
    print("C01_SAFE_REPAIR "+json.dumps({k:data[k] for k in ("asset_id","changed_meshes",
          "expected_triangles","imported_triangles","imported_mesh_count","fbx_import_topology_static")}))
    if fbx_status!="PASS":
        raise SystemExit(4)


if __name__=="__main__":
    main()
