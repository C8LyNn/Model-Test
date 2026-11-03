#!/usr/bin/env python3
"""W27 C01-17: SHA-pinned existing genuine P17-01 BLEND/FBX bolt shading audit.
Read-only production model: open real .blend, reimport current binary FBX, render actual
FBX geometry shaded/wireframe; no native saving/export/prefab or geometry mutation."""
import bpy, bmesh, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector

R = Path(__file__).resolve().parents[2]
SRC = R / "C01InteriorProps_Source/Blender/P17-01.blend"
FBX = R / "Assets/C01InteriorProps/Models/P17-01.fbx"
OUT = R / "C01InteriorProps_Source/QA/PASS27/Artifacts"
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED = {
    "BLEND": "7e7fb3911d7f0d061dfa202804a42b18ef0d99510f95e6cc1b6b42d0c53c17eb",
    "FBX": "cd6a5787bb7b4c088f0af35382385e4274c85c415c60467f9a22e46fe33ef02c",
}
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()
actual={"BLEND":sha(SRC), "FBX":sha(FBX)}
assert actual == EXPECTED, ("FROZEN_SHA_MISMATCH",actual)
assert SRC.read_bytes()[:7] == b"BLENDER", "NOT_NATIVE_BLENDER"
assert FBX.read_bytes()[:21] == b"Kaydara FBX Binary  ", "NOT_BINARY_FBX"
def meshes():
    return [o for o in bpy.data.objects if o.type == 'MESH']
def analyze(tag):
    objects=meshes()
    report={"object_count":len(objects),"triangles":0,"boundary_edges":0,"nonmanifold_edges":0,
            "degenerate_faces":0,"loose_vertices":0,"uv0_missing_objects":0,
            "bolt_objects":[],"bolt_dot_lt_0p2":0,"bolt_negative_dot":0}
    for o in objects:
        m=o.data
        m.calc_loop_triangles()
        report["triangles"]+=len(m.loop_triangles)
        bm=bmesh.new();bm.from_mesh(m)
        report["boundary_edges"]+=sum(e.is_boundary for e in bm.edges)
        report["nonmanifold_edges"]+=sum(not e.is_manifold for e in bm.edges)
        report["loose_vertices"]+=sum(not v.link_edges for v in bm.verts)
        report["degenerate_faces"]+=sum(f.calc_area()<1e-12 for f in bm.faces)
        bm.free()
        if not m.uv_layers: report["uv0_missing_objects"]+=1
        if "bolt" not in o.name.lower(): continue
        bolt={"name":o.name,"triangles":len(m.loop_triangles),"dot_lt_0p2":0,
              "negative_dot":0,"dot_min":1.0,"corner_count":0}
        normal_matrix=o.matrix_world.to_3x3().inverted().transposed()
        for t in m.loop_triangles:
            pos=[o.matrix_world @ m.vertices[i].co for i in t.vertices]
            v=(pos[1]-pos[0]).cross(pos[2]-pos[0])
            if v.length < 1e-12: continue
            v.normalize()
            for i in t.loops:
                if hasattr(m.loops[i],"normal"):
                    n=Vector(m.loops[i].normal)
                elif hasattr(m,"corner_normals"):
                    n=Vector(m.corner_normals[i].vector)
                else:
                    n=Vector(m.vertices[m.loops[i].vertex_index].normal)
                n=normal_matrix @ n
                if n.length < 1e-12: continue
                n.normalize()
                dot=max(-1.0,min(1.0,v.dot(n)))
                bolt["corner_count"]+=1
                bolt["dot_min"]=min(bolt["dot_min"],dot)
                bolt["dot_lt_0p2"]+=int(dot<0.2)
                bolt["negative_dot"]+=int(dot < -0.0001)
        report["bolt_objects"].append(bolt)
        report["bolt_dot_lt_0p2"]+=bolt["dot_lt_0p2"]
        report["bolt_negative_dot"]+=bolt["negative_dot"]
    return report

