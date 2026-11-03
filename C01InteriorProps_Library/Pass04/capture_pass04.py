#!/usr/bin/env python3
"""C01-03 PASS04 read-only byte capture. Does NOT inspect topology or grant QA PASS."""
import argparse, hashlib, json, re, subprocess
from pathlib import Path

BASE=Path(__file__).resolve().parent
LEDGER=BASE/"repair_ledger.json"
H64=re.compile(r"^[0-9a-f]{64}$")
H40=re.compile(r"^[0-9a-f]{40}$")
P0={"P19-05","P19-07","P19-08"}
def load():
    return json.loads(LEDGER.read_text(encoding="utf-8"))
def validate(doc):
    assets=doc["assets"]
    expected={f"C01-P{g}-{i:02d}" for g in range(15,20) for i in (range(1,9) if g==19 else range(1,8))}
    if doc.get("schema")!="C01-MESH-REPAIR-PASS04-1.0" or len(assets)!=36 or {a["asset_id"] for a in assets}!=expected:
        raise ValueError("36 canonical IDs required")
    if len({a["asset_id"] for a in assets})!=36: raise ValueError("duplicate IDs")
    for a in assets:
        ident=a["code"]; before=a["before"]; after=a["after_candidate"]; qa=a["independent_qa"]
        if a["asset_id"]!="C01-"+ident or not H40.fullmatch(before["producer_commit"]) or not H40.fullmatch(after["producer_commit"]):
            raise ValueError(f"{ident}: invalid immutable refs")
        if (a["priority"]=="P0_QA_TRIANGULATION") != (ident in P0):
            raise ValueError(f"{ident}: wrong critical priority")
        for name in ("blend_sha256","fbx_sha256"):
            if before[name] is not None and not H64.fullmatch(before[name]): raise ValueError(f"{ident}: bad immutable BEFORE SHA")
            if after[name] is not None:
                if not H64.fullmatch(after[name]): raise ValueError(f"{ident}: bad candidate AFTER SHA")
                evidence=after.get("byte_evidence")
                if not evidence or not isinstance(evidence.get("run_id"), int) or not isinstance(evidence.get("job_id"),int):
                    raise ValueError(f"{ident}: AFTER hash missing reproducible GitHub Actions evidence")
        if ident in P0 and qa["status"] != "FAIL_P1_TRIANGULATION_AT_PRIOR_INDEPENDENT_SHA" and not qa["signed_after_fbx_sha256"]:
            raise ValueError(f"{ident}: prematurely removed P1 QA blocker")
        if a["release_status"]=="APPROVED":
            if not H64.fullmatch(after.get("fbx_sha256") or "") or not H64.fullmatch(after.get("blend_sha256") or ""):
                raise ValueError(f"{ident}: no verified binary export/source")
            if qa["status"]!="PASS" or qa["signed_after_fbx_sha256"]!=after["fbx_sha256"]:
                raise ValueError(f"{ident}: missing C01-02 signed exact FBX SHA")
            if after["blender_roundtrip"]!="PASS" or after["unity"]!="PASS":
                raise ValueError(f"{ident}: real Blender and Unity gates missing")
    return assets

def inspect(root, relative, kind):
    rec={"path":relative,"sha256":None,"size_bytes":None,"status":"PATH_NOT_REGISTERED"}
    if relative is None:return rec
    parts=relative.split("/")
    if "\\" in relative or any(not p or p in {".",".."} for p in parts) or Path(relative).is_absolute():
        raise ValueError(f"unsafe asset path: {relative}")
    target=(root.resolve()/relative).resolve()
    if not target.is_relative_to(root.resolve()): raise ValueError("path escapes producer checkout")
    if not target.is_file():
        rec["status"]="FILE_NOT_PRESENT"
        return rec
    digest=hashlib.sha256()
    with target.open("rb") as stream:
        header=stream.read(256)
        stream.seek(0)
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            digest.update(chunk)
    rec["size_bytes"]=target.stat().st_size
    if not rec["size_bytes"]:rec["status"]="EMPTY"
    elif header.startswith(b"version https://git-lfs.github.com/spec/v1"):rec["status"]="UNHYDRATED_LFS"
    elif kind=="blend" and not header.startswith(b"BLENDER"):rec["status"]="INVALID_BLEND_HEADER"
    elif kind=="fbx" and not header.startswith(b"Kaydara FBX Binary"):rec["status"]="NOT_BINARY_FBX"
    else:
        rec["sha256"]=digest.hexdigest()
        rec["status"]="BYTE_SHA256_VERIFIED_NOT_TOPOLOGY_QA"
    return rec

def capture(doc,asset_id,checkout):
    asset=next(a for a in validate(doc) if a["code"]==asset_id)
    head=subprocess.check_output(["git","-C",str(checkout),"rev-parse","HEAD"],text=True).strip()
    if head!=asset["after_candidate"]["producer_commit"]:raise ValueError("producer commit changed; refusing unpinned file")
    after=asset["after_candidate"]
    result={"asset_id":asset["asset_id"],"producer_commit":head,"role":"AFTER_CANDIDATE_NOT_APPROVED",
        "blend":inspect(checkout,after["blend_path"],"blend"),
        "fbx":inspect(checkout,after["fbx_path"],"fbx"),
        "baseline_compare":{},
        "topology":"NOT_RUN","independent_qa":asset["independent_qa"]["status"],"unity":"NOT_RUN"}
    for kind in ("blend","fbx"):
        h=result[kind]["sha256"]; before=asset["before"][kind+"_sha256"]
        result["baseline_compare"][kind] = "MISSING" if h is None else ("SAME_BYTES" if h==before else "DIFFERENT_BYTES" if before is not None else "NO_BEFORE_HASH")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("operation",choices=["validate","capture","release"])
    ap.add_argument("--asset");ap.add_argument("--checkout",type=Path);ap.add_argument("--output",type=Path)
    args=ap.parse_args();doc=load()
    try:
        assets=validate(doc)
        if args.operation=="validate":
            print("PASS: 36 IDs; 3 P19 export blockers preserved. NOT mesh or Unity QA.")
            return 0
        if args.operation=="release":
            if any(a["release_status"]!="APPROVED" for a in assets):
                print("BLOCKED: independent C01-02 approval incomplete")
                return 2
            print("Registry release gate satisfied; C01-00 final acceptance still required")
            return 0
        if not all((args.asset,args.checkout,args.output)):raise ValueError("--asset --checkout --output required")
        r=capture(doc,args.asset,args.checkout)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(r))
        return 0 if all(r[role]["sha256"] for role in ("blend","fbx")) else 2
    except (ValueError,StopIteration) as e:
        print("BLOCKED:",e);return 2

if __name__=="__main__":raise SystemExit(main())
