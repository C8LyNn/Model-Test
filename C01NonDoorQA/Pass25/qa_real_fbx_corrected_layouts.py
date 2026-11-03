"""C01-13 W25: Corrected non-door placements from unchanged physical signed FBX.
No imported doors. NOT a real Unity NavMesh or owner-approved walkway threshold.
Uses W24 real-triangle geometric collision and clipping code without running its W24 main().
"""
import bpy, math, csv, heapq, json, sys, types
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(sys.argv[sys.argv.index("--")+1]).resolve()
OUT=ROOT/"C01NonDoorQA"/"Pass25"/"Results"
OUT.mkdir(parents=True,exist_ok=True)
old_script=ROOT/"C01NonDoorQA"/"Pass24"/"qa_real_fbx_multi_nav.py"
old_source=old_script.read_text(encoding="utf-8")
assert old_source.rstrip().endswith("main()"), "W24 CORE CHANGED: FAIL CLOSED"
m=types.ModuleType("w24_real_fbx_triangle_core")
exec(compile(old_source[:old_source.rfind("\nmain()")],str(old_script),"exec"),m.__dict__)
m.OUT=OUT

# Three distinct corrected, actual 1m-snap, 3-asset, 4x4m room layouts.
# Every candidate also has the adjacent 2x4m corridor LEFT EMPTY (no doorway or gate).
# These replace W24 room-center overlapping (458 crossings) / corridor-staggered (711).
LAYOUTS=[
 {"id":"W25_A_UPPER_WALL","placements":[("P17-01",(1,3),0),
                                         ("P18-01",(3,1),90),("P19-03",(3,3),0)]},
 {"id":"W25_B_LOWER_WALL","placements":[("P17-01",(1,1),180),
                                         ("P18-01",(3,3),270),("P19-03",(3,1),0)]},
 {"id":"W25_C_DIAGONAL_WALL","placements":[("P17-01",(1,1),0),
                                            ("P18-01",(1,3),180),("P19-03",(3,3),0)]}
]
SLABS=(0.30,1.00,1.80)
WHAT_IF_M=(0.8,1.0,1.2) # hypothetical; never auto-approve a ship design value
STEP=0.10
ROOM=m.AREAS["ROOM"];CORRIDOR=m.AREAS["CORRIDOR"]

def continuous_lateral_clearance_grid(area,polys):
    """Only lateral fixture walls count as walls for through-route.
    The entering/exiting edge is NOT a physical wall, eliminating W24 0.45m endpoint cap.
    Distance to original FBX clipped triangle polygons (not bounding-box occupancy).
    """
    x0,x1,z0,z1=m.AREAS[area]
    nx=round((x1-x0)/STEP); nz=round((z1-z0)/STEP)
    result=[]
    for iz in range(nz):
        z=z0+(iz+.5)*STEP;row=[]
        for ix in range(nx):
            x=x0+(ix+.5)*STEP
            best=min(z-z0,z1-z) if area=="ROOM" else min(x-x0,x1-x)
            for poly,box in polys:
                if x<box[0]-best or x>box[1]+best or z<box[2]-best or z>box[3]+best:
                    continue
                best=min(best,m.dist_to_poly((x,z),poly))
                if best<=1e-9:break
            row.append(max(0.,best))
        result.append(row)
    return result

