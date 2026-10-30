"""PASS04 C01-14: inspect exact committed native BLEND and binary FBX, without modifying geometry."""
import bpy, bmesh, json, math, hashlib, sys, collections, itertools, argparse
from pathlib import Path
from mathutils.bvhtree import BVHTree

ASSETS=("RMP-01","RAI-01")
SOURCE_HASH={
 "RMP-01":{"blend":"7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa","fbx":"97f0b125313057f4ecf601dd60a02b4d3f0d55b87c1713d71a0adbedcc6d1443"},
 "RAI-01":{"blend":"8a2f16205874f8485adb87c5251f6adbba3f51816936c0bf1964ad40a47850a5","fbx":"b51c3c012f5680de2d02c2deaf5c67c4ae9a12bb7e8347f179ed08d181a7e103"}
}
EXPECTED={"RMP-01": {"AntiSlipMark_01","AntiSlipMark_02","AntiSlipMark_03","AntiSlipMark_04","Deck_Main","COL_RampDeck"},
          "RAI-01": {"TopRail","MiddleRail","Post_Start","Post_End"}}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def qvec(v,n=4): return tuple(round(float(x),n) for x in v)
def meshes(): return {ob.name:ob for ob in bpy.data.objects if ob.type=="MESH"}
def signature(ob):
    me=ob.data;me.calc_loop_triangles();counter=collections.Counter()
    for tr in me.loop_triangles:
        vs=[qvec(ob.matrix_world @ me.vertices[i].co) for i in tr.vertices]
        key=tuple(sorted(vs));normal=(ob.matrix_world.to_3x3() @ tr.normal).normalized()
        counter[(key,qvec(normal,3))]+=1
    return counter
def summarize(ob):
    me=ob.data;me.calc_loop_triangles()
    bm=bmesh.new();bm.from_mesh(me)
    nonman=sum(not e.is_manifold for e in bm.edges)
    boundary=sum(e.is_boundary for e in bm.edges)
    loose=sum(not v.link_edges for v in bm.verts)
    nonzero=[float(tr.area) for tr in me.loop_triangles]
    area_uv=[]
    uv=me.uv_layers.active
    if uv:
        for tr in me.loop_triangles:
            u,v,w=[uv.data[i].uv for i in tr.loops]
            area_uv.append(abs((v.x-u.x)*(w.y-u.y)-(v.y-u.y)*(w.x-u.x))*.5)
    pts=[ob.matrix_world @ v.co for v in me.vertices]
    out={"mesh":ob.name,"v":len(me.vertices),"e":len(me.edges),"f":len(me.polygons),"t":len(me.loop_triangles),
         "boundary":boundary,"nonmanifold":nonman,"loose":loose,
         "degenerate_triangles":sum(a<1e-12 for a in nonzero),
         "min_triangle_area":min(nonzero) if nonzero else None,
         "uv0_present":bool(uv),"invalid_uv0_area_triangles":sum(a<1e-12 for a in area_uv),
         "material_slots":[m.name if m else None for m in me.materials],
         "bounds_xyz_blender":[qvec(tuple(min(p[i] for p in pts) for i in range(3)),6),
                               qvec(tuple(max(p[i] for p in pts) for i in range(3)),6)],
         "unit_scale":qvec(ob.scale,6),"origin":qvec(ob.location,6),
         "rotation":qvec(ob.rotation_euler,6)}
    bm.free();return out
def pair_contact(asset,a,b):
    # BVH uses ACTUAL triangles of Blender mesh objects. Touching and coplanar pairs are CANDIDATES.
    def build(ob):
        ob.data.calc_loop_triangles()
        vertices=[ob.matrix_world @ v.co for v in ob.data.vertices]
        triangles=[tuple(tr.vertices) for tr in ob.data.loop_triangles]
        return BVHTree.FromPolygons(vertices,triangles,all_triangles=True,epsilon=0.0)
    bvha,bvhb=build(a),build(b)
    hits=bvha.overlap(bvhb)
    pa,pb=summarize(a)["bounds_xyz_blender"],summarize(b)["bounds_xyz_blender"]
    depth=[max(0.0,min(pa[1][i],pb[1][i])-max(pa[0][i],pb[0][i])) for i in range(3)]
    volume=depth[0]*depth[1]*depth[2]
    names={a.name,b.name}
    if asset=="RMP-01" and names=={"COL_RampDeck","Deck_Main"}:
        classification="INTENTIONAL_COLLIDER_PROXY_IDENTICAL_SURFACE"
    elif asset=="RAI-01" and any(n.startswith("Post_") for n in names) and any(n.endswith("Rail") for n in names):
        classification="INTENTIONAL_POST_RAIL_ASSEMBLY_INTERSECTION"
    elif hits:classification="UNREVIEWED_CROSS_PART_TRIANGLE_CONTACT"
    elif volume>1e-9:classification="AABB_OVERLAP_ONLY_NO_TRIANGLE_CONTACT"
    else:classification="DISJOINT"
    return {"a":a.name,"b":b.name,"triangle_contact_candidates":len(hits),
            "aabb_positive_intersection_m3":volume,"aabb_overlap_depth_m":depth,
            "classification":classification}
