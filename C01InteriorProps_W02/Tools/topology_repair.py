#!/usr/bin/env python3
"""PASS03: inspect and conservatively weld REAL existing .blend meshes.
No procedural recreation, visual redesign, or joins between objects.
Run: blender -b -t 2 --factory-startup --python-exit-code 1 --python topology_repair.py -- REPO_ROOT
"""
import bpy,bmesh,json,sys,math,hashlib,collections,copy
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index("--")+1]).resolve() if "--" in sys.argv else Path(".").resolve()
FAMILY="W02" if "W02" in str(Path(__file__).resolve()) else "W01"
SRC=R/("C01InteriorProps_W02" if FAMILY=="W02" else "C01InteriorProps_Source")
MODELS=R/("Assets/C01InteriorProps/W02/Models" if FAMILY=="W02" else "Assets/C01InteriorProps/Models")
IDS=["P17-04","P17-05","P17-06","P17-07"] if FAMILY=="W02" else ["P17-01","P17-02","P17-03"]
EVIDENCE=SRC/"QA"/"PASS03"
PREV=EVIDENCE/"Previews"
PREV.mkdir(parents=True,exist_ok=True)
TOL=1e-6
def vec(v): return tuple(round(float(x),7) for x in v)
def components(bm):
    remaining=set(bm.verts);count=0
    while remaining:
        count+=1;stack=[remaining.pop()]
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                u=e.other_vert(v)
                if u in remaining:remaining.remove(u);stack.append(u)
    return count
def audit(ob):
    bm=bmesh.new();bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
    groups=collections.Counter(vec(v.co) for v in bm.verts)
    dup_verts=sum(n-1 for n in groups.values() if n>1)
    loose_vertices=sum(1 for v in bm.verts if not v.link_edges)
    loose_edges=sum(1 for e in bm.edges if not e.link_faces)
    zero_edges=sum(1 for e in bm.edges if e.calc_length()<1e-9)
    degenerate=sum(1 for f in bm.faces if f.calc_area()<1e-11)
    face_set=collections.Counter(tuple(sorted(vec(v.co) for v in f.verts)) for f in bm.faces)
    duplicate_faces=sum(n-1 for n in face_set.values() if n>1)
    bnd=sum(e.is_boundary for e in bm.edges)
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    tris=sum(max(1,len(f.verts)-2) for f in bm.faces)
    n_negative=0;vol=None
    if bnd==0 and len(bm.faces):
        try: vol=float(bm.calc_volume(signed=True))
        except Exception:vol=None
        if vol is not None and vol< -1e-10:n_negative=1
    has_uv=bool(ob.data.uv_layers)
    mat_names=[m.name for m in ob.data.materials if m]
    co=[tuple(v.co) for v in bm.verts]
    b0=[min((v[i] for v in co),default=0) for i in range(3)]
    b1=[max((v[i] for v in co),default=0) for i in range(3)]
    out=dict(name=ob.name,vertices=len(bm.verts),edges=len(bm.edges),faces=len(bm.faces),triangles=tris,
             connected_components=components(bm),coincident_vertices=dup_verts,
             loose_vertices=loose_vertices,loose_edges=loose_edges,zero_length_edges=zero_edges,
             degenerate_faces=degenerate,duplicate_faces=duplicate_faces,boundary_edges=bnd,
             non_manifold_edges=nonmanifold,inverted_closed_volume=int(n_negative),signed_volume=vol,
             uv_layers=len(ob.data.uv_layers),materials=mat_names,bounds_local=[b0,b1],
             self_intersection_candidates="NOT_RUN; requires dedicated BVH narrowphase across separate objects",
             t_junction_candidates="NOT_RUN; no confirmed repair; manual review if source anomaly",
             coplanar_overlap_candidates="NOT_RUN; layered separate components are intentional unless independently proven faulty")
    bm.free();return out