def full_span_widest_path(field,area):
    nz=len(field);nx=len(field[0])
    if area=="ROOM":
        starts=[(iz,0) for iz in range(nz)]
        targets={(iz,nx-1) for iz in range(nz)}
    else:
        starts=[(0,ix) for ix in range(nx)]
        targets={(nz-1,ix) for ix in range(nx)}
    heap=[];scores={};parent={}
    for node in starts:
        value=field[node[0]][node[1]]
        if value<=1e-8:continue
        scores[node]=value;parent[node]=None
        heapq.heappush(heap,(-value,node))
    goal=None
    while heap:
        neg,node=heapq.heappop(heap);score=-neg
        if score<scores[node]-1e-10:continue
        if node in targets:
            goal=node;break
        iz,ix=node
        for dz,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            j=iz+dz;i=ix+dx
            if not (0<=j<nz and 0<=i<nx):continue
            s=min(score,field[j][i])
            if s>scores.get((j,i),0.)+1e-12:
                scores[(j,i)]=s;parent[(j,i)]=node
                heapq.heappush(heap,(-s,(j,i)))
    if goal is None:return 0.0,[]
    route=[];cursor=goal
    while cursor is not None:
        iz,ix=cursor
        route.append((m.AREAS[area][0]+(ix+.5)*STEP,
                      m.AREAS[area][2]+(iz+.5)*STEP))
        cursor=parent[cursor]
    route.reverse()
    return scores[goal],route

def probe_layout(objects,area):
    rows=[]
    for slab in SLABS:
        polys=[q for ob in objects for q in m.footprints(ob["tris"],slab)]
        field=continuous_lateral_clearance_grid(area,polys)
        radius,route=full_span_widest_path(field,area)
        diameter=2*radius
        center=m.centerline_probe(area,polys)
        what_if={f"{t:.1f}m":{"illustrative_meets_this_width":bool(diameter+1e-8>=t),
                              "approved_minimum":False} for t in WHAT_IF_M}
        rows.append({"height_slab_y_m":[0,slab],"polygon_count":len(polys),
                     "widest_route_radius_m":round(radius,5),
                     "widest_route_sampled_width_m":round(diameter,5),
                     "route_sample_count":len(route),
                     "route_xz_m":[[round(x,3),round(z,3)] for x,z in route],
                     "centerline":center,"illustrative_width_comparisons":what_if,
                     "clearance_algorithm":"0.1m 4-neighbor widest route, original FBX triangles clipped to Y slab; ONLY lateral fixture walls constrain through-route; open ends are not walls; NOT Unity PhysX/NavMesh."})
    return rows

def make_objects(assets,spec):
    objects=[]
    for aid,anchor,yaw in spec:
        assert aid in assets and all(round(q)==q for q in anchor)
        assert yaw in (0,90,180,270)
        source=assets[aid]
        objects.append({"id":aid,"sha256":source["sha256"],
           "anchor_xz_m":list(anchor),"yaw_deg":yaw,"tris":m.moved(source,anchor,yaw)})
    return objects

def real_blender_workbench_render(layout,assets):
    """Re-import original SHA-checked FBX into transient scene, preserve mesh/UV/normals.
    Only apply temporary world placement to Blender objects. No new models exported.
    """
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for aid,anchor,yaw in layout["placements"]:
        item=next(s for s in m.SOURCES if s[0]==aid)
        path=ROOT/item[2]
        prior={o.name for o in bpy.context.scene.objects}
        bpy.ops.import_scene.fbx(filepath=str(path),use_custom_normals=True)
        bpy.context.view_layer.update()
        imported=[o for o in bpy.context.scene.objects if o.name not in prior and o.type=="MESH"]
        assert imported, "NO_ORIGINAL_FBX_RENDER_GEOMETRY "+aid
        T=Matrix.Translation(Vector((anchor[0],-anchor[1],-assets[aid]["source_floor_y_m"])))
        R=Matrix.Rotation(-math.radians(yaw),4,"Z")
        for ob in imported:
            orig=ob.matrix_world.copy()
            ob.parent=None
            ob.matrix_world=T@R@orig
            if aid=="P17-01":ob.color=(0.17,0.48,0.70,1.)
            elif aid=="P18-01":ob.color=(0.83,0.54,0.17,1.)
            else:ob.color=(0.53,0.40,0.70,1.)
    camdata=bpy.data.cameras.new("QA_ISO_CAMERA")
    cam=bpy.data.objects.new("QA_ISO_CAMERA",camdata)
    bpy.context.scene.collection.objects.link(cam)
    cam.location=(7.,-9.,7.5)
    focus=Vector((2.,-2.,0.55))
    cam.rotation_euler=(focus-cam.location).to_track_quat("-Z","Y").to_euler()
    camdata.type="ORTHO";camdata.ortho_scale=8.5
    scene=bpy.context.scene;scene.camera=cam
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="OBJECT"
    scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True
    scene.render.resolution_x=1200;scene.render.resolution_y=800
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(OUT/(layout["id"]+"_ORIGINAL_FBX_Blender_Workbench_3D.png"))
    bpy.ops.render.render(write_still=True)

