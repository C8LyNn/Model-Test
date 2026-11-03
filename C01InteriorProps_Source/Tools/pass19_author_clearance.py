#!/usr/bin/env python3
"""C01-17 W19: repair only P17-03 real indexed source, retaining twenty existing objects.
Remove solid material at movable LeverPivot sweep by physically forming TopCap
and LeverSocket as through-open rectangular, connected, closed mesh rings.
This script is deterministic and refuses to rewrite unexpected source versions.
"""
import base64
import collections
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GLTF=ROOT/"Assets/C01InteriorProps/Models/P17-03.gltf"
OBJ=ROOT/"C01InteriorProps_Source/MeshText/P17-03.obj.txt"
SPEC=ROOT/"C01InteriorProps_Source/Specs/P17-03.json"
LAYOUT={
    "TopCap":{"mesh":2,"outer":[.38,.048,.295],"x":[-.052,.052],"z":[-.082,.052]},
    "LeverSocket":{"mesh":6,"outer":[.135,.035,.135],"x":[-.05,.05],"z":[-.058,.058]},
}
def make_ring(cfg):
    sx,sy,sz=cfg["outer"]
    hx,hy,hz=sx/2,sy/2,sz/2
    x0,x1=cfg["x"]
    z0,z1=cfg["z"]
    assert -hx<x0<x1<hx and -hz<z0<z1<hz
    O=[(-hx,-hz),(-hx,hz),(hx,hz),(hx,-hz)]
    I=[(x0,z0),(x0,z1),(x1,z1),(x1,z0)]
    POS,NORM,UV,IDX=[],[],[],[]
    def q(verts,expected):
        a,b,c=verts[:3]
        u=[b[i]-a[i] for i in range(3)]
        v=[c[i]-a[i] for i in range(3)]
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        length=math.sqrt(sum(x*x for x in n))
        assert length>1e-9
        unit=[x/length for x in n]
        if expected=="+Y": assert unit[1]>.9999,unit
        if expected=="-Y": assert unit[1]<-.9999,unit
        st=len(POS)//3
        for p,uv in zip(verts,[(0,0),(1,0),(1,1),(0,1)]):
            POS.extend(p)
            NORM.extend(unit)
            UV.extend(uv)
        IDX.extend((st,st+1,st+2,st,st+2,st+3))
    for i in range(4):
        j=(i+1)%4
        top=lambda v:(v[0],hy,v[1])
        bot=lambda v:(v[0],-hy,v[1])
        q((top(O[i]),top(O[j]),top(I[j]),top(I[i])),"+Y")
        q((bot(O[i]),bot(I[i]),bot(I[j]),bot(O[j])),"-Y")
        q((bot(O[i]),bot(O[j]),top(O[j]),top(O[i])),"SIDE")
        q((bot(I[i]),top(I[i]),top(I[j]),bot(I[j])),"SIDE")
    assert len(POS)==192 and len(NORM)==192 and len(UV)==128 and len(IDX)==96
    return {"positions":POS,"normals":NORM,"uv":UV,"indices":IDX}

def get_acc(g,bb,ix):
    a=g["accessors"][ix]
    v=g["bufferViews"][a["bufferView"]]
    d=bb[v["buffer"]]
    comp={5126:("f",4),5123:("H",2)}[a["componentType"]]
    n={"VEC3":3,"VEC2":2,"SCALAR":1}[a["type"]]
    stride=v.get("byteStride",comp[1]*n)
    return [struct.unpack_from("<"+comp[0]*n,d,
        v.get("byteOffset",0)+a.get("byteOffset",0)+k*stride) for k in range(a["count"])]