def collate(parts):
    keys=["vertices","edges","faces","triangles","connected_components","coincident_vertices",
          "loose_vertices","loose_edges","zero_length_edges","degenerate_faces","duplicate_faces",
          "boundary_edges","non_manifold_edges","inverted_closed_volume"]
    return {key:sum(p[key] for p in parts) for key in keys}
def bound_world(mesh):
    pts=[o.matrix_world@Vector(p) for o in mesh for p in o.bound_box]
    return ([min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)])
def visual(scene,objs,model_id,tag,kind,focus=None):
    # True Blender mesh render: original source geometry, no parametric reconstruction.
    bb0,bb1=bound_world(objs)
    if focus is None:
        center=Vector([(bb0[i]+bb1[i])/2 for i in range(3)])
        extent=max(bb1[i]-bb0[i] for i in range(3))
    else:
        ob=focus
        co=[ob.matrix_world@Vector(x) for x in ob.bound_box]
        center=Vector([(min(v[i] for v in co)+max(v[i] for v in co))/2 for i in range(3)])
        extent=max(max(v[i] for v in co)-min(v[i] for v in co) for i in range(3))
    cam=bpy.data.objects.new("C01_PASS03_CAPTURE_CAMERA",bpy.data.cameras.new("C01_PASS03_CAPTURE_CAMERA"))
    scene.collection.objects.link(cam)
    cam.location=center+Vector((2.7,-3.4,2.6))*(max(extent,.4)/3)
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type="ORTHO";cam.data.ortho_scale=max(extent*(1.58 if focus is None else 1.8),.21)
    scene.camera=cam
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.display.shading.show_cavity=True
    # Blender 4 Workbench render does not expose show_wireframes on View3DShading.
    # Trace actual existing mesh edges into non-persistent render-only curves, never reconstructing meshes.
    overlay=None
    if kind in ("wire","closeup"):
        c=bpy.data.curves.new("PASS03_SOURCE_EDGE_OVERLAY","CURVE")
        c.dimensions="3D";c.bevel_depth=max(extent,0.4)*0.0009;c.bevel_resolution=0
        for obj in objs:
            for e in obj.data.edges:
                s=c.splines.new("POLY");s.points.add(1)
                for i,vid in enumerate(e.vertices):
                    point=obj.matrix_world@obj.data.vertices[vid].co
                    s.points[i].co=(point.x,point.y,point.z,1)
        overlay=bpy.data.objects.new("PASS03_SOURCE_EDGE_OVERLAY",c)
        scene.collection.objects.link(overlay)
    scene.display.shading.show_shadows=(kind=="shaded")
    scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(PREV/(model_id+"_"+tag+".png"))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True)
    if overlay is not None:
        curve=overlay.data
        bpy.data.objects.remove(overlay,do_unlink=True)
        bpy.data.curves.remove(curve)
def repair(ob):
    bm=bmesh.new();bm.from_mesh(ob.data)
    existing_faces=len(bm.faces)
    first_uv_layers=len(ob.data.uv_layers)
    # Weld ONLY coincident vertices within one Mesh Object. UV coordinates stay in per-loop UV layers.
    # Never join different Blender Objects, never touch child/hinge hierarchy.
    pre_vertices=len(bm.verts)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=TOL)
    post_vertices=len(bm.verts)
    bm.normal_update()
    if len(bm.faces)!=existing_faces:raise RuntimeError("Face count changed unexpectedly for "+ob.name)
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    if len(ob.data.uv_layers)!=first_uv_layers:raise RuntimeError("UV0 lost in "+ob.name)
    return pre_vertices-post_vertices
