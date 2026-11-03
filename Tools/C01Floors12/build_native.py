"""C01-12 legacy F01/F02/C01 -- native Blender 4.x authoring and FBX roundtrip.
Standalone compatibility kit, NOT an Interior Props P15-P19 model or ship replacement.
Run: blender --background --factory-startup --python Tools/C01Floors12/build_native.py
"""
from pathlib import Path
import bpy, json, hashlib
ROOT=Path(__file__).resolve().parents[2]/'C01StandaloneKits'/'FloorCeiling'
BLEND=ROOT/'Blend'; FBX=ROOT/'FBX_Blender_Export'; QA=ROOT/'QA'
for folder in (BLEND,FBX,QA): folder.mkdir(parents=True,exist_ok=True)
STEMS={'F01':'C01_SHI_F01_FLOOR_BASIC_v002','F02':'C01_SHI_F02_FLOOR_MARKED_v002','C01':'C01_SHI_C01_CEILING_BASIC_v002'}
COLORS={'M_C01_METAL_GRY':(.34,.40,.44,1),'M_C01_MARKING_WARN':(.94,.67,.10,1),'M_C01_PANEL_DARK':(.12,.17,.20,1)}

def geometry(asset):
    lo,hi=(-.2,0.) if asset!='C01' else (3.,3.2)
    cuts=(0.,.38,.62,1.)
    vertices=[]; ids={}
    for j,x in enumerate(cuts):
        for yi,y in enumerate((lo,hi)):
            for zi,z in enumerate((0.,1.)):
                ids[j,yi,zi]=len(vertices)
                vertices.append((x,-z,y)) # Unity Y-up -> Blender Z-up, right handed
    faces=[]; materials=[]
    def quad(keys,mat):
        faces.append([ids[k] for k in keys]);materials.append(mat)
    for j in range(3):
        mat=(1 if asset=='F02' and j==1 else 2 if asset=='C01' and j in (0,2) else 0)
        quad([(j,1,0),(j,1,1),(j+1,1,1),(j+1,1,0)],0 if asset=='C01' else mat)
        quad([(j,0,0),(j+1,0,0),(j+1,0,1),(j,0,1)],mat if asset=='C01' else 0)
        quad([(j,0,0),(j,1,0),(j+1,1,0),(j+1,0,0)],2)
        quad([(j,0,1),(j+1,0,1),(j+1,1,1),(j,1,1)],2)
    quad([(0,0,0),(0,0,1),(0,1,1),(0,1,0)],2)
    quad([(3,0,0),(3,1,0),(3,1,1),(3,0,1)],2)
    return vertices,faces,materials

def bbox(mesh_objects):
    pts=[obj.matrix_world@v.co for obj in mesh_objects for v in obj.data.vertices]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]

def verify(box,expected,tol=.001):
    assert all(abs(box[a][i]-expected[a][i])<=tol for a in range(2) for i in range(3)),f'Wrong bounds: {box} vs {expected}'

def run():
    results={}
    for asset,stem in STEMS.items():
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        verts,faces,indices=geometry(asset)
        mesh=bpy.data.meshes.new(stem+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update(calc_edges=True)
        obj=bpy.data.objects.new(stem,mesh);bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        for name,color in COLORS.items():
            mat=bpy.data.materials.new(name);mat.diffuse_color=color;mat.use_nodes=True
            bsdf=mat.node_tree.nodes.get('Principled BSDF')
            if bsdf:
                bsdf.inputs['Base Color'].default_value=color
                bsdf.inputs['Metallic'].default_value=.6
                bsdf.inputs['Roughness'].default_value=.55
            mesh.materials.append(mat)
        uv=mesh.uv_layers.new(name='UVMap')
        for face,material in zip(mesh.polygons,indices):
            face.material_index=material;face.use_smooth=False
            for loop_id in face.loop_indices:
                p=mesh.vertices[mesh.loops[loop_id].vertex_index].co
                uv.data[loop_id].uv=(p.x,p.y) if abs(face.normal.z)>.8 else (p.x,p.z)
        bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1.
        obj['C01_AssetId']='C01-12-'+asset;obj['C01_Contract']='C01-MAS-0.2-W02'
        obj['C01_StandaloneOnly']=True
        nativebox=[[0,-1,-.2 if asset!='C01' else 3.],[1,0,0. if asset!='C01' else 3.2]]
        verify(bbox([obj]),nativebox)
        blend=BLEND/(stem+'.blend');fbx=FBX/(stem+'.fbx')
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},
            global_scale=1.,apply_unit_scale=True,axis_forward='-Z',axis_up='Y',
            add_leaf_bones=False,bake_anim=False,use_mesh_modifiers=False)
        assert blend.read_bytes()[:7]==b'BLENDER', 'Not a real .blend file'
        assert fbx.read_bytes().startswith(b'Kaydara FBX Binary  '+bytes([0,26,0])), 'Not binary FBX'
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        bpy.ops.import_scene.fbx(filepath=str(fbx))
        imported=[o for o in bpy.context.scene.objects if o.type=='MESH']
        assert imported,'FBX imported no mesh'
        verify(bbox(imported),nativebox)
        assert all(any(len(layer.data)>0 for layer in o.data.uv_layers) for o in imported), 'FBX import missing UV'
        results[asset]={
            'blend':str(blend.relative_to(ROOT)), 'fbx':str(fbx.relative_to(ROOT)),
            'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
            'fbx_sha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),
            'geometry_faces':len(faces), 'bounds_blender_xyz':nativebox,
            'blender_save':'PASS','blender_fbx_import_roundtrip':'PASS','uv_import':'PASS',
            'unity_editor':'NOT_RUN','unity_playmode':'NOT_RUN','independent_qa':'PENDING'}
        print('C01-12 PASS Blender roundtrip',asset,flush=True)
    (QA/'blender_native_roundtrip.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':run()
