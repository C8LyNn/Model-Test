#!/usr/bin/env python3
"""C01-01 Wave02 immutable-contract and supplier-manifest preflight.

Not an FBX importer, Blender execution, Unity execution, or independent QA approval.
Requires real files and byte hashes for READY_FOR_INDEPENDENT_QA. Python stdlib.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

STATUS = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}
REQUIRED = ("blend", "fbx", "unity_prefab", "preview_front", "preview_side", "preview_top")
EPS = 1e-8


def vec3(v):
    return isinstance(v, (list, tuple)) and len(v) == 3 and all(
        type(n) in (int, float) and math.isfinite(n) for n in v)


def near(a, b, tolerance):
    return vec3(a) and vec3(b) and all(abs(x-y) <= tolerance for x, y in zip(a, b))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def bbox(profile, wdh):
    w, d, h = wdh
    if profile == "floor":
        return [[-w/2, 0, -d/2], [w/2, h, d/2]]
    if profile == "wall":
        return [[-w/2, -h/2, -d], [w/2, h/2, 0]]
    if profile == "ceiling":
        return [[-w/2, -h, -d/2], [w/2, 0, d/2]]
    if profile == "rail":
        return [[0, -h/2, -d/2], [w, h/2, d/2]]
    if profile == "elbow":
        if abs(w-.62) < 1e-8 and abs(d-.62) < 1e-8 and abs(h-.18) < 1e-8:
            return [[-.50,-.09,-.12],[.12,.09,.50]]
        raise ValueError("Elbow nominal class must be 0.62x0.62x0.18")
    raise ValueError("Unknown pivot profile")


def check_contract(w2, w1):
    errors = []
    if w2.get("extends_contract_id") != w1.get("contract_id"):
        errors.append("INCOMPATIBLE_WAVE01_CONTRACT")
    a = w2.get("assets", [])
    ids = [x.get("id") for x in a if isinstance(x, dict)]
    if len(ids) != 20 or len(set(ids)) != 20:
        errors.append("WAVE02_IDS_NOT_EXACTLY_20")
    expected = {f"P{owner}-{n:02d}" for owner in range(15,19) for n in range(4,8)} | {f"P19-{n:02d}" for n in range(5,9)}
    if set(ids) != expected:
        errors.append("WAVE02_ID_COVERAGE_WRONG")
    earlier = {x["id"] for x in w1.get("assets", [])}
    if len(earlier) != 16 or len(earlier & set(ids)):
        errors.append("WAVE01_ID_CONFLICT")
    if set(w2.get("asset_ids_wave01_reserved", [])) != earlier:
        errors.append("WAVE01_RESERVATIONS_WRONG")
    if w2.get("technical_reference", {}).get("metres_per_unity_unit") != 1:
        errors.append("UNIT_CONTRACT_CHANGED")
    if w2.get("technical_reference", {}).get("wdh_to_xyz") != ["X","Z","Y"]:
        errors.append("AXIS_CONTRACT_CHANGED")
    if w2.get("technical_reference", {}).get("root_scale") != [1,1,1]:
        errors.append("ROOT_SCALE_CHANGED")
    allowed = set(w2["materials"]["allowed_families"])
    for x in a:
        aid = x["id"]
        dims = x.get("nominal_wdh_m")
        if not vec3(dims) or any(t<=0 for t in dims):
            errors.append(aid+":INVALID_DIMS")
            continue
        try:
            bounds = bbox(x["pivot_profile"], dims)
        except (KeyError, ValueError):
            errors.append(aid+":UNSUPPORTED_PIVOT")
            continue
        actual = x.get("reference_bounds_xyz_m")
        if not isinstance(actual,list) or len(actual)!=2 or not near(bounds[0],actual[0],EPS) or not near(bounds[1],actual[1],EPS):
            errors.append(aid+":INVALID_BOUNDS")
        if x.get("owner") != "C01-"+aid[1:3] or x.get("issue") != int(aid[1:3])-12:
            errors.append(aid+":OWNERSHIP_MISMATCH")
        materials = x.get("materials", [])
        if not isinstance(materials,list) or not 1<=len(materials)<=min(4,x.get("max_material_slots",0)) or len(set(materials))!=len(materials) or set(materials)-allowed:
            errors.append(aid+":MATERIAL_PALETTE_WRONG")
        if not x.get("required_children") or not x.get("mount_surfaces"):
            errors.append(aid+":CHILD_OR_MOUNT_MISSING")
    s = next((x for x in a if x["id"]=="P15-04"), None)
    e = next((x for x in a if x["id"]=="P15-05"), None)
    if not s or not e or len(s.get("ports", [])) != 2 or len(e.get("ports", [])) != 2:
        errors.append("TRAY_PORT_COUNT")
    else:
        def valid_normal(port):
            n = port["outward_normal"]
            return vec3(n) and abs(dot(n,n)-1)<EPS
        if not all(valid_normal(p) for p in s["ports"]+e["ports"]):
            errors.append("TRAY_PORT_NORMAL_INVALID")
        if not near(s["ports"][1]["local_xyz_m"],[3,0,0],EPS):
            errors.append("TRAY_STRAIGHT_ENDPOINT_INVALID")
        # Corner root at (3.5,0,0). Its A port must mate the straight's B at (3,0,0).
        root = [3.5,0,0]
        corner_a = [root[j]+e["ports"][0]["local_xyz_m"][j] for j in range(3)]
        if not near(corner_a,s["ports"][1]["local_xyz_m"],EPS):
            errors.append("TRAY_CORNER_A_POSITION_MISMATCH")
        if not near(e["ports"][0]["outward_normal"],[-v for v in s["ports"][1]["outward_normal"]],EPS):
            errors.append("TRAY_CORNER_A_AXIS_MISMATCH")
        # Following straight start normal = -X; rotated Y=-90° -> -Z, opposite elbow B +Z.
        corner_b = [root[j]+e["ports"][1]["local_xyz_m"][j] for j in range(3)]
        if not near(corner_b,[3.5,0,.5],EPS) or not near(e["ports"][1]["outward_normal"],[0,0,1],EPS):
            errors.append("TRAY_CORNER_B_MISMATCH")
        if s["ports"][0]["aperture_yz_m"]!=e["ports"][0]["aperture_yz_m"] or e["ports"][0]["aperture_yz_m"]!=e["ports"][1]["aperture_yz_m"]:
            errors.append("TRAY_PORT_SIZE_MISMATCH")
    return errors


def check_manifest(m, spec, root):
    errors, warnings = [], []
    if not isinstance(m,dict):
        return dict(static="FAIL",delivery="BLOCKED",errors=["NOT_OBJECT"],warnings=[])
    if m.get("contract_id") != spec["contract_id"]:
        errors.append("WRONG_CONTRACT")
    ids = {x["id"]:x for x in spec["assets"]}
    aid = m.get("asset_id")
    if aid not in ids:
        return dict(static="FAIL",delivery="BLOCKED",errors=["UNKNOWN_ASSET"],warnings=[])
    ref = ids[aid]
    if m.get("owner_thread") != ref["owner"]:
        errors.append("WRONG_OWNER")
    if m.get("pivot_profile") != ref["pivot_profile"]:
        errors.append("WRONG_PIVOT_PROFILE")
    if m.get("mount_surface") not in ref["mount_surfaces"]:
        errors.append("INVALID_MOUNT_SURFACE")
    if not near(m.get("root_scale_xyz"),[1,1,1],spec["tolerances"]["scale"]):
        errors.append("NON_UNIT_SCALE")
    if not near(m.get("root_rotation_euler_xyz"),[0,0,0],.01):
        errors.append("NON_ZERO_ROOT_ROTATION")
    if not near(m.get("pivot_local_xyz_m"),[0,0,0],spec["tolerances"]["pivot_m"]):
        errors.append("PIVOT_OFFSET")
    dims = m.get("measured_wdh_m")
    if not vec3(dims) or any(x<=0 for x in dims):
        errors.append("INVALID_DIMS")
    else:
        if max(abs(x-y) for x,y in zip(dims,ref["nominal_wdh_m"])) > spec["tolerances"]["nominal_overshoot_requires_approval_m"]:
            ex = m.get("dimension_exception",{})
            if not isinstance(ex,dict) or not ex.get("c01_01_approval_ref") or not ex.get("reason"):
                errors.append("UNAPPROVED_DIMENSION_VARIANCE")
        if ref["pivot_profile"]=="elbow" and not near(dims,ref["nominal_wdh_m"],spec["tolerances"]["dimension_m"]):
            errors.append("ELBOW_PROFILE_CHANGE_REQUIRES_NEW_CLASS")
        else:
            if ref["pivot_profile"]=="elbow":
                expected = ref["reference_bounds_xyz_m"]
            else:
                expected = bbox(ref["pivot_profile"],dims)
            actual = m.get("mesh_bounds_xyz_m")
            if not isinstance(actual,list) or len(actual)!=2 or not near(actual[0],expected[0],spec["tolerances"]["dimension_m"]) or not near(actual[1],expected[1],spec["tolerances"]["dimension_m"]):
                errors.append("MESH_BOUNDS_OUTSIDE_PIVOT")
    mats = m.get("materials")
    if not isinstance(mats,list) or not 1<=len(mats)<=ref["max_material_slots"] or len(set(mats))!=len(mats) or set(mats)-set(spec["materials"]["allowed_families"]):
        errors.append("INVALID_MATERIALS")
    children = m.get("children")
    if not isinstance(children,list) or not set(ref["required_children"]).issubset(set(children)):
        errors.append("REQUIRED_CHILDREN_MISSING")
    if ref.get("moving_parts_policy"):
        mp = m.get("moving_parts")
        if not isinstance(mp,list) or not mp or not all(isinstance(p,dict) and vec3(p.get("pivot_local_xyz_m")) for p in mp):
            errors.append("MOVING_PIVOT_MISSING")
        if not m.get("swept_volume_evidence"):
            warnings.append("SWEPT_VOLUME_EVIDENCE_MISSING")
    required_sockets = {"SOCKET_MOUNT", *ref.get("required_sockets", [])}
    socket_names = m.get("sockets", [])
    if not isinstance(socket_names, list) or not required_sockets.issubset(set(socket_names)):
        errors.append("REQUIRED_SOCKETS_MISSING")
    if ref.get("pickup_policy") and "SOCKET_GRIP" not in socket_names:
        errors.append("GRIP_SOCKET_MISSING")
    if ref.get("ports"):
        ports = m.get("ports",[])
        if not isinstance(ports,list) or len(ports)!=len(ref["ports"]):
            errors.append("PORT_COUNT_MISMATCH")
        else:
            for idx,(a,b) in enumerate(zip(ports,ref["ports"])):
                if a.get("name")!=b["name"] or not near(a.get("local_xyz_m"),b["local_xyz_m"],spec["tolerances"]["port_position_m"]) or not near(a.get("outward_normal"),b["outward_normal"],.001):
                    errors.append("PORT_"+str(idx)+"_MISMATCH")
    if type(m.get("triangle_count")) is not int or m["triangle_count"]<=0:
        errors.append("TRIANGLES_INVALID")
    if not isinstance(m.get("colliders"),list) or not m["colliders"]:
        errors.append("COLLIDERS_MISSING")
    qa = m.get("qa",{})
    if not isinstance(qa,dict) or any(qa.get(k) not in STATUS for k in spec["qa_fields"]):
        errors.append("QA_FIELDS_INVALID")
        qa = {}
    files = m.get("files",{})
    if not isinstance(files,dict):
        errors.append("FILES_NOT_OBJECT")
        files = {}
    all_present = True
    root_resolved = root.resolve()
    for key in REQUIRED:
        entry=files.get(key)
        if not isinstance(entry,dict) or not entry.get("path") or not isinstance(entry.get("sha256"),str) or len(entry["sha256"])!=64:
            all_present=False
            warnings.append("EVIDENCE_MISSING_"+key.upper())
            continue
        candidate = (root / entry["path"]).resolve()
        if not candidate.is_relative_to(root_resolved):
            errors.append("PATH_TRAVERSAL_"+key.upper())
            all_present=False
            continue
        if not candidate.is_file():
            warnings.append("NOT_PRESENT_"+key.upper())
            all_present=False
            continue
        raw=candidate.read_bytes()
        if raw.startswith(b"version https://git-lfs.github.com/spec/v1"):
            warnings.append("UNHYDRATED_LFS_"+key.upper())
            all_present=False
            continue
        if hashlib.sha256(raw).hexdigest()!=entry["sha256"].lower():
            errors.append("HASH_MISMATCH_"+key.upper())
            all_present=False
    static = "FAIL" if errors else "PASS"
    return dict(asset_id=aid,static=static,
                delivery="READY_FOR_INDEPENDENT_QA" if static=="PASS" and all_present and all(qa.get(x)=="PASS" for x in spec["qa_fields"] if x!="independent") else "BLOCKED",
                approval="C01-02_APPROVED" if qa.get("independent")=="PASS" and all_present and static=="PASS" and isinstance(m.get("independent_review"),dict) and m["independent_review"].get("owner")=="C01-02" and m["independent_review"].get("report_url") and m["independent_review"].get("source_commit_sha") else "NOT_APPROVED",
                errors=errors,warnings=warnings)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",type=Path,default=Path(__file__).resolve().parents[2]/"Docs/C01InteriorProps/prop_contract_wave02.json")
    ap.add_argument("--wave01-contract",type=Path,default=Path(__file__).resolve().parents[2]/"Docs/C01InteriorProps/prop_contract.json")
    ap.add_argument("--manifest",type=Path)
    ap.add_argument("--root",type=Path)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    w2=json.loads(a.contract.read_text(encoding="utf8"))
    w1=json.loads(a.wave01_contract.read_text(encoding="utf8"))
    errs=check_contract(w2,w1)
    report={"contract_errors":errs,"contract_status":"FAIL" if errs else "PASS"}
    if a.manifest:
        report["manifest"]=check_manifest(json.loads(a.manifest.read_text(encoding="utf8")),w2,a.root or a.manifest.parent)
    report["status"]="FAIL" if errs or report.get("manifest",{}).get("static")=="FAIL" else "PASS"
    report["note"]="STATIC ONLY. NOT Blender, FBX roundtrip, Unity, or C01-02 acceptance."
    msg=json.dumps(report,ensure_ascii=False,indent=2)
    print(msg)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(msg+"\n",encoding="utf8")
    raise SystemExit(1 if report["status"]=="FAIL" else 0)

if __name__=="__main__":
    main()
