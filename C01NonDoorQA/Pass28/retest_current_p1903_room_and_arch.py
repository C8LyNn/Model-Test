"""C01-13 W28 scoped exact-current-FBX regression, READ ONLY.
Reuse the proven W25/W26 Blender geometry-test algorithms without modifying them.
Only difference is P19-03 new independently STATIC/UV-accepted FBX SHA.
All Claude-delegated door/gate models are strictly excluded.
Run in REAL Blender 4.0 with signed original hydrated FBX files, no export.
"""
import bpy, json, sys, types, hashlib
from pathlib import Path

ROOT=Path(sys.argv[sys.argv.index("--")+1]).resolve()
OUT=ROOT/"C01NonDoorQA"/"Pass28"/"Results"
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_NEW="4a1ad590e79515b0a699f0fb643d9999b4d1726bd68fce97505f401bb8375967"
EXPECTED_OLD="1bd730b2382879d7d9c2f3d67c4b9646b8ca036c04de663e53b3019c403af2df"
NEW_SOURCE=("P19-03","desk","_native/P19-03/Assets/C01InteriorProps/C01-19/Models/P19-03/P19-03.fbx",EXPECTED_NEW)
ORIGINAL_W25=(ROOT/"C01NonDoorQA/Pass25/Results/corrected_non_door_layouts_W25.json")
ORIGINAL_W26=(ROOT/"C01NonDoorQA/Pass26/Results/W26_FBX_W01_F01_NONDOOR_CONTACTS.json")
assert ORIGINAL_W25.is_file() and ORIGINAL_W26.is_file(),"REQUIRE_HISTORICAL_W25_W26_REPORT"
old25=json.loads(ORIGINAL_W25.read_text())
old26=json.loads(ORIGINAL_W26.read_text())
assert next(s for s in old25["source_native"] if s["asset"]=="P19-03")["SHA256_FBX"]==EXPECTED_OLD
assert next(s for s in old26["real_signed_FBX_sources"] if s["id"]=="P19-03")["sha256"]==EXPECTED_OLD
assert old25["summary"]["candidate_room_layouts"]==3
assert old26["summary"]["room_layouts_rechecked"]==3
assert old26["summary"]["actual_W01_strict_crossing_pairs"]==0
def import_old_verified_qa_code(path, name):
    source=path.read_text(encoding="utf-8")
    assert source.rstrip().endswith("main()"), "HISTORIC_MODULE_DRIFT "+name
    module=types.ModuleType(name)
    exec(compile(source[:source.rfind("\nmain()")],str(path),"exec"),module.__dict__)
    return module

room=import_old_verified_qa_code(ROOT/"C01NonDoorQA/Pass25/qa_real_fbx_corrected_layouts.py","W25_existing_verified_methods")
arch=import_old_verified_qa_code(ROOT/"C01NonDoorQA/Pass26/qa_real_mesh_architecture_contacts.py","W26_existing_verified_methods")
assert len(room.m.SOURCES)==3 and len(arch.geo.SOURCES)==3

def replace_only_new_desk(source_list):
    assert [s[0] for s in source_list]==["P17-01","P18-01","P19-03"]
    assert source_list[2][3]==EXPECTED_OLD, "ORIGINAL_SOURCE_MUTATED_NOT_AUTHORIZED"
    return source_list[:2]+[NEW_SOURCE]
room.m.SOURCES=replace_only_new_desk(room.m.SOURCES)
arch.geo.SOURCES=replace_only_new_desk(arch.geo.SOURCES)
room.OUT=OUT/"rooms";room.OUT.mkdir(exist_ok=True,parents=True)
room.m.OUT=room.OUT
arch.OUT=OUT/"architecture";arch.OUT.mkdir(exist_ok=True,parents=True)
arch.geo.OUT=arch.OUT

# Recheck three actual prior placements at new source, physical 3D Blender Workbench.
print("W28_REAL_NEW_FBXS_ROOM_BEGIN",EXPECTED_NEW)
room.main()
print("W28_REAL_NEW_FBXS_ARCH_BEGIN",EXPECTED_NEW)
arch.main()

