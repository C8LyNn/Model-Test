"""C01-19 / PASS04. Open ORIGINAL stored .blend. Blender 4.0.2 native BMesh triangulation.
Do not reconstruct models. No joins, welding, redesign or moving pivot changes.
"""
import bpy,bmesh,json,hashlib,math,pathlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parent.parent
DST=ROOT/"QA"/"PASS04";DST.mkdir(parents=True,exist_ok=True)
# Import only source-derived geometry auditor and native workbench renderer, not its execution.
source=ROOT/"Source"/"pass03_repair.py"
helpers={"__file__":str(source),"__name__":"pass04_imported_helpers"}
txt=source.read_text()
exec(compile(txt.split("\nsummary=[]")[0],str(source),"exec"),helpers)
audit=helpers["audit"];render=helpers["render_png"];bounds=helpers["bounds"]
ID_ORDER=["P19-01","P19-02","P19-03","P19-04"]
IDS=[x for x in ID_ORDER if (ROOT/"Models"/x/(x+".blend")).is_file()]
assert len(IDS)==4,("expected 4 actual native sources",IDS)
EPS=1e-7
TARGET_IDS={"P19-01","P19-02"}
def signed_vol(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    volume=bm.calc_volume(signed=True);bm.free()
    return volume
def jcandidate(objects,tol=1e-5):
    # Vertex strictly inside an existing edge: geometric candidate only, not automatic weld.
    # Same vs different mesh is tracked; child objects and material boundaries intentionally separate.
    allverts=[(o.name,o.matrix_world @ v.co) for o in objects for v in o.data.vertices]
    edges=[(o.name,o.matrix_world @ o.data.vertices[e.vertices[0]].co,
              o.matrix_world @ o.data.vertices[e.vertices[1]].co) for o in objects for e in o.data.edges]
    result=[]
    for owner,pt in allverts:
        for edgeowner,a,b in edges:
            ab=b-a;dd=ab.length_squared
            if dd<1e-14:continue
            t=(pt-a).dot(ab)/dd
            if t<tol or t>1-tol:continue
            err=(pt-(a+t*ab)).length
            if err<tol:
                result.append({"vertex_mesh":owner,"edge_mesh":edgeowner,"same_mesh":owner==edgeowner,
                 "coordinate":[round(z,7) for z in pt],"fraction":round(t,5),"distance":err})
    return result
def metrics():
    geometry=[o for o in bpy.context.scene.objects if o.type=='MESH']
    st=audit()
    ngons=sum(1 for o in geometry for p in o.data.polygons if len(p.vertices)>4)
    triangles_only=all(len(p.vertices)==3 for o in geometry for p in o.data.polygons)
    tri_degenerate=sum(1 for o in geometry for p in o.data.polygons if len(p.vertices)==3 and p.area<1e-12)
    winding_bad=sum(1 for o in geometry for p in o.data.polygons if p.normal.length<.999)
    uv=sum(bool(o.data.uv_layers) for o in geometry)
    st.update({"ngons":ngons,"triangle_only":triangles_only,"degenerate_triangles":tri_degenerate,
       "normal_length_bad":winding_bad,"mesh_count":len(geometry),"uv0_meshes":uv,
       "per_part_signed_volumes":{o.name:signed_vol(o) for o in geometry},
       "hierarchy":sorted((o.name, o.parent.name if o.parent else None,tuple(round(float(y),7) for y in o.matrix_local.translation))
          for o in bpy.context.scene.objects if o.type in ('MESH','EMPTY')),
       "tjunction_candidates":jcandidate(geometry)})
    return st
def max_bbox_diff(a,b):
    return max(abs(a["bounding_xyz_blender"][i][j]-b["bounding_xyz_blender"][i][j]) for i in (0,1) for j in (0,1,2))
def triangulate(o):
    bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table()
    targets=[f for f in bm.faces if len(f.verts)>3]
    result={"name":o.name,"source_polygons":len(bm.faces),"ngons_before":sum(len(f.verts)>4 for f in bm.faces),
            "triangulated_faces":len(targets)}
    if targets:
        bmesh.ops.triangulate(bm,faces=targets,quad_method='BEAUTY',ngon_method='EAR_CLIP')
        bm.normal_update();bm.to_mesh(o.data);o.data.update()
    bm.free()
    result["triangles_after"]=len(o.data.polygons)
    return result
def fbx_roundtrip(model,after):
    bfile=ROOT/"Models"/model/(model+".fbx")
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.context.scene.objects:
        if o.type in ("MESH","EMPTY"):o.select_set(True)
    bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=="MESH")
    bpy.ops.export_scene.fbx(filepath=str(bfile),use_selection=True,axis_forward="-Z",axis_up="Y",
        apply_unit_scale=True,global_scale=1,bake_anim=False,add_leaf_bones=False,
        object_types={"MESH","EMPTY"})
    binary=bfile.read_bytes()
    assert binary.startswith(b"Kaydara FBX Binary  \x00\x1a\x00"),"NOT a real binary FBX"
    original=set(bpy.context.scene.objects)
    bpy.ops.import_scene.fbx(filepath=str(bfile))
    imported=[o for o in bpy.context.scene.objects if o not in original]
    imesh=[o for o in imported if o.type=="MESH"]
    assert imesh,"FBX importer returned no meshes"
    tri=sum(len(p.vertices)-2 for o in imesh for p in o.data.polygons)
    polys_ngons=sum(len(p.vertices)>3 for o in imesh for p in o.data.polygons)
    uv=sum(bool(o.data.uv_layers) for o in imesh)
    ab=bounds(imesh)
    err=max(abs(ab[i][j]-after["bounding_xyz_blender"][i][j]) for i in (0,1) for j in (0,1,2))
    result={"status":"PASS" if tri==after["totals"]["triangles"] and (polys_ngons==0 if model in TARGET_IDS else True)
            and uv==len(imesh) and err<1e-4 else "FAIL",
            "triangles":tri,"imported_meshes":len(imesh),"uv0_meshes":uv,"non_triangle_polygons":polys_ngons,
            "bbox_max_error_m":err,"binary_fbx_sha256":hashlib.sha256(binary).hexdigest(),
            "binary_fbx_bytes":len(binary)}
    for o in imported:bpy.data.objects.remove(o,do_unlink=True)
    assert result["status"]=="PASS",result
    return result
