#!/usr/bin/env python3
"""C01-02 W26 read-only full-SHA FBX 7400 polygon normal / UV audit.
python W26_FBX_POLYGON_QA.py --zip original.zip --member Models/P19-03/P19-03.fbx --sha EXPECTED64 --out results.json
Original polygon Newell normals avoid false inverted normals on concave n-gon fans.
No model mutation, Blender, Unity or door/gate audit. Requires numpy.
"""
import argparse,collections,hashlib,json,pathlib,struct,zipfile,zlib
import numpy as np
class Node:
    def __init__(self,n,p,c):self.name,self.props,self.kids=n,p,c
    def child(self,n):return next((x for x in self.kids if x.name==n),None)
    def children(self,n):return [x for x in self.kids if x.name==n]
def parse(data):
    if not data.startswith(b'Kaydara FBX Binary  \x00\x1a\x00'):raise ValueError('Not original binary FBX')
    ver=struct.unpack_from('<I',data,23)[0]
    if ver<7400 or ver>=7500:raise ValueError('Unverified FBX version')
    def readprop(pos):
        t=chr(data[pos]);pos+=1
        if t in ('Y','C','I','F','D','L'):
            fmt={'Y':'h','C':'B','I':'i','F':'f','D':'d','L':'q'}[t]
            size=struct.calcsize(fmt)
            return struct.unpack_from('<'+fmt,data,pos)[0],pos+size
        if t in ('S','R'):
            n=struct.unpack_from('<I',data,pos)[0];pos+=4
            b=data[pos:pos+n];pos+=n
            return (b.decode('utf8','replace') if t=='S' else b),pos
        if t in ('b','c','i','f','d','l'):
            count,enc,n=struct.unpack_from('<III',data,pos);pos+=12
            raw=data[pos:pos+n];pos+=n
            if enc==1:raw=zlib.decompress(raw)
            elif enc!=0:raise ValueError('Unknown FBX array encoding')
            dt={'b':'i1','c':'u1','i':'<i4','f':'<f4','d':'<f8','l':'<i8'}[t]
            arr=np.frombuffer(raw,dtype=dt)
            if len(arr)!=count:raise ValueError('Corrupt FBX property array')
            return arr,pos
        raise ValueError('Unknown FBX property: '+t)
    def node(pos,limit):
        start=pos
        if pos+13>limit:return None,pos
        end,num,_,nlen=struct.unpack_from('<IIIB',data,pos);pos+=13
        if end==0:return None,pos
        if end<=start or end>len(data):raise ValueError('Invalid FBX node')
        name=data[pos:pos+nlen].decode('utf8','replace');pos+=nlen
        props=[]
        for _ in range(num):
            v,pos=readprop(pos);props.append(v)
        children=[]
        while pos<end-13:
            child,_next=node(pos,end)
            if child is None:break
            children.append(child);pos=_next
        return Node(name,props,children),end
    roots=[];pos=27
    while pos<len(data)-13:
        item,nextpos=node(pos,len(data))
        if item is None:break
        roots.append(item);pos=nextpos
    return roots
