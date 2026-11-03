"""W23 C01-13. Actual hydrated non-door FBX triangle placement audit.
Read-only producer geometry. No doors, no prefabs, no Unity claims.
blender -b --factory-startup --python-exit-code 1 --python qa_real_fbx_placement.py -- ROOT
"""
import bpy,math,hashlib,json,csv,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]).resolve()
OUT=R/'C01NonDoorQA'/'Pass23'/'Results'
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=[
('P17-01','console','_native/P17-01/Assets/C01InteriorProps/Models/P17-01.fbx','cd6a5787bb7b4c088f0af35382385e4274c85c415c60467f9a22e46fe33ef02c'),
('P18-01','crate','_native/P18-01/Assets/C01InteriorProps/C01-18/Models/P18-01.fbx','f541d502ba9eaaf5c7a0a7279c44f71f36dd482e3aed3ba0734058dcf1045f6c'),
('P19-03','desk','_native/P19-03/Assets/C01InteriorProps/C01-19/Models/P19-03/P19-03.fbx','1bd730b2382879d7d9c2f3d67c4b9646b8ca036c04de663e53b3019c403af2df')]
ROOM=(0.,4.,0.,4.)
CORRIDOR=(1.,3.,4.,8.)
ROOM_ANCHORS={'P17-01':(1,3),'P18-01':(1,1),'P19-03':(3,2)}
# The following are explicit illustrative fixture assumptions, NOT ship design limits.
FIXTURE_CEILING_M=3.
FIXTURE_NAV_HEIGHT_M=1.8
COLORS={'P17-01':'#187ba0','P18-01':'#d49436','P19-03':'#8165b0'}

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def load_actual(item):
    aid,label,relative,expected=item
    p=R/relative
    if not p.is_file():raise RuntimeError('MISSING_HYDRATED_FBX '+str(p))
    with open(p,'rb') as f:magic=f.read(23)
    if not magic.startswith(b'Kaydara FBX Binary'):
        raise RuntimeError('NOT_BINARY_FBX_OR_LFS_POINTER '+str(p))
    measured=sha256(p)
    if measured!=expected:raise RuntimeError('FAIL_CURRENT_SHA '+aid+' '+measured)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(p),use_custom_normals=True)
    bpy.context.view_layer.update()
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    if not objs:raise RuntimeError('NO_RENDER_MESH '+aid)
    tris=[];missing_uv=[];bad_normal=[];degenerate=0
    for o in objs:
        if not o.data.uv_layers:missing_uv.append(o.name)
        o.data.calc_loop_triangles()
        for t in o.data.loop_triangles:
            # FBX model and parent matrices are actually evaluated by Blender.
            v=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
            v=[(float(q.x),float(q.z),-float(q.y)) for q in v]
            a,b,c=v;ab=[b[k]-a[k] for k in range(3)];ac=[c[k]-a[k] for k in range(3)]
            cross=(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])
            if sum(x*x for x in cross)<1e-18:degenerate+=1
            tris.append(v)
        for vertex in o.data.vertices:
            if not all(math.isfinite(float(k)) for k in vertex.normal):bad_normal.append(o.name)
    if missing_uv or bad_normal or degenerate:
        raise RuntimeError('SOURCE_TRIANGLE_OR_UV_FAIL '+aid+' '+str((missing_uv,bad_normal,degenerate)))
    points=[p for t in tris for p in t]
    source_bounds=[[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)]
    return {'id':aid,'name':label,'sha':measured,'meshes':len(objs),'triangle_count':len(tris),
            'source_bounds_Unity_XYZ_m':source_bounds,
            'floor_offset_from_source_pivot_m':-source_bounds[1][0],'tris':tris}

def transform(asset,anchor,rotation):
    radians=math.radians(rotation);c=round(math.cos(radians),14);s=round(math.sin(radians),14)
    dy=asset['floor_offset_from_source_pivot_m']
    return [[(anchor[0]+x*c-z*s,y+dy,anchor[1]+x*s+z*c) for x,y,z in t]
            for t in asset['tris']]

def bbox(tris):
    p=[v for t in tris for v in t]
    return [[min(v[k] for v in p),max(v[k] for v in p)] for k in range(3)]

def clip(poly,axis,bound,greater):
    if not poly:return []
    dist=lambda p:(p[axis]-bound)*(1 if greater else -1)
    out=[]
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)];da=dist(a);db=dist(b)
        if da>=-1e-10:out.append(a)
        if (da < -1e-10 and db > 1e-10) or (db < -1e-10 and da > 1e-10):
            t=da/(da-db)
            out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(3)))
    return out