new25=json.loads((room.OUT/"corrected_non_door_layouts_W25.json").read_text())
new26=json.loads((arch.OUT/"W26_FBX_W01_F01_NONDOOR_CONTACTS.json").read_text())
newp=next(s for s in new25["source_native"] if s["asset"]=="P19-03")
newa=next(s for s in new26["real_signed_FBX_sources"] if s["id"]=="P19-03")
assert newp["SHA256_FBX"]==EXPECTED_NEW and newa["sha256"]==EXPECTED_NEW
assert new25["summary"]["room_bvh_candidate_pairs"]==0
assert new25["summary"]["room_crossing_pairs"]==0
assert new25["summary"]["candidate_room_layouts"]==3
assert new25["summary"]["height_slab_cases"]==9
assert new26["summary"]["real_physical_FBX_sha_pass"]==5
assert new26["summary"]["room_layouts_rechecked"]==3
assert new26["summary"]["actual_W01_strict_crossing_pairs"]==0
assert new26["summary"]["actual_floor_submerged_vertices"]==0
assert new26["summary"]["door_assets_read_or_modified"]==0

compare=[]
for n in range(3):
    oldr=old25["valid_room_layouts"][n]
    newr=new25["valid_room_layouts"][n]
    oldarch=old26["layouts"][n]
    newarch=new26["layouts"][n]
    assert oldr["layout_id"]==newr["layout_id"]==oldarch["layout"]==newarch["layout"]
    assert [(p["asset"],p["world_xz_m"],p["yaw_deg"]) for p in oldr["placement"]]==[
            (p["asset"],p["world_xz_m"],p["yaw_deg"]) for p in newr["placement"]]
    assert oldr["real_FBX_bvh_triangle_pair_candidates"]==newr["real_FBX_bvh_triangle_pair_candidates"]==0
    assert oldr["real_FBX_exact_noncoplanar_triangle_crossings"]==newr["real_FBX_exact_noncoplanar_triangle_crossings"]==0
    widths_old=[v["widest_route_sampled_width_m"] for v in oldr["actual_original_triangle_height_slabs"]]
    widths_new=[v["widest_route_sampled_width_m"] for v in newr["actual_original_triangle_height_slabs"]]
    compare.append({
     "layout_id":newr["layout_id"],
     "placements_unchanged":True,
     "old_mesh_candidate_pairs":oldr["real_FBX_bvh_triangle_pair_candidates"],
     "new_mesh_candidate_pairs":newr["real_FBX_bvh_triangle_pair_candidates"],
     "old_strict_triangle_intersections":oldr["real_FBX_exact_noncoplanar_triangle_crossings"],
     "new_strict_triangle_intersections":newr["real_FBX_exact_noncoplanar_triangle_crossings"],
     "old_real_wall_intersections":oldarch["actual_wall_strict_crossing_pairs"],
     "new_real_wall_intersections":newarch["actual_wall_strict_crossing_pairs"],
     "old_below_floor_vertices":oldarch["actual_floor_submersion_vertices"],
     "new_below_floor_vertices":newarch["actual_floor_submersion_vertices"],
     "old_support_plane_boundary_surface_pairs":oldarch["actual_floor_strict_crossing_pairs"],
     "new_support_plane_boundary_surface_pairs":newarch["actual_floor_strict_crossing_pairs"],
     "old_sampled_full_route_widths_three_height_slabs_m":widths_old,
     "new_sampled_full_route_widths_three_height_slabs_m":widths_new,
     "max_absolute_route_sample_width_drift_m":round(max(abs(a-b) for a,b in zip(widths_old,widths_new)),8)
    })