def analyze(data):
    obj=next(x for x in parse(data) if x.name=='Objects')
    out={'sha256':hashlib.sha256(data).hexdigest(),'meshes':0,'polygons':0,
        'opposite_polygon_corner_normals':0,'near_perpendicular_polygon_corner_normals':0,
        'zero_area_UV_polygons_with_positive_3D_area':0,'collapsed_UV_surface_m2':0.,
        'indexed_boundary_edges':0,'indexed_nonmanifold_edges':0,'degenerate_source_polygons':0,'parts':[]}
    for g in obj.children('Geometry'):
        if len(g.props)<3 or str(g.props[2]).lower()!='mesh':continue
        name=str(g.props[1]).split('\0')[0];geo=g.child('Vertices');poly=g.child('PolygonVertexIndex')
        uv=g.child('LayerElementUV');no=g.child('LayerElementNormal')
        if geo is None or poly is None or uv is None or no is None:raise ValueError('Missing mesh data: '+name)
        if uv.child('MappingInformationType').props[0]!='ByPolygonVertex' or uv.child('ReferenceInformationType').props[0]!='IndexToDirect':
            raise ValueError('Unsupported UV0 mapping: '+name)
        if no.child('MappingInformationType').props[0]!='ByPolygonVertex' or no.child('ReferenceInformationType').props[0]!='Direct':
            raise ValueError('Unsupported normal mapping: '+name)
        points=np.asarray(geo.props[0],dtype=float).reshape((-1,3))
        raw=np.asarray(poly.props[0],dtype=int)
        uvpoints=np.asarray(uv.child('UV').props[0],dtype=float).reshape((-1,2))
        uvrefs=np.asarray(uv.child('UVIndex').props[0],dtype=int)
        norms=np.asarray(no.child('Normals').props[0],dtype=float).reshape((-1,3))
        if len(uvrefs)!=len(raw) or len(norms)!=len(raw) or np.any(uvrefs<0) or np.any(uvrefs>=len(uvpoints)):
            raise ValueError('Invalid UV0 / normal corner indexing: '+name)
        if not (np.isfinite(points).all() and np.isfinite(uvpoints).all() and np.isfinite(norms).all()):
            raise ValueError('Nonfinite coordinates: '+name)
        if np.any(abs(np.linalg.norm(norms,axis=1)-1)>.001):raise ValueError('Nonunit normals: '+name)
        faces=[];face=[];corner=[];corners=[]
        for i,v in enumerate(raw):
            j=int(-v-1 if v<0 else v)
            if j<0 or j>=len(points):raise ValueError('Bad vertex index: '+name)
            face.append(j);corner.append(i)
            if v<0:faces.append((face,corner));face=[];corner=[]
        if face:raise ValueError('Unterminated polygon '+name)
        edges=collections.Counter()
        p={'part':name,'polygons':len(faces),'inverted_normals':0,'near_perpendicular_normals':0,
           'collapsed_uv_faces':0,'collapsed_uv_3d_area_m2':0.,'witness':[]}
        for fi,(index,cidx) in enumerate(faces):
            if len(index)<3:raise ValueError('Polygon with <3 corners: '+name)
            for a,b in zip(index,index[1:]+index[:1]):edges[tuple(sorted((a,b)))]+=1
            xyz=points[index];nvec=np.cross(xyz,np.roll(xyz,-1,axis=0)).sum(axis=0)
            physical=float(np.linalg.norm(nvec))/2.
            if physical<1e-14:out['degenerate_source_polygons']+=1;continue
            dots=norms[cidx]@(nvec/(physical*2.))
            inverted=int(np.sum(dots<-.1));near=int(np.sum(dots<.25))
            uvpoly=uvpoints[uvrefs[cidx]];nuv=np.roll(uvpoly,-1,axis=0)
            uvarea=abs(float(np.sum(uvpoly[:,0]*nuv[:,1]-nuv[:,0]*uvpoly[:,1])))/2.
            collapsed=uvarea<1e-12
            p['inverted_normals']+=inverted;p['near_perpendicular_normals']+=near
            p['collapsed_uv_faces']+=int(collapsed)
            if collapsed:p['collapsed_uv_3d_area_m2']+=physical
            if (inverted or collapsed) and len(p['witness'])<5:
                p['witness'].append({'polygon':fi,'corners':len(index),'physical_m2':physical,
                    'uv_area':uvarea,'min_normal_dot':float(np.min(dots))})
        p['indexed_boundary_edges']=sum(v==1 for v in edges.values())
        p['indexed_nonmanifold_edges']=sum(v>2 for v in edges.values())
        out['meshes']+=1;out['polygons']+=len(faces)
        out['opposite_polygon_corner_normals']+=p['inverted_normals']
        out['near_perpendicular_polygon_corner_normals']+=p['near_perpendicular_normals']
        out['zero_area_UV_polygons_with_positive_3D_area']+=p['collapsed_uv_faces']
        out['collapsed_UV_surface_m2']+=p['collapsed_uv_3d_area_m2']
        out['indexed_boundary_edges']+=p['indexed_boundary_edges']
        out['indexed_nonmanifold_edges']+=p['indexed_nonmanifold_edges']
        if any(p[k] for k in ['inverted_normals','near_perpendicular_normals','collapsed_uv_faces','indexed_boundary_edges','indexed_nonmanifold_edges']):
            out['parts'].append(p)
    return out
if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--zip',required=True);a.add_argument('--member',required=True)
    a.add_argument('--sha',required=True);a.add_argument('--out',required=True)
    x=a.parse_args()
    if 'door' in x.member.lower() or 'gate' in x.member.lower():
        raise ValueError('CLAUDE_DOORS_EXTERNAL_HOLD: forbidden file')
    with zipfile.ZipFile(x.zip) as z:
        if z.testzip() is not None:raise ValueError('Failed original artifact ZIP CRC')
        binary=z.read(x.member)
    if hashlib.sha256(binary).hexdigest()!=x.sha.lower():raise ValueError('Full FBX SHA mismatch, fail closed')
    outcome=analyze(binary)
    outcome.update({'archive':pathlib.Path(x.zip).name,'member':x.member,
        'scope':'native binary polygon-only, no Blender app or Unity Editor','release':'HOLD'})
    pathlib.Path(x.out).write_text(json.dumps(outcome,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in outcome.items() if k!='parts'},indent=2))
