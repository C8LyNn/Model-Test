#!/usr/bin/env python3
"""C01-14 PASS05: read-only exact binary FBX 7.4 indexed mesh/UV/normals audit.
Run against hydrated files: python3 Tools/C01Structures14/fbx_raw_pass05.py DIR OUT.json
This is not a substitute for Blender/Unity import, nor for independent C01-02 QA.
"""
import collections, hashlib, json, math, pathlib, struct, sys, zlib
import numpy as np

SHA={
"C01_14_RMP-01_v002.fbx":"97f0b125313057f4ecf601dd60a02b4d3f0d55b87c1713d71a0adbedcc6d1443",
"C01_14_RAI-01_v002.fbx":"b51c3c012f5680de2d02c2deaf5c67c4ae9a12bb7e8347f179ed08d181a7e103",
"C01_14_RMP-01_v002.blend":"7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa",
"C01_14_RAI-01_v002.blend":"8a2f16205874f8485adb87c5251f6adbba3f51816936c0bf1964ad40a47850a5",
}
MAGIC=b"Kaydara FBX Binary  \x00\x1a\x00"
class Reader:
    def __init__(self,raw):
        assert raw.startswith(MAGIC)
        self.b=raw;self.version=struct.unpack_from("<I",raw,len(MAGIC))[0]
        assert 7400<=self.version<7500,self.version
        self.i=len(MAGIC)+4
    def prop(self):
        b=self.b;t=chr(b[self.i]);self.i+=1
        fmt={"Y":"<h","C":"<B","I":"<i","F":"<f","D":"<d","L":"<q"}
        if t in fmt:
            f=fmt[t];val=struct.unpack_from(f,b,self.i)[0];self.i+=struct.calcsize(f);return val
        if t in "SR":
            n=struct.unpack_from("<I",b,self.i)[0];self.i+=4
            v=b[self.i:self.i+n];self.i+=n
            return v.decode("utf8","replace") if t=="S" else v
        if t in "fdilbc":
            n,enc,size=struct.unpack_from("<III",b,self.i);self.i+=12
            v=b[self.i:self.i+size];self.i+=size
            if enc==1:v=zlib.decompress(v)
            else:assert enc==0
            dt={"f":"<f4","d":"<f8","i":"<i4","l":"<i8","b":"i1","c":"i1"}[t]
            assert len(v)==n*np.dtype(dt).itemsize,(t,n,len(v))
            return np.frombuffer(v,dtype=dt).copy()
        raise ValueError("unknown FBX property "+t)
    def node(self,limit):
        b=self.b;start=self.i
        end,nprops,proplen,nlen=struct.unpack_from("<IIIB",b,self.i);self.i+=13
        if not (end or nprops or proplen or nlen):return None
        assert start<end<=limit,(start,end,limit)
        name=b[self.i:self.i+nlen].decode("utf8","replace");self.i+=nlen
        mark=self.i;props=[self.prop() for _ in range(nprops)]
        assert self.i-mark==proplen
        children=[]
        while self.i+13<=end and b[self.i:self.i+13]!=bytes(13):
            child=self.node(end)
            if child:children.append(child)
        self.i=end
        return {"name":name,"props":props,"children":children}
    def root(self):
        out=[]
        while self.i+13<=len(self.b) and self.b[self.i:self.i+13]!=bytes(13):
            out.append(self.node(len(self.b)))
        return out
def child(n,name):
    return next((x for x in n["children"] if x["name"]==name),None)
def children(n,name):
    return [x for x in n["children"] if x["name"]==name]
def values(n,name):
    v=child(n,name);return v["props"][0] if v else None