assets=[{"id":a["asset"],"sha256":a["SHA256_FBX"],"meshes":a["mesh_count"],"triangles":a["triangle_count"]} for a in new25["source_native"]]
assets += [{"id":a["id"],"sha256":a["sha256"],"size_bytes":a["bytes"]} for a in new26["real_signed_FBX_sources"] if a["id"] in ["W01","F01"]]
summary={
 "real_hydrated_original_binary_FBX_sha256_verified":5,
 "changed_model_ids_since_old_spatial_QA":["P19-03"],
 "current_P19_03_sha256":EXPECTED_NEW,
 "old_P19_03_sha256":EXPECTED_OLD,
 "same_three_w25_layouts_retained":3,
 "same_w26_actual_architecture_layouts_retained":3,
 "current_1m_real_W01_wall_instances":16,
 "current_1m_real_F01_floor_instances":16,
 "current_new_source_triangle_BVH_overlap_candidates":sum(x["new_mesh_candidate_pairs"] for x in compare),
 "current_new_source_triangle_surface_intersections":sum(x["new_strict_triangle_intersections"] for x in compare),
 "current_new_source_wall_strict_crossings":sum(x["new_real_wall_intersections"] for x in compare),
 "current_new_source_vertices_below_floor":sum(x["new_below_floor_vertices"] for x in compare),
 "all_nine_vertical_slab_routes_remeasured":9,
 "new_prod_asset_exports":0,"doors_or_gates_read_modified_tested":0,
 "unity_editor":"NOT_RUN","independent_native_static_source":"C01-02_W27_NEW_SHA_STATIC_UV_PASS","independent_visual":"PENDING",
 "owner_min_corridor_width":"OWNER_DECISION_UNDEFINED","merge":False
}
report={
 "schema":"C01-13-W28-CURRENT-NEW-P1903-SCOPED-FBX-ROOM-W01-F01-SPATIAL-REGRESSION-V1",
 "scope":"P19-03 changed SHA only, retain old W25 3 room layouts and actual W26 W01/F01 1m assembly test, physical FBX SHA independently verified in Blender",
 "original_blender_data":"Physical hydrated original P17-01/P18-01 and NEW accepted native P19-03, native W01/F01; no Claude door/gate assets in checkout",
 "source_evidence":assets,"summary":summary,"layout_old_vs_new":compare,
 "original_W25_report":"C01NonDoorQA/Pass25/Results/corrected_non_door_layouts_W25.json",
 "original_W26_report":"C01NonDoorQA/Pass26/Results/W26_FBX_W01_F01_NONDOOR_CONTACTS.json",
 "current_new_source_W28_retest_rooms":"C01NonDoorQA/Pass28/Results/rooms/corrected_non_door_layouts_W25.json",
 "current_new_source_W28_retest_architecture":"C01NonDoorQA/Pass28/Results/architecture/W26_FBX_W01_F01_NONDOOR_CONTACTS.json",
 "prior_W27_dependency_gate":"C01NonDoorQA/Pass27/W27_PROVENANCE_DEPENDENCY_AND_QA_GATE.json",
 "limitations":["Original SHA native Blender source accepted STATIC/UV, but independent visual signoff remains PENDING.",
               "No official corridor or level placement approval; clearances depend on illustrative 0.1m raster and source render meshes.",
               "Expected floor plane support contacts are not physical volume penetrations; no ground penetration based on all vertices >=0.",
               "Solid wall test fixture uses existing W01 and F01 original FBX, no doors, not a full engine scene.",
               "No real Unity Editor, PlayMode, NavMesh, physics colliders, or independently signed C01-02 final release acceptance."],
 "disposition":"CURRENT_NEW_FBX_SPATIAL_REGRESSION_GEOMETRY_PASS__UNITY_NOT_RUN__VISUAL_AND_OWNER_GATES_PENDING"
}
(OUT/"W28_CURRENT_P19_03_SIGNED_SPATIAL_REGRESSION.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("W28_CURRENT_SHA_SCOPED_SPATIAL_REGRESSION",json.dumps(summary))
for r in compare:print("W28_LAYOUT_NEW_SHA",r["layout_id"],r["new_mesh_candidate_pairs"],r["new_real_wall_intersections"],r["new_sampled_full_route_widths_three_height_slabs_m"])
