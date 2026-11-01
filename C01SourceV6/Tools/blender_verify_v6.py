"""Check every Blender assembly placement against the Unity source manifest."""
import bpy
import json
import math
from pathlib import Path

here=Path(__file__).resolve().parent
project=here/"UnityProject" if (here/"UnityProject/Assets").is_dir() else here.parent.parent
qa=here/"QA" if (here/"UnityProject/Assets").is_dir() else here.parent/"QA"
data=json.loads((project/"Assets/C01ShipV6/Data/ship_v6.json").read_text(encoding="utf8"))
bpy.context.view_layer.update()
errors=[]
for p in data["placements"]:
    obj=bpy.data.objects.get(p["id"])
    if obj is None:
        errors.append(p["id"]+": missing")
        continue
    actual=obj.matrix_world.translation
    expected=(p["x"],-p["z"],p["y"])
    if any(abs(actual[i]-expected[i])>1e-4 for i in range(3)):
        errors.append(p["id"]+": position")
    expected_yaw=math.radians(p["yaw"])
    if abs(math.atan2(math.sin(obj.rotation_euler.z-expected_yaw),math.cos(obj.rotation_euler.z-expected_yaw)))>1e-4:
        errors.append(p["id"]+": rotation")
    if obj.get("model_id")!=p["model"]:
        errors.append(p["id"]+": model")
report=dict(status="PASS" if not errors else "FAIL",placements=len(data["placements"]),
            errors=len(errors),examples=errors[:30])
qa.mkdir(parents=True,exist_ok=True)
(qa/"blender_assembly_v6.json").write_text(json.dumps(report,indent=2),encoding="utf8")
print("BLENDER_ASSEMBLY",json.dumps(report))
if errors:
    raise RuntimeError("Blender assembly differs from the Unity manifest")
