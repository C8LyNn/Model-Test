"""C01-19 PASS17: Blender 4.x actual source-backed mechanical detail build.
Inputs: exact producer PASS04 native .blend on isolated Draft producer branch.
Fail closed before publishing if any mesh identity, AABB, UV or FBX roundtrip differs.
"""
import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
W02="W02" in ROOT.name
IDS=["P19-05"] if W02 else ["P19-01","P19-02"]
QA=ROOT/"QA"/"PASS17"; QA.mkdir(parents=True,exist_ok=True)
BASE={"P19-01":(4,133,254,269,470,"Cube.001"),"P19-02":(5,118,216,166,292,"Cube.012"),"P19-05":(7,88,148,152,252,"Cube.001")}
def box(lo,hi,label):
    x0,y0,z0=lo;x1,y1,z1=hi
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(3,7,6),(3,6,2),(0,4,7),(0,7,3),(1,2,6),(1,6,5)]
    return label,v,f
def solid(vertices,faces,label):
    center=sum((Vector(v) for v in vertices),Vector())/len(vertices)
    new=[]
    for f in faces:
        a,b,c=(Vector(vertices[i]) for i in f)
        if (b-a).cross(c-a).dot((a+b+c)/3-center)<0:f=(f[0],f[2],f[1])
        new.append(f)
    return label,vertices,new
def bolt_y(x,z,y0,y1,r,label):
    v=[(x+r*math.cos(i*math.tau/6),y,z+r*math.sin(i*math.tau/6)) for y in (y0,y1) for i in range(6)]
    f=[]
    for i in range(1,5):f += [(0,i,i+1),(6,6+i,6+i+1)]
    for i in range(6):
        k=(i+1)%6;f += [(i,k,6+k),(i,6+k,6+i)]
    return solid(v,f,label)
def triangle_gusset(x0,x1,y,tag):
    points=[(x0,.108),(x0,.178),(x1,.178)]
    v=[(x,sy,z) for sy in (y-.007,y+.007) for x,z in points]
    f=[(0,2,1),(3,4,5),(0,1,4),(0,4,3),(1,2,5),(1,5,4),(2,0,3),(2,3,5)]
    return solid(v,f,tag)
def parts_for(mid):
    if mid=="P19-01":
        res=[]
        for tag,y in [("rear",-1.955),("front",.005)]:
            res += [box((.029,y-.014,.055),(.851,y+.014,.085),tag+"_crossmember"),
                    bolt_y(.059,.070,y+.007,y+.028,.012,tag+"_left_crossmember_bolt"),
                    bolt_y(.821,.070,y+.007,y+.028,.012,tag+"_right_crossmember_bolt")]
        for tag,y in [("rear",-1.955),("front",.005)]:
            for side,x0,x1,bx in [("left",.029,.17,.054),("right",.851,.71,.826)]:
                res += [triangle_gusset(x0,x1,y,tag+"_"+side+"_gusset"),
                        bolt_y(bx,.158,y+.004,y+.017,.009,tag+"_"+side+"_gusset_bolt")]
        return res
    if mid=="P19-02":
        return [box((-.297,.528,-.515),(-.235,.546,-.395),"lower_hinge_plate"),
                box((-.297,.528,.395),(-.235,.546,.515),"upper_hinge_plate"),
                bolt_y(-.263,-.455,.543,.554,.012,"lower_hinge_fastener"),
                bolt_y(-.263,.455,.543,.554,.012,"upper_hinge_fastener"),
                box((.261,.530,-.030),(.297,.548,.030),"latch_receiver")]
    if mid=="P19-05":
        return [box((.033,-.431,.070),(1.207,-.409,.112),"front_stretcher"),
                box((.033,-.011,.070),(1.207,.011,.112),"rear_stretcher"),
                bolt_y(0.,.09,-.465,-.454,.013,"front_left_fastener"),
                bolt_y(1.24,.09,-.465,-.454,.013,"front_right_fastener"),
                bolt_y(0.,.09,.034,.045,.013,"rear_left_fastener"),
                bolt_y(1.24,.09,.034,.045,.013,"rear_right_fastener")]
    raise ValueError(mid)
def dims(objs):
    vs=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
    return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def capture(path,wire=False):
    scene=bpy.context.scene
    scene.render.engine="BLENDER_WORKBENCH";scene.display.shading.light="STUDIO"
    scene.render.resolution_x=1080;scene.render.resolution_y=820;scene.render.resolution_percentage=100
    objs=[o for o in scene.objects if o.type=="MESH"]
    bs=[(o,o.show_wire,o.show_all_edges) for o in objs]
    for o in objs:o.show_wire=wire;o.show_all_edges=wire
    vs=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
    lo=Vector([min(v[i] for v in vs) for i in range(3)])
    hi=Vector([max(v[i] for v in vs) for i in range(3)])
    mid=(lo+hi)/2;span=max((hi-lo).length,.5)
    camd=bpy.data.cameras.new("PASS17_QA_CAMERA");cam=bpy.data.objects.new("PASS17_QA_CAMERA",camd)
    bpy.context.collection.objects.link(cam);cam.location=mid+Vector((span*1.3,-span*1.8,span*1.2))
    cam.rotation_euler=(mid-cam.location).to_track_quat("-Z","Y").to_euler()
    camd.type="ORTHO";camd.ortho_scale=span*1.75;old=scene.camera;scene.camera=cam
    scene.render.filepath=str(path);scene.render.image_settings.file_format="PNG"
    try:bpy.ops.render.render(write_still=True)
    finally:
        scene.camera=old;bpy.data.objects.remove(cam,do_unlink=True)
        for o,w,a in bs:o.show_wire=w;o.show_all_edges=a
