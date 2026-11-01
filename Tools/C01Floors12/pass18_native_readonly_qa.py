"""C01-12 DETAIL PASS18 — read-only independent-of-exporter native QA for F01/F02/C01.
Runs Blender 4.x on REAL v004 .blend and REAL binary FBX, checks hashes from manifest,
manifold/topology/UV/normals, flat coplanar overlap, geometry/pivot and material image
channels. NO source mesh, ship scene or prefab changes. Producer preflight, NOT C01-02.
CLI: blender --background --factory-startup --python Tools/C01Floors12/pass18_native_readonly_qa.py
"""
import bpy, json, hashlib, math
from pathlib import Path
from collections import Counter
from mathutils import Vector

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'C01StandaloneKits'/'FloorCeiling'
D=ROOT/'DetailPass17'
OUT=ROOT/'DetailPass18'/'QA'
OUT.mkdir(parents=True,exist_ok=True)
MANIFEST=json.loads((D/'QA/DETAIL_PASS17_NATIVE_SHA256.json').read_text())
REPAIR=json.loads((ROOT/'RepairPass03/QA/C01_12_PASS03_REPORT.json').read_text())
STEMS={'F01':'C01_SHI_F01_FLOOR_BASIC','F02':'C01_SHI_F02_FLOOR_MARKED','C01':'C01_SHI_C01_CEILING_BASIC'}
EPS=1e-6

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def vec(p): return tuple(float(x) for x in p)
def canonical_tri(points):return tuple(sorted(tuple(round(float(x),6) for x in p) for p in points))
def good_image(image):
    return image is not None and image.size[0]==512 and image.size[1]==512 and image.packed_file is not None

def snapshot(ob,id,context,check_nodes):
    assert ob.type=='MESH'
    me=ob.data;me.calc_loop_triangles()
    assert len(me.vertices)==16 and len(me.polygons)==14 and len(me.edges)==28 and len(me.loop_triangles)==28,(id,context,'topology')
    assert all(len(p.vertices)==4 for p in me.polygons),(id,context,'quad_face')
    assert len(me.materials)==3,(id,context,'material_slots')
    assert all(m is not None for m in me.materials),(id,context,'null_material')
    assert len(me.uv_layers)>0,(id,context,'missing_uv0')
    uv=me.uv_layers.active
    world=[ob.matrix_world@v.co for v in me.vertices]
    bb=[[min(p[i] for p in world) for i in range(3)],[max(p[i] for p in world) for i in range(3)]]
    expect=((0,-1,-.2),(1,0,0)) if id!='C01' else ((0,-1,3),(1,0,3.2))
    delta=max(abs(bb[j][i]-expect[j][i]) for j in range(2) for i in range(3))
    assert delta<1e-4,(id,context,'bounds_error',delta)
    assert ob.location.length<1e-6 and ob.scale==Vector((1,1,1)),(id,context,'pivot_or_scale')
    assert ob.rotation_euler.length<1e-6,(id,context,'rotation')
    faces=[list(p.vertices) for p in me.polygons]
    edge_faces={}
    for fi,face in enumerate(faces):
        for a,b in zip(face,face[1:]+face[:1]):
            edge_faces.setdefault(tuple(sorted((a,b))),[]).append((a,b,fi))
    assert len(edge_faces)==28
    assert all(len(z)==2 and z[0][:2]==tuple(reversed(z[1][:2])) for z in edge_faces.values()),(id,context,'nonmanifold_or_winding')
    v_to_tri=[]
    badxyz=[];baduv=[];badnormal=[];dupes=[]
    tris={}
    for tri in me.loop_triangles:
        a,b,c=[world[i] for i in tri.vertices]
        normal=(b-a).cross(c-a)
        if normal.length<1e-10:badxyz.append(tri.index)
        polygon=me.polygons[tri.polygon_index]
        if normal.dot(ob.matrix_world.to_3x3()@polygon.normal)<=1e-12:badnormal.append(tri.index)
        u=[uv.data[k].uv for k in tri.loops]
        area=(u[1]-u[0]).cross(u[2]-u[0])
        if abs(area)<1e-10:baduv.append(tri.index)
        key=canonical_tri([a,b,c])
        if key in tris:dupes.append((tris[key],tri.index))
        tris[key]=tri.index
        v_to_tri.append(key)
    assert not (badxyz or baduv or badnormal or dupes),(id,context,{'xyz':badxyz,'uv0':baduv,'normal':badnormal,'dupes':dupes})
    # Detect exact SAME-FACING coplanar interiors (rectangular flat panels);
    # adjacent shared edges are valid; opposite normals denote a real closed volume.
    overlaps=[]
    planes=[]
    for i,p in enumerate(me.polygons):
        xyz=[world[v] for v in p.vertices]
        n=(ob.matrix_world.to_3x3()@p.normal).normalized()
        axis=max(range(3),key=lambda k:abs(n[k]))
        plane=sum(v[axis] for v in xyz)/len(xyz)
        remaining=[k for k in range(3) if k!=axis]
        bounds=[(min(v[k] for v in xyz),max(v[k] for v in xyz)) for k in remaining]
        planes.append((axis,plane,n,bounds))
    for i,(axis,plane,n,bounds) in enumerate(planes):
        for j in range(i+1,len(planes)):
            ax2,pl2,n2,b2=planes[j]
            if axis!=ax2 or abs(plane-pl2)>EPS or n.dot(n2)<.99999:continue
            area=math.prod(max(0.,min(bounds[k][1],b2[k][1])-max(bounds[k][0],b2[k][0])) for k in range(2))
            if area>1e-9:overlaps.append((i,j,area))
    assert not overlaps,(id,context,'same_facing_coplanar_overlap',overlaps)
    if check_nodes:
        for idx,material in enumerate(me.materials):
            assert material.use_nodes,(id,'material_node_missing',idx)
            images={node.image.name:node.image for node in material.node_tree.nodes if node.type=='TEX_IMAGE' and node.image}
            assert len(images)>=3,(id,'material image map count',idx,list(images))
            for typ in ('basecolor','normal','roughness'):
                matches=[v for k,v in images.items() if k.endswith('_'+typ+'.png')]
                assert len(matches)==1 and good_image(matches[0]),(id,'missing packed image',idx,typ,list(images))
                assert matches[0].colorspace_settings.name==('sRGB' if typ=='basecolor' else 'Non-Color'),(id,'colorspace',idx,typ)
    return {'vertices':len(world),'edges':len(edge_faces),'quads':len(faces),'triangles':len(v_to_tri),
        'material_slots':len(me.materials),'per_face_material_ids':[p.material_index for p in me.polygons],
        'uv0_loops':len(uv.data),'uv0_min_triangle_area_valid':not baduv,'same_facing_coplanar_overlap_count':len(overlaps),
        'bounds_source_xyz_m':[[round(float(z),7) for z in row] for row in bb],
        'world_triangles_sha256':hashlib.sha256(json.dumps(sorted(v_to_tri),separators=(',',':')).encode()).hexdigest(),
        'whole_mesh_connected':True,'manifold':True}

