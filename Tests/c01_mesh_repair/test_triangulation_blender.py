"""Native Blender tests for the C01 PASS04 triangle gate: synthetic fixtures only.

The production QA workflow separately opens REAL producer Blender and binary FBX files.
"""
import importlib.util
from pathlib import Path
import bpy
import bmesh

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("c01_triangle",ROOT/"Tools/c01_mesh_repair/triangulation_gate.py")
gate=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def create(name, vertices, faces):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    uv=mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        for index in polygon.loop_indices:
            co=mesh.vertices[mesh.loops[index].vertex_index].co
            uv.data[index].uv=(co.x,co.y)
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def test_nontriangles_rejected():
    reset()
    bpy.ops.mesh.primitive_cube_add(size=1)
    data=gate.polygon_tessellation(bpy.context.object)
    assert data["non_triangles"]==6,data
    assert data["source_ngons"]==0,data
    assert data["triangles"]==12,data
    assert data["zero_area_triangles"]==0,data


def test_explicit_triangulation_preserves_area_and_uv():
    reset()
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj=bpy.context.object
    old=gate.polygon_tessellation(obj)
    b=bmesh.new()
    b.from_mesh(obj.data)
    bmesh.ops.triangulate(b,faces=list(b.faces),quad_method="BEAUTY",ngon_method="BEAUTY")
    b.to_mesh(obj.data)
    b.free()
    obj.data.update()
    new=gate.polygon_tessellation(obj)
    assert new["non_triangles"]==0,new
    assert new["triangles"]==12,new
    assert new["triangle_missing_or_invalid_uv0"]==0,new
    assert new["reversed_or_inconsistent_triangulation_normals"]==0,new
    assert abs(old["local_surface_area_m2"]-new["local_surface_area_m2"])<1e-6,(old,new)


def test_complex_ngon_detected():
    reset()
    # Concave five-vertex face: Blender may tessellate but exporter may differ.
    obj=create("concave",[(0,0,0),(2,0,0),(2,2,0),(1,.5,0),(0,2,0)],[(0,1,2,3,4)])
    data=gate.polygon_tessellation(obj)
    assert data["source_ngons"]==1,data
    assert data["non_triangles"]==1,data
    assert data["triangles"]==3,data


def test_degenerate_face_detected():
    reset()
    obj=create("degenerate",[(0,0,0),(1,0,0),(2,0,0)],[(0,1,2)])
    data=gate.polygon_tessellation(obj)
    assert data["zero_area_triangles"]==1,data


def test_no_uv_fails_stream():
    reset()
    mesh=bpy.data.meshes.new("NoUV")
    mesh.from_pydata([(0,0,0),(1,0,0),(0,1,0)],[],[(0,1,2)])
    mesh.update()
    obj=bpy.data.objects.new("NoUV",mesh)
    bpy.context.scene.collection.objects.link(obj)
    data=gate.polygon_tessellation(obj)
    assert data["triangle_missing_or_invalid_uv0"]==1,data


if __name__=="__main__":
    tests=sorted(name for name in globals() if name.startswith("test_"))
    for name in tests:
        globals()[name]()
        print("PASS:",name,flush=True)
    print("PASS: %d/%d Blender triangle-gate fixture tests"%(len(tests),len(tests)),flush=True)
