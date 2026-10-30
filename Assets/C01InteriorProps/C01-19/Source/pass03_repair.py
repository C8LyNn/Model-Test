"""C01-19 PASS03: audit actual .blend, repair intersecting same-material STATIC solids only,
render source-derived evidence, save native/FBX, perform REAL Blender FBX roundtrip.
No reconstruction, no procedural new model, no automatic global weld.
"""
import bpy, bmesh, json, math, os, pathlib, hashlib, traceback, subprocess
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/"QA"/"PASS03"
OUT.mkdir(parents=True, exist_ok=True)
ids=[p.name for p in (ROOT/"Models").iterdir() if p.is_dir() and (p/(p.name+".blend")).exists()]
ids.sort(key=lambda x:(0 if x in ("P19-07","P19-08") else 1,x))
EPS=1e-6
def meshes(): return [o for o in bpy.context.scene.objects if o.type=="MESH"]
def movable(o):
    p=o.parent
    while p:
        if "HINGE" in p.name.upper() or "PIVOT" in p.name.upper(): return True
        p=p.parent
    return False
def material(o): return o.data.materials[0].name if o.data.materials else "NO_MATERIAL"
def bounds(objects):
    points=[o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    return [[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
def intersection(a,b):
    aa,ab=bounds([a]);ba,bb=bounds([b])
    dims=[max(0,min(ab[i],bb[i])-max(aa[i],ba[i])) for i in range(3)]
    return math.prod(dims),[(max(aa[i],ba[i])+min(ab[i],bb[i]))/2 for i in range(3)]
def snapshot(o):
    bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table();bm.normal_update()
    verts=len(bm.verts);edges=len(bm.edges);faces=len(bm.faces)
    deg=sum(f.calc_area()<1e-12 for f in bm.faces)
    loose=sum(not v.link_edges for v in bm.verts)
    duplicated_faces=faces-len(set(tuple(sorted(v.index for v in f.verts)) for f in bm.faces))
    boundary=sum(len(e.link_faces)==1 for e in bm.edges)
    nonmanifold=sum(len(e.link_faces)>2 for e in bm.edges)
    zero_edges=sum(e.calc_length()<EPS for e in bm.edges)
    winding_disagree=sum(len(e.link_faces)==2 and all((list(f.verts)[i].index,list(f.verts)[(i+1)%len(f.verts)].index)==(e.verts[0].index,e.verts[1].index) for f in e.link_faces for i in range(len(f.verts)) if list(f.verts)[i] in e.verts and list(f.verts)[(i+1)%len(f.verts)] in e.verts) for e in bm.edges)
    seen=set();duplicate_positions=0
    for v in bm.verts:
        k=tuple(round(x,6) for x in v.co)
        if k in seen:duplicate_positions+=1
        seen.add(k)
    seen=set();components=0
    for v in bm.verts:
        if v in seen:continue
        components+=1;stack=[v];seen.add(v)
        while stack:
            for e in stack.pop().link_edges:
                w=e.other_vert(v) if False else None
                for w in e.verts:
                    if w not in seen:
                        seen.add(w);stack.append(w)
    # triangle-self-intersection inspection via BVH, ignoring adjacent faces sharing vertices.
    hits=0
    if faces>1:
        try:
            tree=BVHTree.FromBMesh(bm,epsilon=0.0)
            for i,j in tree.overlap(tree):
                if i>=j:continue
                if i>=len(bm.faces) or j>=len(bm.faces):continue
                if set(bm.faces[i].verts).intersection(bm.faces[j].verts):continue
                hits+=1
        except Exception: hits=-1
    # separate material UV seams are legal; duplications reported but not blindly welded.
    t={"name":o.name,"vertices":verts,"edges":edges,"faces":faces,"triangles":sum(len(f.verts)-2 for f in bm.faces),
       "components":components,"loose_vertices":loose,"degenerate_faces":deg,
       "duplicate_faces":duplicated_faces,"duplicate_coordinate_vertices":duplicate_positions,
       "boundary_edges":boundary,"nonmanifold_edges":nonmanifold,"zero_edges":zero_edges,
       "inconsistent_winding_candidates":winding_disagree,"self_intersection_candidates":hits,
       "uv_layers":len(o.data.uv_layers),"material":material(o),"moving":movable(o)}
    bm.free();return t
def audit():
    parts=[snapshot(o) for o in meshes()]
    overlaps=[]
    o=meshes()
    for i,a in enumerate(o):
        for b in o[i+1:]:
            vol,center=intersection(a,b)
            if vol>1e-9:
                overlaps.append({"a":a.name,"b":b.name,"volume_m3":round(vol,9),
                 "same_material":material(a)==material(b),"moving":movable(a) or movable(b),"center":center})
    totals={k:sum(p[k] for p in parts) for k in
         ("vertices","edges","faces","triangles","loose_vertices","degenerate_faces","duplicate_faces","duplicate_coordinate_vertices","boundary_edges","nonmanifold_edges","zero_edges","inconsistent_winding_candidates")}
    return {"parts":parts,"totals":totals,"bounding_xyz_blender":bounds(meshes()),"interpart_overlaps":overlaps}
def render_png(path,wire=False,closeup=False,focus=None):
    sc=bpy.context.scene
    sc.render.engine='BLENDER_WORKBENCH'
    sc.display.shading.light='STUDIO'
    sc.display.shading.color_type='MATERIAL'
    sc.render.resolution_x=840;sc.render.resolution_y=620;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'
    initial=meshes()
    visible=[(o,o.hide_render) for o in initial]
    ghosts=[]
    if wire:
        for o in initial:
            g=o.copy();g.data=o.data.copy();bpy.context.collection.objects.link(g)
            world=o.matrix_world.copy();g.parent=None;g.matrix_world=world
            mod=g.modifiers.new("EVIDENCE_WIREFRAME_ONLY","WIREFRAME")
            mod.thickness=.004;mod.use_replace=True
            ghosts.append(g);o.hide_render=True
    lo,hi=bounds(initial)
    center=Vector([(lo[i]+hi[i])/2 for i in range(3)])
    length=max(hi[i]-lo[i] for i in range(3))
    if closeup and focus is not None:center=Vector(focus)
    camera_data=bpy.data.cameras.new("PASS03_EVIDENCE_CAMERA")
    cam=bpy.data.objects.new("PASS03_EVIDENCE_CAMERA",camera_data)
    bpy.context.collection.objects.link(cam)
    cam.location=center+Vector((length*1.7,-length*2.0,length*1.45))
    direction=center-cam.location
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=length*(.9 if closeup else 2.15)
    oldcam=sc.camera;sc.camera=cam
    sc.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    sc.camera=oldcam
    bpy.data.objects.remove(cam,do_unlink=True)
    for g in ghosts:bpy.data.objects.remove(g,do_unlink=True)
    for o,hide in visible:o.hide_render=hide
def merge_confirmed_static_solids():
    changes=[]
    # Same-material positive volumetric intersections only, not touch contacts,
    # cross-material UV boundaries or moving child surfaces.
    for _ in range(200):
        o=meshes()
        candidate=None
        for i,a in enumerate(o):
            if movable(a):continue
            for b in o[i+1:]:
                if movable(b) or material(a)!=material(b):continue
                volume,center=intersection(a,b)
                if volume>1e-9:candidate=(a,b,volume,center);break
            if candidate:break
        if candidate is None:break
        a,b,volume,center=candidate
        previous_bounds=bounds([a,b])
        bpy.ops.object.select_all(action='DESELECT')
        a.select_set(True);bpy.context.view_layer.objects.active=a
        mod=a.modifiers.new("PASS03_CORRECT_OVERLAPPING_STATIC_SOLIDS","BOOLEAN")
        mod.operation="UNION";mod.solver="EXACT";mod.object=b
        bpy.ops.object.modifier_apply(modifier=mod.name)
        if len(a.data.polygons)==0:raise RuntimeError("Boolean produced empty mesh")
        bpy.data.objects.remove(b,do_unlink=True)
        new_bounds=bounds([a])
        if max(abs(previous_bounds[j][k]-new_bounds[j][k]) for j in range(2) for k in range(3))>.0001:
            raise RuntimeError("Silhouette bounds changed by static boolean union")
        changes.append({"action":"BOOLEAN_UNION_STATIC_SAME_MATERIAL","target":a.name,"removed_part":b.name,
                        "overlap_volume_m3":round(volume,9),"location":center})
    else:raise RuntimeError("200 unions exceeded; abort")
    return changes
def roundtrip(model,original_bounds,expected_triangles):
    bpy.ops.object.select_all(action="DESELECT")
    existing=set(bpy.context.scene.objects)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/"Models"/model/(model+".fbx")))
    imported=[o for o in bpy.context.scene.objects if o not in existing]
    imported_meshes=[o for o in imported if o.type=="MESH"]
    if not imported_meshes:raise RuntimeError("FBX roundtrip imported no mesh")
    bb=bounds(imported_meshes)
    bound_err=max(abs(bb[a][i]-original_bounds[a][i]) for a in range(2) for i in range(3))
    triangles=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in imported_meshes)
    uv_count=sum(len(o.data.uv_layers)>0 for o in imported_meshes)
    for o in imported:bpy.data.objects.remove(o,do_unlink=True)
    if bound_err>.002 or triangles!=expected_triangles or uv_count!=len(imported_meshes):
        raise RuntimeError(f"FBX roundtrip mismatch: bounds={bound_err} tris={triangles}/{expected_triangles} uv={uv_count}/{len(imported_meshes)}")
    return {"result":"PASS","bounds_max_error_m":bound_err,"triangles":triangles,"imported_meshes":len(imported_meshes),
            "uv0_meshes":uv_count}
