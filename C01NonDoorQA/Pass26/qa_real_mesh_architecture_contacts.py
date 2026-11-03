"""C01-13 W26 — real signed non-door props versus actual F01 floor and W01 solid wall meshes.
Scoped read-only instance placement QA; NO doors/gates, NO live ship modifications.
Real Blender 4 FBX import, full SHA byte-match, no source geometry edits.
Replay: blender -b --factory-startup --python-exit-code 1 --python this_file -- ROOT
"""
import bpy, sys, json, csv, hashlib, math, types, itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(sys.argv[sys.argv.index("--")+1]).resolve()
OUT=ROOT/"C01NonDoorQA"/"Pass26"/"Results"
OUT.mkdir(parents=True,exist_ok=True)
baseline=ROOT/"C01NonDoorQA"/"Pass24"/"qa_real_fbx_multi_nav.py"
base_src=baseline.read_text(encoding="utf-8")
assert base_src.rstrip().endswith("main()"), "PASS24_FBX_GEOMETRY_CORE_UNEXPECTED"
geo=types.ModuleType("realFBX_geometry_core")
exec(compile(base_src[:base_src.rfind("\nmain()")],str(baseline),"exec"),geo.__dict__)
APPEND=[
 ("W01","wall","_arch/W01/Assets/C01Architecture/Walls_W01_W04/FBX/W01_FULL_WALL_1M.fbx",
  "4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f"),
 ("F01","floor","_arch/F01/C01StandaloneKits/FloorCeiling/DetailPass17/FBX/C01_SHI_F01_FLOOR_BASIC_v004.fbx",
  "46acac987ca3f8387472b2dc8b611cd871c90cd3e7d4773568c9005c84cb5c09")
]
LAYOUTS=[
 ("W25_A_UPPER_WALL",[("P17-01",(1,3),0),("P18-01",(3,1),90),("P19-03",(3,3),0)]),
 ("W25_B_LOWER_WALL",[("P17-01",(1,1),180),("P18-01",(3,3),270),("P19-03",(3,1),0)]),
 ("W25_C_DIAGONAL_WALL",[("P17-01",(1,1),0),("P18-01",(1,3),180),("P19-03",(3,3),0)])
]
def extents(tris):
    v=[p for t in tris for p in t]
    return [[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)]
def actual_move(tris,anchor,yaw=0):
    """World-space instance transform of ORIGINAL Blender-imported FBX triangle positions."""
    ang=math.radians(yaw);c=round(math.cos(ang),14);s=round(math.sin(ang),14)
    x0,z0=anchor
    return [[(x0+c*x-s*z,y,z0+s*x+c*z) for x,y,z in face] for face in tris]
def combine_parts(parts):
    return [t for tr in parts for t in tr]
def signed_sha(asset):
    path=ROOT/asset[2]
    if not path.is_file():raise AssertionError("MISSING_PHYSICAL_FBX "+str(path))
    data=path.read_bytes()
    if not data.startswith(b"Kaydara FBX Binary"):raise AssertionError("LFS_POINTER_NOT_HYDRATED "+str(path))
    measured=hashlib.sha256(data).hexdigest()
    if measured!=asset[3]:raise AssertionError("CURRENT_NATIVE_SHA_MISMATCH "+asset[0]+" "+measured)
    return {"id":asset[0],"sha256":measured,"bytes":len(data)}
def aligned_box(actual,wanted,epsilon=2e-3):
    return all(abs(actual[k][i]-wanted[k][i])<=epsilon for k in range(3) for i in range(2))
def surface_witness(first,second):
    """BVH candidate count + proven NONCOPLANAR triangle segment intersection count.
    Coplanar intentional bearing / support at y=0 not erroneously declared a penetration.
    """
    cand=geo.bvh(first).overlap(geo.bvh(second))
    proved=[]
    for a,b in cand:
        xyz=geo.triangle_cross(first[a],second[b])
        if xyz is not None:proved.append({"triangle_a":a,"triangle_b":b,"xyz":[round(t,6) for t in xyz]})
    return {"bvh_candidates":len(cand),"strict_surface_crossing_pairs":len(proved),
            "witnesses":proved[:10],"unresolved_candidates":len(cand)-len(proved)}