def intervals_at_z(tris,z):
    ints=[]
    for t in tris:
        if min(v[2] for v in t)>z+.025 or max(v[2] for v in t)<z-.025:continue
        poly=list(t)
        for axis,bound,greater in ((2,z-.025,True),(2,z+.025,False),(1,0.,True),(1,FIXTURE_NAV_HEIGHT_M,False)):
            poly=clip(poly,axis,bound,greater)
            if not poly:break
        if poly:
            lo=max(CORRIDOR[0],min(p[0] for p in poly))
            hi=min(CORRIDOR[1],max(p[0] for p in poly))
            if hi>lo+1e-8:ints.append((lo,hi))
    return ints

def free_width(ints):
    start=CORRIDOR[0];best=0.
    for lo,hi in sorted(ints):
        if lo>start:best=max(best,lo-start)
        start=max(start,hi)
    return max(best,CORRIDOR[1]-start)

def measure(asset,area,rot,anchor):
    tris=transform(asset,anchor,rot);b=bbox(tris)
    x0,x1,z0,z1=ROOM if area=='ROOM' else CORRIDOR
    outside=sum(1 for t in tris for x,y,z in t
                if x<x0-1e-6 or x>x1+1e-6 or z<z0-1e-6 or z>z1+1e-6)
    margins={'left':b[0][0]-x0,'right':x1-b[0][1],
             'front':b[2][0]-z0,'back':z1-b[2][1]}
    widths=[free_width(intervals_at_z(tris,4.1+0.2*j)) for j in range(20)] if area=='CORRIDOR' else []
    return {'asset_id':asset['id'],'source_FBX_sha256':asset['sha'],'area':area,
            'yaw_deg':rot,'integer_grid_anchor_xz_m':anchor,
            'render_bounds_world_XYZ_m':[[round(v,6) for v in pair] for pair in b],
            'signed_wall_clearances_m':{k:round(v,6) for k,v in margins.items()},
            'min_wall_clearance_m':round(min(margins.values()),6),
            'actual_triangle_vertices_outside_test_volume':outside,
            'floor_contact_after_explicit_adjustment_m':round(b[1][0],6),
            'source_pivot_to_floor_adjustment_m':round(asset['floor_offset_from_source_pivot_m'],6),
            'example_3m_ceiling_gap_m':round(FIXTURE_CEILING_M-b[1][1],6),
            'corridor_min_max_free_width_over_z_samples_m':round(min(widths),5) if widths else None,
            'corridor_free_width_per_sample_m':[round(w,5) for w in widths],
            'disposition':'EXAMPLE_GEOMETRY_CROSSES_FIXTURE_BOUNDARY' if outside else 'MEASURED_NO_BOUNDARY_CROSSING__THRESHOLD_OWNER_DECISION'}

def bvh_pair(a,b):
    def make(t):
        vertices=[Vector(v) for tri in t for v in tri]
        faces=[(3*i,3*i+1,3*i+2) for i in range(len(t))]
        return BVHTree.FromPolygons(vertices,faces,all_triangles=True)
    return len(make(a).overlap(make(b))) # BVH candidate, not definitive intersection