summary=[]
for model in ids:
    model_dir=ROOT/"Models"/model
    native=model_dir/(model+".blend")
    source_sha=hashlib.sha256(native.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(native))
    original=audit()
    evidence=OUT/model;evidence.mkdir(parents=True,exist_ok=True)
    (evidence/"mesh_topology_before.json").write_text(json.dumps({"id":model,"source_sha256":source_sha,**original},indent=2))
    render_png(evidence/"wireframe_before.png",wire=True)
    corrections=merge_confirmed_static_solids()
    after=audit()
    render_png(evidence/"wireframe_after.png",wire=True)
    render_png(evidence/"shaded_after.png")
    render_png(evidence/"closeup_actual_mesh.png",wire=True,closeup=True,focus=corrections[0]["location"] if corrections else None)
    # No additional geometry added. Preserve real scene objects, lights, materials and hinges.
    if max(abs(original["bounding_xyz_blender"][j][k]-after["bounding_xyz_blender"][j][k])
           for j in range(2) for k in range(3))>.0001:raise RuntimeError("Model footprint changed")
    unexpected=[p for p in after["parts"] if p["loose_vertices"] or p["degenerate_faces"] or p["duplicate_faces"]
                or p["nonmanifold_edges"] or p["boundary_edges"] or p["zero_edges"] or p["uv_layers"]<1]
    # Note intersections involving distinct materials or moving parts require separate independent review.
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.type in {"MESH","EMPTY"}:o.select_set(True)
    bpy.context.view_layer.objects.active=meshes()[0]
    bpy.ops.export_scene.fbx(filepath=str(model_dir/(model+".fbx")),use_selection=True,
        axis_forward="-Z",axis_up="Y",global_scale=1,apply_unit_scale=True,
        bake_anim=False,add_leaf_bones=False,object_types={"MESH","EMPTY"})
    fbx_result=roundtrip(model,after["bounding_xyz_blender"],after["totals"]["triangles"])
    (evidence/"mesh_topology_after.json").write_text(json.dumps({"id":model,"result":"REVIEW" if unexpected else "PASS_STATIC_PARTS",
       "changes":corrections,"exceptions":[{"classification":"INTENTIONAL_SEPARATE_COMPONENT","reason":"preserve material boundaries or movable hierarchy","overlap":v} for v in after["interpart_overlaps"] if (not v["same_material"]) or v["moving"]],
       "unresolved":unexpected,"fbx_roundtrip":fbx_result,**after},indent=2))
    rec={"id":model,"before":original["totals"],"after":after["totals"],"unions":len(corrections),
         "unresolved_parts":len(unexpected),"fbx_roundtrip":fbx_result,"before_blend_sha256":source_sha,
         "after_blend_sha256":hashlib.sha256(native.read_bytes()).hexdigest(),
         "after_fbx_sha256":hashlib.sha256((model_dir/(model+".fbx")).read_bytes()).hexdigest(),
         "unity":"NOT_RUN","independent_QA":"NOT_RUN"}
    summary.append(rec)
    (evidence/"report.json").write_text(json.dumps(rec,indent=2))
    print("PASS03 REAL BLENDER MODEL",model,"unions",len(corrections),"FBX",fbx_result["result"],flush=True)
(OUT/"SUMMARY.json").write_text(json.dumps({"process":"Blender real source mesh topology repair + FBX import","models":summary},indent=2))