summary=[]
for id in IDS:
    native=ROOT/"Models"/id/(id+".blend")
    before_sha=hashlib.sha256(native.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(native))
    before=metrics()
    evidence=DST/id;evidence.mkdir(parents=True,exist_ok=True)
    render(evidence/"wireframe_before.png",wire=True)
    repair=[triangulate(o) if id in TARGET_IDS else {"name":o.name,"action":"NO_TRIANGULATION_REQUIRED"} for o in bpy.context.scene.objects if o.type=="MESH"]
    after=metrics()
    assert (after["triangle_only"] and after["ngons"]==0) if id in TARGET_IDS else after["totals"]["triangles"]==before["totals"]["triangles"]
    assert before["mesh_count"]==after["mesh_count"] and before["hierarchy"]==after["hierarchy"]
    assert before["totals"]["triangles"]==after["totals"]["triangles"],"Triangle count changed"
    assert max_bbox_diff(before,after)<1e-6,"Silhouette bbox changed"
    assert after["uv0_meshes"]==after["mesh_count"]
    assert after["degenerate_triangles"]==0 and after["normal_length_bad"]==0
    for key in ("boundary_edges","nonmanifold_edges","zero_edges","duplicate_faces","loose_vertices"):
        assert after["totals"][key]==0,(id,key,after["totals"][key])
    for key in before["per_part_signed_volumes"]:
        a=before["per_part_signed_volumes"][key];b=after["per_part_signed_volumes"][key]
        assert abs(a-b)<=max(1e-6,abs(a)*1e-4),(id,key,"volume change",a,b)
    render(evidence/"wireframe_after.png",wire=True)
    render(evidence/"shaded_after.png")
    render(evidence/"closeup_actual_mesh.png",wire=True,closeup=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    fbx=fbx_roundtrip(id,after)
    after_sha=hashlib.sha256(native.read_bytes()).hexdigest()
    rec={"id":id,"source_before_sha256":before_sha,"source_after_sha256":after_sha,
         "fix":"EXPLICIT_BMESH_EAR_CLIP_TRIANGULATION_NO_GEOMETRIC_REDESIGN",
         "parts":repair,"before":before,"after":after,"fbx_roundtrip":fbx,
         "tjunction_note":"geometric candidates only, moving separate parts are allowed; no forced welding",
         "unity":"NOT_RUN","independent_C01_02":"PENDING"}
    (evidence/"mesh_topology_before.json").write_text(json.dumps(before,indent=2))
    (evidence/"mesh_topology_after.json").write_text(json.dumps(after,indent=2))
    (evidence/"repair_and_roundtrip.json").write_text(json.dumps(rec,indent=2))
    summary.append(rec)
    print("PASS04",id,"n-gons before",before["ngons"],"triangles",after["totals"]["triangles"],
          "T junction candidates before/after",len(before["tjunction_candidates"]),len(after["tjunction_candidates"]),
          "FBX roundtrip",fbx["status"],flush=True)
(DST/"SUMMARY.json").write_text(json.dumps({"scope":"REAL_NATIVE_BLEND_FBX_PASS04","models":summary,
     "unity":"NOT_RUN","independent_QA":"PENDING"},indent=2))
