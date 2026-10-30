#!/usr/bin/env python3
"""Fail-closed binary glTF verification in CI, including normals, UV0 and bounds."""
import json,base64,math,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for id in ("P17-04","P17-05","P17-06","P17-07"):
 spec=json.loads((R/"Specs"/(id+".json")).read_text())
 g=json.loads((R.parent/"Assets/C01InteriorProps/W02/Models"/(id+".gltf")).read_text())
 buf=base64.b64decode(g["buffers"][0]["uri"].split(",",1)[1])
 assert len(buf)==g["buffers"][0]["byteLength"]
 assert len(g["materials"])<=4 and len(g["meshes"])==spec["mesh_parts"]
 node={n["name"]:n for n in g["nodes"]}
 assert id+"_ROOT" in node
 for p in spec["moving_parts"]: assert p["name"] in node
 lo=[math.inf]*3;hi=[-math.inf]*3;tri=0
 def access(i):
  a=g["accessors"][i];v=g["bufferViews"][a["bufferView"]]
  return a["count"],v.get("byteOffset",0)+a.get("byteOffset",0)
 for m in spec["parts"]:
  prim=g["meshes"][node[m["name"]]["mesh"]]["primitives"][0]
  assert "TEXCOORD_0" in prim["attributes"]
  n,ps=access(prim["attributes"]["POSITION"])
  nn,ns=access(prim["attributes"]["NORMAL"])
  nu,us=access(prim["attributes"]["TEXCOORD_0"])
  ni,ix=access(prim["indices"])
  assert n==nn==nu and ni%3==0
  verts=[struct.unpack_from("<fff",buf,ps+i*12) for i in range(n)]
  normals=[struct.unpack_from("<fff",buf,ns+i*12) for i in range(n)]
  uv=[struct.unpack_from("<ff",buf,us+i*8) for i in range(n)]
  ids=struct.unpack_from("<"+"H"*ni,buf,ix)
  assert all(math.isfinite(v) and -.001<=v<=1.001 for v2 in uv for v in v2)
  parent=next((x["p"] for x in spec["moving_parts"] if x["name"]==m["parent"]),[0,0,0])
  for v in verts:
   for k in range(3):
    x=v[k]+m["p"][k]+parent[k]
    lo[k]=min(lo[k],x);hi[k]=max(hi[k],x)
  for j in range(0,len(ids),3):
   a,b,c=[verts[ids[j+i]] for i in range(3)]
   v=[b[k]-a[k] for k in range(3)];w=[c[k]-a[k] for k in range(3)]
   cross=[v[1]*w[2]-v[2]*w[1],v[2]*w[0]-v[0]*w[2],v[0]*w[1]-v[1]*w[0]]
   assert math.hypot(*cross)>1e-9,(id,m["name"],"degenerate")
   assert sum(cross[k]*normals[ids[j]][k] for k in range(3))>1e-10,(id,m["name"],"normal")
   tri+=1
 d=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]
 assert all(abs(d[k]-spec["dimensions_WDH_m"][k])<.002 for k in range(3)),(id,d)
 assert tri==spec["triangle_count"],(id,tri)
 if spec["mount"]=="floor": assert abs(lo[1])<.001
 if spec["mount"]=="wall": assert abs(lo[2])<.001
 print("PASS STATIC",id,"tris",tri,"UV0",len(g["meshes"]), "dimensions WDH",d)