for model_id in IDS:
    blend=SRC/"Blender"/(model_id+".blend")
    if not blend.exists(): raise RuntimeError("SOURCE MISSING: "+str(blend))
    src_sha=hashlib.sha256(blend.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    scene=bpy.context.scene
    objects=[o for o in scene.objects if o.type=="MESH"]
    if not objects:raise RuntimeError(model_id+" has no real source meshes")
    meshes_pre={o.name:audit(o) for o in objects}
    before=[meshes_pre[o.name] for o in objects]
    totals_before=collate(before)
    world0=bound_world(objects)
    pivots_before={o.name:tuple(o.matrix_world) for o in scene.objects if o.type=="EMPTY"}
    mats_before={o.name:[m.name if m else None for m in o.data.materials] for o in objects}
    visual(scene,objects,model_id,"BEFORE_WIREFRAME","wire")
    modified=[]
    for o in objects:
        if meshes_pre[o.name]["coincident_vertices"]>0:
            weld_count=repair(o)
            modified.append({"mesh":o.name,"welded":weld_count})
    bpy.context.view_layer.update()
    after=[audit(o) for o in objects]
    totals_after=collate(after)
    world1=bound_world(objects)
    if any(abs(world0[j][k]-world1[j][k])>5e-6 for j in range(2) for k in range(3)):
        raise RuntimeError(model_id+" visible bounds changed after topology repair")
    if totals_before["faces"]!=totals_after["faces"] or totals_before["triangles"]!=totals_after["triangles"]:
        raise RuntimeError(model_id+" polygons/triangles unexpectedly changed")
    if totals_after["degenerate_faces"] or totals_after["duplicate_faces"] or totals_after["zero_length_edges"]:
        raise RuntimeError(model_id+" remaining local topology defect")
    if totals_after["coincident_vertices"] or totals_after["boundary_edges"] or totals_after["non_manifold_edges"]:
        # Any intentional open surfaces must be explicitly documented; these props use closed primitive shells.
        raise RuntimeError(model_id+" mesh is still non-manifold or has split coincident vertices")
    for o in objects:
        if mats_before[o.name]!=[m.name if m else None for m in o.data.materials]:
            raise RuntimeError("Materials changed "+model_id+"/"+o.name)
    for o in scene.objects:
        if o.type=="EMPTY" and o.name in pivots_before and tuple(o.matrix_world)!=pivots_before[o.name]:
            raise RuntimeError("Pivot changed "+o.name)
    focus=next((o for o in objects if o.name in [p["mesh"] for p in modified]),objects[0])
    visual(scene,objects,model_id,"AFTER_WIREFRAME","wire")
    visual(scene,objects,model_id,"AFTER_SHADED","shaded")
    visual(scene,objects,model_id,"AFTER_CLOSEUP","closeup",focus=focus)
    report=dict(model_id=model_id,source_blend_before_sha256=src_sha,
                source_origin="real preexisting .blend from branch before PASS03, not reconstructed",
                tolerance_m=TOL,before=totals_before,after=totals_after,
                parts_before=before,parts_after=after,meshes_modified=modified,
                preserved_dimensions=True,preserved_polygons=True,preserved_materials=True,
                preserved_pivots=True,source_mesh_topology="PASS" if not totals_after["non_manifold_edges"] else "FAIL",
                blender_native_repair="PASS",fbx_round_trip="PENDING next CI step",unity="NOT RUN",independent_c01_02="PENDING")
    (EVIDENCE/(model_id+"_mesh_topology_before.json")).write_text(json.dumps(dict(model_id=model_id,summary=totals_before,parts=before),indent=2)+"\n")
    (EVIDENCE/(model_id+"_mesh_topology_after.json")).write_text(json.dumps(dict(model_id=model_id,summary=totals_after,parts=after,changes=modified),indent=2)+"\n")
    (EVIDENCE/(model_id+"_REPAIR_EVIDENCE.json")).write_text(json.dumps(report,indent=2)+"\n")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
        p=ob.parent
        while p:
            p.select_set(True);p=p.parent
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.fbx(filepath=str(MODELS/(model_id+".fbx")),use_selection=True,
        object_types={"MESH","EMPTY"},axis_forward="-Z",axis_up="Y",
        apply_unit_scale=True,global_scale=1.0,bake_anim=False)
    print("PASS03",model_id,"BEFORE",totals_before,"AFTER",totals_after,
          "fixed",len(modified),"parts",flush=True)
print("PASS03 Blender native topology repair completed",FAMILY,flush=True)
