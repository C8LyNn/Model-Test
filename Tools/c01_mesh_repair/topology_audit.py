#!/usr/bin/env python3
"""C01-01 / PASS03: audyt *oryginalnego* Blender Mesh, bez automatycznych zmian.

Uruchomienie: blender -b REAL.blend --python Tools/c01_mesh_repair/topology_audit.py -- \
  --asset-id P17-04 --stage BEFORE --out ./QA/P17-04/topology_before.json

Pomiar BMesh; wyniki BEFORE/AFTER nie są dowodem wykonanej naprawy.
Dla otwartych powierzchni i niezależnych części wymagaj jawnej dokumentacji.
"""
import argparse
import collections
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

EPS_LEN = 1e-7
EPS_AREA = 1e-12
CANDIDATE_CAP = 100


def _arguments():
    tail = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--asset-id", required=True)
    p.add_argument("--stage", choices=("BEFORE", "AFTER"), default="BEFORE")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--policy", type=Path)
    p.add_argument("--sample-limit", type=int, default=CANDIDATE_CAP)
    return p.parse_args(tail)


def _components(bm):
    unseen = set(bm.verts)
    sizes=[]
    while unseen:
        seed = unseen.pop()
        stack=[seed]
        size=0
        while stack:
            vert=stack.pop()
            size+=1
            for edge in vert.link_edges:
                v=edge.other_vert(vert)
                if v in unseen:
                    unseen.remove(v)
                    stack.append(v)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def _rounded_key(pos, precision=6):
    return tuple(round(float(a),precision) for a in pos)


def _duplicates(bm, limit):
    """Approximate co-located verts: diagnostic; Blender may intentionally split UV/hard edges."""
    grouped=collections.defaultdict(list)
    for v in bm.verts:
        grouped[_rounded_key(v.co)].append(v.index)
    pairs=[]
    total=0
    for indices in grouped.values():
        if len(indices)<2:
            continue
        total+=len(indices)-1
        if len(pairs)<limit:
            pairs.append(indices[:8])
    return total,pairs


def _faces_duplicate(bm, limit):
    """Different faces with identical vertex *locations* are possible z-fighting suspects."""
    seen={}
    dup=[]
    total=0
    for f in bm.faces:
        sig=tuple(sorted(_rounded_key(v.co) for v in f.verts))
        if sig in seen:
            total+=1
            if len(dup)<limit:
                dup.append([seen[sig], f.index])
        else:
            seen[sig]=f.index
    return total,dup


def _tj_candidates(bm, limit, epsilon=1e-5):
    """Interior-on-edge unconnected vertex candidates; never auto-weld."""
    if len(bm.verts)>40000 or len(bm.edges)>50000:
        return None, [], "SKIPPED_LIMIT_40000V_50000E"
    kd=KDTree(len(bm.verts))
    for v in bm.verts:
        kd.insert(v.co, v.index)
    kd.balance()
    found=[]
    seen=set()
    count=0
    for e in bm.edges:
        a,b=[v.co for v in e.verts]
        ab=b-a
        l2=ab.length_squared
        if l2<EPS_LEN**2:
            continue
        midpoint=(a+b)*.5
        radius=math.sqrt(l2)*.5+epsilon
        for _,index,_ in kd.find_range(midpoint,radius):
            if index in (e.verts[0].index,e.verts[1].index):
                continue
            p=bm.verts[index].co
            t=(p-a).dot(ab)/l2
            if t <= 1e-5 or t >= 1-1e-5:
                continue
            delta=p-(a+ab*t)
            if delta.length_squared<=epsilon*epsilon:
                key=(e.index,index)
                if key not in seen:
                    count+=1
                    seen.add(key)
                    if len(found)<limit:
                        found.append(dict(edge=e.index, vertex=index, ratio=round(float(t),7)))
    return count,found,None


def _self_overlap(bm, limit):
    """BVH face triangle candidates, excluding faces sharing verts; NOT proof of actual intersections."""
    if len(bm.faces)>10000:
        return None, [], "SKIPPED_LIMIT_10000_FACES"
    try:
        bvh=BVHTree.FromBMesh(bm, epsilon=0.0)
        raw=bvh.overlap(bvh)
    except Exception as exc:
        return None,[], "UNAVAILABLE_"+type(exc).__name__
    seen=set()
    samples=[]
    for a,b in raw:
        if a==b:
            continue
        key=tuple(sorted((a,b)))
        if key in seen:
            continue
        seen.add(key)
        if a>=len(bm.faces) or b>=len(bm.faces):
            continue
        fa,fb=bm.faces[a],bm.faces[b]
        if {v.index for v in fa.verts} & {v.index for v in fb.verts}:
            continue
        if len(samples)<limit:
            samples.append(list(key))
    return len(samples),samples,"CANDIDATES_ONLY_BVH_MAY_INCLUDE_CONTACT"


