import math
EPS=1e-6
def polygon_area(p):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))/2)
def ccw(p):
    p=[[round(v[0],7),round(v[1],7)] for v in p]
    if sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))<0:p.reverse()
    return p
def clip_rect(poly,x0,x1,z0,z1):
    poly=[list(p) for p in poly]
    for axis,limit,sign in [(0,x0,1),(0,x1,-1),(1,z0,1),(1,z1,-1)]:
        out=[]
        if not poly:return []
        for a,b in zip(poly,poly[1:]+poly[:1]):
            ia=(a[axis]-limit)*sign>=-EPS;ib=(b[axis]-limit)*sign>=-EPS
            if ia:out.append(a)
            if ia!=ib:
                t=(limit-a[axis])/(b[axis]-a[axis]);v=[a[k]+t*(b[k]-a[k]) for k in range(2)];v[axis]=limit;out.append(v)
        poly=out
    clean=[]
    for p in poly:
        if not clean or math.dist(p,clean[-1])>EPS:clean.append(p)
    if len(clean)>1 and math.dist(clean[0],clean[-1])<EPS:clean.pop()
    return ccw(clean) if len(clean)>=3 and polygon_area(clean)>EPS else []
def transform_poly(poly,pos,yaw):
    c=math.cos(math.radians(yaw));s=math.sin(math.radians(yaw))
    return [[pos[0]+c*p[0]+s*p[1],pos[2]-s*p[0]+c*p[1]] for p in poly]
def overlap_poly(a,b,eps=1e-5):
    for poly in [a,b]:
        for p,q in zip(poly,poly[1:]+poly[:1]):
            dx=q[0]-p[0];dz=q[1]-p[1];length=math.hypot(dx,dz)
            if length<EPS:continue
            n=(-dz/length,dx/length);aa=[v[0]*n[0]+v[1]*n[1] for v in a];bb=[v[0]*n[0]+v[1]*n[1] for v in b]
            if min(max(aa),max(bb))-max(min(aa),min(bb))<=eps:return False
    return True
def strip_polygons(points,width):
    def offset_line(a,b,d):
        vx=b[0]-a[0];vz=b[1]-a[1];l=math.hypot(vx,vz);n=(-vz/l*d,vx/l*d)
        return [a[0]+n[0],a[1]+n[1]],[b[0]+n[0],b[1]+n[1]]
    def line_intersection(a,b,c,d):
        v=[b[k]-a[k] for k in range(2)];w=[d[k]-c[k] for k in range(2)];det=v[0]*w[1]-v[1]*w[0]
        if abs(det)<EPS:return b
        t=((c[0]-a[0])*w[1]-(c[1]-a[1])*w[0])/det
        return [a[k]+t*v[k] for k in range(2)]
    sides=[]
    for direction in [1,-1]:
        lines=[offset_line(a,b,direction*width/2) for a,b in zip(points,points[1:])]
        side=[lines[0][0]]+[line_intersection(*lines[i-1],*lines[i]) for i in range(1,len(lines))]+[lines[-1][1]];sides.append(side)
    return [ccw([sides[0][i],sides[0][i+1],sides[1][i+1],sides[1][i]]) for i in range(len(points)-1)]

def triangulate(poly):
    poly=ccw(poly);indices=list(range(len(poly)));out=[]
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    while len(indices)>3:
        for j,b in enumerate(indices):
            a=indices[j-1];c=indices[(j+1)%len(indices)]
            if cross(poly[a],poly[b],poly[c])<=EPS:continue
            if any(all(cross(poly[u],poly[v],poly[k])>=-EPS for u,v in [(a,b),(b,c),(c,a)]) for k in indices if k not in [a,b,c]):continue
            out.append([poly[a],poly[b],poly[c]]);indices.pop(j);break
        else:raise ValueError('Unable to triangulate polygon')
    out.append([poly[k] for k in indices]);return out
