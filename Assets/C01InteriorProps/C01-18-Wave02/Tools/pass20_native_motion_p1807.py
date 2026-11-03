"""C01-18 W20: NON-MUTATING genuine Blender4 source + imported binary FBX lid sweep.
Never exports/edits actual source .blend or binary .fbx. Any contact is REVIEW, not silent weld.
Run: blender -b --factory-startup --python-exit-code 1 --python this.py -- ROOT
"""
import bpy, sys, pathlib, hashlib, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=pathlib.Path(sys.argv[sys.argv.index("--")+1]).resolve()
PIN={"blend":"ca81b1b5b03354f6988657324f2f30b28ff1b785529388fb692469ffb2d3f9c3",
     "fbx":"38d93a5c2dc9f1511e568925998d7ea42c26dffc1f14e99cdaae80f1501273da"}
paths={"blend":ROOT/"Sources"/"P18-07.blend","fbx":ROOT/"Models"/"P18-07.fbx"}
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
for k,p in paths.items():
    assert p.exists() and p.stat().st_size>40000,(k,p)
    assert digest(p)==PIN[k],("STALE native",k,digest(p))
assert paths["blend"].read_bytes()[:8]==b"BLENDER-"
assert paths["fbx"].read_bytes()[:20]==b"Kaydara FBX Binary  "
assert bpy.app.version[:2]==(4,0) or bpy.app.version >= (4,0,0)
def mesh_bvh(obj):
    obj.data.calc_loop_triangles()
    verts=[tuple(obj.matrix_world@v.co) for v in obj.data.vertices]
    tris=[tuple(t.vertices) for t in obj.data.loop_triangles]
    return BVHTree.FromPolygons(verts,tris,all_triangles=True,epsilon=0)
def part_bounds(o):
    pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
def gather(tag):
    meshes=sorted([x for x in bpy.context.scene.objects if x.type=="MESH"],key=lambda x:x.name)
    assert len(meshes)==10,(tag,len(meshes),[o.name for o in meshes])
    names={o.name:o for o in meshes}
    assert sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)==120
    h=bpy.data.objects.get("Toolbox_LidHinge")
    assert h and h.type=="EMPTY",("missing actual moving hinge",tag)
    lid=names["Bin_Lid"];label=names["Lid_Label"]
    assert lid.parent==h and label.parent==h,("lid/label not descendants",tag,lid.parent,label.parent)
    p=h.matrix_world.translation
    assert abs(p.x)<0.001 and abs(p.y-.17)<.001 and abs(p.z-.23)<.001,("hinge pivot changed",tag,tuple(p))
    assert all(o.data.uv_layers for o in meshes)
    stationary=[o for o in meshes if o.name not in ("Bin_Lid","Lid_Label")]
    original=h.rotation_euler.copy()
    records=[];pairs={}
    for deg in range(0,111,5):
        # Opening side: front edge moves upwards about BACK X-axis, so Blender rotation is -X.
        h.rotation_euler=original.copy()
        h.rotation_euler.x=original.x-math.radians(deg)
        bpy.context.view_layer.update()
        blockers=[]
        for mover in (lid,label):
            ma=mesh_bvh(mover)
            for st in stationary:
                hits=ma.overlap(mesh_bvh(st))
                if hits:
                    blockers.append({"moving":mover.name,"stationary":st.name,"triangle_pairs":len(hits)})
                    key=mover.name+" / "+st.name
                    pairs.setdefault(key,[]).append(deg)
        records.append({"opening_angle_degrees":deg,"detected_world_triangle_BVH_pairs":blockers})
    h.rotation_euler=original
    bpy.context.view_layer.update()
    lid_minmax=part_bounds(lid)
    lock_minmax=part_bounds(names["Front_Lock"])
    # Blender -Y is Unity +Z.
    lid_z=-lid_minmax[1][0]
    lock_z=-lock_minmax[1][0]
    gap_mm=1000*(lock_z-lid_z)
    assert abs(gap_mm-1)<.05,(tag,"front face projection mismatch",gap_mm)
    return {"test":tag,"mesh_parts":len(meshes),"triangles":120,
      "hinge_blender_world_xyz":[float(x) for x in p],
      "front_face_lid_unity_z_m":lid_z,"front_face_lock_unity_z_m":lock_z,
      "front_plane_outward_offset_mm":gap_mm,
      "opening_axis":"Blender -X (Unity rear X-axis), 0→110 degrees",
      "angles_tested":len(records),"moving_parts":[lid.name,label.name],
      "fixed_parts":[o.name for o in stationary],
      "blocking_contact_pairs":{k:sorted(set(v)) for k,v in pairs.items()},
      "pose_samples":records,
      "motion_disposition":"PRODUCER_BVH_CONTACTS_REVIEW" if pairs else "PRODUCER_BVH_CLEAR_FOR_SAMPLED_POSES",
      "caveat":"Surface BVH triangle overlap may report touching surfaces; do not infer 3D penetration without a subsequent narrowphase and physical unlocked-latch state. Opening side -X only; Unity PhysX NOT RUN."}
bpy.ops.wm.open_mainfile(filepath=str(paths["blend"]))
source=gather("real_authoring_blend")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(paths["fbx"]))
fbx=gather("actual_blender_reimported_binary_fbx")
data={"asset":"P18-07","wave":"W20","owner":"C01-18","source_blend_sha256":PIN["blend"],"binary_fbx_sha256":PIN["fbx"],
"no_geometry_or_export_changes":True,"source":source,"binary_fbx_reimport":fbx,
"source_fbx_pair_agreement":source["blocking_contact_pairs"]==fbx["blocking_contact_pairs"],
"max_front_offset_difference_mm":abs(source["front_plane_outward_offset_mm"]-fbx["front_plane_outward_offset_mm"]),
"C01_02_independent_motion":"NOT_RUN","Unity6_URP":"NOT_RUN","final_release":"HOLD"}
out=ROOT/"QA"/"Pass20"/"P18-07_NATIVE_HINGE_BVH_SWEEP.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("C01_W20_P18_07_ACTUAL_BLENDER_FBX_HINGE_SWEEP",json.dumps(
 {"blend":PIN["blend"],"fbx":PIN["fbx"],"source_contacts":source["blocking_contact_pairs"],
  "fbx_contacts":fbx["blocking_contact_pairs"],"agreement":data["source_fbx_pair_agreement"],
  "offset_mm":fbx["front_plane_outward_offset_mm"]}),flush=True)
assert data["source_fbx_pair_agreement"], "Actual native BLEND/FBX hinge behavior diverged"
assert data["max_front_offset_difference_mm"]<0.05,"Source/FBX front lock offset drift"
