"""W26 C01-16 genuine Blender 4.x audit. READ ONLY on all 7 original signed FBX/BLEND.
No exports, saving, mesh repairs, door imports, prefab or Unity claims.
Output JSON and genuine geometry wireframe SVG to evidence/ only.
"""
import bpy, bmesh, json, hashlib, math, pathlib, sys
from mathutils.bvhtree import BVHTree

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
W01 = ROOT / "C01Source/Lighting"
W02 = ROOT / "C01Source/LightingW02"
MANIFEST = json.loads((W02 / "MeshRepairPASS17/GENUINE_BLENDER_SHA_AND_QA.json").read_text())
OUT = HERE / "evidence"
OUT.mkdir(exist_ok=True)
COUNTS = {"P16-01": (12,220), "P16-02": (12,220), "P16-03": (12,220),
          "P16-04": (27,452), "P16-05": (19,344), "P16-06": (23,388),
          "P16-07": (11,208)}
TOL = 1e-8

def signed_bytes(path, sha, signature):
    payload = path.read_bytes()
    assert payload.startswith(signature), "UNHYDRATED_OR_INVALID: " + str(path)
    actual = hashlib.sha256(payload).hexdigest()
    assert actual == sha, "WRONG_BINARY_SHA: " + str(path) + " " + actual
    return len(payload)

def mesh_state():
    objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    stats = {"meshes":len(objects),"tris":0,"vertices":0,"edges":0,
             "boundary_edges":0,"nonmanifold_edges":0,"degenerate_faces":0,
             "uv0_missing":0,"uv0_zero_area":0,"inverted_face_corners":0,
             "nonfinite_coords":0}
    entries = []
    for o in objects:
        me = o.data
        stats["vertices"] += len(me.vertices)
        stats["edges"] += len(me.edges)
        stats["tris"] += sum(len(f.vertices)-2 for f in me.polygons)
        bm = bmesh.new()
        bm.from_mesh(me)
        boundary = sum(e.is_boundary for e in bm.edges)
        nonmanifold = sum(not e.is_manifold and not e.is_boundary for e in bm.edges)
        stats["boundary_edges"] += boundary
        stats["nonmanifold_edges"] += nonmanifold
        bm.free()
        uv = me.uv_layers.active
        if uv is None: stats["uv0_missing"] += 1
        bad = 0
        for p in me.polygons:
            if p.area <= TOL*TOL: stats["degenerate_faces"] += 1
            if uv is not None:
                ls = [uv.data[j].uv.copy() for j in p.loop_indices]
                for k in range(1,len(ls)-1):
                    a,b,c=ls[0],ls[k],ls[k+1]
                    uva=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*0.5
                    if uva < TOL*TOL: stats["uv0_zero_area"] += 1
        for v in me.vertices:
            if not all(math.isfinite(float(x)) for x in v.co):
                stats["nonfinite_coords"] += 1
        entries.append({"name":o.name,"verts":len(me.vertices),
                        "triangles":sum(len(p.vertices)-2 for p in me.polygons),
                        "boundary_edges":boundary,"nonmanifold_edges":nonmanifold,
                        "uv0":bool(uv)})
    return objects,stats,entries

def real_world_bounds(objs):
    vs = [o.matrix_world @ vert.co for o in objs for vert in o.data.vertices]
    if not vs: raise AssertionError("NO_MESH_VERTICES")
    return [[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)]

def cross_mesh_overlap_pairs(objs):
    pairs = []
    trees=[]
    for o in objs:
        vv = [o.matrix_world @ v.co for v in o.data.vertices]
        faces = [tuple(p.vertices) for p in o.data.polygons]
        trees.append(BVHTree.FromPolygons(vv,faces,all_triangles=False))
    for i in range(len(objs)):
        for j in range(i+1,len(objs)):
            found = trees[i].overlap(trees[j])
            if found: pairs.append({"a":objs[i].name,"b":objs[j].name,
                                    "bvh_overlap_triangle_pairs":len(found)})
    return pairs

