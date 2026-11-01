#!/usr/bin/env python3
"""C01-11 isolated W01-W04 authoring: native .blend, FBX, 3-angle previews.

PASS17: W02 authentic original source is recovered exactly, not re-designed.
Outputs are quarantined QA candidates; no ship, prefab, or deploy paths edited.
Run with: blender -b --factory-startup --python-exit-code 1 --python build_wall_models.py
"""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path
# Blender --python may not add the invoked script's directory to sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from original_r2_w02 import build_exact as original_r2_w02
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
PASS17_QUARANTINE = ROOT / "QA_Candidates" / "PASS17_SourceRecovery"
BLEND = PASS17_QUARANTINE / "Blender"
FBX = PASS17_QUARANTINE / "FBX"
PREVIEW = PASS17_QUARANTINE / "Previews"
QA = PASS17_QUARANTINE / "QA"
for directory in (BLEND, FBX, PREVIEW, QA):
    directory.mkdir(parents=True, exist_ok=True)
EXPECTED = {
    "W01": ((0, 0, 0), (1, 3, .2)),
    "W02": ((0, 0, 0), (1, 3, .2)),
    "W03": ((-.5, 0, -.5), (.5, 3, .5)),
    "W04": ((0, 0, 0), (2, 3, .2)),
}
NAMES = {
    "W01": "FULL_WALL_1M", "W02": "PANEL_WALL_1M",
    "W03": "CORNER_90_1M", "W04": "DOOR_OPENING_2M"
}
COLORS = {
    "W01": (.43, .51, .58, 1), "W02": (.26, .38, .48, 1),
    "W03": (.49, .53, .57, 1), "W04": (.40, .54, .62, 1)
}

def unity_to_blender(v):
    return (float(v[0]), -float(v[2]), float(v[1]))

def blender_to_unity(v):
    return (float(v[0]), float(v[2]), -float(v[1]))

def clean():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

def extrude_polygon(vertices_2d, start, end, orientation):
    # Cap shape in X-Y (normal along Unity Z) or X-Z (normal along Unity Y).
    n = len(vertices_2d)
    def uv_vert(pair, depth):
        x, t = pair
        return (x, t, depth) if orientation == "XY" else (x, depth, t)
    uverts = [uv_vert(p, start) for p in vertices_2d]
    uverts += [uv_vert(p, end) for p in vertices_2d]
    faces = [tuple(reversed(range(n))), tuple(range(n, n*2))]
    faces += [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)]
    mesh = bpy.data.meshes.new("C01_Wall_Mesh")
    mesh.from_pydata([unity_to_blender(v) for v in uverts], [], faces)
    mesh.update(calc_edges=True)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    # Planar metric UVs: 1 UV unit = 1 meter in each dominant plane.
    uv = mesh.uv_layers.new(name="UVMap")
    for p in mesh.polygons:
        ids = [mesh.loops[i].vertex_index for i in p.loop_indices]
        a, b, c = (Vector(blender_to_unity(mesh.vertices[i].co)) for i in ids[:3])
        normal = (b-a).cross(c-a)
        axis = max(range(3), key=lambda i: abs(normal[i]))
        for li in p.loop_indices:
            x, y, z = blender_to_unity(mesh.vertices[mesh.loops[li].vertex_index].co)
            uv.data[li].uv = ((z,y) if axis==0 else ((x,z) if axis==1 else (x,y)))
    return mesh

def setup_material(mid):
    mat = bpy.data.materials.new("C01_" + mid + "_STEEL")
    mat.diffuse_color = COLORS[mid]
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = COLORS[mid]
        bsdf.inputs["Metallic"].default_value = .45
        bsdf.inputs["Roughness"].default_value = .68
    return mat

