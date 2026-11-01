"""C01-13 PASS18: import exact PASS16 GLB in real Blender; native .blend, FBX, reimport, Workbench.
D01/D02 legacy only, outside 36-asset P15-P19 count. No proxy or historical source replacement.
"""
import bpy, lzma, base64, json, hashlib, math
from pathlib import Path
from collections import Counter
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"Native"; PREV=ROOT/"Previews"; OUT.mkdir(exist_ok=True);PREV.mkdir(exist_ok=True)
SIZES=[38748,38808,25116,30372]
IDS=["D01_AFTER","D02_AFTER","D01_BEFORE","D02_BEFORE"]
SHA={"D01_AFTER":"19b5132d07eef279589699ec49ed4504d40310fbf7ab8dba7ef367bf7a936125",
"D02_AFTER":"5d21e10dc29c79325bd4c4f7c43a84b2f99df4dd6f3a596b93242f63cba7525b",
"D01_BEFORE":"4be7d2ac91e29c28535eb01e69ea80d62fe2bd00507c92f59a8848e73f3c9e2b",
"D02_BEFORE":"0a5b89fa425b23ccfa32fe3cb530b7a71b7ab5463a90acc24ac55b210935e4bf"}
def hashbytes(x):return hashlib.sha256(x).hexdigest()
encoded="".join((ROOT/("part%02d.txt"%i)).read_text().strip() for i in range(4))
assert len(encoded)==12048,"Incomplete physical source transfer"
payload=base64.b64decode(encoded)
assert hashbytes(payload)=="7c7596c6e8967557a04223630ea46a3c7cd817855687fc2d284bc49bbaea821f"
raw=lzma.decompress(payload)
assert len(raw)==sum(SIZES)
o=0
for id,size in zip(IDS,SIZES):
    b=raw[o:o+size];o+=size
    assert b.startswith(b"glTF") and hashbytes(b)==SHA[id],("Wrong actual source",id)
    (ROOT/(id+".glb")).write_bytes(b)

EXPECTED={"D01":(33,1468),"D02":(34,1248)}
def reset():bpy.ops.wm.read_factory_settings(use_empty=True)
def meshes():return [o for o in bpy.context.scene.objects if o.type=="MESH"]
def triangles():
    for o in meshes():o.data.calc_loop_triangles()
    return sum(len(o.data.loop_triangles) for o in meshes())
def worldbounds():
    points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
    return [[min(float(v[i]) for v in points) for i in range(3)],
            [max(float(v[i]) for v in points) for i in range(3)]]
def keys():
    c=Counter()
    for o in meshes():
        o.data.calc_loop_triangles()
        for t in o.data.loop_triangles:
            tri=tuple(sorted(tuple(round(float((o.matrix_world@o.data.vertices[i].co)[k]),4)
                for k in range(3)) for i in t.vertices))
            c[tri]+=1
    return c
def audit(count,tri):
    assert len(meshes())==count,(len(meshes()),count)
    assert triangles()==tri,(triangles(),tri)
    result=[]
    for o in meshes():
        m=o.data
        assert len(m.uv_layers)>0 and len(m.materials)>0,(o.name,"UV0/material missing")
        assert all(math.isfinite(float(z)) for v in m.vertices for z in v.co)
        assert all(t.area>1e-12 for t in m.loop_triangles),(o.name,"degenerate triangle")
        # GLB source stores UV0 but no explicit NORMAL accessors. Blender derives
        # vertex/loop normals from actual geometry; test exported FBX after reimport.
        assert all(math.isfinite(float(z)) for p in m.polygons for z in p.normal),(o.name,"invalid normal")
        result.append({"name":o.name,"vertices":len(m.vertices),"triangles":len(m.loop_triangles),
                       "uv0":len(m.uv_layers[0].data),"material_slots":len(m.materials)})
    return result
def import_glb(id):
    reset();bpy.ops.import_scene.gltf(filepath=str(ROOT/(id+".glb")))
    bpy.context.view_layer.update()
    key=id.split("_")[0]
    root=bpy.data.objects.new(key+("_HINGE_PIVOT" if key=="D02" else "_FIXED_ROOT"),None)
    bpy.context.collection.objects.link(root)
    for ob in meshes():
        w=ob.matrix_world.copy();ob.parent=root;ob.matrix_world=w
    bpy.context.view_layer.update()
    assert root.location.length<1e-9
    return root
