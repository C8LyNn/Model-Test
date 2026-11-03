import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent/'v5_dependencies'))
from validate_ship_v5 import collision_audit
data=json.loads((root/'Assets/C01ShipV65/Data/ship_v65.json').read_text(encoding='utf8'))
out=root/'C01ShipV65_QA';out.mkdir(exist_ok=True)
failed=False
for pose in (0, .25, .5, .75, 1):
    report=collision_audit(data,pose)
    (out/f'geometry_{pose}.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('pose',pose,'penetrations',report['penetrations'],flush=True)
    failed |= report['penetrations']>0
sys.exit(1 if failed else 0)
