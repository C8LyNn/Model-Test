"""C01-12 PASS17 — native Blender 4.x material-only upgrade of the REAL v003 floor tiles.
No generated substitute geometry. No changes to vertices, faces, UV0, original face
material indices, transforms, ship architecture or model IDs.
"""
import bpy, hashlib, json, math, struct, zlib
from pathlib import Path
from mathutils import Vector

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'C01StandaloneKits'/'FloorCeiling'
OLD=ROOT/'RepairPass03'
OUT=ROOT/'DetailPass17'
STEMS={'F01':'C01_SHI_F01_FLOOR_BASIC','F02':'C01_SHI_F02_FLOOR_MARKED','C01':'C01_SHI_C01_CEILING_BASIC'}
EXPECTED=json.loads((OLD/'QA'/'C01_12_PASS03_REPORT.json').read_text())
for sub in ('Blend','FBX','GLB','Textures','Previews','QA'):
    (OUT/sub).mkdir(parents=True,exist_ok=True)
SIZE=512

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def write_png(path,pixels):
    def chunk(t,data):return struct.pack('!I',len(data))+t+data+struct.pack('!I',zlib.crc32(t+data)&0xffffffff)
    raw=b''.join(b'\x00'+pixels[y*SIZE*3:(y+1)*SIZE*3] for y in range(SIZE))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',SIZE,SIZE,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))

def texture(id,kind):
    path=OUT/'Textures'/f'{id}_{kind}.png'
    out=bytearray()
    for y in range(SIZE):
        v=(y+.5)/SIZE
        for x in range(SIZE):
            u=(x+.5)/SIZE
            grain=math.sin(2*math.pi*21*u)*math.sin(2*math.pi*23*v)
            seam=min(u,1-u,v,1-v)
            edge=int(seam<.018)
            r=min(math.hypot(u-a,v-b) for a in (.085,.915) for b in (.085,.915))
            fixing=int(.013<r<.024)
            if kind=='basecolor':
                base={'F01':(105,115,125),'F02':(113,119,123),'C01':(139,144,148)}[id]
                delta=int(grain*3)-17*edge-23*fixing
                if id=='F02' and .08<v<.18:
                    delta+=12 if int(u*18)%2==0 else -10
                rgb=[max(0,min(255,n+delta)) for n in base]
            elif kind=='roughness':
                n=int(168+grain*8+edge*14+fixing*8)
                rgb=[n,n,n]
            else:
                # OpenGL +Y tangent-space; Unity import convention must be verified.
                sx=math.sin(2*math.pi*u)*.028+(-.17 if .012<u<.020 else 0)+(.17 if .980<u<.988 else 0)
                sy=math.sin(2*math.pi*v)*.028+(-.17 if .012<v<.020 else 0)+(.17 if .980<v<.988 else 0)
                inv=1/math.sqrt(sx*sx+sy*sy+1)
                rgb=[int(round(127.5*(n*inv+1))) for n in (sx,sy,1)]
            out.extend(rgb)
    write_png(path,bytes(out))
    return {'path':str(path.relative_to(REPO)),'sha256':sha(path),'bytes':path.stat().st_size}

def signature(obj):
    me=obj.data;me.calc_loop_triangles()
    uv=me.uv_layers.active
    assert uv and len(me.materials)==3
    assert (len(me.vertices),len(me.edges),len(me.polygons),len(me.loop_triangles))==(16,28,14,28)
    assert all(len(p.vertices)==4 for p in me.polygons)
    vertices=[tuple(float(z) for z in v.co) for v in me.vertices]
    return {'vertices':vertices,'faces':[tuple(p.vertices) for p in me.polygons],
        'material_indices':[p.material_index for p in me.polygons],
        'uv0':[tuple(float(a) for a in loop.uv) for loop in uv.data],
        'root':{'location':list(obj.location),'scale':list(obj.scale),'rotation':list(obj.rotation_euler)},
        'bounds':[[min(v[i] for v in vertices) for i in range(3)],
                  [max(v[i] for v in vertices) for i in range(3)]]}

def setup_materials(obj,images):
    for i in range(3):
        original=obj.data.materials[i]
        assert original is not None
        tint=tuple(original.diffuse_color)
        mat=original.copy()
        mat.name=f'{obj.name}_PASS17_slot{i}_{original.name}'
        obj.data.materials[i]=mat
        mat.use_nodes=True
        nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
        output=nodes.new('ShaderNodeOutputMaterial')
        shader=nodes.new('ShaderNodeBsdfPrincipled')
        links.new(shader.outputs['BSDF'],output.inputs['Surface'])
        col=nodes.new('ShaderNodeTexImage');col.image=images['basecolor']
        mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY'
        mix.inputs[0].default_value=.55
        mix.inputs[2].default_value=(*tint[:3],1.0)
        links.new(col.outputs['Color'],mix.inputs[1])
        links.new(mix.outputs['Color'],shader.inputs['Base Color'])
        rough=nodes.new('ShaderNodeTexImage');rough.image=images['roughness']
        links.new(rough.outputs['Color'],shader.inputs['Roughness'])
        normal_tex=nodes.new('ShaderNodeTexImage');normal_tex.image=images['normal']
        normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.36
        links.new(normal_tex.outputs['Color'],normal.inputs['Color'])
        links.new(normal.outputs['Normal'],shader.inputs['Normal'])
        mat.diffuse_color=tuple(max(0,min(1,a*.91+.025)) for a in tint[:3])+(1,)

