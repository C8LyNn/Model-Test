"""C01-13 PASS24: NON-DOOR physical FBX multi-prop clearance and sampled navigation.
Input mesh triangles only: real Blender FBX import at 3 immutable SHAs.
Example room/corridor are ANALYTICAL fixtures, not live ship, prefab, or NavMesh.
No door assets, no geometry rewrites, no inventing mandatory passage widths.
Run: blender -b --factory-startup --python-exit-code 1 --python this_file -- ROOT
"""
import bpy, math, hashlib, json, csv, sys, heapq, itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(sys.argv[sys.argv.index("--")+1]).resolve()
OUT=ROOT/"C01NonDoorQA"/"Pass24"/"Results"
OUT.mkdir(parents=True,exist_ok=True)
SOURCES=[
 ("P17-01","console","_native/P17-01/Assets/C01InteriorProps/Models/P17-01.fbx","cd6a5787bb7b4c088f0af35382385e4274c85c415c60467f9a22e46fe33ef02c"),
 ("P18-01","crate","_native/P18-01/Assets/C01InteriorProps/C01-18/Models/P18-01.fbx","f541d502ba9eaaf5c7a0a7279c44f71f36dd482e3aed3ba0734058dcf1045f6c"),
 ("P19-03","desk","_native/P19-03/Assets/C01InteriorProps/C01-19/Models/P19-03/P19-03.fbx","1bd730b2382879d7d9c2f3d67c4b9646b8ca036c04de663e53b3019c403af2df")
]
COLORS={"P17-01":"#227ba5","P18-01":"#d18b28","P19-03":"#8667b3"}
AREAS={"ROOM":(0.,4.,0.,4.),"CORRIDOR":(1.,3.,4.,8.)}
# Example probes, not design threshold. Same geometry sampled through these height slabs.
SLABS=[0.30,1.00,1.80]
PROBE_RADII_M=[0.10,0.20,0.35]
GRID_STEP_M=0.10
# Every placement anchor XZ is on the actual 1m module grid. No doors/openings.
LAYOUTS=[
 {"id":"ROOM_WALL_ADJACENT_3","area":"ROOM",
  "placements":[("P17-01",(1,3),90),("P18-01",(2,1),0),("P19-03",(3,3),90)]},
 {"id":"ROOM_CENTER_CROWDED_3","area":"ROOM",
  "placements":[("P17-01",(1,2),0),("P18-01",(2,2),0),("P19-03",(3,2),0)]},
 {"id":"CORRIDOR_TWO_SEQUENTIAL_2","area":"CORRIDOR",
  "placements":[("P17-01",(2,5),90),("P19-03",(2,7),90)]},
 {"id":"CORRIDOR_STAGGERED_CROWDED_3","area":"CORRIDOR",
  "placements":[("P17-01",(2,5),90),("P18-01",(2,6),0),("P19-03",(2,7),90)]},
 {"id":"CORRIDOR_CENTRAL_SIDE_GAPS_2","area":"CORRIDOR",
  "placements":[("P17-01",(2,5),0),("P19-03",(2,7),0)]}
]

def sha256(file):
    h=hashlib.sha256()
    with open(file,"rb") as f:
        for chunk in iter(lambda:f.read(2**20),b""):h.update(chunk)
    return h.hexdigest()

def source_triangle_world(asset):
    aid,kind,relative,expected=asset
    f=ROOT/relative
    if not f.is_file():raise RuntimeError("MISSING_FBX "+str(f))
    with open(f,"rb") as fh:
        if not fh.read(23).startswith(b"Kaydara FBX Binary"):
            raise RuntimeError("NOT_HYDRATED_BINARY_FBX "+str(f))
    real=sha256(f)
    if real!=expected:raise RuntimeError("SHA256_MISMATCH "+aid+" "+real)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(f),use_custom_normals=True)
    bpy.context.view_layer.update()
    tris=[];number=0
    for ob in bpy.context.scene.objects:
        if ob.type!="MESH":continue
        number+=1
        if not ob.data.uv_layers:raise RuntimeError("MISSING_UV0 "+aid+" "+ob.name)
        ob.data.calc_loop_triangles()
        for face in ob.data.loop_triangles:
            v=[ob.matrix_world @ ob.data.vertices[i].co for i in face.vertices]
            points=[(float(p.x),float(p.z),-float(p.y)) for p in v] # Blender Z-up to Unity Y-up
            a,b,c=map(Vector,points)
            if (b-a).cross(c-a).length<1e-9:raise RuntimeError("DEGENERATE_REAL_FBX_TRI "+aid)
            tris.append(points)
    if not number:raise RuntimeError("NO_FBX_MESH "+aid)
    floor=min(v[1] for t in tris for v in t)
    return {"id":aid,"type":kind,"sha256":real,"mesh_count":number,
            "triangle_count":len(tris),"source_floor_y_m":floor,"tris":tris}

