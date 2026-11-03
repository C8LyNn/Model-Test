#!/usr/bin/env python3
"""C01-17 source QA: inspect real glTF instances, shared meshes, buffers and pivots.

Works with glTF Y-up, multiple embedded buffers, and T*R*S parent transforms.
No native Blender/Unity pass is implied by this static inspection.
"""
import base64
import json
import math
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"C01InteriorProps_Source"
MODELS=ROOT/"Assets/C01InteriorProps/Models"
DIM={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}
COMP={5121:("B",1),5123:("H",2),5125:("I",4),5126:("f",4)}

def read_accessor(g, buffers, index):
    a=g["accessors"][index]
    v=g["bufferViews"][a["bufferView"]]
    code,size=COMP[a["componentType"]]
    n=DIM[a["type"]]
    stride=v.get("byteStride",n*size)
    assert stride>=n*size,(index,"bad stride")
    data=buffers[v["buffer"]]
    start=v.get("byteOffset",0)+a.get("byteOffset",0)
    fmt="<"+code*n
    out=[]
    for i in range(a["count"]):
        pos=start+i*stride
        assert pos+n*size <= v.get("byteOffset",0)+v["byteLength"],(index,"accessor overflow")
        out.append(struct.unpack_from(fmt,data,pos))
    return out

def rot(q,p):
    x,y,z,w=q
    u=(x,y,z)
    def cross(a,b):
        return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    uv=cross(u,p)
    uuv=cross(u,uv)
    return [p[i]+2*(w*uv[i]+uuv[i]) for i in range(3)]

def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])

for asset in ("P17-01","P17-02","P17-03"):
    spec=json.loads((SRC/"Specs"/(asset+".json")).read_text(encoding="utf-8"))
    g=json.loads((MODELS/(asset+".gltf")).read_text(encoding="utf-8"))
    buffers=[base64.b64decode(b["uri"].split(",",1)[1],validate=True) for b in g["buffers"]]
    assert len(buffers)==len(g["buffers"])
    assert all(len(b)==item["byteLength"] for b,item in zip(buffers,g["buffers"]))
    assert len(g["materials"])<=4,(asset,"materials")
    parts={p["name"]:p for p in spec["children"]}
    assert len(parts)==len(spec["children"]),(asset,"duplicate spec child")
    assert len(g["nodes"])>0 and g["nodes"][0]["name"]==asset+"_ROOT"
    if asset=="P17-03":assert any(n["name"]=="LeverPivot" for n in g["nodes"])
    out={}
    lo=[math.inf]*3
    hi=[-math.inf]*3
    seen=set()
    triangles=0

    def visit(index,parent_transform):
        nonlocal_dummy = None
        global triangles
        assert index not in seen,(asset,"duplicate node reference",index)
        seen.add(index)
        node=g["nodes"][index]
        t=node.get("translation",[0,0,0])
        s=node.get("scale",[1,1,1])
        q=node.get("rotation",[0,0,0,1])
        def xf(p):
            loc=rot(q,[float(p[i])*s[i] for i in range(3)])
            return parent_transform([loc[i]+t[i] for i in range(3)])
        if "mesh" in node:
            assert node["name"] in parts,(asset,"undeclared part",node["name"])
            mi=node["mesh"]
            assert 0<=mi<len(g["meshes"]),(asset,node["name"],"mesh index")
            primitives=g["meshes"][mi]["primitives"]
            assert primitives,(asset,node["name"],"empty primitive list")
            count=0
            for prim in primitives:
                assert prim.get("mode",4)==4,(asset,node["name"],"nontriangles")
                at=prim["attributes"]
                assert all(k in at for k in ("POSITION","NORMAL","TEXCOORD_0"))
                p=read_accessor(g,buffers,at["POSITION"])
                normals=read_accessor(g,buffers,at["NORMAL"])
                uv=read_accessor(g,buffers,at["TEXCOORD_0"])
                indices=[i[0] for i in read_accessor(g,buffers,prim["indices"])]
                assert len(p)==len(normals)==len(uv)
                assert len(indices)%3==0
                assert all(math.isfinite(c) for vv in p+normals+uv for c in vv)
                assert all(sum(x*x for x in n)>1e-10 for n in normals)
                assert all(0<=i<len(p) for i in indices)
                world=[xf(v) for v in p]
                for wv in world:
                    for axis in range(3):
                        lo[axis]=min(lo[axis],wv[axis])
                        hi[axis]=max(hi[axis],wv[axis])
                for k in range(0,len(indices),3):
                    a,b,c=(world[indices[k+j]] for j in range(3))
                    u=[b[j]-a[j] for j in range(3)]
                    v=[c[j]-a[j] for j in range(3)]
                    cr=cross(u,v)
                    assert sum(x*x for x in cr)>1e-19,(asset,node["name"],"degenerate triangle",k//3)
                count+=len(indices)//3
            out[node["name"]]=count
            triangles+=count
        for child in node.get("children",[]):
            visit(child,xf)
    visit(0,lambda x:x)
    assert len(out)==len(parts),(asset,"instance count",len(out),len(parts),sorted(set(parts)-set(out)))
    assert set(out)==set(parts),(asset,"parts differ",sorted(set(out)^set(parts)))
    assert len(seen)==len(g["nodes"]),(asset,"unreachable nodes")
    actual=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]
    assert all(abs(actual[i]-spec["dimensions"][i])<0.003 for i in range(3)),(asset,"Y-up dims",actual,spec["dimensions"])
    assert triangles==spec["expectedTriangleCount"],(asset,"triangles",triangles,spec["expectedTriangleCount"])
    if spec["mount"]=="floor":assert abs(lo[1])<0.001,(asset,"floor pivot",lo)
    if str(spec["mount"]).startswith("wall"):assert abs(lo[2])<0.001,(asset,"wall pivot",lo)
    if asset=="P17-03":
        node=next(n for n in g["nodes"] if n["name"]=="LeverPivot")
        childnames={g["nodes"][i]["name"] for i in node.get("children",[])}
        assert childnames=={"LeverShaft","LeverGrip","PivotAnchorVisual"},(asset,"moving pivot children",childnames)
    print("PASS SOURCE",asset,"instances",len(out),"unique_meshes",len(g["meshes"]),
          "triangles",triangles,"dimensions_WDH",actual,"buffers",len(buffers),flush=True)