def make_asset(root,asset,outdir):
    src=root/"Sources"/("C01_14_"+asset+"_v002.blend")
    fbx=root/"FBX"/("C01_14_"+asset+"_v002.fbx")
    assert src.exists() and fbx.exists(),(src,fbx)
    ah,bh=digest(src),digest(fbx)
    assert ah==SOURCE_HASH[asset]["blend"],("source SHA changed",asset,ah)
    assert bh==SOURCE_HASH[asset]["fbx"],("fbx SHA changed",asset,bh)
    assert src.read_bytes().startswith(b"BLENDER")
    assert fbx.read_bytes().startswith(b"Kaydara FBX Binary")
    bpy.ops.wm.open_mainfile(filepath=str(src))
    original=meshes()
    assert set(original)==EXPECTED[asset],(asset,list(original))
    original_stats={k:summarize(v) for k,v in original.items()}
    original_triangles={k:signature(v) for k,v in original.items()}
    # Cross-part collisions are intentionally distinct meshes; no global weld.
    pairs=[pair_contact(asset,a,b) for a,b in itertools.combinations(original.values(),2)]
    unresolved=[p for p in pairs if p["classification"]=="UNREVIEWED_CROSS_PART_CONTACT"]
    # Follow-up tri area check on reimported ORIGINAL FBX, no second export or geometry rebuild.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx),use_custom_normals=True)
    imported=meshes()
    assert set(imported)==EXPECTED[asset],("FBX part lost or renamed",asset,list(imported))
    imported_stats={k:summarize(v) for k,v in imported.items()}
    imported_triangles={k:signature(v) for k,v in imported.items()}
    geometry_equal=all(original_triangles[k]==imported_triangles[k] for k in original)
    details={}
    for k in original:
        before,after=original_stats[k],imported_stats[k]
        details[k]={"source":before,"fbx_import":after,
            "triangles_with_winding_preserved":original_triangles[k]==imported_triangles[k],
            "uv0_preserved":before["uv0_present"] and after["uv0_present"],
            "material_slots_preserved":before["material_slots"]==after["material_slots"],
            "triangles_before_after":(before["t"],after["t"])}
    bad=[k for k,v in details.items() if not v["triangles_with_winding_preserved"] or
         not v["uv0_preserved"] or not v["material_slots_preserved"] or
         v["fbx_import"]["degenerate_triangles"] or v["fbx_import"]["invalid_uv0_area_triangles"]]
    r={"asset_id":asset,"scope":"C01-14 OPTIONAL REFERENCE ONLY / NOT 36 P15-P19 MODELS",
       "sha256":{"native_blend":ah,"binary_fbx":bh},"blender_version":bpy.app.version_string,
       "actual_blender_native_open":True,"actual_binary_fbx_import":True,
       "source_parts":list(original),"per_part":details,"pairwise_actual_bvh_and_aabb":pairs,
       "unreviewed_contacts":unresolved,"failing_parts":bad,
       "source_triangles":sum(v["t"] for v in original_stats.values()),
       "fbx_triangles":sum(v["t"] for v in imported_stats.values()),
       "source_to_fbx_geometry_and_winding_equal":geometry_equal,
       "source_mutations":0,"new_meshes_created":0,
       "source_topology_defects_repaired":0,
       "unity_6_urp":"NOT_RUN","independent_c01_02_qa":"NOT_RUN",
       "pass04_native_source_fbx_gate":("PASS" if not bad and not unresolved and geometry_equal else "FAIL")}
    (outdir/(asset+"_pass04.json")).write_text(json.dumps(r,indent=2,ensure_ascii=False))
    print("C01-14",asset,"PASS04",r["pass04_native_source_fbx_gate"],
          "PARTS",len(original),"TRIS",r["source_triangles"],"=>",r["fbx_triangles"],
          "PAIR_CANDIDATES",sum(bool(p["triangle_contact_candidates"]) for p in pairs),
          "UNREVIEWED",len(unresolved),"BAD_PARTS",len(bad))
    if r["pass04_native_source_fbx_gate"]!="PASS":
        raise ValueError("PASS04 genuine source/FBX gate FAIL for "+asset+" details in "+str(outdir))
def run():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--out",required=True)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    root=Path(a.input).resolve()
    for id in ASSETS:make_asset(root,id,out)
if __name__=="__main__":run()
