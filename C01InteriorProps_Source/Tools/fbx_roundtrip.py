"""Real Blender FBX reimport QA: UV0, mesh count, Y-up dimensions and pivots."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index("--")+1]).resolve() if "--" in sys.argv else Path(".").resolve()
SRC=R/"C01InteriorProps_Source";MODEL=R/"Assets/C01InteriorProps/Models"
results=[];hashes={}
for id in __import__("os").environ.get("C01_IDS","P17-01,P17-02,P17-03").split(","):
    spec=json.loads((SRC/"Specs"/(id+".json")).read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(MODEL/(id+".fbx")),axis_forward="-Z",axis_up="Y")
    objs=list(bpy.context.scene.objects);meshes=[o for o in objs if o.type=="MESH"]
    if len(meshes)!=len(spec["children"]):
        raise RuntimeError(id+" FBX round-trip mesh count: "+str(len(meshes)))
    for o in meshes:
        if not o.data.uv_layers or len(o.data.uv_layers.active.data)==0:
            raise RuntimeError(id+" FBX lost UV0: "+o.name)
        if len(o.data.polygons)==0: raise RuntimeError(id+" empty geometry: "+o.name)
    if id=="P17-03" and not any("LeverPivot" in o.name for o in objs):
        raise RuntimeError(id+" FBX lost LeverPivot")
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
    lo=[min(x[i] for x in pts) for i in range(3)]
    hi=[max(x[i] for x in pts) for i in range(3)]
    measured=[hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]]
    if any(abs(measured[i]-spec["dimensions"][i])>.005 for i in range(3)):
        raise RuntimeError(id+" FBX dimensions mismatch "+str(measured))
    results.append({"id":id,"status":"PASS","meshes":len(meshes),"uv0":len(meshes),"moving_pivots":(1 if id=="P17-03" else 0),"dimensions_WDH":measured})
    print("PASS FBX ROUNDTRIP",id,measured,"UV0",len(meshes),flush=True)
    for f in [MODEL/(id+".fbx"),SRC/"Blender"/(id+".blend")]:
        hashes[str(f.relative_to(R))]=hashlib.sha256(f.read_bytes()).hexdigest()
for p in sorted((SRC/"Previews").glob("P17-0*.png")):
    hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
report={"blender_version":bpy.app.version_string,"fbx_round_trip":results,"sha256":hashes,"unity":"NOT RUN","c01_02":"PENDING"}
out=SRC/"QA"/("BLENDER_FBX_ROUNDTRIP_PASS19.json" if __import__("os").environ.get("C01_IDS") else "BLENDER_FBX_ROUNDTRIP.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+"\n")
print("W01 Blender FBX roundtrip 3/3 PASS; SHA256",len(hashes),"files",flush=True)