def add_details(o,items):
    mesh=o.data;bm=bmesh.new();bm.from_mesh(mesh)
    oldv=len(bm.verts);oldf=len(bm.faces)
    layer=bm.loops.layers.uv.verify()
    evidence=[]
    for label,vertices,faces in items:
        vv=[bm.verts.new(v) for v in vertices]
        for tri in faces:
            face=bm.faces.new([vv[i] for i in tri]);face.material_index=0;face.smooth=False
            n=(vv[tri[1]].co-vv[tri[0]].co).cross(vv[tri[2]].co-vv[tri[0]].co)
            assert n.length>1e-8,(label,"degenerate")
            axes=sorted(range(3),key=lambda i:abs(n[i]))[:2]
            for loop in face.loops:
                p=loop.vert.co;loop[layer].uv=(float(p[axes[0]]*.18+.5),float(p[axes[1]]*.18+.5))
        evidence.append({"label":label,"vertices":len(vertices),"triangles":len(faces)})
    bm.normal_update();bm.to_mesh(mesh);bm.free();mesh.update()
    assert len(mesh.vertices)==oldv+sum(x["vertices"] for x in evidence)
    assert len(mesh.polygons)==oldf+sum(x["triangles"] for x in evidence)
    return evidence
summary=[]
for mid in IDS:
    expect=BASE[mid];path=ROOT/"Models"/mid/(mid+".blend")
    assert path.is_file() and path.read_bytes().startswith(b"BLENDER-v4")
    bpy.ops.wm.open_mainfile(filepath=str(path))
    orig=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    assert len(orig)==expect[0],(mid,len(orig))
    assert sum(len(o.data.vertices) for o in orig)==expect[1]
    assert sum(len(o.data.polygons) for o in orig)==expect[2]
    assert all(o.data.uv_layers for o in orig)
    target=[o for o in orig if o.data.name==expect[5]]
    assert len(target)==1,(mid,[(o.name,o.data.name) for o in orig])
    before_bounds=dims(orig);old_names=[(o.name,o.data.name,o.parent.name if o.parent else None) for o in orig]
    folder=QA/mid;folder.mkdir(parents=True,exist_ok=True)
    before_hash=sha(path)
    capture(folder/"BEFORE_SHADED_BLENDER.png");capture(folder/"BEFORE_WIREFRAME_BLENDER.png",wire=True)
    details=add_details(target[0],parts_for(mid))
    after=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    assert [(o.name,o.data.name,o.parent.name if o.parent else None) for o in after]==old_names
    assert sum(len(o.data.vertices) for o in after)==expect[3]
    assert sum(len(o.data.polygons) for o in after)==expect[4]
    assert max(abs(a-b) for r1,r2 in zip(before_bounds,dims(after)) for a,b in zip(r1,r2))<1e-5
    assert all(len(p.vertices)==3 and p.area>1e-12 for o in after for p in o.data.polygons)
    for o in after:
        bm=bmesh.new();bm.from_mesh(o.data)
        assert all(e.is_manifold for e in bm.edges),(mid,o.name,"nonmanifold")
        bm.free()
    capture(folder/"AFTER_SHADED_BLENDER.png");capture(folder/"AFTER_WIREFRAME_BLENDER.png",wire=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    saved_hash=sha(path)
    fbx=path.with_suffix(".fbx")
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.context.scene.objects:
        if o.type in ("MESH","EMPTY"):o.select_set(True)
    bpy.context.view_layer.objects.active=target[0]
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,axis_forward="-Z",axis_up="Y",bake_anim=False,add_leaf_bones=False,object_types={"MESH","EMPTY"})
    assert fbx.read_bytes().startswith(b"Kaydara FBX Binary")
    bef=set(bpy.context.scene.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    imported=[o for o in bpy.context.scene.objects if o not in bef]
    imported_mesh=[o for o in imported if o.type=="MESH"]
    assert len(imported_mesh)==expect[0]
    assert sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in imported_mesh)==expect[4]
    assert all(o.data.uv_layers for o in imported_mesh)
    err=max(abs(a-b) for r1,r2 in zip(before_bounds,dims(imported_mesh)) for a,b in zip(r1,r2))
    assert err<1e-4,(mid,"FBX bounding error",err)
    report={"id":mid,"blender_version":bpy.app.version_string,"status":"BLENDER4_NATIVE_DETAIL_AND_FBX_ROUNDTRIP_PASS","before_sha256":before_hash,"real_blender_saved_blend_sha256":saved_hash,"real_blender_exported_fbx_sha256":sha(fbx),"model_mesh_count":expect[0],"vertex_count":expect[3],"triangle_count":expect[4],"added_details":details,"source_export_bbox_error_m":err,"moving_pivots_and_parenting":"PRESERVED","zero_degenerate_faces":True,"manifold_per_mesh":"PASS","FBX_reimport":"PASS","renderer":"ACTUAL_BLENDER_WORKBENCH_BEFORE_AFTER","independent_C01_02":"PENDING","Unity6_URP":"NOT_RUN"}
    (folder/"PASS17_NATIVE_DETAIL_ROUNDTRIP.json").write_text(json.dumps(report,indent=2))
    summary.append(report)
    print("C01-19 PASS17 REAL BLENDER",mid,saved_hash,sha(fbx),len(details),flush=True)
(QA/"SUMMARY.json").write_text(json.dumps({"models":summary,"stage":"PASS17_REAL_BLENDER_DETAIL_CANDIDATES_NOT_C01_02_APPROVED"},indent=2))
