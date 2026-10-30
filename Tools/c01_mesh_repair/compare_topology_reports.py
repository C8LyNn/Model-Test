#!/usr/bin/env python3
"""C01-01 PASS03: evidence-aware BEFORE/AFTER topology comparison.

Makes no repair and NEVER issues final Blender/FBX/Unity or independent QA PASS.
Identical original hashes with alleged repair -> FAIL; topology candidates -> REVIEW_REQUIRED.
"""
import argparse
import json
from pathlib import Path

HARD=("zero_length_edges","degenerate_faces","loose_vertices",
      "loose_edges","nonmanifold_overconnected_edges","inconsistent_winding_edges")
CANDIDATES=("colocated_vertex_candidates","duplicate_face_candidates",
            "t_junction_candidates","bvh_overlap_candidates")
DIM_TOL=.001


def compare(before, after, repair_claimed=False):
    errors=[]
    review=[]
    def issue(s): errors.append(s)
    if before.get("schema")!="C01-MESH-TOPOLOGY-1.0" or after.get("schema")!="C01-MESH-TOPOLOGY-1.0":
        issue("REPORT_SCHEMA_MISMATCH")
    if before.get("asset_id")!=after.get("asset_id"):
        issue("ASSET_ID_CHANGED")
    if before.get("stage")!="BEFORE" or after.get("stage")!="AFTER":
        issue("STAGE_ORDER_INVALID")
    if before.get("source_sha256") is None or after.get("source_sha256") is None:
        issue("SOURCE_HASH_MISSING")
    if repair_claimed and before.get("source_sha256")==after.get("source_sha256"):
        issue("REPAIR_CLAIM_WITH_IDENTICAL_SOURCE_BYTES")
    left={a.get("object"):a for a in before.get("object_data", [])}
    right={a.get("object"):a for a in after.get("object_data", [])}
    if not left or not right:
        issue("EMPTY_OBJECT_SET")
    if set(left)!=set(right):
        issue("OBJECT_HIERARCHY_CHANGED")
    for name in sorted(set(left)&set(right)):
        old=left[name]
        new=right[name]
        if old.get("parent")!=new.get("parent"):
            issue(name+":PARENT_CHANGED")
        if old.get("material_slots")!=new.get("material_slots"):
            issue(name+":MATERIAL_SLOTS_CHANGED")
        if set(m["name"] for m in old.get("uv_maps",[]))!=set(m["name"] for m in new.get("uv_maps",[])):
            issue(name+":UV_MAP_NAMES_CHANGED")
        for field in ("local_aabb_xyz","world_object_dimensions_xyz"):
            x,y=old.get(field),new.get(field)
            try:
                if field=="local_aabb_xyz":
                    x=[v for pair in x for v in pair]
                    y=[v for pair in y for v in pair]
                if len(x)!=len(y) or max(abs(a-b) for a,b in zip(x,y))>DIM_TOL:
                    issue(name+":"+field.upper()+"_CHANGED")
            except (ValueError, TypeError):
                issue(name+":"+field.upper()+"_MALFORMED")
        ot,nt=old.get("transform",{}),new.get("transform",{})
        for key in ("local_scale","local_rotation_euler","matrix_world"):
            a,b=ot.get(key),nt.get(key)
            if key=="matrix_world":
                if a:a=[n for row in a for n in row]
                if b:b=[n for row in b for n in row]
            if not a or not b or len(a)!=len(b) or max(abs(i-j) for i,j in zip(a,b))>DIM_TOL:
                issue(name+":TRANSFORM_"+key.upper()+"_CHANGED")
        metrics=new.get("mesh_issues",{})
        allowed={(e["object"],e["metric"]) for e in after.get("exceptions_declared",[]) if
                 e.get("classification")=="INTENTIONAL_UNVERIFIED" and e.get("reason")}
        for metric in HARD:
            if isinstance(metrics.get(metric),int) and metrics[metric]>0 and (name,metric) not in allowed:
                issue(name+":PERSISTENT_"+metric.upper())
            if (name,metric) in allowed:
                review.append(name+":EXCEPTION_NOT_INDEPENDENTLY_APPROVED_"+metric)
        boundary=metrics.get("boundary_edges")
        if isinstance(boundary,int) and boundary>0:
            if (name,"boundary_edges") not in allowed:
                review.append(name+":OPEN_BOUNDARY_REQUIRES_EXPLICIT_EXCEPTION")
            else:
                review.append(name+":OPEN_BOUNDARY_EXCEPTION_REQUIRES_REVIEW")
        for metric in CANDIDATES:
            if isinstance(metrics.get(metric),int) and metrics[metric]>0:
                review.append(name+":CANDIDATE_"+metric.upper())
    state="FAIL" if errors else "REVIEW_REQUIRED"
    return dict(asset_id=after.get("asset_id"),status=state,geometry_final_qa="NOT_APPROVED",
                independent_qa="NOT_RUN",fbx_roundtrip="NOT_RUN",unity="NOT_RUN",
                errors=sorted(set(errors)),review_items=sorted(set(review)),
                note="Review must inspect original .blend with intentional exceptions and actual FBX/Unity evidence; does not approve assets.")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("before",type=Path)
    p.add_argument("after",type=Path)
    p.add_argument("--repair-claimed",action="store_true")
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=compare(json.loads(a.before.read_text(encoding="utf8")),
                   json.loads(a.after.read_text(encoding="utf8")),a.repair_claimed)
    s=json.dumps(result,indent=2,ensure_ascii=False)
    print(s)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(s+"\n",encoding="utf8")
    raise SystemExit(1 if result["status"]=="FAIL" else 0)


if __name__=="__main__":
    main()