def build_architecture(wall,floor):
    b1=extents(wall["tris"]);b2=extents(floor["tris"])
    if not aligned_box(b1,[[0,1],[0,3],[0,.2]]):
        raise AssertionError("W01_REAL_FBX_BOUNDS_DIFFER_FROM_MODULE_CONTRACT "+str(b1))
    if not aligned_box(b2,[[0,1],[-.2,0],[0,1]]):
        raise AssertionError("F01_REAL_FBX_BOUNDS_DIFFER_FROM_MODULE_CONTRACT "+str(b2))
    # Four sides made ONLY of W01: no doorway mesh, no gate geometry, no functional doors.
    copies=[]
    for i in range(4):
        copies.extend([
            actual_move(wall["tris"],(i,-.2),0),
            actual_move(wall["tris"],(i,4),0),
            actual_move(wall["tris"],(0,i),90),
            actual_move(wall["tris"],(4,i+1),270)
        ])
    floors=[actual_move(floor["tris"],(x,z),0) for x in range(4) for z in range(4)]
    wbounds=[extents(x) for x in copies]
    fbounds=[extents(x) for x in floors]
    wall_volume_within=(all(
        (abs(box[0][0]+.2)<2e-3 or abs(box[0][1]-4.2)<2e-3
         or abs(box[2][0]+.2)<2e-3 or abs(box[2][1]-4.2)<2e-3)
        for box in wbounds))
    if not wall_volume_within:raise AssertionError("W01_TILED_WALL_NOT_AT_EXPECTED_BOUNDARY")
    assert len(copies)==16 and len(floors)==16
    return {"wall_instances":copies,"floor_instances":floors,
       "walls_combined":combine_parts(copies),
       "floors_combined":combine_parts(floors),
       "source_bounds":{"W01":b1,"F01":b2},
       "fixture_wall_bboxes":wbounds,"fixture_floor_bboxes":fbounds}
def snap_check(arch):
    # Actual 4x4 tiling produces the original (unscaled) 1m physical extents.
    floor=arch["fixture_floor_bboxes"]
    center=[(int(round(x[0][0])),int(round(x[2][0]))) for x in floor]
    if len(set(center))!=16:raise AssertionError("F01_TILE_DUPLICATE_ROOTS")
    if set(center)!={(i,j) for i in range(4) for j in range(4)}:
        raise AssertionError("F01_NON_INTEGRAL_1M_SOURCE_MODULES")
    for b in floor:
        if abs(b[0][1]-b[0][0]-1)>0.002 or abs(b[2][1]-b[2][0]-1)>0.002:
            raise AssertionError("F01_MESH_DIMENSIONS_WRONG")
        if abs(b[1][1])>.002:raise AssertionError("F01_SURFACE_NOT_Y0")
    return {"grid_m":1,"real_F01_tiles":16,"real_W01_tiles":16,
            "floor_gap_positions_between_1m_tiles":0,"world_floor_top_y_m":0,
            "evidence":"Actual imported 1x1m floor tile dimension & world boxes, not geometry weld or union."}
def test_layout(name,spec,assets,arch):
    measurements=[]
    for aid,anchor,yaw in spec:
        tri=geo.moved(assets[aid],anchor,yaw)
        # Cross W01 actual wall 16 modules as a whole, unchanged original source triangles.
        wall=surface_witness(tri,arch["walls_combined"])
        floor=surface_witness(tri,arch["floors_combined"])
        v=[p for t in tri for p in t]
        bottom=min(p[1] for p in v)
        below=sum(p[1]<-1e-5 for p in v)
        b=extents(tri)
        # Deliberate zero-height contact with actual floor is correct.
        measurements.append({
          "asset":aid,"anchor":[anchor[0],0,anchor[1]],"yaw":yaw,
          "real_FBX_sha256":assets[aid]["sha256"],
          "bounds_m":b,
          "bottom_to_real_F01_top_m":round(bottom,7),
          "below_floor_vertices":below,
          "W01_walls_actual_triangle":wall,
          "F01_floor_actual_triangle":floor,
          "actual_floor_contacts_are_allowed":True
        })
    wallcross=sum(t["W01_walls_actual_triangle"]["strict_surface_crossing_pairs"] for t in measurements)
    floorcross=sum(t["F01_floor_actual_triangle"]["strict_surface_crossing_pairs"] for t in measurements)
    return {"layout":name,"model_results":measurements,
       "actual_wall_strict_crossing_pairs":wallcross,
       "actual_floor_strict_crossing_pairs":floorcross,
       "actual_floor_submersion_vertices":sum(x["below_floor_vertices"] for x in measurements),
       "disposition":"ARCH_INTERFERENCE_WITNESS_REVIEW" if wallcross or floorcross else "MEASURED_REAL_ARCH_WALL_AND_FLOOR_CLEAR"}