bpy.ops.wm.open_mainfile(filepath=str(SRC))
native=analyze("source_BLEND")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(FBX), use_custom_normals=True)
fbx=analyze("imported_FBX")
assert fbx["object_count"]==25 and fbx["triangles"]==380, ("FBX_MODEL_PARITY_FAIL", fbx)
assert fbx["uv0_missing_objects"]==0, "FBX_MISSING_UV0"
assert fbx["degenerate_faces"]==0 and fbx["loose_vertices"]==0, "FBX_MESH_DEGENERATE"
render_objects=meshes()
coords=[o.matrix_world @ v.co for o in render_objects for v in o.data.vertices]
mins=Vector([min(p[i] for p in coords) for i in range(3)])
maxs=Vector([max(p[i] for p in coords) for i in range(3)])
center=(mins+maxs)*0.5
size=(maxs-mins).length
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1280;scene.render.resolution_y=960;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
sh=scene.display.shading
sh.light='STUDIO'
sh.color_type='MATERIAL'
sh.show_shadows=True
sh.show_cavity=True
sh.cavity_type='BOTH'
sh.show_specular_highlight=True
cam_data=bpy.data.cameras.new("W27_TEST_CAMERA")
camera=bpy.data.objects.new("W27_TEST_CAMERA",cam_data)
scene.collection.objects.link(camera)
scene.camera=camera
cam_data.type='ORTHO'
cam_data.lens=40
def camera_set(target, offset, scale):
    camera.location=target+Vector(offset)
    direction=target-camera.location
    camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    cam_data.ortho_scale=scale
    scene.camera=camera
def render(name, wire):
    sh.show_wireframes=wire
    sh.show_cavity=not wire
    sh.show_shadows=not wire
    scene.render.filepath=str(OUT/name)
    bpy.ops.render.render(write_still=True)
    path=OUT/name
    assert path.exists() and path.stat().st_size>1000, "EMPTY_RENDER "+str(path)
    return {"filename":name,"bytes":path.stat().st_size,"sha256":sha(path)}
shots=[]
base=max(size,0.5)
camera_set(center,(base*1.5,-base*1.7,base*1.25),base*1.8)
shots.append(render("P17-01_REAL_FBX_ISO_SHADED.png",False))
shots.append(render("P17-01_REAL_FBX_ISO_WIREFRAME.png",True))
camera_set(center,(0,-base*2.6,base*0.35),base*1.65)
shots.append(render("P17-01_REAL_FBX_FRONT_SHADED.png",False))
shots.append(render("P17-01_REAL_FBX_FRONT_WIREFRAME.png",True))
bolts=[o for o in render_objects if "bolt" in o.name.lower()]
assert len(bolts)>=4, ("MISSING_ORIGINAL_BOLT_OBJECTS", [x.name for x in bolts])
bolt=bolts[0]
boltcoords=[bolt.matrix_world @ v.co for v in bolt.data.vertices]
boltcenter=Vector([sum(p[i] for p in boltcoords)/len(boltcoords) for i in range(3)])
camera_set(boltcenter,(0.1,-0.2,0.15),0.13)
shots.append(render("P17-01_REAL_FBX_BOLT_CLOSEUP_SHADED.png",False))
shots.append(render("P17-01_REAL_FBX_BOLT_CLOSEUP_WIREFRAME.png",True))
report={
  "schema":"C01-17-W27-SHA-PINNED-ORIGINAL-NATIVE-BLENDER4-FBX-SHADING",
  "actual_blender_version":bpy.app.version_string,
  "source_sha256":actual["BLEND"],"fbx_sha256":actual["FBX"],
  "native_blend":native,"reimported_binary_fbx":fbx,
  "world_bounds_min":list(mins),"world_bounds_max":list(maxs),
  "scope":"P17-01 original unchanged native BLEND and FBX ONLY",
  "images":shots,"visual_disposition":"REVIEW_SHOTS_BY_INDEPENDENT_C01_02_AND_HUMAN; NOT AUTOMATIC_URP_PASS",
  "unity6_urp":"NOT_RUN","production_changes":0,
  "doors_gates_touched":0
}
reportpath=OUT/"P17-01_W27_REAL_BLENDER_FBX_BOLT_SHADING_QA.json"
reportpath.write_text(json.dumps(report,indent=2)+"\n")
print("C01-17 W27 REAL BLENDER FBX QA",json.dumps({"blend":actual["BLEND"],"fbx":actual["FBX"],"native_meshes":native["object_count"],"fbx_meshes":fbx["object_count"],"fbx_triangles":fbx["triangles"],"bolt_corners":fbx["bolt_dot_lt_0p2"],"images":len(shots),"json":str(reportpath)}),flush=True)
