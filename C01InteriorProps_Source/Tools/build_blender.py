import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(sys.argv[sys.argv.index("--")+1]).resolve() if "--" in sys.argv else Path(".").resolve()
SRC=ROOT/"C01InteriorProps_Source"
MODELS=ROOT/"Assets/C01InteriorProps/Models"
BLEND=SRC/"Blender"
PREV=SRC/"Previews"
for p in (BLEND,PREV):p.mkdir(parents=True,exist_ok=True)
def bounds(meshes):
    pts=[o.matrix_world@Vector(corner) for o in meshes for corner in o.bound_box]
    return [min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]
for asset in ["P17-01","P17-02","P17-03"]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    path=MODELS/(asset+".gltf")
    if not path.exists():raise RuntimeError("Missing glTF "+str(path))
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported=list(bpy.context.scene.objects)
    meshes=[o for o in imported if o.type=="MESH"]
    if not meshes:raise RuntimeError("No mesh in "+asset)
    for o in meshes:
        if not o.data.vertices or not o.data.polygons:raise RuntimeError("Empty "+o.name)
    bpy.context.view_layer.update()
    lo,hi=bounds(meshes)
    dimensions=[hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]]
    spec=json.loads((SRC/"Specs"/(asset+".json")).read_text())
    expected=[spec["dimensions"][0],spec["dimensions"][1],spec["dimensions"][2]]
    if any(abs(a-b)>.003 for a,b in zip(dimensions,expected)):
        raise RuntimeError("Blender dimensions "+str(dimensions)+" expected "+str(expected))
    if asset=="P17-03" and not any("LeverPivot" in o.name for o in imported):
        raise RuntimeError("Missing lever pivot")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND/(asset+".blend")))
    bpy.ops.object.select_all(action="DESELECT")
    for o in imported:o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    bpy.ops.export_scene.fbx(filepath=str(MODELS/(asset+".fbx")),
        use_selection=True,object_types={'MESH','EMPTY'},
        axis_forward="-Z",axis_up="Y",global_scale=1.0,
        apply_unit_scale=True,use_mesh_modifiers=True,bake_anim=False)
    # Actual Blender Workbench renders, three camera angles.
    for label,az,ht in [("front",-math.pi/2,.2),("side",0,.2),("iso",-math.pi/4,.65)]:
        cam=bpy.data.objects.new("QA_CAMERA",bpy.data.cameras.new("QA_CAMERA"))
        bpy.context.scene.collection.objects.link(cam)
        center=Vector([(lo[i]+hi[i])*.5 for i in range(3)])
        cam.location=center+Vector((math.cos(az)*3,math.sin(az)*3,ht*3))
        cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
        cam.data.type="ORTHO"
        cam.data.ortho_scale=max(max(dimensions)*1.6,.5)
        scene=bpy.context.scene
        scene.camera=cam
        scene.render.engine="BLENDER_WORKBENCH"
        scene.display.shading.color_type="MATERIAL"
        scene.display.shading.light="STUDIO"
        scene.render.resolution_x=900
        scene.render.resolution_y=900
        scene.render.resolution_percentage=100
        scene.render.image_settings.file_format="PNG"
        scene.render.filepath=str(PREV/(asset+"_"+label+".png"))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(cam,do_unlink=True)
    print("PASS Blender",asset,len(meshes),dimensions)