def preview(obj,id,phase,wire):
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=900;scene.render.resolution_y=660
    scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True
    camera=bpy.data.objects.new('PASS17_CAMERA',bpy.data.cameras.new('PASS17_CAMERA'))
    scene.collection.objects.link(camera);scene.camera=camera
    z=3.1 if id=='C01' else -.1
    target=Vector((.5,-.5,z))
    camera.location=target+Vector((1.6,-2.4,1.95 if id!='C01' else -1.95))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=2.1
    overlay=None
    if wire:
        curve=bpy.data.curves.new('PASS17_TRUE_EDGES','CURVE')
        curve.dimensions='3D';curve.bevel_depth=.0026
        for edge in obj.data.edges:
            line=curve.splines.new('POLY');line.points.add(1)
            for j,vi in enumerate(edge.vertices):
                p=obj.data.vertices[vi].co
                line.points[j].co=(p.x,p.y,p.z,1)
        overlay=bpy.data.objects.new('PASS17_TRUE_EDGES',curve)
        scene.collection.objects.link(overlay)
        overlay.color=(.95,.55,.07,1)
        scene.display.shading.color_type='OBJECT'
        obj.hide_render=True
    path=OUT/'Previews'/f'{id}_{phase}_{"WIREFRAME" if wire else "SHADED"}.png'
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    obj.hide_render=False
    if overlay:bpy.data.objects.remove(overlay,do_unlink=True)
    bpy.data.objects.remove(camera,do_unlink=True)
    return {'path':str(path.relative_to(REPO)),'sha256':sha(path)}

def one(id,stem):
    original=OLD/'Blend'/f'{stem}_v003.blend'
    assert sha(original)==EXPECTED[id]['repaired_blend_sha256'],id
    bpy.ops.wm.open_mainfile(filepath=str(original))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(meshes)==1,(id,'original mesh count',len(meshes))
    obj=meshes[0];before=signature(obj)
    assert before['root']['location']==[0,0,0]
    assert before['root']['scale']==[1,1,1]
    views_before=[preview(obj,id,'BEFORE',False),preview(obj,id,'BEFORE',True)]
    textures={k:texture(id,k) for k in ('basecolor','normal','roughness')}
    images={}
    for kind,row in textures.items():
        img=bpy.data.images.load(str(REPO/row['path']),check_existing=False)
        img.colorspace_settings.name='sRGB' if kind=='basecolor' else 'Non-Color'
        img.pack();images[kind]=img
    setup_materials(obj,images)
    after=signature(obj)
    assert before==after,(id,'geometry/UV/face-material/root changed')
    views_after=[preview(obj,id,'AFTER',False),preview(obj,id,'AFTER',True)]
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True);bpy.context.view_layer.objects.active=obj
    blend=OUT/'Blend'/f'{stem}_v004.blend'
    fbx=OUT/'FBX'/f'{stem}_v004.fbx'
    glb=OUT/'GLB'/f'{stem}_v004.glb'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=False)
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},
       global_scale=1,apply_unit_scale=True,axis_forward='-Z',axis_up='Y',
       add_leaf_bones=False,bake_anim=False,use_mesh_modifiers=False,
       path_mode='COPY',embed_textures=True)
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True)
    assert blend.read_bytes().startswith(b'BLENDER')
    assert fbx.read_bytes().startswith(b'Kaydara FBX Binary  '+bytes((0,26,0)))
    assert glb.read_bytes().startswith(b'glTF')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(objs)==1,(id,'FBX mesh count',len(objs))
    imported=signature(objs[0])
    assert len(imported['faces'])==14 and len(imported['uv0'])==len(before['uv0'])
    assert max(abs(a-b) for lo,hi in zip(before['bounds'],imported['bounds']) for a,b in zip(lo,hi))<1e-4
    assert all(math.isfinite(x) for uv in imported['uv0'] for x in uv)
    return {'input_blend_sha256':EXPECTED[id]['repaired_blend_sha256'],
      'before_mesh_signature_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),
      'after_mesh_signature_sha256':hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest(),
      'mesh_geometry_unchanged':True,'native_blender_4_save':'PASS','fbx_binary_roundtrip':'PASS',
      'blender_fbx_material_texture_URP':'NOT_RUN','unity6_urp':'NOT_RUN',
      'C01_02_independent_final_QA':'PENDING',
      'texture_files':textures,'previews':{'before':views_before,'after':views_after},
      'native':{kind:{'path':str(path.relative_to(REPO)),'sha256':sha(path),'bytes':path.stat().st_size}
                for kind,path in (('blend',blend),('fbx',fbx),('glb',glb))}}

if __name__=='__main__':
    results={}
    for key,stem in STEMS.items():
        results[key]=one(key,stem)
        print('C01-12 DETAIL PASS17 REAL BLENDER4+FBX:',key,flush=True)
    report={'schema':'C01-12-DETAIL-PASS17-v1',
       'material_only_no_ship_redesign':True,'asset_ids':results,
       'unity6_urp':'NOT_RUN','independent_C01_02_final_QA':'PENDING',
       'merge':'NOT_EXECUTED'}
    (OUT/'QA'/'DETAIL_PASS17_NATIVE_SHA256.json').write_text(json.dumps(report,indent=2)+'\n')
    print('C01-12 DETAIL PASS17 NATIVE EXPORTS COMPLETED',flush=True)
