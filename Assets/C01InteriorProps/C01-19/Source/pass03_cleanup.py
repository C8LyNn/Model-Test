"""Localized follow-up for precisely observed post-Boolean zero edges/degenerate faces.
Loads actual previously repaired .blend, never reconstructs geometry from boxes."""
import bpy,bmesh, pathlib, json, hashlib
SCRIPT=pathlib.Path(__file__).resolve()
ns={"__file__":str(SCRIPT),"__name__":"c01_19_real_mesh_helpers"}
full=(SCRIPT.parent/"pass03_repair.py").read_text()
assert "\nsummary=[]" in full
exec(compile(full.split("\nsummary=[]")[0],str(SCRIPT.parent/"pass03_repair.py"),"exec"),ns)
R=SCRIPT.parent.parent;qa=R/"QA"/"PASS03"
records=json.loads((qa/"SUMMARY.json").read_text())
cleanup=[]
for mid in ("P19-01","P19-02"):
    model=R/"Models"/mid/(mid+".blend")
    before_sha=hashlib.sha256(model.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(model))
    pre=ns["audit"]()
    targets=[o for o in ns["meshes"]() if "zero_edges" in next(p for p in pre["parts"] if p["name"]==o.name) and
             (next(p for p in pre["parts"] if p["name"]==o.name)["zero_edges"] or next(p for p in pre["parts"] if p["name"]==o.name)["degenerate_faces"])]
    assert len(targets)==1,(mid,len(targets))
    o=targets[0]
    bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table()
    zero_edges=[e for e in bm.edges if e.calc_length()<1e-6]
    # Reviewed exact-zero edge endpoints only, not arbitrary UV seams/hard edges.
    suspect=set(v for e in zero_edges for v in e.verts)
    if suspect:bmesh.ops.remove_doubles(bm,verts=list(suspect),dist=1e-7)
    bm.edges.ensure_lookup_table()
    bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges))
    bm.normal_update()
    bm.to_mesh(o.data);bm.free();o.data.update()
    post=ns["audit"]()
    defects={k:post["totals"][k] for k in ("loose_vertices","degenerate_faces","duplicate_faces","boundary_edges","nonmanifold_edges","zero_edges")}
    if any(defects.values()):raise RuntimeError(f"{mid} localized cleanup still defective: {defects}")
    if max(abs(pre["bounding_xyz_blender"][a][i]-post["bounding_xyz_blender"][a][i]) for a in range(2) for i in range(3))>1e-5:
        raise RuntimeError(mid+" repair changed silhouette bounds")
    ev=qa/mid
    ns["render_png"](ev/"wireframe_after.png",wire=True)
    ns["render_png"](ev/"shaded_after.png",wire=False)
    ns["render_png"](ev/"closeup_actual_mesh.png",wire=True,closeup=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(model))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        if obj.type in ("MESH","EMPTY"):obj.select_set(True)
    bpy.context.view_layer.objects.active=ns["meshes"]()[0]
    bpy.ops.export_scene.fbx(filepath=str(R/"Models"/mid/(mid+".fbx")),use_selection=True,
        axis_forward="-Z",axis_up="Y",global_scale=1,apply_unit_scale=True,
        bake_anim=False,add_leaf_bones=False,object_types={"MESH","EMPTY"})
    rt=ns["roundtrip"](mid,post["bounding_xyz_blender"],post["totals"]["triangles"])
    afterfile=ev/"mesh_topology_after.json"
    after=json.loads(afterfile.read_text())
    after.update({"result":"PASS_STATIC_PARTS_AFTER_LOCAL_CLEANUP",
                  "cleanup":{"type":"ZERO_EDGE_ENDPOINT_WELD_AND_DEGENERATE_DISSOLVE",
                             "mesh":o.name,"zero_edges_before":pre["totals"]["zero_edges"],
                             "zero_edges_after":post["totals"]["zero_edges"],
                             "degenerate_faces_before":pre["totals"]["degenerate_faces"],
                             "degenerate_faces_after":post["totals"]["degenerate_faces"]},
                  "parts":post["parts"],"totals":post["totals"],"fbx_roundtrip":rt})
    afterfile.write_text(json.dumps(after,indent=2))
    item=next(x for x in records["models"] if x["id"]==mid)
    item["after"]=post["totals"]
    item["unresolved_parts"]=0
    item["fbx_roundtrip"]=rt
    item["followup_cleanup"]="PASS"
    item["after_blend_sha256"]=hashlib.sha256(model.read_bytes()).hexdigest()
    item["after_fbx_sha256"]=hashlib.sha256((R/"Models"/mid/(mid+".fbx")).read_bytes()).hexdigest()
    (ev/"report.json").write_text(json.dumps(item,indent=2))
    cleanup.append({"id":mid,"mesh":o.name,"before":pre["totals"],"after":post["totals"],
                    "before_blend_sha256":before_sha,"after_blend_sha256":item["after_blend_sha256"],
                    "fbx_roundtrip":rt})
    print("PASS03 CLEANUP",mid,defects,flush=True)
(qa/"SUMMARY.json").write_text(json.dumps(records,indent=2))
(qa/"FOLLOWUP_CLEANUP.json").write_text(json.dumps({"results":cleanup},indent=2))