def audit_fbxf(path):
    raw=path.read_bytes();reader=Reader(raw);roots=reader.root()
    objects=next(x for x in roots if x["name"]=="Objects")
    parts=[]
    for g in children(objects,"Geometry"):
        if len(g["props"])<3 or g["props"][2]!="Mesh":continue
        name=g["props"][1].split("\x00")[0].split("::")[-1]
        vertices=np.asarray(values(g,"Vertices"),dtype=np.float64).reshape(-1,3)
        indices=np.asarray(values(g,"PolygonVertexIndex"),dtype=np.int64)
        polys=[];p=[]
        for q in indices:
            q=int(q)
            p.append(-q-1 if q<0 else q)
            if q<0:polys.append(p);p=[]
        assert not p
        assert np.isfinite(vertices).all()
        assert all(len(f)==3 and min(f)>=0 and max(f)<len(vertices) for f in polys),name
        nl=next((x for x in children(g,"LayerElementNormal")),None)
        ul=next((x for x in children(g,"LayerElementUV")),None)
        assert nl and ul,(name,"UV0 or normals absent")
        normals=np.asarray(values(nl,"Normals"),dtype=np.float64).reshape(-1,3)
        uv=np.asarray(values(ul,"UV"),dtype=np.float64).reshape(-1,2)
        uvindex=np.asarray(values(ul,"UVIndex"),dtype=np.int64)
        assert len(normals)==len(indices)==len(uvindex),(name,"bad vertex streams")
        assert len(uv)>0 and np.isfinite(uv).all() and np.isfinite(normals).all()
        assert (uvindex>=0).all() and (uvindex<len(uv)).all(),name
        edges=collections.Counter();direct=collections.defaultdict(list)
        seen=collections.Counter()
        degenerates=bad_uv_area=bad_normals=0;min_normal_cos=1.0
        for i,f in enumerate(polys):
            seen[tuple(sorted(f))]+=1
            a,b,c=vertices[f]
            n=np.cross(b-a,c-a);area=float(np.linalg.norm(n))
            if area<2e-12:degenerates+=1
            else:
                n/=area
                for raw_normal in normals[i*3:(i+1)*3]:
                    nd=float(np.linalg.norm(raw_normal))
                    cos=float(np.dot(n,raw_normal)/nd) if nd>1e-15 else -1.0
                    min_normal_cos=min(min_normal_cos,cos)
                    if cos<0.99:bad_normals+=1
            ua,ub,uc=uv[uvindex[i*3:(i+1)*3]]
            det=float(np.linalg.det(np.array([[ub[0]-ua[0],ub[1]-ua[1]],
                                              [uc[0]-ua[0],uc[1]-ua[1]]])))
            if abs(det)<1e-12:bad_uv_area+=1
            for va,vb in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
                key=tuple(sorted((va,vb)))
                edges[key]+=1;direct[key].append((va,vb))
        used={idx for f in polys for idx in f}
        coincident=collections.Counter(map(tuple,np.round(vertices,7)))
        parts.append({"name":name,"vertices":len(vertices),"edges":len(edges),
            "faces":len(polys),"triangles":len(polys),
            "loose_vertices":len(vertices)-len(used),
            "coincident_vertex_coordinate_groups":sum(x>1 for x in coincident.values()),
            "boundary_edges":sum(v==1 for v in edges.values()),
            "nonmanifold_edges":sum(v>2 for v in edges.values()),
            "inconsistent_edge_winding":sum(len(v)==2 and v[0]==v[1] for v in direct.values()),
            "duplicate_faces":sum(x-1 for x in seen.values() if x>1),
            "degenerate_triangles":degenerates,"zero_uv_area_triangles":bad_uv_area,
            "normal_mismatch_corners":bad_normals,"min_normal_cos":min_normal_cos,
            "uv0":True,"finite_normals":True})
    if not parts:raise ValueError("FBX contains no Mesh geometry")
    return {"file":path.name,"version":reader.version,"sha256":hashlib.sha256(raw).hexdigest(),
       "mesh_parts":parts,"totals":{k:sum(x[k] for x in parts) for k in
           ("vertices","edges","faces","triangles","loose_vertices","boundary_edges",
            "nonmanifold_edges","inconsistent_edge_winding","duplicate_faces",
            "degenerate_triangles","zero_uv_area_triangles","normal_mismatch_corners")}}
def main(directory,destination):
    root=pathlib.Path(directory);documents=[]
    for name,expected in SHA.items():
        p=root/name;data=p.read_bytes()
        actual=hashlib.sha256(data).hexdigest()
        assert actual==expected,(name,actual,expected)
        if name.endswith(".blend"):
            assert data.startswith(b"BLENDER"),name
            documents.append({"file":name,"sha256":actual,"native_blender_header":True})
        else:
            x=audit_fbxf(p);assert x["sha256"]==expected;documents.append(x)
            errs=("loose_vertices","boundary_edges","nonmanifold_edges",
                  "inconsistent_edge_winding","duplicate_faces",
                  "degenerate_triangles","zero_uv_area_triangles","normal_mismatch_corners")
            assert all(x["totals"][key]==0 for key in errs),(name,x["totals"])
            print("PASS indexed binary FBX",name,x["totals"])
    report={"status":"STATIC_BINARY_FBX_PASS_ONLY",
        "actual_blender_v4_run":"NOT_RUN_PASS05; prior SUCCESS 41089475908",
        "actual_unity6":"NOT_RUN","independent_c01_02":"PENDING",
        "native_source_or_mesh_modified":False,
        "data_origin":"Actual SHA-pinned Blender-generated binary FBX from PR24 PASS03",
        "files":documents}
    target=pathlib.Path(destination);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main(sys.argv[1],sys.argv[2])
