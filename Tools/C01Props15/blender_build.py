import bpy, json, math
from mathutils import Vector
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'Tools/C01MeshPass26/P15'))
from uv_layout import layout_custom_mesh_uv
BASE=R/'Assets/C01InteriorProps/P15'
S=json.loads((BASE/'Sources/geometry_spec.json').read_text(encoding='utf-8'))
BL=BASE/'Sources/Blender';FBX=BASE/'Models/FBX';PRE=BASE/'Previews/Blender'
for p in (BL,FBX,PRE):p.mkdir(parents=True,exist_ok=True)
def to_b(v):return (v[0],-v[2],v[1])
def select(items):
    bpy.ops.object.select_all(action='DESELECT')
    for o in items:o.select_set(True)
    bpy.context.view_layer.objects.active=items[0]
def export(path,items):
    select(items)
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,global_scale=1,
        apply_unit_scale=True,axis_forward='-Z',axis_up='Y',add_leaf_bones=False,
        bake_anim=False,object_types={'EMPTY','MESH'},path_mode='AUTO')
def material(name,color):
    m=bpy.data.materials.new('C01_P15_'+name);m.diffuse_color=tuple(color);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs:bs.inputs['Base Color'].default_value=tuple(color);bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.42
    return m
# DETAIL PASS 13: true closed hollow hinge barrels and notched original door leaf.
# Uses the existing P15-03 root/part hierarchy; no new asset ID.
def c01_detail13_earclip(poly):
    def cross(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def inside(p,a,b,c):
        return all(cross(v,w,p)>=-1e-12 for v,w in ((a,b),(b,c),(c,a)))
    indices=list(range(len(poly)))
    area=sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))
    if area<=0:raise RuntimeError("P15-03 notched door polygon winding invalid")
    tris=[]
    while len(indices)>3:
        found=False
        for k in range(len(indices)):
            a,b,c=[indices[(k+q)%len(indices)] for q in (-1,0,1)]
            if cross(poly[a],poly[b],poly[c])<1e-10:continue
            if any(inside(poly[q],poly[a],poly[b],poly[c]) for q in indices if q not in (a,b,c)):continue
            tris.append((a,b,c));indices.pop(k);found=True;break
        if not found:raise RuntimeError("P15-03 door edge relief cannot triangulate")
    tris.append(tuple(indices))
    return tris