def _mesh_report(obj, limit):
    mesh=obj.data
    bm=bmesh.new()
    try:
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bm.verts.index_update()
        bm.edges.index_update()
        bm.faces.index_update()
        bm.normal_update()
        nverts=len(bm.verts)
        edges=len(bm.edges)
        faces=len(bm.faces)
        tris=sum(max(0,len(f.verts)-2) for f in bm.faces)
        area=sum(float(f.calc_area()) for f in bm.faces)
        deg=[f.index for f in bm.faces if f.calc_area()<EPS_AREA]
        zero=[e.index for e in bm.edges if (e.verts[0].co-e.verts[1].co).length_squared<EPS_LEN**2]
        loose_v=[v.index for v in bm.verts if not v.link_edges]
        loose_e=[e.index for e in bm.edges if not e.link_faces]
        boundary=[e.index for e in bm.edges if e.is_boundary]
        multi=[e.index for e in bm.edges if len(e.link_faces)>2]
        flipped=[e.index for e in bm.edges if e.is_manifold and not e.is_contiguous]
        coincident,coincident_examples=_duplicates(bm,limit)
        dup_faces,dup_face_examples=_faces_duplicate(bm,limit)
        tj,tj_examples,tj_note=_tj_candidates(bm,limit)
        bvh_count,bvh_examples,bvh_note=_self_overlap(bm,limit)
        try:
            signed_volume=float(bm.calc_volume(signed=True))
        except Exception:
            signed_volume=None
        dims=[round(float(x),7) for x in obj.dimensions]
        bmin=[min((v.co[i] for v in bm.verts),default=0) for i in range(3)]
        bmax=[max((v.co[i] for v in bm.verts),default=0) for i in range(3)]
        data={
            "object":obj.name,"mesh":mesh.name,"parent":obj.parent.name if obj.parent else None,
            "counts":dict(vertices=nverts,edges=edges,faces=faces,triangles=tris,components=_components(bm)),
            "local_aabb_xyz":[list(map(float,bmin)),list(map(float,bmax))],
            "world_object_dimensions_xyz":dims,
            "mesh_issues":{
                "loose_vertices":len(loose_v),"loose_edges":len(loose_e),
                "zero_length_edges":len(zero),"degenerate_faces":len(deg),
                "boundary_edges":len(boundary),"nonmanifold_overconnected_edges":len(multi),
                "inconsistent_winding_edges":len(flipped),
                "colocated_vertex_candidates":coincident,"duplicate_face_candidates":dup_faces,
                "t_junction_candidates":tj,"bvh_overlap_candidates":bvh_count
            },
            "examples":{
                "loose_vertices":loose_v[:limit],"loose_edges":loose_e[:limit],"zero_length_edges":zero[:limit],
                "degenerate_faces":deg[:limit],"boundary_edges":boundary[:limit],
                "nonmanifold_overconnected_edges":multi[:limit],"inconsistent_winding_edges":flipped[:limit],
                "colocated_vertices":coincident_examples,"duplicate_faces":dup_face_examples,
                "t_junctions":tj_examples,"bvh_overlaps":bvh_examples
            },
            "bvh_note":bvh_note,"tjunction_note":tj_note,
            "signed_volume_closed_mesh_only":signed_volume if len(boundary)==0 and len(loose_e)==0 else None,
            "surface_area_m2_local":round(area,9),
            "uv_maps":[{"name":l.name,"active":l.active} for l in mesh.uv_layers],
            "material_slots":[s.name if s else None for s in mesh.materials],
            "has_custom_split_normals": bool(getattr(mesh,"has_custom_normals",False)),
            "transform":{
                "local_scale":list(map(float,obj.scale)),
                "local_rotation_euler":list(map(float,obj.rotation_euler)),
                "matrix_world": [[round(float(obj.matrix_world[i][j]),8) for j in range(4)] for i in range(4)]
            }
        }
        return data
    finally:
        bm.free()


def audit(asset_id, stage, policy=None, limit=CANDIDATE_CAP):
    objects=sorted((o for o in bpy.data.objects if o.type=="MESH"),key=lambda o:o.name)
    scene=bpy.context.scene
    checks=[_mesh_report(o,limit) for o in objects]
    sums=collections.Counter()
    for o in checks:
        for k,v in o["mesh_issues"].items():
            if isinstance(v,int):
                sums[k]+=v
    exceptions={}
    if policy:
        exceptions=policy.get("exceptions",{})
    # Only exception reasons explicitly bound to existing mesh/metric become documented exceptions.
    annotations=[]
    for obj in checks:
        for key,val in obj["mesh_issues"].items():
            if not isinstance(val,int) or val==0:
                continue
            decl=exceptions.get(obj["object"],{}).get(key)
            if isinstance(decl,dict) and decl.get("reason") and decl.get("classification")=="INTENTIONAL":
                annotations.append({"object":obj["object"],"metric":key,"count":val,
                                    "classification":"INTENTIONAL_UNVERIFIED","reason":decl["reason"]})
    return {
        "schema":"C01-MESH-TOPOLOGY-1.0","asset_id":asset_id,"stage":stage,
        "source_blend":bpy.data.filepath,"source_sha256":_sha256(Path(bpy.data.filepath)),
        "blender_version":bpy.app.version_string,"scene":scene.name,
        "objects_mesh_count":len(checks),"object_data":checks,
        "totals":dict(sums),"exceptions_declared":annotations,
        "qa_geometry":"NOT_APPROVED", "qa_blender":"AUDIT_EXECUTED" if checks else "BLOCKED_NO_MESH",
        "qa_fbx_roundtrip":"NOT_RUN","qa_unity":"NOT_RUN",
        "note":"Candidate metrics are NOT automatically repaired. Exporter may legitimately split vertices at sharp/UV seams."
    }


def _sha256(file):
    if not file.is_file():
        return None
    h=hashlib.sha256()
    with file.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    a=_arguments()
    if not bpy.data.filepath or not Path(bpy.data.filepath).is_file():
        raise RuntimeError("REAL .blend must be opened (not a synthetic replacement)")
    policy=json.loads(a.policy.read_text()) if a.policy else None
    report=audit(a.asset_id,a.stage,policy,a.sample_limit)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("C01_TOPOLOGY_AUDIT "+json.dumps({"asset_id":a.asset_id,"stage":a.stage,
        "status":report["qa_blender"],"objects":report["objects_mesh_count"],"totals":report["totals"]},
        sort_keys=True))
    if not report["objects_mesh_count"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
