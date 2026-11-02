"""C01-13 PASS04: actual original/repaired indexed-OBJ geometry preflight.
Run with Python+NumPy: python Assets/C01DoorsAccess13/LegacyPass03/audit_indexed_geometry.py
Reads BEFORE files from original PASS03 local package (not committed in PR) and AFTER OBJs from this branch.
This is STATIC QA, not Blender, FBX importer or Unity.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json,numpy as np
def load(path):
    verts=[];faces=[]
    for line in path.read_text().splitlines():
        tokens=line.split()
        if not tokens:continue
        if tokens[0]=='v':verts.append(tuple(map(float,tokens[1:4])))
        elif tokens[0]=='f':faces.append([int(t.split('/')[0])-1 for t in tokens[1:]])
    return np.asarray(verts,dtype=float),np.asarray(faces,dtype=int)
def audit(path):
    v,f=load(path)
    assert f.ndim==2 and f.shape[1]==3,'Input must be real triangulated source'
    edges=Counter(tuple(sorted((int(a),int(b)))) for a,b,c in f for a,b in ((a,b),(b,c),(c,a)))
    adjacency=defaultdict(set)
    for a,b in edges:adjacency[a].add(b);adjacency[b].add(a)
    connected=set(map(int,f.flat));unused=len(v)-len(connected);islands=0
    while connected:
        islands+=1;stack=[connected.pop()]
        while stack:
            for neighbor in adjacency[stack.pop()]:
                if neighbor in connected:
                    connected.remove(neighbor);stack.append(neighbor)
    face_areas=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
    candidates=[]
    for vertex,p in enumerate(v):
        for a,b in edges:
            if vertex in (a,b):continue
            vec=v[b]-v[a];sq=np.dot(vec,vec)
            if sq<1e-16:continue
            t=np.dot(p-v[a],vec)/sq
            if 1e-7<t<1-1e-7 and np.linalg.norm(v[a]+t*vec-p)<1e-7:
                candidates.append([int(vertex),int(a),int(b)])
    return dict(vertices=int(len(v)),edges=int(len(edges)),faces=int(len(f)),
        triangles=int(len(f)),components=islands,nonmanifold_edges=sum(i>2 for i in edges.values()),
        boundary_edges=sum(i==1 for i in edges.values()),
        loose_vertices=unused,zero_length_edges=sum(np.linalg.norm(v[a]-v[b])<1e-7 for a,b in edges),
        degenerate_faces=int(sum(face_areas<1e-10)),
        duplicate_faces=len(f)-len(set(tuple(sorted(map(int,tri))) for tri in f)),
        duplicate_vertex_coordinates=len(v)-len(set(tuple(np.round(x,8)) for x in v)),
        t_junction_candidates=len(candidates),t_junction_candidates_detail=candidates,
        min_xyz=v.min(axis=0).tolist(),max_xyz=v.max(axis=0).tolist(),
        signed_volume=float(np.einsum('ij,ij->',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]]))/6),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest())
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--before-dir',type=Path,help='Directory with C01_SHI_D01/D02_BEFORE_original_v002.obj')
    p.add_argument('--out',type=Path,default=Path('C01_13_PASS04_indexed_report.json'))
    args=p.parse_args()
    root=Path(__file__).parent
    results={}
    for key in ('D01','D02'):
        before=args.before_dir/f'C01_SHI_{key}_BEFORE_original_v002.obj' if args.before_dir else None
        after=root/f'{key}_REPAIRED_v003_source_topology.obj'
        results[key]={'before':audit(before) if before and before.exists() else 'MISSING_NOT_RECONSTRUCTED',
                      'after':audit(after)}
        if isinstance(results[key]['before'],dict):
            a=results[key]['before'];b=results[key]['after']
            results[key]['bbox_error']=max(abs(x-y) for pair in ('min_xyz','max_xyz') for x,y in zip(a[pair],b[pair]))
            results[key]['volume_error']=abs(a['signed_volume']-b['signed_volume'])
    payload={'scope':'ACTUAL indexed source geometry; Blender/Unity NOT_RUN','results':results}
    args.out.write_text(json.dumps(payload,indent=2))
    print(json.dumps(payload,indent=2))
