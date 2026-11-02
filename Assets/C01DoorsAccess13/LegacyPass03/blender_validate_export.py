"""C01-13 PASS03 Blender 4.x native .blend + real Blender FBX export/import.
Run from repo root:
blender -b -t 2 --python Assets/C01DoorsAccess13/LegacyPass03/blender_validate_export.py
STATUS: NOT RUN in ChatGPT runtime; do not count as DCC PASS until executed.
"""
import bpy, json, hashlib, math
import bmesh
from collections import Counter
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

def source_topology(obj):
    # BMesh mesh connectivity is evaluated on actual Blender data, not GLB/FBX metadata.
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    loose_v=sum(1 for v in bm.verts if not v.link_edges)
    loose_e=sum(1 for e in bm.edges if not e.link_faces)
    boundary=sum(1 for e in bm.edges if e.is_boundary)
    nonmanifold=sum(1 for e in bm.edges if not e.is_manifold)
    degenerate=sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    # Exported triangles may have more vertices due to UV/sharp split.
    obj.data.calc_loop_triangles()
    out={"vertices":len(bm.verts),"edges":len(bm.edges),"faces":len(bm.faces),
         "tris":len(obj.data.loop_triangles),"boundary_edges":boundary,
         "nonmanifold_edges":nonmanifold,"degenerate_faces":degenerate,
         "loose_vertices":loose_v,"loose_edges":loose_e,
         "uv_layers":len(obj.data.uv_layers)}
    bm.free()
    return out

def triangle_keys(obj):
    obj.data.calc_loop_triangles()
    def corner_key(v):
        p=obj.matrix_world @ obj.data.vertices[v].co
        return tuple(round(float(c),5) for c in p)
    return Counter(tuple(sorted(corner_key(i) for i in t.vertices))
                   for t in obj.data.loop_triangles)

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

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
    topology_before=source_topology(ob)
    assert topology_before['boundary_edges']==0,topology_before
    assert topology_before['nonmanifold_edges']==0,topology_before
    assert topology_before['degenerate_faces']==0,topology_before
    assert topology_before['loose_vertices']==0,topology_before
    assert topology_before['uv_layers']>0,topology_before
    triangles_before=triangle_keys(ob)
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
    imported_mesh=next(o for o in bpy.context.scene.objects if o.type=="MESH")
    assert len(imported_mesh.data.uv_layers)>0
    triangles_after=triangle_keys(imported_mesh)
    assert triangles_before==triangles_after, (
      "FBX roundtrip altered world-space triangle topology", 
      sum((triangles_before-triangles_after).values()),
      sum((triangles_after-triangles_before).values())
    )
    assert all(math.isfinite(c) for p in imported_mesh.data.uv_layers.active.data for c in p.uv)
    topology_after=source_topology(imported_mesh)
    assert topology_before["tris"]==topology_after["tris"],topology_after
    return {"blend":str(scene),"fbx":str(binary),"roundtrip":"PASS",
            "bbox_max_error_m":err,"source_vertices":len(verts),"source_tris":len(faces),
            "blender_source_topology":topology_before,
            "fbx_reimport_topology":topology_after,
            "source_blend_sha256":sha256(scene),
            "export_fbx_sha256":sha256(binary),
            "source_triangle_multiset_exact_5dp":True}

report={key:make(key) for key in ("D01","D02")}
(OUT/"blender_validation.json").write_text(json.dumps(report,indent=2))
print("C01-13 BLENDER PASS03",json.dumps(report))