def preview(label,wire):
    s=bpy.context.scene;lo,hi=worldbounds()
    center=Vector([(lo[i]+hi[i])/2 for i in range(3)])
    longest=max(hi[i]-lo[i] for i in range(3))
    cam=bpy.data.objects.new("QA_CAM",bpy.data.cameras.new("QA_CAM"))
    s.collection.objects.link(cam)
    cam.location=center+Vector((longest*2,-longest*2.5,longest*1.4))
    cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO";cam.data.ortho_scale=longest*1.8;s.camera=cam
    s.render.engine="BLENDER_WORKBENCH";s.display.shading.light="STUDIO"
    s.display.shading.color_type="MATERIAL"
    if hasattr(s.display.shading,"show_wireframes"):s.display.shading.show_wireframes=wire
    s.render.resolution_x=850;s.render.resolution_y=850;s.render.resolution_percentage=100
    s.render.image_settings.file_format="PNG"
    p=PREV/(label+("_WIREFRAME" if wire else "_SHADED")+".png")
    s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    assert p.exists() and p.stat().st_size>1000
    bpy.data.objects.remove(cam,do_unlink=True)
    return {"file":p.name,"sha256":hashbytes(p.read_bytes())}
results={}
for key in ("D01","D02"):
    import_glb(key+"_BEFORE")
    original=(21,700) if key=="D01" else (28,864)
    audit(*original)
    before=[preview(key+"_BEFORE",False),preview(key+"_BEFORE",True)]
    import_glb(key+"_AFTER")
    src_audit=audit(*EXPECTED[key]);tri_src=keys();bounds_src=worldbounds()
    blend=OUT/(key+"_DETAIL_PASS18.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    assert blend.read_bytes().startswith(b"BLENDER")
    after=[preview(key+"_AFTER",False),preview(key+"_AFTER",True)]
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.context.scene.objects:
        if o.type in {"MESH","EMPTY"}:o.select_set(True)
    bpy.context.view_layer.objects.active=meshes()[0]
    fbx=OUT/(key+"_DETAIL_PASS18.fbx")
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,
       object_types={"MESH","EMPTY"},axis_forward="-Z",axis_up="Y",
       global_scale=1,apply_unit_scale=True,bake_anim=False)
    assert fbx.read_bytes().startswith(b"Kaydara FBX Binary")
    reset();bpy.ops.import_scene.fbx(filepath=str(fbx))
    bpy.context.view_layer.update()
    imported=audit(*EXPECTED[key]);bounds_new=worldbounds()
    d=max(abs(bounds_src[i][j]-bounds_new[i][j]) for i in range(2) for j in range(3))
    assert d<.0002,(key,"FBX reimport bounds change",d)
    assert keys()==tri_src,(key,"FBX world triangle parity FAIL")
    assert key!="D02" or any("HINGE_PIVOT" in o.name for o in bpy.context.scene.objects)
    results[key]={"status":"REAL_BLENDER_FBX_REIMPORT_PASS",
       "source_sha256":SHA[key+"_AFTER"],"before_sha256":SHA[key+"_BEFORE"],
       "mesh_parts":len(src_audit),"triangles":EXPECTED[key][1],
       "fbx_parts":len(imported),"max_bounds_error_m":d,"world_triangle_multiset_0_1mm":"IDENTICAL",
       "blend_sha256":hashbytes(blend.read_bytes()),"fbx_sha256":hashbytes(fbx.read_bytes()),
       "previews_before":before,"previews_after":after,"per_object":src_audit,
       "independent_C01_02":"PENDING","Unity6_URP":"NOT_RUN"}
(OUT/"PASS18_NATIVE_QA.json").write_text(json.dumps(results,indent=2))
print("C01-13 ACTUAL BLENDER PASS18",json.dumps({k:{p:v for p,v in item.items() if p!="per_object"} for k,item in results.items()}))
