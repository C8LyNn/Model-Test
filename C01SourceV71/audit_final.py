"""Check full assembled geometry, planned surfaces and access to each lift."""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'C01SourceV71/Tools'))
sys.path.insert(0, str(ROOT / 'C01SourceV71/Tools/v5_dependencies'))
from audit_floor_v6 import audit as floor_audit
from audit_ceiling_v6 import audit as ceiling_audit
from audit_routes_v6 import audit as routes_audit
from validate_ship_v5 import collision_audit

data = json.loads((ROOT / 'C01SourceV71/Data/ship_v71.json').read_text(encoding='utf8'))
report = {'floor': floor_audit(data), 'ceiling': ceiling_audit(data), 'routes': routes_audit(data)}
report['geometry'] = [collision_audit(data, pose) for pose in (0, .5, 1)]
qa = ROOT / 'C01ShipV71_QA'
qa.mkdir(exist_ok=True)
(qa / 'source_audit.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report, indent=2))
if (report['floor']['status'] != 'PASS' or report['ceiling']['status'] != 'PASS'
        or any(item['missing'] for item in report['routes'])
        or any(item['status'] != 'PASS' for item in report['geometry'])):
    sys.exit(1)
