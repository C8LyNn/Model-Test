"""Metre-based Unity-Y-up box geometry. Touching faces are not intersections."""
import math
from itertools import product

EPS=1e-6

def point(p, pos, yaw):
    c=math.cos(math.radians(yaw)); s=math.sin(math.radians(yaw))
    return [pos[0]+c*p[0]+s*p[2], pos[1]+p[1], pos[2]-s*p[0]+c*p[2]]

def aabb(box, pos=(0,0,0), yaw=0):
    pts=[point(p,pos,yaw) for p in product(*zip(box['lo'],box['hi']))]
    return {'lo':[min(p[k] for p in pts) for k in range(3)], 'hi':[max(p[k] for p in pts) for k in range(3)]}

def overlap(a,b,eps=EPS):
    return all(min(a['hi'][k],b['hi'][k])-max(a['lo'][k],b['lo'][k])>eps for k in range(3))

def connected(a,b):
    d=[min(a['hi'][k],b['hi'][k])-max(a['lo'][k],b['lo'][k]) for k in range(3)]
    return min(d)>=-EPS and sum(v>EPS for v in d)>=2

def obb_overlap(a,apos,ayaw,b,bpos,byaw):
    """Exact SAT for Y-up boxes, including arbitrary door angles."""
    ac=point([(a['lo'][k]+a['hi'][k])/2 for k in range(3)],apos,ayaw)
    bc=point([(b['lo'][k]+b['hi'][k])/2 for k in range(3)],bpos,byaw)
    ae=[(a['hi'][k]-a['lo'][k])/2 for k in range(3)]
    be=[(b['hi'][k]-b['lo'][k])/2 for k in range(3)]
    if ae[1]+be[1]-abs(ac[1]-bc[1])<=EPS: return False
    def axes(y):
        c=math.cos(math.radians(y));s=math.sin(math.radians(y))
        return [(c,-s),(s,c)]
    aa,ba=axes(ayaw),axes(byaw)
    for n in aa+ba:
        ra=ae[0]*abs(sum(n[k]*aa[0][k] for k in range(2)))+ae[2]*abs(sum(n[k]*aa[1][k] for k in range(2)))
        rb=be[0]*abs(sum(n[k]*ba[0][k] for k in range(2)))+be[2]*abs(sum(n[k]*ba[1][k] for k in range(2)))
        if ra+rb-abs((ac[0]-bc[0])*n[0]+(ac[2]-bc[2])*n[1])<=EPS:return False
    return True

def world_parts(spec, door_angle=0):
    modules={m['id']:m for m in spec['modules']}; out=[]
    def add(mid,pos,yaw,tag):
        m=modules[mid]
        for i,p in enumerate(m['parts']):
            out.append(dict(aabb(p,pos,yaw),role=p['role'],tag=tag,part=i,source=p,pos=pos,yaw=yaw,moving=(mid=='D02_Door_Hinged')))
        for child in m.get('children',[]):
            cp=point(child['position'],pos,yaw)
            add(child['module'],cp,yaw+child.get('yaw',0)+(door_angle if child['module']=='D02_Door_Hinged' else 0),tag+'/'+child['socket'])
    for p in spec['placements']:
        add(p['id'],[p['x'],p['y'],p['z']],p['yaw'],p['tag'])
    return out

def rectangle_missing(rects, bounds):
    """Exact coordinate-compressed uncovered area, not a collision-only test."""
    x0,x1,z0,z1=bounds
    xs=sorted({x0,x1}|{max(x0,min(x1,r[k])) for r in rects for k in (0,1)})
    zs=sorted({z0,z1}|{max(z0,min(z1,r[k])) for r in rects for k in (2,3)})
    missing=0
    for a,b in zip(xs,xs[1:]):
        for c,d in zip(zs,zs[1:]):
            x=(a+b)/2;z=(c+d)/2
            if not any(r[0]-EPS<=x<=r[1]+EPS and r[2]-EPS<=z<=r[3]+EPS for r in rects): missing+=(b-a)*(d-c)
    return missing

def volume_missing(parts, lo, hi):
    """Exact union coverage in every critical depth slab of the required volume."""
    zs=sorted({lo[2],hi[2]}|{max(lo[2],min(hi[2],p[k][2])) for p in parts for k in ['lo','hi']})
    missing=0
    for za,zb in zip(zs,zs[1:]):
        z=(za+zb)/2
        rects=[(p['lo'][0],p['hi'][0],p['lo'][1],p['hi'][1]) for p in parts if p['lo'][2]<=z<=p['hi'][2]]
        missing+=rectangle_missing(rects,(lo[0],hi[0],lo[1],hi[1]))*(zb-za)
    return missing