def c01_detail13_custom_primitive(p):
    shape=p["shape"]
    if shape=="hollow_cylinder":
        if p.get("axis")!="Y":raise RuntimeError("Only existing Y-axis hinge barrels supported")
        n=p.get("sides",12);r=p["inner_radius"];R=p["radius"];depth=p["depth"]
        if not (n>=8 and 0<r<R and depth>0):raise RuntimeError("Invalid hinge bore")
        verts=[]
        for rad,z in ((R,-depth/2),(R,depth/2),(r,-depth/2),(r,depth/2)):
            verts.extend([(rad*math.cos(2*math.pi*i/n),rad*math.sin(2*math.pi*i/n),z) for i in range(n)])
        faces=[]
        for i in range(n):
            j=(i+1)%n
            faces.extend(((i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                          (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)))
    elif shape=="notched_box":
        dx,dy,dz=p["size"]
        x0,x1=-dx/2,dx/2
        y0,y1=-dy/2,dy/2
        ring=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        for notch in sorted(p["notches"],key=lambda n:n["center_y"],reverse=True):
            yc=notch["center_y"]-p["center"][1];h=notch["height"]/2;xx=x0+notch["depth_x"]
            if not (x0<xx<x1 and y0<yc-h<yc+h<y1):raise RuntimeError("Invalid door relief dimensions")
            ring.extend(((x0,yc+h),(xx,yc+h),(xx,yc-h),(x0,yc-h)))
        n=len(ring)
        verts=[to_b((x,y,-dz/2)) for x,y in ring]+[to_b((x,y,dz/2)) for x,y in ring]
        cap=c01_detail13_earclip(ring)
        faces=[]
        for a,b,c in cap:faces.extend(((c,b,a),(n+a,n+b,n+c)))
        for i in range(n):
            j=(i+1)%n
            faces.append((i,j,n+j,n+i))
    else:
        raise RuntimeError("Unexpected custom primitive "+shape)
    data=bpy.data.meshes.new(p["name"]+"_MESH")
    data.from_pydata(verts,[],faces)
    data.update()
    # PASS26: correct UV0 for true side faces and annular caps without moving any vertices.
    layout_custom_mesh_uv(data,shape,p)
    o=bpy.data.objects.new(p["name"],data)
    bpy.context.collection.objects.link(o)
    return o

def primitive(p,m):
    if p['shape'] in ('notched_box','hollow_cylinder'):
        o=c01_detail13_custom_primitive(p)
    elif p['shape']=='box':
        bpy.ops.mesh.primitive_cube_add(size=1)
        o=bpy.context.object;o.dimensions=(p['size'][0],p['size'][2],p['size'][1])
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    elif p['shape']=='cylinder':
        bpy.ops.mesh.primitive_cylinder_add(vertices=p.get('sides',16),radius=p['radius'],depth=p['depth'])
        o=bpy.context.object
        if p['axis']=='X':o.rotation_euler[1]=math.pi/2
        if p['axis']=='Z':o.rotation_euler[0]=math.pi/2
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    o.name=p['name'];o.location=to_b(p['center']);o.data.materials.append(m)
    return o
def snapshot(center,size,view,path):
    data=bpy.data.cameras.new('QA_Camera');cam=bpy.data.objects.new('QA_Camera',data);bpy.context.scene.collection.objects.link(cam)
    cx,cy,cz=center
    u={'front':(0,.10,3.2),'iso':(2.4,1.6,2.8),'side':(3.3,.10,0)}[view]
    cam.location=to_b((cx+u[0]*size,cy+u[1]*size,cz+u[2]*size))
    cam.rotation_euler=(Vector(to_b(center))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=size*1.65
    sc=bpy.context.scene;sc.camera=cam;sc.render.engine='BLENDER_WORKBENCH'
    sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL'
    sc.render.resolution_x=900;sc.render.resolution_y=700;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True)
for asset,meta in S['assets'].items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    mats={k:material(k,v) for k,v in S['materials'].items()}
    roots={};parts={'Body':[],'Door':[]}
    for comp in ('Body','Door'):
        if not any(p['asset']==asset and p['component']==comp for p in S['parts']):continue
        root=bpy.data.objects.new(asset+'_'+comp+'_ROOT',None);bpy.context.collection.objects.link(root)
        root.location=to_b(meta.get('hinge',[0,0,0])) if comp=='Door' else (0,0,0)
        roots[comp]=root
    for p in S['parts']:
        if p['asset']!=asset:continue
        o=primitive(p,mats[p['material']]);o.parent=roots[p['component']]
        parts[p['component']].append(o)
    bpy.ops.wm.save_as_mainfile(filepath=str(BL/(asset+'.blend')),compress=False)
    full=sum(([root]+parts[c] for c,root in roots.items()),[])
    export(FBX/(asset+'.fbx'),full)
    if asset=='P15-03':
        export(FBX/'P15-03_Body.fbx',[roots['Body']]+parts['Body'])
        hinge=roots['Door'];old=hinge.location.copy();hinge.location=(0,0,0);bpy.context.view_layer.update()
        export(FBX/'P15-03_Door.fbx',[hinge]+parts['Door'])
        hinge.location=old;bpy.context.view_layer.update()
    center={'P15-01':(.5,0,.07),'P15-02':(0,0,.04),'P15-03':(0,.9,0)}[asset]
    for view in ('front','iso','side'):
        snapshot(center,max(meta['size_wdh']),view,PRE/(asset+'_'+view+'.png'))
print('C01-15: BLENDER SOURCE / FBX / PREVIEW EXPORT COMPLETE')