def moved(asset,anchor,yaw):
    angle=math.radians(yaw);c=round(math.cos(angle),14);s=round(math.sin(angle),14)
    x0,z0=anchor;floor=asset["source_floor_y_m"]
    return [[(x0+c*x-s*z,y-floor,z0+s*x+c*z) for x,y,z in face] for face in asset["tris"]]

def clip3(poly,axis,bound,keep_greater):
    if not poly:return []
    sign=1 if keep_greater else -1
    dist=lambda p:sign*(p[axis]-bound)
    out=[]
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]; da=dist(a);db=dist(b)
        if da>=-1e-10:out.append(a)
        if (da < -1e-10 < db) or (db < -1e-10 < da):
            t=da/(da-db)
            out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(3)))
    return out

def footprints(tris,max_y):
    out=[]
    for t in tris:
        if min(p[1] for p in t)>max_y+1e-8:continue
        p=clip3(t,1,0.,True)
        p=clip3(p,1,max_y,False)
        if len(p)<2:continue
        poly=tuple((v[0],v[2]) for v in p)
        out.append((poly,(min(q[0] for q in poly),max(q[0] for q in poly),
                          min(q[1] for q in poly),max(q[1] for q in poly))))
    return out

def inside_2d(poly,p):
    # Winding-independent ray crossing; degenerate line triangles handled by distances.
    inside=False
    x,y=p
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]
        if (a[1]>y)!=(b[1]>y):
            xin=a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1])
            if xin>=x:inside=not inside
    return inside

