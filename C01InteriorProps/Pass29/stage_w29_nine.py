#!/usr/bin/env python3
"""Read and hydrate exactly nine allowlisted FBX LFS blobs; no producer checkout, no W04."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--repo",default=".")
p.add_argument("--apply",action="store_true")
args=p.parse_args();root=Path(args.repo).resolve()
m=json.loads((Path(__file__).resolve().parent/"W29_SIGNED_NONDOOR_NINE.json").read_text())
ids={"W01","F01","C01","P16-01","P17-02","P18-01","P19-03","P15-03","P18-03"}
assert m["schema"]=="C01-W29-SIGNED-FBX-9-V1" and len(m["inputs"])==9 and {x["id"] for x in m["inputs"]}==ids
assert (root/".git").exists() and (root/"ProjectSettings/ProjectVersion.txt").exists()
def call(*cmd,stdin=None):
    proc=subprocess.run(cmd,cwd=root,input=stdin,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if proc.returncode:raise RuntimeError("Git/LFS command failed or not authorized")
    return proc.stdout
def sha(data):return hashlib.sha256(data).hexdigest()
for x in m["inputs"]:
    assert re.fullmatch(r"[a-f0-9]{40}",x["commit"])
    assert re.fullmatch(r"[a-f0-9]{64}",x["sha"])
    assert x["path"].endswith(".fbx") and ".." not in x["path"]
    assert not Path(x["path"]).name.startswith(("D01","D02","W04"))
if not args.apply:
    print("PREVIEW: nine exact signed FBX; no source downloaded; Unity NOT_RUN")
    for x in m["inputs"]:print(x["id"],x["sha"])
    raise SystemExit(0)
data=[]
for x in m["inputs"]:
    call("git","fetch","--no-tags","origin",x["branch"])
    pointer=call("git","show",x["commit"]+":"+x["path"])
    lines=pointer.decode("utf-8","strict").splitlines()
    assert lines[0]=="version https://git-lfs.github.com/spec/v1"
    assert "oid sha256:"+x["sha"] in lines and "size "+str(x["bytes"]) in lines
    # Smudge the specific pinned object ONLY; never checkout W04/source branch.
    fb=call("git","lfs","smudge",stdin=pointer)
    if not fb.startswith(b"Kaydara FBX Binary") or len(fb)!=x["bytes"] or sha(fb)!=x["sha"]:
        raise RuntimeError(x["id"]+" physical FBX signature/SHA/size mismatch")
    data.append((x,fb))
for x,fb in data:
    f=root/"Assets"/"C01InteriorProps"/"Pass29Incoming"/x["id"]/(x["id"]+".fbx")
    if f.exists() and sha(f.read_bytes())!=x["sha"]:raise FileExistsError("Refuse to overwrite "+x["id"])
for x,fb in data:
    f=root/"Assets"/"C01InteriorProps"/"Pass29Incoming"/x["id"]/(x["id"]+".fbx")
    f.parent.mkdir(parents=True,exist_ok=True)
    if not f.exists():f.write_bytes(fb)
    assert sha(f.read_bytes())==x["sha"]
report=root/"C01InteriorProps_QA"/"PASS29"/"STAGED_NINE_PHYSICAL_SHA.json"
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps({"state":"SOURCE_ONLY","count":9,"unity":"NOT_RUN",
 "items":[{"id":x["id"],"sha256":x["sha"],"commit":x["commit"]} for x,_ in data]},indent=2)+"\n")
print("Signed physical FBX 9/9 staged. NOT Unity or release PASS.")
