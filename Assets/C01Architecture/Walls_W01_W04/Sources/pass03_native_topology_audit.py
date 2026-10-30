#!/usr/bin/env python3
"""C01-11 PASS03: audit actual existing .blend, FBX reimport, no blind welding.

DO NOT replace existing W02 r2 with the 12-triangle W02 candidate produced by
this branch. All results refer to GitHub branch .blend/.fbx only.
"""
import bpy, bmesh, json, math, hashlib
from collections import Counter, defaultdict
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "QA"
OUT.mkdir(exist_ok=True, parents=True)
PRE = ROOT / "Previews"
PRE.mkdir(exist_ok=True, parents=True)
NAMES = {
 "W01":"FULL_WALL_1M", "W02":"PANEL_WALL_1M",
 "W03":"CORNER_90_1M", "W04":"DOOR_OPENING_2M"
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def inspect(obj):
    mesh=obj.data
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    verts=[tuple(round(x,9) for x in v.co) for v in bm.verts]
    tris=sum(len(f.verts)-2 for f in bm.faces)
    edges=Counter(tuple(sorted((v.index for v in e.verts))) for e in bm.edges)
    face_keys=[tuple(sorted(v.index for v in f.verts)) for f in bm.faces]
    loose_v=sum(len(v.link_edges)==0 for v in bm.verts)
    loose_e=sum(len(e.link_faces)==0 for e in bm.edges)
    duplicate_v=len(verts)-len(set(verts))
    duplicate_f=len(face_keys)-len(set(face_keys))
    invalid_f=sum(f.calc_area()<1e-10 for f in bm.faces)
    nonmanifold_e=sum(len(e.link_faces)>2 for e in bm.edges)
    boundary_e=sum(len(e.link_faces)==1 for e in bm.edges)
    zero_edges=sum((e.verts[0].co-e.verts[1].co).length<1e-10 for e in bm.edges)
    # Count geometric vertex connections with a DFS over linked edges.
    unseen=set(bm.verts)
    components=0
    while unseen:
        components+=1; stack=[unseen.pop()]
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                for u in e.verts:
                    if u in unseen:
                        unseen.remove(u);stack.append(u)
    issues={
      "loose_vertices":loose_v,"loose_edges":loose_e,"duplicate_positions":duplicate_v,
      "duplicate_faces":duplicate_f,"zero_area_faces":invalid_f,
      "nonmanifold_edges":nonmanifold_e,"unexpected_boundary_edges":boundary_e,
      "zero_length_edges":zero_edges
    }
    data={
      "vertices":len(bm.verts),"edges":len(bm.edges),"faces":len(bm.faces),
      "triangles":tris,"connected_components":components,
      **issues,"uv0_present":bool(mesh.uv_layers),
      "material_slots":len(obj.material_slots),
      "root_location":list(obj.location),"root_scale":list(obj.scale),
      "root_rotation":list(obj.rotation_euler),
      "mesh_bounds_local":[[min(v[i] for v in verts) for i in range(3)],
                           [max(v[i] for v in verts) for i in range(3)]]
    }
    bm.free()
    return data

def triangles_world(obj):
    mesh=obj.data
    mesh.calc_loop_triangles()
    w=obj.matrix_world
    tri=[]
    for t in mesh.loop_triangles:
        p=[tuple(round(float(x),5) for x in w @ mesh.vertices[i].co)
           for i in t.vertices]
        tri.append(tuple(sorted(p)))
    return sorted(tri)

def capture(obj,mid,tag):
    # Render directly from imported genuine model; camera is helper, never saved.
    camera_data=bpy.data.cameras.new("PASS03_Camera")
    camera=bpy.data.objects.new("PASS03_Camera",camera_data)
    bpy.context.scene.collection.objects.link(camera)
    corners=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    target=sum(corners,Vector())/8
    camera.location=target+Vector((5,-6,3.5))
    camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
    camera_data.type="ORTHO";camera_data.ortho_scale=4.8
    sc=bpy.context.scene;sc.camera=camera
    sc.render.engine="BLENDER_WORKBENCH"
    sc.display.shading.light="STUDIO"
    sc.display.shading.color_type="MATERIAL"
    # Temporary Blender wireframe modifier renders exact existing source edges.
    # It is NOT applied to data or saved into .blend/FBX: evidence only.
    preview_modifier=None
    if "wire" in tag:
        preview_modifier=obj.modifiers.new("PASS03_PREVIEW_ONLY_REAL_EDGES","WIREFRAME")
        preview_modifier.thickness=0.006
        preview_modifier.use_replace=True
    sc.render.resolution_x=980;sc.render.resolution_y=720
    sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG"
    obj.show_wire=("wire" in tag)
    obj.show_all_edges=("wire" in tag)
    sc.render.filepath=str(PRE/(mid+"_PASS03_"+tag+".png"))
    bpy.ops.render.render(write_still=True)
    if preview_modifier is not None:
        obj.modifiers.remove(preview_modifier)
    obj.show_wire=False;obj.show_all_edges=False
    bpy.data.objects.remove(camera,do_unlink=True)
    bpy.data.cameras.remove(camera_data)

results=[]
for mid,name in NAMES.items():
    src=ROOT/"Blender"/(mid+"_"+name+".blend")
    fbx=ROOT/"FBX"/(mid+"_"+name+".fbx")
    assert src.is_file() and fbx.is_file(),mid
    assert src.read_bytes()[:7]==b"BLENDER"
    assert fbx.read_bytes()[:20]==b"Kaydara FBX Binary  "
    bpy.ops.wm.open_mainfile(filepath=str(src))
    objects=[o for o in bpy.data.objects if o.type=="MESH"]
    assert len(objects)==1, (mid,"expected one intentional solid",len(objects))
    obj=objects[0]
    before=inspect(obj)
    source_tris=triangles_world(obj)
    capture(obj,mid,"before_wire")
    fatal=[k for k in (
      "loose_vertices","loose_edges","duplicate_positions","duplicate_faces",
      "zero_area_faces","nonmanifold_edges","unexpected_boundary_edges",
      "zero_length_edges") if before[k]!=0]
    # Do not blindly weld seams / hard edges. No change without proof.
    # Preserve original native source SHA and FBX SHA.
    capture(obj,mid,"after_wire")
    capture(obj,mid,"after_shaded")
    for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=False)
    imported=[o for o in bpy.data.objects if o.type=="MESH"]
    assert len(imported)==1,(mid,"FBX imported mesh count",len(imported))
    after=inspect(imported[0])
    import_tris=triangles_world(imported[0])
    counts_ok=(before["triangles"]==after["triangles"])
    geometry_match=(source_tris==import_tris)
    uv_ok=before["uv0_present"] and after["uv0_present"]
    result={
      "id":mid,"source_blend_sha256":sha(src),"source_fbx_sha256":sha(fbx),
      "mesh_topology_before":before,"mesh_topology_after":before,
      "original_mesh_modified":False,"repairs_performed":[],
      "source_topology_issues":fatal,
      "blender_fbx_roundtrip":{"imported_mesh_parts":len(imported),
      "source_triangles":len(source_tris),"imported_triangles":len(import_tris),
      "triangle_world_positions_match":geometry_match,
      "count_match":counts_ok,"UV0_present":uv_ok,
      "source_material_slots":before["material_slots"],
      "import_material_slots":after["material_slots"],
      "status":"PASS" if geometry_match and counts_ok and uv_ok else "FAIL"},
      "source_gate":"PASS_UNCHANGED" if not fatal else "BLOCKED_TOPOLOGY_REVIEW",
      "Unity":"NOT_RUN",
      "production_art_note": "W02 from this PR is 12 triangles, NOT the previous detailed W02 r2 (572 triangles)" if mid=="W02" else ""
    }
    results.append(result)
    (OUT/(mid+"_mesh_topology_before.json")).write_text(json.dumps(before,indent=2)+"\n")
    (OUT/(mid+"_mesh_topology_after.json")).write_text(json.dumps(before,indent=2)+"\n")
(OUT/"PASS03_blender_fbx_roundtrip.json").write_text(json.dumps(results,indent=2)+"\n")
if any(r["source_gate"]!="PASS_UNCHANGED" or r["blender_fbx_roundtrip"]["status"]!="PASS" for r in results):
    raise RuntimeError("PASS03 Blender+FBX detected issues. See QA/PASS03_blender_fbx_roundtrip.json")
print("PASS03 Blender native source / FBX roundtrip completed on original PR22 Blender meshes; Unity NOT_RUN")