def dist_to_segment(p,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
    t=max(0.,min(1.,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den>1e-22 else 0.
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def dist_to_poly(p,poly):
    if len(poly)>=3 and inside_2d(poly,p):return 0.
    return min(dist_to_segment(p,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))

def clearance_grid(area,fp):
    x0,x1,z0,z1=AREAS[area]; step=GRID_STEP_M
    nx=round((x1-x0)/step);nz=round((z1-z0)/step)
    field=[]
    for iz in range(nz):
        row=[]
        z=z0+(iz+.5)*step
        for ix in range(nx):
            x=x0+(ix+.5)*step
            best=min(x-x0,x1-x,z-z0,z1-z)
            for poly,b in fp:
                if x<b[0]-best or x>b[1]+best or z<b[2]-best or z>b[3]+best:continue
                best=min(best,dist_to_poly((x,z),poly))
                if best<1e-8:break
            row.append(max(0.,best))
        field.append(row)
    return field

def centerline_probe(area,footprints_at_height):
    """Independent straight walking-centerline obstruction check on REAL triangle projections.
    It is not the alternative-route result and is not an approved agent width.
    """
    x0,x1,z0,z1=AREAS[area]
    # Sample only the matching interior start-to-goal section, not the walls themselves.
    start=0.5;length=(x1-x0-1.) if area=="ROOM" else (z1-z0-1.)
    n=int(round(length/.05))+1
    hits=[]
    for i in range(n):
        along=start+i*length/(n-1)
        x,z=(x0+along,(z0+z1)/2.) if area=="ROOM" else ((x0+x1)/2.,z0+along)
        for poly,box in footprints_at_height:
            if box[0]-1e-8<=x<=box[1]+1e-8 and box[2]-1e-8<=z<=box[3]+1e-8:
                if dist_to_poly((x,z),poly)<=1e-8:
                    hits.append((x,z));break
    return {"sample_step_m":0.05,"sample_count":n,
        "sampled_occupied_centers":len(hits),
        "centerline_geometrically_free_at_sample_points":len(hits)==0,
        "occupied_sample_points_xz_m":[[round(x,4),round(z,4)] for x,z in hits[:10]],
        "description":"Straight centerline independently tested against actual 0..height FBX triangle projections; not the route-around-object result."}

def widest_path(field,area):
    nz=len(field);nx=len(field[0])
    # Analytical planes half a metre inside the fixture; no door/opening assumptions.
    if area=="ROOM":
        sources=[(iz,4) for iz in range(nz)]
        targets={(iz,nx-5) for iz in range(nz)}
    else:
        sources=[(4,ix) for ix in range(nx)]
        targets={(nz-5,ix) for ix in range(nx)}
    best={};parent={};heap=[]
    for iz,ix in sources:
        if field[iz][ix]<=0:continue
        value=field[iz][ix];node=(iz,ix)
        best[node]=value;parent[node]=None
        heapq.heappush(heap,(-value,node))
    reached=None
    while heap:
        neg,node=heapq.heappop(heap);value=-neg
        if value<best[node]-1e-10:continue
        if node in targets:
            reached=node;break
        iz,ix=node
        for dz,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            j=iz+dz;i=ix+dx
            if not 0<=j<nz or not 0<=i<nx:continue
            cand=min(value,field[j][i])
            if cand>best.get((j,i),0.)+1e-12:
                best[(j,i)]=cand;parent[(j,i)]=node
                heapq.heappush(heap,(-cand,(j,i)))
    if reached is None:return 0.,[]
    nodes=[];p=reached
    while p is not None:
        nodes.append(p);p=parent[p]
    nodes.reverse()
    x0,x1,z0,z1=AREAS[area]
    return best[reached],[(x0+(ix+.5)*GRID_STEP_M,z0+(iz+.5)*GRID_STEP_M) for iz,ix in nodes]

def bvh(tris):
    return BVHTree.FromPolygons(
        [Vector(p) for tri in tris for p in tri],
        [(3*i,3*i+1,3*i+2) for i in range(len(tris))],
        all_triangles=True,epsilon=1e-8)

def segment_triangle_hit(p0,p1,tri,eps=1e-8):
    a,b,c=map(Vector,tri)
    start=Vector(p0);direction=Vector(p1)-start
    e1=b-a;e2=c-a
    h=direction.cross(e2);det=e1.dot(h)
    if abs(det)<eps:return None # Coplanar contact not certified by this method.
    inv=1./det;s=start-a
    u=inv*s.dot(h)
    if u<-eps or u>1+eps:return None
    q=s.cross(e1);v=inv*direction.dot(q)
    if v<-eps or u+v>1+eps:return None
    t=inv*e2.dot(q)
    if eps<t<1-eps:return tuple(start+t*direction)
    return None

def triangle_cross(a,b):
    for tri,other in ((a,b),(b,a)):
        for i in range(3):
            witness=segment_triangle_hit(tri[i],tri[(i+1)%3],other)
            if witness is not None:return witness
    return None

def true_mesh_pairs(objects):
    results=[]
    for a,b in itertools.combinations(objects,2):
        t1=a["tris"];t2=b["tris"]
        candidates=bvh(t1).overlap(bvh(t2))
        witnesses=[]
        for i,j in candidates:
            hit=triangle_cross(t1[i],t2[j])
            if hit is not None:
                witnesses.append({"triangle_a":i,"triangle_b":j,
                    "xyz_m":[round(v,6) for v in hit]})
        results.append({"asset_a":a["id"],"asset_b":b["id"],
            "bvh_triangle_candidates":len(candidates),
            "exact_non_coplanar_surface_crossing_pairs":len(witnesses),
            "witnesses_xyz_m":witnesses[:8],
            "unresolved_bvh_candidates":len(candidates)-len(witnesses),
            "caution":"Edge/triangle proper crossings proven; coplanar contacts or full containment not certified."})
    return results

def wall_bounds(objects,area):
    x0,x1,z0,z1=AREAS[area]
    outside=[];ceiling=0.
    for ob in objects:
        pts=[p for t in ob["tris"] for p in t]
        offending=sum(1 for x,y,z in pts if x<x0-1e-6 or x>x1+1e-6 or z<z0-1e-6 or z>z1+1e-6)
        outside.append({"id":ob["id"],"out_of_fixture_source_vertices":offending,
            "min_floor_y_m":round(min(p[1] for p in pts),6),
            "max_height_y_m":round(max(p[1] for p in pts),6),
            "signed_x_wall_m":round(min(p[0]-x0 for p in pts),6),
            "signed_x_other_m":round(min(x1-p[0] for p in pts),6),
            "signed_z_wall_m":round(min(p[2]-z0 for p in pts),6),
            "signed_z_other_m":round(min(z1-p[2] for p in pts),6)})
    return outside

def svg_image(name,objects,area,path,headroom,isometric=False):
    # Renders real FBX triangle projections, plus clearly differentiated QA route.
    x0,x1,z0,z1=AREAS[area]; w=1200;h=800
    if isometric:
        def project(p):
            x,y,z=p
            return (600+(x-z)*94,250+(x+z)*40-y*90)
    else:
        scale=min(145,650/(x1-x0),650/(z1-z0))
        def project(p):
            x,y,z=p
            return (135+(x-x0)*scale,70+(z-z0)*scale)
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">',
           '<rect width="1200" height="800" fill="#fbfcfe"/>',
           '<text x="26" y="30" font-family="sans-serif" font-size="23" fill="#1e293b">C01-13 W24 — '+name+' — actual FBX triangles</text>']
    for x in range(int(x0),int(x1)+1):
        a=project((x,0,z0));b=project((x,0,z1))
        parts.append('<path d="M %.2f,%.2f L %.2f,%.2f" stroke="#d1d5db" stroke-width="1" stroke-dasharray="4,6"/>'%(*a,*b))
    for z in range(int(z0),int(z1)+1):
        a=project((x0,0,z));b=project((x1,0,z))
        parts.append('<path d="M %.2f,%.2f L %.2f,%.2f" stroke="#d1d5db" stroke-width="1" stroke-dasharray="4,6"/>'%(*a,*b))
    faces=[]
    for ob in objects:
        for t in ob["tris"]:
            points=" ".join("%.2f,%.2f"%project(v) for v in t)
            key=sum(p[0]+p[2]-p[1] for p in t)
            faces.append((key,'<polygon points="%s" fill="%s" fill-opacity=".38" stroke="%s" stroke-width=".55"/>'%
                          (points,COLORS[ob["id"]],COLORS[ob["id"]])))
    for _,face in sorted(faces,key=lambda q:q[0],reverse=isometric):parts.append(face)
    if path and not isometric:
        d=" ".join(("M" if i==0 else "L")+" %.2f %.2f"%project((x,0,z)) for i,(x,z) in enumerate(path))
        parts.append('<path d="%s" fill="none" stroke="#c026d3" stroke-width="3.2" stroke-linejoin="round"/>'%d)
        for x,z in (path[0],path[-1]):
            px,py=project((x,0,z))
            parts.append('<circle cx="%.2f" cy="%.2f" r="5" fill="#c026d3"/>'%(px,py))
    parts.append('<text x="845" y="88" font-family="sans-serif" font-size="17" fill="#334155">Fixture: %s</text>'%area)
    parts.append('<text x="845" y="122" font-family="sans-serif" font-size="15" fill="#334155">1m grid / render-triangle surface</text>')
    parts.append('<text x="845" y="155" font-family="sans-serif" font-size="15" fill="#334155">Sampled slab: 0–%.2fm</text>'%headroom)
    if path and not isometric:
        parts.append('<text x="845" y="185" font-family="sans-serif" font-size="15" fill="#a21caf">Purple: raster widest-path probe</text>')
    for i,ob in enumerate(objects):
        parts.append('<text x="845" y="%d" font-family="sans-serif" font-size="15" fill="%s">%s — SHA %.10s…</text>'%
                     (235+28*i,COLORS[ob["id"]],ob["id"],ob["sha256"]))
    parts.append('<text x="25" y="771" font-family="sans-serif" font-size="13" fill="#475569">Illustrative placements only; no doors / no Unity / no approved walkway width. Shaded-wire projection uses original FBX triangles.</text>')
    parts.append("</svg>")
    (OUT/(name+".svg")).write_text("\n".join(parts),encoding="utf-8")

def main():
    assets={a["id"]:a for a in [source_triangle_world(s) for s in SOURCES]}
    reports=[];rows=[]
    for fixture in LAYOUTS:
        objects=[]
        for aid,anchor,yaw in fixture["placements"]:
            if any(int(v)!=v for v in anchor) or yaw not in (0,90,180,270):
                raise RuntimeError("NON_GRID_OR_NON_CARDINAL_FIXTURE")
            source=assets[aid]
            objects.append({"id":aid,"anchor_xz_m":list(anchor),"yaw_deg":yaw,
                "sha256":source["sha256"],"tris":moved(source,anchor,yaw)})
        pairs=true_mesh_pairs(objects)
        wall=wall_bounds(objects,fixture["area"])
        levels=[]
        for slab in SLABS:
            polys=[p for o in objects for p in footprints(o["tris"],slab)]
            field=clearance_grid(fixture["area"],polys)
            radius,path=widest_path(field,fixture["area"])
            probe={str(r):{"sampled_connection":radius>=r+1e-8,
                            "interpretation":"ANALYTICAL_RADIUS_PROBE_NOT_OWNER_THRESHOLD"}
                   for r in PROBE_RADII_M}
            levels.append({"sampled_height_slab_max_m":slab,
                "projected_actual_FBX_triangle_polygons":len(polys),
                "widest_0_1m_grid_route_bottleneck_radius_m":round(radius,5),
                "approx_diameter_m":round(2*radius,5),
                "probe_radii_m":probe,
                "route_steps":len(path),"route_xz_m":[[round(x,3),round(z,3)] for x,z in path],
                "straight_centerline":centerline_probe(fixture["area"],polys),
                "method":"Conservative 2D projection of actual FBX triangle surfaces clipped to Y slab, sampled 0.10m clearance field, widest 4-neighbor path. NOT Unity NavMesh."})
        crossing=sum(p["exact_non_coplanar_surface_crossing_pairs"] for p in pairs)
        boundaries=sum(z["out_of_fixture_source_vertices"] for z in wall)
        verdict=("EXAMPLE_PLACEMENT_GEOMETRY_CROSSING" if crossing else
                 "EXAMPLE_PLACEMENT_OUTSIDE_FIXTURE" if boundaries else
                 "MEASURED_DESIGN_THRESHOLD_UNDEFINED")
        rec={"fixture_id":fixture["id"],"area":fixture["area"],
             "placement":[{"asset":o["id"],"source_FBX_sha256":o["sha256"],
                 "integer_grid_anchor_xz_m":o["anchor_xz_m"],"yaw_deg":o["yaw_deg"]}
                 for o in objects],
             "non_coplanar_actual_triangle_pair_evidence":pairs,
             "fixture_wall_bounds":wall,"vertical_slab_navigation_grid":levels,
             "total_exact_surface_crossing_pairs":crossing,
             "total_outside_fixture_render_vertices":boundaries,
             "disposition":verdict}
        reports.append(rec)
        for lvl in levels:
            rows.append({"fixture_id":fixture["id"],"area":fixture["area"],
              "height_slab_max_m":lvl["sampled_height_slab_max_m"],
              "grid_bottleneck_radius_m":lvl["widest_0_1m_grid_route_bottleneck_radius_m"],
              "approx_continuous_diameter_m":lvl["approx_diameter_m"],
              "probe_r_0_1_connected":lvl["probe_radii_m"]["0.1"]["sampled_connection"],
              "probe_r_0_2_connected":lvl["probe_radii_m"]["0.2"]["sampled_connection"],
              "probe_r_0_35_connected":lvl["probe_radii_m"]["0.35"]["sampled_connection"],
              "centerline_occupied_grid_samples":lvl["straight_centerline"]["sampled_occupied_centers"],
              "centerline_sampled_clear":lvl["straight_centerline"]["centerline_geometrically_free_at_sample_points"],
              "surface_cross_pairs":crossing,"out_of_fixture_vertices":boundaries,
              "status":verdict})
        if fixture["id"] in ("ROOM_WALL_ADJACENT_3","ROOM_CENTER_CROWDED_3",
                             "CORRIDOR_STAGGERED_CROWDED_3","CORRIDOR_TWO_SEQUENTIAL_2"):
            svg_image(fixture["id"]+"_top_actual_FBX",objects,fixture["area"],
                levels[-1]["route_xz_m"],SLABS[-1])
        if fixture["id"] in ("ROOM_WALL_ADJACENT_3","ROOM_CENTER_CROWDED_3"):
            svg_image(fixture["id"]+"_iso_actual_FBX",objects,fixture["area"],[],SLABS[-1],True)
        print("W24_LAYOUT",fixture["id"],"SURFACE_CROSS",crossing,
              "OUTSIDE",boundaries,"SLAB_BOTTLENECK",
              [x["widest_0_1m_grid_route_bottleneck_radius_m"] for x in levels])
    manifest={"schema":"C01-13-W24-NONDOOR-REAL-FBX-MULTIOBJECT-GRID-PATH-1",
      "assets":[{"id":a["id"],"source_SHA256_FBX":a["sha256"],"meshes":a["mesh_count"],
                 "triangles":a["triangle_count"]} for a in assets.values()],
      "fixture_conditions":{"room_m":[4,4],"corridor_m":[2,4],
        "snap_grid_m":1,"nav_sampling_grid_m":GRID_STEP_M,
        "slabs_max_y_m":SLABS,"example_probe_radii_m":PROBE_RADII_M,
        "floor":"mesh minimum bottom aligned to 0m without changing source pivot",
        "minimum_required_walkable_width":"DESIGN_THRESHOLD_UNDEFINED",
        "model_collision":"EXACT_NONCOPLANAR_TRIANGLE_SEGMENT_CROSSING_WITNESSES",
        "navigation":"SAMPLED_FOOTPRINT_NOT_NAVMESH"},
      "layout_results":reports,
      "summary":{"real_signed_FBX":len(assets),"multi_object_layouts":len(reports),
        "sampled_slab_scenarios":len(rows),
        "surface_crossing_layouts":sum(bool(x["total_exact_surface_crossing_pairs"]) for x in reports),
        "out_of_test_bounds_layouts":sum(bool(x["total_outside_fixture_render_vertices"]) for x in reports),
        "unity":"NOT_RUN","door_or_gate_files_touched":0,"production_models_reexported":0},
      "notes":["Examples are not approved ship layout or corridors; no doors, doorway/opening or ship changes.",
       "Real triangle non-coplanar crossings proved; coplanar overlaps/complete containment require supplementary test.",
       "0.1m cell size and conservative footprint mean sampled path is approximate; radius probes are NOT compliance criteria.",
       "Samples include all visible geometry in y=[0,slab] rather than game physics colliders.",
       "Straight centerline can be blocked even when a separate alternate route exists; both are reported independently.",
       "Unapproved walkway width owner decision required, no automatic placement acceptance.",
       "Unity/NavMesh and final physical clearance tests: NOT RUN."],
      "disposition":"MEASURED_NONDOOR_MULTIPROP_QA__DESIGN_THRESHOLD_UNDEFINED__UNITY_NOT_RUN"}
    (OUT/"multi_object_clearance_W24.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    with open(OUT/"multi_object_clearance_W24.csv","w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        writer.writeheader();writer.writerows(rows)
    print("W24_FINAL_SUMMARY",json.dumps(manifest["summary"]))
    for ob in manifest["assets"]:
        print("PINNED_FBX_VERIFIED",ob["id"],ob["source_SHA256_FBX"],ob["meshes"],ob["triangles"])

main()