def scene_tris(g):
    buffers=[base64.b64decode(x["uri"].split(",")[1]) for x in g["buffers"]]
    result=[]
    def rotate(q,p):
        x,y,z,w=q
        uv=(y*p[2]-z*p[1],z*p[0]-x*p[2],x*p[1]-y*p[0])
        uu=(y*uv[2]-z*uv[1],z*uv[0]-x*uv[2],x*uv[1]-y*uv[0])
        return [p[i]+2*(w*uv[i]+uu[i]) for i in range(3)]
    def visit(index,parent):
        node=g["nodes"][index]
        s=node.get("scale",[1,1,1])
        t=node.get("translation",[0,0,0])
        q=node.get("rotation",[0,0,0,1])
        def transform(p):
            rotated=rotate(q,[p[i]*s[i] for i in range(3)])
            return parent([rotated[i]+t[i] for i in range(3)])
        if "mesh" in node:
            for prim in g["meshes"][node["mesh"]]["primitives"]:
                p=[transform(x) for x in get_acc(g,buffers,prim["attributes"]["POSITION"])]
                uv=get_acc(g,buffers,prim["attributes"]["TEXCOORD_0"])
                norm=get_acc(g,buffers,prim["attributes"]["NORMAL"])
                ix=[v[0] for v in get_acc(g,buffers,prim["indices"])]
                assert len(p)==len(uv)==len(norm) and len(ix)%3==0,node["name"]
                for j in range(0,len(ix),3):
                    result.append([p[k] for k in ix[j:j+3]])
        for i in node.get("children",[]):visit(i,transform)
    visit(0,lambda p:p)
    return result

def obj_rebuild(old,gen,nodes):
    header=[]
    blocks=[]
    active=None
    total=0
    for line in old.splitlines():
        if line.startswith("o "):
            active={"name":line[2:],"start":total,"verts":[],"faces":[],"material":None}
            blocks.append(active)
        elif active is None:header.append(line)
        elif line.startswith("v "):
            active["verts"].append(line)
            total+=1
        elif line.startswith("f "):
            indices=[int(x.split("/")[0])-active["start"] for x in line[2:].split()]
            assert len(indices)==3 and all(1<=i<=len(active["verts"]) for i in indices),(active["name"],indices)
            active["faces"].append(indices)
        elif line.startswith("usemtl "):active["material"]=line
    assert len(blocks)==20 and sum(len(x["faces"]) for x in blocks)==424
    lines=header[:]
    vbase=0
    for block in blocks:
        name=block["name"]
        lines.append("o "+name)
        if block["material"]:lines.append(block["material"])
        if name in gen:
            node=nodes[name]
            assert not node.get("rotation") and not node.get("scale")
            ring=gen[name]
            pts=ring["positions"]
            for i in range(0,len(pts),3):
                coords=[pts[i+k]+node["translation"][k] for k in range(3)]
                lines.append("v "+" ".join("%.8f"%c for c in coords))
            for i in range(0,len(ring["indices"]),3):
                lines.append("f "+" ".join(str(vbase+1+k) for k in ring["indices"][i:i+3]))
            vbase+=len(pts)//3
        else:
            lines.extend(block["verts"])
            for f in block["faces"]:
                lines.append("f "+" ".join(str(vbase+k) for k in f))
            vbase+=len(block["verts"])
    return "\n".join(lines)+"\n"

def coord_key(tri):
    return tuple(sorted(tuple(round(float(x),6) for x in p) for p in tri))

def check_parity(g,obj):
    wanted=collections.Counter(coord_key(t) for t in scene_tris(g))
    vertices=[]
    actual=[]
    for line in obj.splitlines():
        if line.startswith("v "):
            vertices.append(tuple(map(float,line[2:].split())))
        elif line.startswith("f "):
            actual.append([vertices[int(k)-1] for k in line[2:].split()])
    got=collections.Counter(coord_key(t) for t in actual)
    assert wanted==got,{"missing":sum((wanted-got).values()),"extra":sum((got-wanted).values())}
    assert len(actual)==464
    return {"glTF_world_triangles":464,"OBJ_world_triangles":464,"mismatched_triangles_at_1um":0}