def build(mid):
    if mid == "W02":
        # PASS17: genuinely restore original r2, never the 12-triangle proxy.
        # Authored records reproduce exact 288 vertices and 572 triangles.
        unity_vertices, faces = original_r2_w02()
        mesh = bpy.data.meshes.new("W02_original_r2_572_triangles")
        mesh.from_pydata([unity_to_blender(p) for p in unity_vertices], [], faces)
        mesh.update(calc_edges=True)
        uv = mesh.uv_layers.new(name="UVMap")
        for poly in mesh.polygons:
            ids = [mesh.loops[li].vertex_index for li in poly.loop_indices]
            a, b, c = (Vector(unity_vertices[k]) for k in ids)
            normal = (b-a).cross(c-a)
            axis = max(range(3), key=lambda k: abs(normal[k]))
            for li in poly.loop_indices:
                x, y, z = unity_vertices[mesh.loops[li].vertex_index]
                uv.data[li].uv = ((z,y) if axis == 0 else
                                  ((x,z) if axis == 1 else (x,y)))
        assert len(mesh.vertices) == 288
        assert len(mesh.polygons) == 572
    elif mid == "W01":
        mesh = extrude_polygon([(0,0),(1,0),(1,3),(0,3)], 0, .2, "XY")
    elif mid == "W03":
        # One watertight L-solid; internal and external arms share no volume.
        mesh = extrude_polygon(
            [(-.5,-.5),(.5,-.5),(.5,-.3),(-.3,-.3),(-.3,.5),(-.5,.5)],
            0, 3, "XZ")
    else:
        # One connected U-solid; nominal opening X=.20..1.80, Y=0..2.40.
        mesh = extrude_polygon(
            [(0,0),(.2,0),(.2,2.4),(1.8,2.4),
             (1.8,0),(2,0),(2,3),(0,3)],
            0, .2, "XY")
    mesh.name = mid+"_mesh"
    obj = bpy.data.objects.new(mid+"_"+NAMES[mid], mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(setup_material(mid))
    obj.location = (0,0,0)
    obj.rotation_euler = (0,0,0)
    obj.scale = (1,1,1)
    obj["C01_grid_m"] = 1.0
    obj["C01_source_owner"] = "C01-11"
    obj["C01_contract"] = "PROVISIONAL_until_C01-01_and_C01-13_approval"
    return obj

def audit(mid, obj):
    actual = [blender_to_unity(v.co) for v in obj.data.vertices]
    low = tuple(round(min(v[i] for v in actual), 6) for i in range(3))
    high = tuple(round(max(v[i] for v in actual), 6) for i in range(3))
    expected_low, expected_high = EXPECTED[mid]
    assert low == expected_low and high == expected_high, (mid, low, high)
    assert len(obj.data.uv_layers) == 1
    if mid == "W02":
        # Refuse any future unintended drop of the actual mechanical panel.
        assert len(obj.data.vertices) == 288
        assert sum(len(p.vertices)-2 for p in obj.data.polygons) == 572
    assert tuple(obj.scale) == (1,1,1)
    assert tuple(obj.location) == (0,0,0)
    assert all(p.area > 1e-9 for p in obj.data.polygons), mid
    bm = bmesh.new();bm.from_mesh(obj.data)
    manifold = all(e.is_manifold for e in bm.edges)
    bm.free()
    assert manifold, mid + " is not manifold"
    return {"id":mid, "bounds_min_xyz_m":low,"bounds_max_xyz_m":high,
            "triangles":sum(len(p.vertices)-2 for p in obj.data.polygons),
            "uv_layers":len(obj.data.uv_layers),"manifold":manifold,
            "scale":[1,1,1],"pivot":[0,0,0],"status":"BLENDER_STATIC_PASS"}

def render(mid, obj, view):
    camera_data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera",camera_data)
    bpy.context.collection.objects.link(camera)
    target = Vector((.5,-.1,1.5)) if mid in ("W01","W02") else (
        Vector((0,0,1.5)) if mid=="W03" else Vector((1,-.1,1.5)))
    camera.location = target + {"iso":Vector((4,-6,3)),
                                "front":Vector((0,-7,.5)),
                                "side":Vector((6,-.2,.5))}[view]
    direction=target-camera.location
    camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    camera_data.type="ORTHO";camera_data.ortho_scale=4.7
    scene=bpy.context.scene;scene.camera=camera
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.render.resolution_x=900;scene.render.resolution_y=700
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(PREVIEW / (mid+"_"+view+".png"))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
    bpy.data.cameras.remove(camera_data)

bpy.context.scene.unit_settings.system="METRIC"
bpy.context.scene.unit_settings.scale_length=1.0
results=[]
for mid in ("W01","W02","W03","W04"):
    clean()
    obj=build(mid)
    results.append(audit(mid,obj))
    bpy.context.view_layer.objects.active=obj
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND / (mid+"_"+NAMES[mid]+".blend")))
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(FBX / (mid+"_"+NAMES[mid]+".fbx")),
        use_selection=True,axis_forward="-Z",axis_up="Y",
        apply_unit_scale=True,apply_scale_options="FBX_SCALE_UNITS",
        global_scale=1.0,object_types={"MESH"},add_leaf_bones=False,
        bake_anim=False,use_mesh_modifiers=True,mesh_smooth_type="FACE")
    for view in ("iso","front","side"):
        render(mid,obj,view)
(QA/"blender_static_report.json").write_text(json.dumps(results,indent=2)+"\n")
print("C01-11 PASS17 QA_ONLY native outputs generated; independent C01-02 + Unity gates still required")
