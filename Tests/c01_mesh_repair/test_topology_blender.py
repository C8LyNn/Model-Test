"""Real Blender runtime self-tests of topology_audit.py on GENERATED TEST FIXTURES.

Fixtures are explicitly synthetic test inputs and must never be presented as source production evidence.
Run: blender --background --factory-startup --python Tests/c01_mesh_repair/test_topology_blender.py
"""
import importlib.util
import sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
S=importlib.util.spec_from_file_location("c01_topology",ROOT/"Tools/c01_mesh_repair/topology_audit.py")
mod=importlib.util.module_from_spec(S)
S.loader.exec_module(mod)


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def create(name, verts, faces):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def test_closed_cube():
    clear()
    bpy.ops.mesh.primitive_cube_add(size=1)
    a=mod._mesh_report(bpy.context.object,20)
    assert a["counts"]["vertices"]==8, a
    assert a["counts"]["edges"]==12, a
    assert a["counts"]["faces"]==6, a
    assert a["counts"]["triangles"]==12, a
    assert a["mesh_issues"]["boundary_edges"]==0, a
    assert a["mesh_issues"]["nonmanifold_overconnected_edges"]==0, a
    assert a["mesh_issues"]["degenerate_faces"]==0, a


def test_open_plane_not_force_watertight():
    clear()
    o=create("intentional_open_panel",[(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,2,3)])
    a=mod._mesh_report(o,20)
    assert a["mesh_issues"]["boundary_edges"]==4,a
    assert a["mesh_issues"]["nonmanifold_overconnected_edges"]==0,a
    assert a["counts"]["components"]==[4],a


def test_duplicate_face_candidate():
    clear()
    o=create("coplanar_faces",[(0,0,0),(1,0,0),(0,1,0),
                              (0,0,0),(1,0,0),(0,1,0)],[(0,1,2),(3,4,5)])
    a=mod._mesh_report(o,20)
    assert a["mesh_issues"]["colocated_vertex_candidates"]==3,a
    assert a["mesh_issues"]["duplicate_face_candidates"]==1,a
    assert a["counts"]["components"]==[3,3],a


def test_detect_t_junction():
    clear()
    o=create("tjunction",[(0,0,0),(1,0,0),(0,1,0),(.5,0,0),(.5,.5,0)],
             [(0,1,2),(3,4,2)])
    a=mod._mesh_report(o,20)
    assert a["mesh_issues"]["t_junction_candidates"]>=1,a


def test_loose_and_degenerate():
    clear()
    o=create("loose_and_zero_triangle",[(0,0,0),(1,0,0),(2,0,0),(3,3,3)],[(0,1,2)])
    a=mod._mesh_report(o,20)
    assert a["mesh_issues"]["degenerate_faces"]==1,a
    assert a["mesh_issues"]["loose_vertices"]==1,a


def main():
    count=0
    for name in sorted(x for x in globals() if x.startswith("test_")):
        globals()[name]()
        count+=1
        print("PASS:",name,flush=True)
    print("PASS: %d/%d native Blender fixture tests"%(count,count),flush=True)


if __name__=="__main__":
    main()
