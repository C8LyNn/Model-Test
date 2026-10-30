"""C01-13 PASS03 Blender 4.x native .blend + real Blender FBX export/import.
Run from repo root:
blender -b -t 2 --python Assets/C01DoorsAccess13/LegacyPass03/blender_validate_export.py
STATUS: NOT RUN in ChatGPT runtime; do not count as DCC PASS until executed.
"""
import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"BlenderValidated";OUT.mkdir(exist_ok=True)

def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system="METRIC"
    bpy.context.scene.unit_settings.scale_length=1.0

def bounds():
    points=[tuple(o.matrix_world@v.co) for o in bpy.context.scene.objects
            if o.type=="MESH" for v in o.data.vertices]
    assert points,"No imported mesh!"
    return [[min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)]]

def make(key):
    reset()
    src=ROOT/(key+"_REPAIRED_v003_source_topology.obj")
    verts=[];uv=[];faces=[]
    for line in src.read_text().splitlines():
        parts=line.split()
        if not parts:continue
        if parts[0]=="v":verts.append(tuple(map(float,parts[1:4])))
        if parts[0]=="vt":uv.append(tuple(map(float,parts[1:3])))
        if parts[0]=="f":faces.append([tuple(map(int,word.split("/"))) for word in parts[1:]])
    assert all(len(f)==3 for f in faces)
    # Convert verified Unity-Y-up source mesh coordinates to Blender Z-up.
    pts=[(v[0],-v[2],v[1]) for v in verts]
    faces_v=[[corner[0]-1 for corner in face] for face in faces]
    mesh=bpy.data.meshes.new(key+"_REPAIRED")
    mesh.from_pydata(pts,[],faces_v)
    assert not mesh.validate(verbose=False)
    mesh.update()
    ob=bpy.data.objects.new(key+"_REPAIRED",mesh)
    bpy.context.collection.objects.link(ob)
    layer=mesh.uv_layers.new(name="UVMap")
    for poly,source in zip(mesh.polygons,faces):
        poly.use_smooth=False
        for corner,li in zip(source,poly.loop_indices):
            layer.data[li].uv=uv[corner[1]-1]
    material=bpy.data.materials.new("M_C01_FRAME" if key=="D01" else "M_C01_LEAF")
    material.diffuse_color=(.36,.45,.52,1) if key=="D01" else (.60,.49,.31,1)
    mesh.materials.append(material)
    assert tuple(ob.scale)==(1,1,1) and tuple(ob.location)==(0,0,0)
    scene=OUT/(key+"_REPAIRED_v003.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(scene))
    ob.select_set(True);bpy.context.view_layer.objects.active=ob
    binary=OUT/(key+"_REPAIRED_v003_BLENDER.fbx")
    bpy.ops.export_scene.fbx(filepath=str(binary),use_selection=True,object_types={"MESH"},
        global_scale=1,apply_unit_scale=True,axis_forward="-Z",axis_up="Y",
        mesh_smooth_type="FACE",bake_space_transform=False)
    assert binary.read_bytes().startswith(b"Kaydara FBX Binary")
    before=bounds()
    reset()
    bpy.ops.import_scene.fbx(filepath=str(binary))
    after=bounds()
    err=max(abs(before[k][i]-after[k][i]) for k in range(2) for i in range(3))
    assert err<0.001,("FBX imported bounds differ by >1mm",err)
    assert len([o for o in bpy.context.scene.objects if o.type=="MESH"])==1
    assert len(bpy.context.scene.objects[0].data.uv_layers)>0
    return {"blend":str(scene),"fbx":str(binary),"roundtrip":"PASS",
            "bbox_max_error_m":err,"source_vertices":len(verts),"source_tris":len(faces)}

report={key:make(key) for key in ("D01","D02")}
(OUT/"blender_validation.json").write_text(json.dumps(report,indent=2))
print("C01-13 BLENDER PASS03",json.dumps(report))