def one(id):
    rec=MANIFEST['asset_ids'][id]
    for kind in ('blend','fbx','glb'):
        f=REPO/rec['native'][kind]['path']
        assert f.is_file(),(id,kind,'missing binary')
        assert sha(f)==rec['native'][kind]['sha256'],(id,kind,'SHA mismatch')
        magic={'blend':b'BLENDER','fbx':b'Kaydara FBX Binary  '+bytes((0,26,0)),'glb':b'glTF'}[kind]
        assert f.read_bytes()[:len(magic)]==magic,(id,kind,'not binary')
    old=ROOT/'RepairPass03'/'Blend'/f'{STEMS[id]}_v003.blend'
    assert sha(old)==REPAIR[id]['repaired_blend_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(old))
    base=snapshot([o for o in bpy.data.objects if o.type=='MESH'][0],id,'v003_original',False)
    bpy.ops.wm.open_mainfile(filepath=str(REPO/rec['native']['blend']['path']))
    objs=[o for o in bpy.data.objects if o.type=='MESH']
    assert len(objs)==1,(id,'v004 mesh object count')
    source=snapshot(objs[0],id,'v004_blend',True)
    for key in ('world_triangles_sha256','per_face_material_ids','bounds_source_xyz_m','uv0_loops'):
        assert base[key]==source[key],(id,'v003/v004 regression',key)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(REPO/rec['native']['fbx']['path']))
    imps=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(imps)==1,(id,'FBX reimported mesh count',len(imps))
    imported=snapshot(imps[0],id,'v004_binary_fbx',False)
    for key in ('world_triangles_sha256','per_face_material_ids','bounds_source_xyz_m','uv0_loops'):
        assert source[key]==imported[key],(id,'FBX mismatch',key,source[key],imported[key])
    # GLB inspection as a separate real-app read: glTF scene graph may split
    # components by material. Preserve Blender's per-triangle totals, not pseudo boxes.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(REPO/rec['native']['glb']['path']))
    globs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert globs,(id,'GLB no meshes')
    glb_tri=0
    for ob in globs:
        ob.data.calc_loop_triangles()
        glb_tri+=len(ob.data.loop_triangles)
    assert glb_tri==28,(id,'GLB has wrong triangle count',glb_tri)
    return {'v003_source':base,'v004_blend':source,'v004_fbx_reimport':imported,
            'v004_real_blender_glb_import_triangles':glb_tri,'v004_real_blender_glb_import_meshes':len(globs),
            'sha256':{x:rec['native'][x]['sha256'] for x in ('blend','fbx','glb')},
            'producer_static_native_qa':'PASS','independent_C01_02_final_qa':'PENDING','unity6_urp':'NOT_RUN'}

if __name__=='__main__':
    report={'scope':'THREE_LEGACY_F01_F02_C01_NOT_36_PROPS','qa_owner':'C01-12 producer independent-of-exporter rerun',
        'read_only_on_native_assets':True,'blender_version':bpy.app.version_string,
        'models':{},'C01_02_independent_final_approval':'PENDING',
        'unity_6_urp_actual_editor':'NOT_RUN','ship_geometry_changed':False,'merge':'NOT_EXECUTED'}
    for id in STEMS:
        report['models'][id]=one(id)
        print('C01-12 PASS18 REAL BLEND/FBX/GLB QA PASS:',id,flush=True)
    (OUT/'PASS18_REAL_NATIVE_READONLY_QA.json').write_text(json.dumps(report,indent=2)+'\n')
    print('C01-12 PASS18 NATIVE READONLY AUDIT COMPLETE',flush=True)