def wireframe_svg(objs,name):
    # Signed FBX geometry only: project actual transformed world mesh edges, not placeholder boxes.
    lines=[]
    for o in objs:
        p = [o.matrix_world @ v.co for v in o.data.vertices]
        shade = "#83c5e7" if "_ROTOR_" in o.name else ("#ebaa70" if "Emission" in o.name else "#9ba8b8")
        for e in o.data.edges:
            a,b=(p[e.vertices[0]],p[e.vertices[1]])
            # Isometric basis X-Y / X+Y-2Z
            aa=(.8660254*(a.x-a.y), .5*(a.x+a.y)-a.z)
            bb=(.8660254*(b.x-b.y), .5*(b.x+b.y)-b.z)
            lines.append((aa,bb,shade))
    allxy=[xy for a,b,c in lines for xy in (a,b)]
    xmin=min(p[0] for p in allxy);xmax=max(p[0] for p in allxy)
    ymin=min(p[1] for p in allxy);ymax=max(p[1] for p in allxy)
    scale=min(900/max(xmax-xmin,1e-6),620/max(ymax-ymin,1e-6))
    def proj(p):
        return round(60+(p[0]-xmin)*scale,2),round(85+(ymax-p[1])*scale,2)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 800">',
         '<rect width="1040" height="800" fill="#111925"/>',
         '<text x="40" y="42" fill="#f2f5f9" font-size="24" font-family="Arial">'+name+' ORIGINAL SIGNED FBX WIREFRAME</text>',
         '<text x="40" y="772" fill="#a8b4c5" font-size="13" font-family="Arial">Actual imported mesh edges · Blender Z up · no repair / no replacement geometry</text>']
    for a,b,c in lines:
        x1,y1=proj(a);x2,y2=proj(b)
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="0.72" opacity=".65"/>')
    svg.append('</svg>')
    (OUT/(name+"_W26_original_wireframe.svg")).write_text("\n".join(svg)+"\n")

results=[]
for item in MANIFEST["models"]:
    aid=item["id"]
    origin=W01 if aid in ("P16-01","P16-02","P16-03") else W02
    blend=origin/"Blender"/(aid+".blend")
    fbx=origin/"FBX"/(aid+".fbx")
    bsize=signed_bytes(blend,item["blend_sha256"],b"BLENDER-")
    fsize=signed_bytes(fbx,item["fbx_sha256"],b"Kaydara FBX Binary")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    native,native_stat,_=mesh_state()
    before=real_world_bounds(native)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(fbx), automatic_bone_orientation=False)
    bpy.context.view_layer.update()
    imported,stat,entries=mesh_state()
    after=real_world_bounds(imported)
    assert stat["meshes"]==COUNTS[aid][0],(aid,"mesh count",stat)
    assert stat["tris"]==COUNTS[aid][1],(aid,"tri count",stat)
    for key in ("boundary_edges","nonmanifold_edges","degenerate_faces",
                "uv0_missing","uv0_zero_area","nonfinite_coords"):
        assert stat[key]==0,(aid,key,stat[key])
    maxdelta=max(abs(before[d][s]-after[d][s]) for d in range(3) for s in range(2))
    assert maxdelta < 1e-5,(aid,"BLEND_FBX_BOUNDS_DIFF",maxdelta)
    moving=[o for o in imported if "_ROTOR_" in o.name]
    if aid=="P16-06": assert len(moving)==8,(aid,"rotor hierarchy",len(moving))
    else: assert len(moving)==0,(aid,"UNEXPECTED_MOVING_PARTS")
    overlaps=cross_mesh_overlap_pairs(imported)
    if aid=="P16-06":
        assert not [p for p in overlaps if ("_ROTOR_" in p["a"])!=("_ROTOR_" in p["b"])], "STATIC_ROTOR_0_DEG_OVERLAP"
    wireframe_svg(imported,aid)
    row={"id":aid,"native_blend_sha256":item["blend_sha256"],
         "native_fbx_sha256":item["fbx_sha256"],"native_blend_bytes":bsize,
         "native_fbx_bytes":fsize,"native_blend":native_stat,"fbx_import":stat,
         "max_blend_fbx_aabb_delta_m":maxdelta,"per_mesh":entries,
         "bvh_intersecting_component_pairs":overlaps,
         "bvh_pair_count":len(overlaps),
         "overlap_verdict":"ASSEMBLY_INTENT_REVIEW_NOT_AUTOMATIC_DEFECT",
         "static_topology_gate":"PASS","unity":"NOT_RUN"}
    results.append(row)
    print("W26_REAL_BLENDER_FBX_PASS",aid,stat["meshes"],stat["tris"],
          "component_overlap_pairs",len(overlaps),flush=True)
summary={"schema":"C01-16-W26-GENUINE-BLENDER-READONLY-FBX-QA",
         "blender_version":bpy.app.version_string,"source":"signed W01/W02 current repo LFS",
         "original_blend_fbx_pair_count":len(results),"verdict":"PASS_STATIC_TOPOLOGY_ASSEMBLY_REVIEW",
         "details":results,"no_native_model_modified":True,"unity_editor":"NOT_RUN",
         "independent_C01_02_W26":"PENDING"}
(OUT/"C01_16_W26_REAL_BLENDER_FBX_REPORT.json").write_text(json.dumps(summary,indent=2)+"\n")
print("W26_COMPLETED",len(results),"static_PASS; per-assembly overlap review needed",flush=True)