def preview(name,instances,isometric=False):
    def proj(p):
        x,y,z=p
        return (440+(x-z)*45,140+(x+z)*24-y*52) if isometric else (160+x*95,65+z*68)
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 660">',
           '<rect width="880" height="660" fill="#fbfcfe"/>',
           '<text x="20" y="32" font-size="21" fill="#243149">C01-13 W23: '+name+' — ACTUAL FBX triangles</text>']
    for x in range(5):
        a,b=proj((x,0,0)),proj((x,0,8))
        parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#d9dfe6" stroke-dasharray="3,6"/>'%(*a,*b))
    for z in range(9):
        a,b=proj((0,0,z)),proj((4,0,z))
        parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#d9dfe6" stroke-dasharray="3,6"/>'%(*a,*b))
    for rect in [[(0,0,0),(4,0,0),(4,0,4),(0,0,4)],[(1,0,4),(3,0,4),(3,0,8),(1,0,8)]]:
        parts.append('<polygon points="%s" fill="none" stroke="#334155" stroke-width="2"/>'%' '.join('%.1f,%.1f'%proj(p) for p in rect))
    faces=[]
    for a,anchor,rot in instances:
        triangles=transform(a,anchor,rot)
        step=max(1,len(triangles)//900)
        for t in triangles[::step]:
            pts=' '.join('%.2f,%.2f'%proj(p) for p in t)
            depth=sum(p[0]+p[1]+p[2] for p in t)
            faces.append((depth,'<polygon points="%s" fill="%s" fill-opacity="0.4" stroke="%s" stroke-width=".35"/>'%(pts,COLORS[a['id']],COLORS[a['id']])))
    for _,poly in sorted(faces,key=lambda x:x[0],reverse=isometric):parts.append(poly)
    for i,(a,_,_) in enumerate(instances):
        parts.append('<text x="20" y="%d" fill="%s" font-size="15">%s %s</text>'%(65+i*23,COLORS[a['id']],a['id'],a['name']))
    parts.append('<text x="20" y="635" fill="#64748b" font-size="12">Only real imported FBX triangles. Analytical 1 m grid, 4x4 room + 2x4 corridor. No doors. Unity NOT RUN.</text></svg>')
    (OUT/(name+'.svg')).write_text(''.join(parts),encoding='utf-8')

def main():
    assets=[load_actual(s) for s in SOURCE]
    cases=[]
    for a in assets:
        for rotation in (0,90,180,270):
            cases.append(measure(a,'ROOM',rotation,ROOM_ANCHORS[a['id']]))
            cases.append(measure(a,'CORRIDOR',rotation,(2,6)))
    room_tris=[transform(a,ROOM_ANCHORS[a['id']],0) for a in assets]
    pair_checks=[]
    for i in range(len(assets)):
        for j in range(i+1,len(assets)):
            pair_checks.append({'a':assets[i]['id'],'b':assets[j]['id'],
                'actual_FBX_triangle_BVH_overlap_candidates':bvh_pair(room_tris[i],room_tris[j]),
                'interpretation':'BROADPHASE_REVIEW_ONLY_NOT_EXACT_PENETRATION'})
    preview('room_top_actual_FBX',[(a,ROOM_ANCHORS[a['id']],0) for a in assets])
    preview('room_iso_actual_FBX',[(a,ROOM_ANCHORS[a['id']],0) for a in assets],True)
    preview('corridor_top_actual_FBX',[(assets[1],(2,6),90)])
    counts={'real_FBX_SHA_verified':len(assets),'cardinal_rotation_scenarios':len(cases),
            'fixture_boundary_crossing_scenarios':sum(bool(x['actual_triangle_vertices_outside_test_volume']) for x in cases),
            'inside_fixture_scenarios':sum(not x['actual_triangle_vertices_outside_test_volume'] for x in cases)}
    result={'schema':'C01-13-W23-REAL-FBX-NONDOOR-PLACEMENT-1',
        'inputs':[{k:v for k,v in a.items() if k!='tris'} for a in assets],
        'test_fixture':{'room_m':[4,4],'corridor_m':[2,4],'grid_m':1,
            'ceiling_3m':'UNAPPROVED_EXAMPLE_ONLY','navigation_slab_1_8m':'UNAPPROVED_EXAMPLE_ONLY',
            'mandatory_min_free_width':'THRESHOLD_OWNER_DECISION'},
        'methods':'Actual Blender FBX importer, evaluated world triangles in Unity Y-up, cardinal rotations around unmodified origin, explicit floor offset, analytical test boundaries and triangle slice width. No proxy asset meshes.',
        'cases':cases,'example_room_BVH_triangle_candidates':pair_checks,'counts':counts,
        'limitations':['Example placement does not prove defects in producer meshes',
                       'BVH overlap is potential triangle proximity, not certified penetration',
                       'Fixture boundaries are analytical; actual ship wall meshes and NavMesh not tested',
                       'No building code or owner-approved minimum navigation threshold exists'],
        'unity6':'NOT_RUN','producer_files_changed':0,'doors_touched':0,'merges':0,
        'status':'REAL_FBX_SPATIAL_MEASUREMENTS__THRESHOLD_OWNER_DECISION__UNITY_NOT_RUN'}
    (OUT/'non_door_placement_W23.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    fields=['asset_id','source_FBX_sha256','area','yaw_deg','integer_grid_anchor_xz_m',
        'min_wall_clearance_m','actual_triangle_vertices_outside_test_volume','floor_contact_after_explicit_adjustment_m',
        'source_pivot_to_floor_adjustment_m','example_3m_ceiling_gap_m','corridor_min_max_free_width_over_z_samples_m','disposition']
    with open(OUT/'non_door_placement_W23.csv','w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in cases:w.writerow({k:r.get(k) for k in fields})
    print('W23_ACTUAL_NONDOOR_FBX_RESULT',json.dumps(counts))
    for a in assets:print('EXACT_FBX',a['id'],a['sha'],'MESHES',a['meshes'],'TRIS',a['triangle_count'],'BOUNDS',a['source_bounds_Unity_XYZ_m'])
    for p in pair_checks:print('ACTUAL_BVH_CANDIDATE',json.dumps(p))
    for c in cases:print('MEASURED',c['asset_id'],c['area'],c['yaw_deg'],c['min_wall_clearance_m'],c['corridor_min_max_free_width_over_z_samples_m'],c['disposition'])

main()
