#!/usr/bin/env python3
"""C01-15 PASS05: run EXACT committed PASS04 audit on hydrated real asset binaries.
No proxy models, no mesh writes, no success claim if Blender/FBX/QA is absent.
Run on Windows, macOS or Linux from a checkout of an EXISTING PR branch.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, shutil, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parents[3]
OWNERS = {
    "W01": {"branch": "c01/props-15-installations", "dir": "P15",
            "ids": ["P15-01","P15-02","P15-03"]},
    "W02": {"branch": "c01/props-15-installations-wave02", "dir": "P15Wave02",
            "ids": ["P15-04","P15-05","P15-06","P15-07"]},
}
AUDIT = REPO/"Tools"/"C01MeshPass04"/"P15"/"audit_native.py"

def execute(argv, env=None):
    r=subprocess.run(argv,cwd=str(REPO),env=env,text=True,capture_output=True,check=False)
    return r.returncode, r.stdout, r.stderr

def sha256(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for piece in iter(lambda:f.read(1<<20),b""):h.update(piece)
    return h.hexdigest()

def fail(message):
    print("PASS05 BLOCKED: "+message,file=sys.stderr)
    return 2

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wave",choices=("W01","W02"),required=True)
    ap.add_argument("--blender",help="Full path to Blender 4.x executable; default PATH or BLENDER_BIN")
    ap.add_argument("--no-hydrate",action="store_true",help="Only when verified Git LFS bytes already exist")
    a=ap.parse_args()
    s=OWNERS[a.wave]
    base=REPO/"Assets"/"C01InteriorProps"/s["dir"]
    qa=base/"QA"/"Pass04"
    report=qa/"PASS04_PRECHECK_SOURCE_OIDS.json"
    if not report.exists():return fail("Missing SHA-pinned PASS04 producer precheck "+str(report))
    info=json.loads(report.read_text(encoding="utf-8"))
    records=info.get("model_records",info.get("records"))
    if not records or [x["id"] for x in records]!=s["ids"]:
        return fail("Unexpected ID list or missing per-asset SHA in precheck")
    code,out,err=execute(["git","rev-parse","--abbrev-ref","HEAD"])
    if code or out.strip()!=s["branch"]:
        return fail("Wrong branch; expected "+s["branch"]+", got "+out.strip())
    if not a.no_hydrate:
        code,out,err=execute(["git","lfs","pull"])
        if code:return fail("git lfs pull failed: "+err[-1500:])
    blender=a.blender or os.getenv("BLENDER_BIN") or shutil.which("blender")
    if not blender and os.name=="nt":
        for version in ("4.5","4.4","4.3","4.2","4.1","4.0"):
            candidate=pathlib.Path(os.environ.get("ProgramFiles",r"C:\Program Files"))/"Blender Foundation"/("Blender "+version)/"blender.exe"
            if candidate.is_file():blender=str(candidate);break
    if not blender:return fail("Blender binary not installed; set --blender or BLENDER_BIN")
    code,out,err=execute([blender,"--version"])
    if code:return fail("Blender --version failed: "+err[-1500:])
    version=out.splitlines()[0] if out else ""
    if not version.startswith("Blender 4."):return fail("Require Blender 4.x, got "+version)
    receipt={}
    for r in records:
        aid=r["id"]
        paths={
          "source_blend":base/"Sources"/"Blender"/(aid+".blend"),
          "binary_fbx":base/"Models"/"FBX"/(aid+".fbx"),
        }
        hashes={}
        for key,p in paths.items():
            if not p.is_file():return fail("Missing actual file "+str(p))
            magic=p.open("rb").read(24)
            if key=="source_blend" and not magic.startswith(b"BLENDER-"):
                return fail("Not a native .blend (maybe LFS pointer): "+str(p))
            if key=="binary_fbx" and not magic.startswith(b"Kaydara FBX Binary"):
                return fail("Not a binary Blender FBX (maybe LFS pointer): "+str(p))
            got=sha256(p)
            if got!=r[key]["sha256"]:
                return fail(f"{aid} {key}: unexpected SHA256 {got} != {r[key]['sha256']}")
            hashes[key]=got
        receipt[aid]=hashes
    env=dict(os.environ,C01_P15_WAVE=a.wave)
    cmd=[blender,"--background","--python",str(AUDIT)]
    code,out,err=execute(cmd,env=env)
    qa.mkdir(parents=True,exist_ok=True)
    (qa/"PASS05_BLENDER_STDOUT.txt").write_text(out,encoding="utf-8")
    (qa/"PASS05_BLENDER_STDERR.txt").write_text(err,encoding="utf-8")
    result={
      "schema":"C01_P15_PASS05_REAL_EXECUTION_V1",
      "recorded_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "branch":s["branch"],"wave":a.wave,"blender_version":version,
      "exact_command":cmd,"exit_code":code,
      "actual_hydrated_source_and_fbx_sha256":receipt,
      "unity":"NOT RUN","independent_C01_02_QA":"NOT RUN",
      "native_audit":"FAIL" if code else "PENDING_REPORT_VERIFICATION",
    }
    pass04=qa/"PASS04_SUMMARY.json"
    if code==0 and pass04.exists():
        data=json.loads(pass04.read_text(encoding="utf-8"))
        complete=(data.get("status")=="PASS" and set(data.get("models",{}))==set(s["ids"]))
        same=(all(
          data["models"][id]["source_sha256"]==receipt[id]["source_blend"]
          and data["models"][id]["fbx_sha256"]==receipt[id]["binary_fbx"]
          for id in s["ids"]
        ) if complete else False)
        if complete and same:
            result["native_audit"]="PASS_PRODUCER"
            result["fbx_roundtrip"]="PASS_PRODUCER"
            result["independent_C01_02_QA"]="NOT RUN"
            # Surface overlaps are REVIEW_REQUIRED, not automatically topology PASS.
            flagged=[id for id,metrics in data["models"].items()
                if metrics.get("self_overlap_candidate_count",0)
                or metrics.get("exact_cross_mesh_duplicate_triangle_pair_groups",0)]
            result["candidate_intersections_requires_review"]=flagged
        else:
            result["native_audit"]="FAIL_SHA_OR_RESULT_MISMATCH"
    result["status"]="PASS_PRODUCER" if result["native_audit"]=="PASS_PRODUCER" else "FAIL"
    (qa/"PASS05_EXECUTION.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    if result["status"]!="PASS_PRODUCER":return fail("Actual Blender audit failure; inspect PASS05_BLENDER_STDOUT/ERR and report")
    print("PASS05 Blender native source + binary FBX roundtrip checked:",len(s["ids"]),"models",version)
    print("Output:",qa/"PASS05_EXECUTION.json")
    print("C01-02 independent QA NOT RUN; Unity NOT RUN. No source files edited.")
    return 0

if __name__=="__main__":
    sys.exit(main())
