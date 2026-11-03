#!/usr/bin/env python3
"""P17-03 W19: import actual authored post-clearance glTF and save real Blender source."""
import bpy
import hashlib
import json
import sys
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index("--")+1]).resolve() if "--" in sys.argv else Path(".").resolve()
s=json.loads((R/"C01InteriorProps_Source/Specs/P17-03.json").read_text())
assert s["expectedTriangleCount"]==464 and len(s["children"])==20
file=R/"Assets/C01InteriorProps/Models/P17-03.gltf"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(file))
ob=list(bpy.context.scene.objects)
mesh=[o for o in ob if o.type=="MESH"]
assert len(mesh)==20,("missing source mesh part",len(mesh))
assert sum(len(o.data.polygons) for o in mesh)==464,("source mesh triangle count",[(o.name,len(o.data.polygons)) for o in mesh])
assert all(o.data.uv_layers for o in mesh)
assert any(o.name=="LeverPivot" and o.type=="EMPTY" for o in ob)
piv=bpy.data.objects["LeverPivot"]
assert {o.name for o in piv.children}=={"LeverShaft","LeverGrip","PivotAnchorVisual"}
bpy.context.view_layer.update()
pts=[o.matrix_world@Vector(v) for o in mesh for v in o.bound_box]
bounds=[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)]
size=[b-a for a,b in bounds]
assert all(abs(size[i]-[.4,.3,.55][i])<.003 for i in range(3)),size
dest=R/"C01InteriorProps_Source/Blender/P17-03.blend"
dest.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
print("PASS19 ORIGINAL EDITED SOURCE IMPORT",len(mesh),"triangles",464,"dimensionsXYZ",size,"BLENDER",bpy.app.version_string,flush=True)
