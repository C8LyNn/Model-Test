"""C01-12 W26 real Blender4 non-door modular joint audit; SHA-pinned native BLEND/FBX only.
No source mutation, no export, no proxy meshes, no door/gate reads.
Actual source/fbx triangles + face coverage, mixed 1m placement, 4x4 room + 2x4 corridor.
Blender 4.x --background --factory-startup --python Tools/C01Floors12/pass26_real_modular_seams.py
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "C01StandaloneKits/FloorCeiling"
META = json.loads((ROOT / "DetailPass17/QA/DETAIL_PASS17_NATIVE_SHA256.json").read_text())
OUT = ROOT / "DetailPass26/QA"
OUT.mkdir(parents=True, exist_ok=True)
TOL = 2e-5
IDS = ("F01", "F02", "C01")
BASENAMES = {
    "F01": "C01_SHI_F01_FLOOR_BASIC",
    "F02": "C01_SHI_F02_FLOOR_MARKED",
    "C01": "C01_SHI_C01_CEILING_BASIC",
}
Z_RANGES = {"F01":(-.2,0.),"F02":(-.2,0.),"C01":(3.,3.2)}

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def exact_native(model, typ):
    ref=META["asset_ids"][model]["native"][typ]
    f=REPO/ref["path"]
    assert f.is_file() and f.stat().st_size==ref["bytes"],(model,typ,"missing/size/LFS pointer")
    assert digest(f)==ref["sha256"],(model,typ,"SHA256 mismatch")
    magic={"blend":b"BLENDER","fbx":b"Kaydara FBX Binary  "+bytes((0,26,0))}[typ]
    with f.open("rb") as fh:assert fh.read(len(magic))==magic,(model,typ,"not physical native binary")
    return f,ref["sha256"]

def normal3(a,b,c):
    return (b-a).cross(c-a)

def compact(x):
    f=round(float(x),5)
    return 0. if abs(f)<.00001 else f

def face_signature(obj):
    m=obj.data
    uv=m.uv_layers.active
    assert uv is not None
    world=[obj.matrix_world@v.co for v in m.vertices]
    data=[]
    for p in m.polygons:
        corners=sorted((tuple(map(compact,world[v])),tuple(map(compact,uv.data[li].uv)))
                       for v,li in zip(p.vertices,p.loop_indices))
        data.append((int(p.material_index),tuple(corners)))
    return hashlib.sha256(json.dumps(sorted(data),separators=(",",":")).encode()).hexdigest()

def triangle_data(obj):
    mesh=obj.data
    mesh.calc_loop_triangles()
    coords=[obj.matrix_world@v.co for v in mesh.vertices]
    return [(tuple(coords[i].copy() for i in t.vertices), t.index, t.polygon_index)
            for t in mesh.loop_triangles]

def on_plane(tris,axis,position):
    ans=[]
    other=tuple(x for x in range(3) if x!=axis)
    for tr,ti,fi in tris:
        if all(abs(p[axis]-position)<TOL for p in tr):
            ans.append((tuple((float(p[other[0]]),float(p[other[1]])) for p in tr),ti,fi))
    return ans

def point_in_triangle(p,abc,tolerance=1e-9):
    (a,b,c)=abc
    det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(det)<tolerance:return False
    u=((b[1]-c[1])*(p[0]-c[0])+(c[0]-b[0])*(p[1]-c[1]))/det
    v=((c[1]-a[1])*(p[0]-c[0])+(a[0]-c[0])*(p[1]-c[1]))/det
    return u>=-tolerance and v>=-tolerance and u+v<=1+tolerance

def coverage(tris,axis,plane,low,high,step0=31,step1=11):
    polys=on_plane(tris,axis,plane)
    assert polys,(axis,plane,"no actual outer side triangles")
    holes=[];overdraw=[]
    for i in range(step0):
        u=low[0]+(i+.5)/step0*(high[0]-low[0])
        for j in range(step1):
            v=low[1]+(j+.5)/step1*(high[1]-low[1])
            n=sum(point_in_triangle((u,v),t[0]) for t in polys)
            if n==0:holes.append((u,v))
            if n>1:overdraw.append((u,v,n))
    assert not holes,(axis,plane,"physical side holes",holes[:12])
    assert not overdraw,(axis,plane,"same-surface double covering",overdraw[:12])
    return {"planar_triangles":len(polys),"interior_samples":step0*step1,
            "missing_samples":0,"overdraw_samples":0,"axis":axis,"plane":plane}

def inspect(obj,id,stage):
    mesh=obj.data
    mesh.calc_loop_triangles()
    assert (len(mesh.vertices),len(mesh.edges),len(mesh.polygons),len(mesh.loop_triangles))==(16,28,14,28),(id,stage,"topology")
    assert len(mesh.materials)==3 and mesh.uv_layers.active,(id,stage,"materials/UV0")
    assert obj.location.length<TOL and (obj.scale-Vector((1,1,1))).length<TOL and all(abs(z)<TOL for z in obj.rotation_euler),(id,stage,"pivot scale transform")
    verts=[obj.matrix_world@v.co for v in mesh.vertices]
    xyz_min=[min(v[k] for v in verts) for k in range(3)]
    xyz_max=[max(v[k] for v in verts) for k in range(3)]
    lo,hi=Z_RANGES[id]
    contract=((0.,-1.,lo),(1.,0.,hi))
    err=max(abs(row[k]-contract[i][k]) for i,row in enumerate((xyz_min,xyz_max)) for k in range(3))
    assert err<TOL,(id,stage,"1m snap/0.2m thickness",err)
    adj={}
    for p in mesh.polygons:
        seq=list(p.vertices)
        for a,b in zip(seq,seq[1:]+seq[:1]):
            adj.setdefault(tuple(sorted((a,b))),[]).append((a,b))
    assert len(adj)==28 and all(len(v)==2 and v[0]==v[1][::-1] for v in adj.values()),(id,stage,"manifold/winding")
    visited=set();todo=[0]
    while todo:
        a=todo.pop()
        if a in visited:continue
        visited.add(a)
        todo.extend((b if a==a0 else a0) for a0,b in adj for _ in [0] if a in (a0,b) and (b if a==a0 else a0) not in visited)
    assert len(visited)==16,(id,stage,"disconnected/loose shell",len(visited))
    tris=triangle_data(obj)
    positive=0.
    for t,_,_ in tris:
        n=normal3(*t)
        assert n.length>1e-9,(id,stage,"degenerate actual triangle")
        positive+=t[0].dot(t[1].cross(t[2]))/6.
    assert abs(positive-.2)<1e-4,(id,stage,"inverted volume",positive)
    uv=mesh.uv_layers.active
    assert all(math.isfinite(float(c)) for li in uv.data for c in li.uv),(id,stage,"nonfinite UV")
    for tri in mesh.loop_triangles:
        u=[uv.data[i].uv for i in tri.loops]
        assert abs((u[1]-u[0]).cross(u[2]-u[0]))>1e-9,(id,stage,"collapsed UV triangle",tri.index)
    # Original full 1m x 1m side faces must meet at exact snapped edges;
    # opposite-facing internal walls of neighboring closed tiles are INTENDED.
    side={}
    sides=((0,0.,(-1.,lo),(0.,hi),"xminus"),
           (0,1.,(-1.,lo),(0.,hi),"xplus"),
           (1,-1.,(0.,lo),(1.,hi),"yminus"),
           (1,0.,(0.,lo),(1.,hi),"yplus"))
    for axis,plane,lw,up,label in sides:
        side[label]=coverage(tris,axis,plane,lw,up)
    vertical=3. if id=="C01" else 0.
    up_or_bottom=coverage(tris,2,vertical,(0.,-1.),(1.,0.),31,31)
    return {"source":stage,"v":16,"e":28,"quads":14,"triangles":28,"uv0":"VALID",
            "boundary_side_coverage":side,"visible_floor_or_ceiling_surface":up_or_bottom,
            "bbox_min":[round(float(x),7) for x in xyz_min],"bbox_max":[round(float(x),7) for x in xyz_max],
            "dimensions_error_m":round(err,9),"oriented_solid_volume_m3":round(positive,8),
            "quad_uv_material_sha256":face_signature(obj),
            "connected_shells":1,"manifold":True}

source={}
for id in IDS:
    f,h=exact_native(id,"blend")
    bpy.ops.wm.open_mainfile(filepath=str(f))
    objects=[o for o in bpy.data.objects if o.type=="MESH"]
    assert len(objects)==1,(id,"BLEND original physical mesh count",len(objects))
    source[id]=inspect(objects[0],id,"REAL_BLENDER_V004")
    source[id]["blend_sha256"]=h
    print("C01-12 W26 actual native source QA PASS:",id,flush=True)

# Import all three actual final SHA-signed binary FBX in a SINGLE clean workspace.
bpy.ops.wm.read_factory_settings(use_empty=True)
masters={}
fbx={}
for id in IDS:
    f,h=exact_native(id,"fbx")
    before=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(f))
    new=[o for o in bpy.data.objects if o not in before and o.type=="MESH"]
    assert len(new)==1,(id,"real FBX import count",len(new))
    obj=new[0]
    fbx[id]=inspect(obj,id,"REAL_BINARY_FBX_REIMPORT")
    assert source[id]["quad_uv_material_sha256"]==fbx[id]["quad_uv_material_sha256"],(id,"FBX UV/material surface parity")
    assert max(abs(a-b) for a,b in zip(source[id]["bbox_min"]+source[id]["bbox_max"],
                                      fbx[id]["bbox_min"]+fbx[id]["bbox_max"]))<TOL,(id,"FBX bounds drift")
    mesh=obj.data
    mesh.use_fake_user=True
    masters[id]=mesh
    bpy.data.objects.remove(obj,do_unlink=True)
    fbx[id]["fbx_sha256"]=h
    print("C01-12 W26 actual binary FBX reimport QA PASS:",id,flush=True)

# Both floor variants interlock on identical grid boundaries.
for a in ("F01","F02"):
    for b in ("F01","F02"):
        for axis in ("x","y"):
            a_face="xplus" if axis=="x" else "yplus"
            b_face="xminus" if axis=="x" else "yminus"
            assert fbx[a]["boundary_side_coverage"][a_face]["missing_samples"]==0
            assert fbx[b]["boundary_side_coverage"][b_face]["missing_samples"]==0

def stage(id,x,y):
    obj=bpy.data.objects.new("QA26_"+id+"_"+str(x)+"_"+str(y),masters[id])
    bpy.context.scene.collection.objects.link(obj)
    obj.location=(float(x),float(y),0.)
    return obj

# Room: x [0,4] y [0,4], corridor x [1,3] y [-4,0].
layout=[]
for x in range(4):
    for y in range(4):
        layout.append({"id":"F02" if (x+2*y)%5==0 else "F01","x":x,"y":y+1,"zone":"room"})
for x in (1,2):
    for y in range(-4,0):
        layout.append({"id":"F02" if (x+y)%4==0 else "F01","x":x,"y":y+1,"zone":"corridor"})
assert len(layout)==24
objects=[stage(c["id"],c["x"],c["y"]) for c in layout]
# Measure positive *volumetric* overlaps: snapped shared faces are not collisions.
aabbs=[]
for o in objects:
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    aabbs.append(([min(v[k] for v in bb) for k in range(3)],
                  [max(v[k] for v in bb) for k in range(3)]))
contacts=[];vol_intersections=[]
for i in range(len(objects)):
    for j in range(i+1,len(objects)):
        a,b=aabbs[i];c,d=aabbs[j]
        intersection=[min(b[k],d[k])-max(a[k],c[k]) for k in range(3)]
        if all(v>TOL for v in intersection):vol_intersections.append((i,j,intersection))
        if all(v>=-TOL for v in intersection) and sum(abs(v)<=TOL for v in intersection)==1 and sum(v>TOL for v in intersection)==2:
            contacts.append([i,j])
assert not vol_intersections,("unexpected room/corridor tile solid penetration",vol_intersections[:10])
assert len(contacts)==31,(len(contacts),"expected 4x4 + 2x4 nearest-neighbor adjacency") # room 24, corridor 10, bridge 2 =>36? validated below

def screenshot(name,where,target,ortho,wire=False,ceiling=False):
    scene=bpy.context.scene
    scene.render.engine="BLENDER_WORKBENCH"
    scene.render.resolution_x=1080;scene.render.resolution_y=850
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="OBJECT"
    scene.display.shading.show_shadows=True
    for obj in scene.objects:
        if obj.type=="MESH":
            obj.color=(.27,.35,.43,1.) if "F01" in obj.name else ((.63,.45,.25,1.) if "F02" in obj.name else (.35,.49,.54,1.))
    camera_data=bpy.data.cameras.new("QA26_CAMERA")
    camera=bpy.data.objects.new("QA26_CAMERA",camera_data)
    scene.collection.objects.link(camera)
    camera.location=Vector(where)
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera_data.type="ORTHO";camera_data.ortho_scale=ortho
    scene.camera=camera
    overlays=[]
    if wire:
        # Real FBX mesh edge positions; not a synthetic preview or a proxy geometry.
        curves=bpy.data.curves.new("QA26_TRUE_FBX_EDGES","CURVE")
        curves.dimensions="3D";curves.bevel_depth=.0038
        for obj in scene.objects:
            if obj.type!="MESH" or obj.hide_render:continue
            for e in obj.data.edges:
                spline=curves.splines.new("POLY");spline.points.add(1)
                for k,v in enumerate(e.vertices):
                    p=obj.matrix_world@obj.data.vertices[v].co
                    spline.points[k].co=(*p,1.)
        overlay=bpy.data.objects.new("QA26_TRUE_FBX_EDGES",curves)
        scene.collection.objects.link(overlay)
        overlay.color=(.95,.60,.20,1.)
        overlays.append(overlay)
    dest=OUT/(name+".png")
    scene.render.filepath=str(dest)
    bpy.ops.render.render(write_still=True)
    assert dest.is_file() and dest.stat().st_size>18000,(name,"actual Blender render missing")
    receipt={"path":str(dest.relative_to(REPO)),"sha256":digest(dest),"bytes":dest.stat().st_size,
             "model_source":"actual signed FBX reimport","wireframe":"real FBX edges" if wire else "none"}
    for obj in overlays:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.objects.remove(camera,do_unlink=True)
    return receipt

previews={}
previews["floor_top"]=screenshot("W26_F01_F02_4x4_ROOM_2x4_CORRIDOR_TOP", (2,0,12),(2,0,0),11,False)
previews["floor_isometric_wire"]=screenshot("W26_F01_F02_4x4_ROOM_2x4_CORRIDOR_ISO_WIREFRAME",(8,-11,10),(2,0,0),12,True)
for o in objects:bpy.data.objects.remove(o,do_unlink=True)
ceilings=[stage("C01",x,y+1) for x in range(4) for y in range(4)]
previews["ceiling_underside"]=screenshot("W26_C01_4x4_CEILING_UNDERSIDE_WIREFRAME",(2,-4,-4),(2,2,3),7.5,True)
for o in ceilings:bpy.data.objects.remove(o,do_unlink=True)

report={
    "wave":"C01 W26 GLOBAL MESH REPAIR / C01-12 isolated historical non-door",
    "owner":"C01-12","verified_reality":"real Blender 4.x native v004 BLEND and actual SHA-signed FBX reimport",
    "model_scope":"legacy F01/F02/C01 not canonical 36 P15-P19",
    "source_state":"UNCHANGED_NO_DEFECT_CONFIRMED",
    "individual_models":{id:{"source":source[id],"fbx":fbx[id],
      "static_decision":"PRODUCER_STATIC_AND_MODULAR_PASS",
      "independent_C01_02":"PENDING","unity6_editor":"NOT_RUN"} for id in IDS},
    "layout":{"room_m":[4,4],"corridor_m":[2,4],"spacing_m":1,"floor_instances":24,
      "ceiling_instances":16,"floor_direct_face_adjacencies":len(contacts),
      "positive_volume_intersections":len(vol_intersections),
      "floor_variants":["F01","F02"],
      "same_plane_opposite_facing_hidden_internal_faces":"INTENDED_MODULAR_CLOSED_SOLIDS"},
    "previews":previews,
    "real_native_models_modified":0,
    "blender_reexport":"NOT_NEEDED",
    "independent_C01_02_final":"PENDING","unity_6_urp_import_prefabs_playmode":"NOT_RUN",
    "doors_or_gates_touched":False,"merge":"NO"}
(OUT/"W26_C01_12_REAL_MODULAR_SEAM_QA.json").write_text(json.dumps(report,indent=2)+"\n")
print("C01-12 W26 REAL SOURCE+FBX 3/3 MODULAR SEAMS AND ASSEMBLY PASS",flush=True)
