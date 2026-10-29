import json,base64,math,struct
from pathlib import Path
src=Path(__file__).resolve().parents[1]
models=src.parent/"Assets/C01InteriorProps/Models"
for asset in ["P17-01","P17-02","P17-03"]:
    spec=json.loads((src/"Specs"/(asset+".json")).read_text())
    g=json.loads((models/(asset+".gltf")).read_text())
    data=base64.b64decode(g["buffers"][0]["uri"].split(",")[1])
    assert len(data)==g["buffers"][0]["byteLength"]
    assert len(g["meshes"])==len(spec["children"])
    assert len(g["materials"])<=4
    nodes={n["name"]:n for n in g["nodes"]}
    assert asset+"_ROOT" in nodes
    if asset=="P17-03":assert "LeverPivot" in nodes
    minimum=[math.inf]*3;maximum=[-math.inf]*3;tris=0
    def acc(index):
        a=g["accessors"][index];v=g["bufferViews"][a["bufferView"]]
        return a["count"],v.get("byteOffset",0)+a.get("byteOffset",0)
    for n,p in enumerate(spec["children"]):
        prim=g["meshes"][n]["primitives"][0]
        vcount,vstart=acc(prim["attributes"]["POSITION"])
        _,nstart=acc(prim["attributes"]["NORMAL"])
        icount,istart=acc(prim["indices"])
        vertices=[struct.unpack_from("<fff",data,vstart+12*i) for i in range(vcount)]
        normals=[struct.unpack_from("<fff",data,nstart+12*i) for i in range(vcount)]
        indices=struct.unpack_from("<"+"H"*icount,data,istart)
        assert icount%3==0
        parent=spec.get("lever",{}).get("pos",[0,0,0]) if p["parent"]=="LeverPivot" else [0,0,0]
        offset=[p["pos"][i]+parent[i] for i in range(3)]
        for v in vertices:
            for i in range(3):
                minimum[i]=min(minimum[i],v[i]+offset[i])
                maximum[i]=max(maximum[i],v[i]+offset[i])
        for t in range(0,icount,3):
            u,v,w=[vertices[indices[t+i]] for i in range(3)]
            a=[v[i]-u[i] for i in range(3)];b=[w[i]-u[i] for i in range(3)]
            cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
            assert math.sqrt(sum(x*x for x in cross))>1e-9,(asset,p["name"],"degenerate")
            norm=normals[indices[t]]
            assert sum(cross[i]*norm[i] for i in range(3))>1e-9,(asset,p["name"],"normal")
            tris+=1
    dims=[maximum[0]-minimum[0],maximum[2]-minimum[2],maximum[1]-minimum[1]]
    assert all(abs(dims[i]-spec["dimensions"][i])<.002 for i in range(3)),(asset,dims)
    assert tris==spec["expectedTriangleCount"],asset
    if spec["mount"]=="floor":assert abs(minimum[1])<.001
    if spec["mount"].startswith("wall"):assert abs(minimum[2])<.001
    print("PASS",asset,"triangles",tris,"W/D/H",dims)