def main():
    sources={a["id"]:a for a in [m.source_triangle_world(s) for s in m.SOURCES]}
    # Single mathematical empty corridor fixture: NO props in corridor (door-free, 2m wide).
    empty_corridor=probe_layout([],"CORRIDOR")
    assert all(z["widest_route_sampled_width_m"]>1.8 for z in empty_corridor)
    all_layouts=[];csvrows=[]
    for layout in LAYOUTS:
        objects=make_objects(sources,layout["placements"])
        pair_results=m.true_mesh_pairs(objects)
        boundary=m.wall_bounds(objects,"ROOM")
        bvh=sum(pair["bvh_triangle_candidates"] for pair in pair_results)
        crossings=sum(pair["exact_non_coplanar_surface_crossing_pairs"] for pair in pair_results)
        out=sum(x["out_of_fixture_source_vertices"] for x in boundary)
        # Strict conservative candidate: NO face-pair BVH contact of any kind, NO boundary overflow.
        assert bvh==0 and crossings==0 and out==0,(layout["id"],bvh,crossings,out)
        slabs=probe_layout(objects,"ROOM")
        assert len(slabs)==3 and all(z["widest_route_sampled_width_m"]>=0.8 for z in slabs),layout["id"]
        comparison={"original_invalid_W24_fixture":"ROOM_CENTER_CROWDED_3",
                    "original_actual_triangle_cross_pairs":458,
                    "corrected_actual_triangle_cross_pairs":crossings,
                    "improvement_in_surface_crossings":458-crossings}
        data={"layout_id":layout["id"],"area":"ROOM",
          "placement":[{"asset":ob["id"],"world_xz_m":ob["anchor_xz_m"],"world_y_m":0,
                        "yaw_deg":ob["yaw_deg"],"FBX_SHA256":ob["sha256"]} for ob in objects],
          "real_FBX_bvh_triangle_pair_candidates":bvh,
          "real_FBX_exact_noncoplanar_triangle_crossings":crossings,
          "triangle_pair_collision_proof":pair_results,
          "wall_contact_and_bounds":boundary,
          "actual_original_triangle_height_slabs":slabs,
          "corridor_fixture":"NO_OBJECTS_IN_CENTERLINE__EMPTY_2m_WIDE__MEASURED_SEPARATELY",
          "reference_bad_layout_before_after":comparison,
          "verdict":"CANDIDATE_NONOVERLAP_MEASURED__CLEARANCE_THRESHOLD_NOT_APPROVED"}
        all_layouts.append(data)
        m.svg_image(layout["id"]+"_actual_FBX_TOP_WIREFRAME",objects,"ROOM",slabs[-1]["route_xz_m"],1.8)
        m.svg_image(layout["id"]+"_actual_FBX_ISO_WIREFRAME",objects,"ROOM",[],1.8,True)
        # Physically rendered shaded 3D using the SAME original FBX authoring normals, not proxy shapes.
        real_blender_workbench_render(layout,sources)
        for z in slabs:
            csvrows.append({"layout":layout["id"],"height_to_m":z["height_slab_y_m"][1],
                 "room_route_width_m":z["widest_route_sampled_width_m"],
                 "centerline_blocked_sample_count":z["centerline"]["sampled_occupied_centers"],
                 "width_0_8m_whatif":z["illustrative_width_comparisons"]["0.8m"]["illustrative_meets_this_width"],
                 "width_1_0m_whatif":z["illustrative_width_comparisons"]["1.0m"]["illustrative_meets_this_width"],
                 "width_1_2m_whatif":z["illustrative_width_comparisons"]["1.2m"]["illustrative_meets_this_width"],
                 "real_triangle_bvh_pairs":bvh,"real_surface_crossing_pairs":crossings})
        print("W25_REAL_VALID_LAYOUT",layout["id"],"BVH",bvh,"CROSS",crossings,"OUTSIDE",out,
              "WIDTHS",[x["widest_route_sampled_width_m"] for x in slabs])
    # Empty corridor line free and proof no fabricated external objects; render analytical plan from real room geometry.
    corridor_comparison={
      "old_W24_example":"CORRIDOR_STAGGERED_CROWDED_3",
      "old_actual_triangle_crossing_pairs":711,
      "corrected_room_storage":"All three existing FBX located in room layout, NO standalone corridor props",
      "current_corridor_triangle_pairs":0,
      "current_corridor_centerline_occupied_samples":0,
      "corridor_navigability":empty_corridor,
      "owner_minimum_width":"THRESHOLD_OWNER_DECISION",
      "note":"Empty 2m analytical corridor is deliberate placement recommendation, not a ship scene or doorway test"}
    result={"schema":"C01-13-W25-CORRECTED-REAL-FBX-ROOM-AND-CORRIDOR-1",
      "source_native":[{"asset":a["id"],"SHA256_FBX":a["sha256"],
         "mesh_count":a["mesh_count"],"triangle_count":a["triangle_count"]}
         for a in sources.values()],
      "valid_room_layouts":all_layouts,
      "corridor_comparison":corridor_comparison,
      "sampled_vertical_slabs_max_y_m":SLABS,
      "sampling_grid_m":STEP,
      "hypothetical_width_options_m":WHAT_IF_M,
      "recommend_owner_default_m":1.0,
      "owner_default_is_approved":False,
      "owner_approval_request":"Approve or reject minimum unobstructed walkable width 1.0m for room circulation and 2m corridors; 0.8m and 1.2m shown as what-if alternatives only. Keep all freestanding props out of corridor until policy approved.",
      "limits":["W25 fixes W24 end-wall endpoint clipping by treating through-route ends as OPEN, not as physical walls.",
                "Triangle surface BVH 0 pairs is strong nonoverlap witness; not a physics collider test.",
                "Paths are sampled 0.1m and original render triangle footprint includes overhang; not Unity NavMesh.",
                "Room and corridor separate analytic polygons, not an authored ship scene or door clearance.",
                "Source .blend, FBX, producer pivots/UV/normals and ALL door assets unchanged."],
      "summary":{"candidate_room_layouts":len(all_layouts),"signed_current_original_FBX":len(sources),
        "room_crossing_pairs":sum(x["real_FBX_exact_noncoplanar_triangle_crossings"] for x in all_layouts),
        "room_bvh_candidate_pairs":sum(x["real_FBX_bvh_triangle_pair_candidates"] for x in all_layouts),
        "room_outside_fixture_vertices":0,
        "height_slab_cases":len(csvrows),"corridor_empty":True,
        "unity_editor":"NOT_RUN","navmesh":"NOT_RUN","doors_touched":0,"producer_files_changed":0,
        "merge":False},
      "release":"THREE_VALID_NONOVERLAP_CANDIDATES__DESIGN_THRESHOLD_OWNER_DECISION__UNITY_NOT_RUN"}
    (OUT/"corrected_non_door_layouts_W25.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    with open(OUT/"corrected_non_door_layouts_W25.csv","w",newline="",encoding="utf-8") as f:
        fields=list(csvrows[0].keys());w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader();w.writerows(csvrows)
    print("W25_FINAL",json.dumps(result["summary"]))
    for i in result["source_native"]:print("SIGNED_FULL_BINARY_FBX",i["asset"],i["SHA256_FBX"])

main()
