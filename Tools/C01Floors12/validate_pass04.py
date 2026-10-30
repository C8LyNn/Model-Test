"""C01-12 PASS04: read-only real Blender v003 / binary FBX triangulation & normals audit.
No meshes written, welded, exported, triangulated destructively, or replaced.
CI: blender --background --factory-startup --python Tools/C01Floors12/validate_pass04.py
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2] / "C01StandaloneKits" / "FloorCeiling"
REP=ROOT / "RepairPass03"
STEMS={
  "F01":"C01_SHI_F01_FLOOR_BASIC_v003",
  "F02":"C01_SHI_F02_FLOOR_MARKED_v003",
  "C01":"C01_SHI_C01_CEILING_BASIC_v003",
}
EXPECTED_BOUNDS={
  "F01":((0.,-1.,-.2),(1.,0.,0.)),
  "F02":((0.,-1.,-.2),(1.,0.,0.)),
  "C01":((0.,-1.,3.),(1.,0.,3.2)),
}
TOL=1e-5
AREA_TOL=1e-10

def good(value):
    assert math.isfinite(value)
    return float(value)

def mesh_snapshot(obj, asset_id, context):
    assert obj.type=="MESH", (asset_id,context,"not_mesh")
    me=obj.data
    assert len(me.vertices)==16 and len(me.polygons)==14, (asset_id,context,"mesh_counts")
    me.calc_loop_triangles()
    pts=[obj.matrix_world @ v.co for v in me.vertices]
    lo=[min(good(p[i]) for p in pts) for i in range(3)]
    hi=[max(good(p[i]) for p in pts) for i in range(3)]
    expected=EXPECTED_BOUNDS[asset_id]
    bound_error=max(abs(value-target) for a,b in zip((lo,hi),expected) for value,target in zip(a,b))
    assert bound_error<TOL, (asset_id,context,"bounds_error",bound_error)
    assert (obj.scale-Vector((1,1,1))).length<TOL, (asset_id,context,"unit_scale")
    assert obj.location.length<TOL, (asset_id,context,"origin_location")
    assert obj.rotation_euler.length<TOL, (asset_id,context,"root_rotation")
    assert len(me.edges)==28 and len(me.loop_triangles)==28, (asset_id,context,"triangles")
    assert set(len(p.vertices) for p in me.polygons)=={4}, (asset_id,context,"non_quad")
    assert len(me.materials)==3 and all(m is not None for m in me.materials), (asset_id,context,"materials")
    assert all(not p.use_smooth for p in me.polygons), (asset_id,context,"unintended_smoothing")
    uv=me.uv_layers.active
    assert uv is not None, (asset_id,context,"missing_uv0")
    center=sum(pts, Vector())/len(pts)
    edges={}
    for p in me.polygons:
        face=list(p.vertices)
        assert len(set(face))==len(face), (asset_id,context,"duplicate_face_vertex")
        for a,b in zip(face,face[1:]+face[:1]):
            key=tuple(sorted((a,b)))
            edges.setdefault(key,[]).append((a,b))
    assert len(edges)==28, (asset_id,context,"edge_key_count")
    assert all(len(v)==2 and v[0]==v[1][::-1] for v in edges.values()), (asset_id,context,"manifold_or_winding")
    assert all((pts[b]-pts[a]).length>1e-8 for a,b in edges), (asset_id,context,"zero_length_edge")
    tri_areas=[]
    uv_tri_areas=[]
    tri_by_poly={}
    bad_normal=[]
    degenerate=[]
    for triangle in me.loop_triangles:
        a,b,c=(pts[v] for v in triangle.vertices)
        cross=(b-a).cross(c-a)
        area=.5*cross.length
        if area<AREA_TOL:degenerate.append(triangle.index)
        tri_areas.append(area)
        polygon=me.polygons[triangle.polygon_index]
        world_normal=obj.matrix_world.to_3x3() @ polygon.normal
        if cross.dot(world_normal) <= 0:bad_normal.append(triangle.index)
        tri_by_poly.setdefault(polygon.index,[]).append(area)
        uvp=[uv.data[loop].uv.copy() for loop in triangle.loops]
        for point in uvp:
            assert math.isfinite(point.x) and math.isfinite(point.y), (asset_id,context,"uv_nan_inf")
        uv_area=.5*abs((uvp[1]-uvp[0]).cross(uvp[2]-uvp[0]))
        uv_tri_areas.append(float(uv_area))
    assert not degenerate, (asset_id,context,"degenerate_triangles",degenerate)
    assert not bad_normal, (asset_id,context,"triangle_vs_polygon_normal",bad_normal)
    assert min(uv_tri_areas)>AREA_TOL, (asset_id,context,"zero_area_uv_triangle",min(uv_tri_areas))
    area_error=max(abs(sum(tri_by_poly[p.index])-p.area) for p in me.polygons)
    assert area_error<TOL, (asset_id,context,"triangulation_area_mismatch",area_error)
    # Exterior facing: 14 quads are box shell subdivisions, not nested or moving islands
    inward=[]
    for p in me.polygons:
        centroid=sum((pts[v] for v in p.vertices),Vector()) / len(p.vertices)
        normal=(obj.matrix_world.to_3x3() @ p.normal).normalized()
        if normal.dot(centroid-center)<1e-5:inward.append(p.index)
    assert not inward, (asset_id,context,"inward_faces",inward)
    adjacent={i:set() for i in range(len(pts))}
    for a,b in edges:
        adjacent[a].add(b);adjacent[b].add(a)
    visited=set()
    components=0
    for index in adjacent:
        if index not in visited:
            components+=1
            todo=[index];visited.add(index)
            while todo:
                for nxt in adjacent[todo.pop()]:
                    if nxt not in visited:
                        visited.add(nxt);todo.append(nxt)
    assert components==1 and len(visited)==len(pts), (asset_id,context,"loose_geometry_or_components")
    poly_materials=[p.material_index for p in me.polygons]
    assert all(0<=m<len(me.materials) for m in poly_materials),(asset_id,context,"invalid_material_index")
    return {
        "vertices":len(me.vertices),"edges":len(me.edges),"faces":len(me.polygons),
        "triangles":len(me.loop_triangles),"quads":len(me.polygons),
        "components":components,"boundary_edges":0,"nonmanifold_edges":0,
        "degenerate_triangles":len(degenerate),"misoriented_triangles":len(bad_normal),
        "inward_faces":len(inward),"uv0_zero_area_triangles":sum(x<=AREA_TOL for x in uv_tri_areas),
        "min_triangle_area_m2":min(tri_areas),"min_triangle_uv0_area":min(uv_tri_areas),
        "triangulation_area_max_delta_m2":area_error,
        "material_names":[m.name for m in me.materials],
        "per_polygon_material_indices":poly_materials,
        "bounds_world_xyz":[lo,hi],
        "bounds_max_error_m":bound_error,
        "source_mesh_signature":{
            "vertices_xyz":[[round(float(t),7) for t in v.co] for v in me.vertices],
            "faces_vertex_indices":[list(p.vertices) for p in me.polygons]
        }
    }

def check(id,stem):
    blend=REP/"Blend"/(stem+".blend")
    fbx=REP/"FBX"/(stem+".fbx")
    assert blend.exists() and fbx.exists(),(id,"missing_binary")
    assert blend.read_bytes().startswith(b"BLENDER"),(id,"invalid_blend_header")
    assert fbx.read_bytes().startswith(b"Kaydara FBX Binary  "+bytes((0,26,0))),(id,"invalid_fbx_header")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    objs=[o for o in bpy.data.objects if o.type=="MESH"]
    assert len(objs)==1,(id,"blend_mesh_parts")
    src=mesh_snapshot(objs[0],id,"original_v003_blend")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    objs=[o for o in bpy.data.objects if o.type=="MESH"]
    assert len(objs)==1,(id,"fbx_mesh_parts")
    dst=mesh_snapshot(objs[0],id,"fbx_reimport")
    for key in ("vertices","edges","faces","triangles","components","material_names","per_polygon_material_indices"):
        assert src[key]==dst[key],(id,"roundtrip_mismatch",key,src[key],dst[key])
    for axis in range(3):
        for limit in range(2):
            assert abs(src["bounds_world_xyz"][limit][axis]-dst["bounds_world_xyz"][limit][axis])<TOL
    return {
        "asset_id":"C01-12-"+id,
        "scope":"LEGACY_STANDALONE_NOT_IN_36_P15_P19",
        "blend_source_sha256":hashlib.sha256(blend.read_bytes()).hexdigest(),
        "binary_fbx_sha256":hashlib.sha256(fbx.read_bytes()).hexdigest(),
        "blend_native_real_test":"PASS",
        "fbx_binary_real_import_test":"PASS",
        "source":src,
        "fbx_roundtrip":dst,
        "unity6_urp":"NOT_RUN",
        "independent_C01_02_qa":"PENDING",
        "mesh_modified_by_pass04":False
    }

if __name__=="__main__":
    report={k:check(k,stem) for k,stem in STEMS.items()}
    a,b=report["F01"]["source"],report["F02"]["source"]
    assert a["source_mesh_signature"]==b["source_mesh_signature"],"F01 F02 physical slot mismatch"
    assert a["per_polygon_material_indices"]!=b["per_polygon_material_indices"],"F01/F02 material-only variant lost"
    out=ROOT/"QA"/"Pass04_readonly_validation.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"models":report,"F01_F02_same_geometry":True,
      "no_mesh_changes":True,"independent_qa":"PENDING","unity":"NOT_RUN"},indent=2,ensure_ascii=False)+"\n")
    print("C01-12 PASS04 READONLY REAL BLENDER/FBX TESTS PASSED",flush=True)