def main():
    selected=geo.SOURCES+APPEND
    signed=[signed_sha(a) for a in selected]
    # Preserve original source FBX and primitive pivot transforms; no authoring edits.
    objects={a["id"]:a for a in [geo.source_triangle_world(q) for q in selected]}
    arch=build_architecture(objects["W01"],objects["F01"])
    tiling=snap_check(arch)
    out=[test_layout(name,spec,objects,arch) for name,spec in LAYOUTS]
    report={"schema":"C01-13-W26-REAL-FBX-PROP-VS-REAL-W01-F01-1",
      "real_signed_FBX_sources":signed,
      "source_geometry_counts":[{"id":q["id"],"meshes":q["mesh_count"],"tris":q["triangle_count"]}
                                for q in objects.values()],
      "module_signature_and_1m_tiling":tiling,
      "source_architecture_bounds":arch["source_bounds"],
      "analytical_scene":"existing 3 non-door FBX in 4x4m room with 16 physical W01 full-wall modules and 16 physical F01 floor tiles; no doors/openings created or touched",
      "layouts":out,
      "limits":["Only canonical P17-01/P18-01/P19-03 placement candidates, NOT entire 36-model production QA.",
         "W01/F01 are genuine existing assets outside 36, with exact pinned native FBX SHA.",
         "A 4x4 wall-ring is a QA test fixture, NOT a claim about complete ship layout or door clearance.",
         "Genuine intentional coplanar floor support is NOT an unwanted intersection.",
         "Strict noncoplanar triangle crossing cannot rule out all co-planar z-fighting or containment.",
         "This is read-only Blender FBX placement QA, not final C01-02 release, Unity physics, NavMesh or PlayMode."],
      "summary":{"real_physical_FBX_sha_pass":len(signed),"original_F01_instances":16,
         "original_W01_instances":16,"room_layouts_rechecked":len(out),
         "actual_W01_strict_crossing_pairs":sum(a["actual_wall_strict_crossing_pairs"] for a in out),
         "actual_F01_strict_crossing_pairs":sum(a["actual_floor_strict_crossing_pairs"] for a in out),
         "actual_floor_submerged_vertices":sum(a["actual_floor_submersion_vertices"] for a in out),
         "door_assets_read_or_modified":0,
         "producer_sources_changed":0,"unity6_editor":"NOT_RUN",
         "independent_c01_02_release":"PENDING","merge":False},
      "status":"REAL_NONDOOR_ARCHITECTURE_CONTACT_AUDIT__UNITY_NOT_RUN__OWNER_QA_PENDING"}
    (OUT/"W26_FBX_W01_F01_NONDOOR_CONTACTS.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    fields=["layout","asset","floor_gap_m","vertices_below_floor","wall_bvh",
      "wall_cross","floor_bvh","floor_cross","status"]
    with (OUT/"W26_FBX_W01_F01_NONDOOR_CONTACTS.csv").open("w",newline="",encoding="utf-8") as stream:
        wr=csv.DictWriter(stream,fieldnames=fields);wr.writeheader()
        for scene in out:
            for q in scene["model_results"]:
                wr.writerow({"layout":scene["layout"],"asset":q["asset"],
                   "floor_gap_m":q["bottom_to_real_F01_top_m"],
                   "vertices_below_floor":q["below_floor_vertices"],
                   "wall_bvh":q["W01_walls_actual_triangle"]["bvh_candidates"],
                   "wall_cross":q["W01_walls_actual_triangle"]["strict_surface_crossing_pairs"],
                   "floor_bvh":q["F01_floor_actual_triangle"]["bvh_candidates"],
                   "floor_cross":q["F01_floor_actual_triangle"]["strict_surface_crossing_pairs"],
                   "status":scene["disposition"]})
    for q in signed:print("W26_SIGNED_PHYSICAL_FBX_PASS",q["id"],q["sha256"],q["bytes"])
    for q in out:
        print("W26_ACTUAL_ARCH_SCENE",q["layout"],
              "WALL_CROSS",q["actual_wall_strict_crossing_pairs"],
              "FLOOR_CROSS",q["actual_floor_strict_crossing_pairs"],
              "BELOW_FLOOR_VERTICES",q["actual_floor_submersion_vertices"])
    print("W26_ACTUAL_ARCH_SUMMARY",json.dumps(report["summary"]))

main()