def main():
    g=json.loads(GLTF.read_text())
    s=json.loads(SPEC.read_text())
    orig=OBJ.read_text()
    assert s["expectedTriangleCount"]==424 and len(s["children"])==20
    assert len(g["nodes"])==22 and len(g["meshes"])==13 and len(g["buffers"])==2
    pivot=next(n for n in g["nodes"] if n["name"]=="LeverPivot")
    assert pivot["translation"]==[0,.35,-.015]
    assert [g["nodes"][i]["name"] for i in pivot["children"]]==["LeverShaft","LeverGrip","PivotAnchorVisual"]
    oldshas={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (GLTF,OBJ,SPEC)}
    generation={}
    for name,cfg in LAYOUT.items():
        mesh=g["meshes"][cfg["mesh"]]
        assert mesh["name"]==name and len(mesh["primitives"])==1
        p=mesh["primitives"][0]
        material=p["material"]
        data=make_ring(cfg)
        generation[name]=data
        buffer_index=len(g["buffers"])
        start_accessor=len(g["accessors"])
        pieces=[]
        offset=0
        for values,fmt,dim in ((data["positions"],"f",3),
                               (data["normals"],"f",3),
                               (data["uv"],"f",2),
                               (data["indices"],"H",1)):
            by=struct.pack("<"+fmt*len(values),*values)
            view_index=len(g["bufferViews"])
            g["bufferViews"].append(dict(buffer=buffer_index,byteOffset=offset,
                                          byteLength=len(by),target=34963 if fmt=="H" else 34962))
            acc=dict(bufferView=view_index,componentType=5123 if fmt=="H" else 5126,
                     count=len(values)//dim,type={1:"SCALAR",2:"VEC2",3:"VEC3"}[dim])
            if values is data["positions"]:
                sx,sy,sz=cfg["outer"]
                acc.update(min=[-sx/2,-sy/2,-sz/2],max=[sx/2,sy/2,sz/2])
            g["accessors"].append(acc)
            pieces.append(by)
            offset+=len(by)
        blob=b"".join(pieces)
        g["buffers"].append(dict(byteLength=len(blob),uri="data:application/octet-stream;base64,"+base64.b64encode(blob).decode("ascii")))
        mesh["primitives"]=[dict(attributes=dict(POSITION=start_accessor,
                                 NORMAL=start_accessor+1,TEXCOORD_0=start_accessor+2),
                                 indices=start_accessor+3,material=material,mode=4)]
        child=next(c for c in s["children"] if c["name"]==name)
        assert child["type"]=="box" and all(abs(a-b)<1e-8 for a,b in zip(child["size"],cfg["outer"]))
        child["type"]="rectangular_through_aperture"
        child["opening"]={"x":cfg["x"],"z":cfg["z"],"cutThroughAxis":"Y"}
        child["meshTriangles"]=32
    s["expectedTriangleCount"]=464
    s["version"]="0.3.0"
    s["state"]="PASS19_SOURCE_CLEARANCE_REPAIR__AWAIT_NATIVE_DYNAMIC_QA"
    s["detailPass19"]={"model":"P17-03","parts":20,"trianglesBefore":424,"trianglesAfter":464,
        "defect":"LeverShaft and PivotAnchorVisual intersected solid TopCap and LeverSocket in PASS18 FBX sweep",
        "fix":"Real manifold through-openings in two EXISTING fixed meshes; no proxy, no new part, no pivot edit",
        "pivotUnchanged":[0,.35,-.015],"motionSweep":"PENDING real Blender reimport",
        "Unity6":"NOT RUN"}
    node_by_name={n["name"]:n for n in g["nodes"]}
    new_obj=obj_rebuild(orig,generation,node_by_name)
    checks=check_parity(g,new_obj)
    GLTF.write_text(json.dumps(g,separators=(",",":"))+"\n")
    OBJ.write_text(new_obj)
    SPEC.write_text(json.dumps(s,indent=2)+"\n")
    output={"model":"P17-03","parts":20,"triangles":464,
        "geometryChange":["TopCap:12->32T","LeverSocket:12->32T"],
        "originalSourceSHA256":oldshas,
        "authoredSourceSHA256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (GLTF,OBJ,SPEC)},
        "sourceParity":checks,"nativeExport":"PENDING","release":"NOT APPROVED"}
    qa=ROOT/"C01InteriorProps_Source/QA/PASS19"
    qa.mkdir(parents=True,exist_ok=True)
    (qa/"P17-03_REAL_AUTHORING_QA.json").write_text(json.dumps(output,indent=2)+"\n")
    print("PASS W19 AUTHORING",json.dumps(output),flush=True)
if __name__=="__main__":main()
