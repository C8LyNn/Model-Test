import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'C01SourceV71/Tools'))
sys.path.insert(0, str(ROOT / 'C01SourceV71/Tools/v5_dependencies'))
from audit_floor_v6 import audit as floors
from audit_ceiling_v6 import audit as ceilings
from audit_routes_v6 import audit as routes
from validate_ship_v5 import collision_audit

data = json.loads((ROOT / 'C01SourceV73/Data/ship_v73.json').read_text(encoding='utf8'))
result = {'floors': floors(data), 'ceilings': ceilings(data), 'routes': routes(data),
          'geometry': [collision_audit(data, pose) for pose in (0, .5, 1)]}
qa = ROOT / 'C01ShipV73_QA'
qa.mkdir(exist_ok=True)
(qa / 'source_audit.json').write_text(json.dumps(result, indent=2), encoding='utf8')
print(json.dumps(result, indent=2))
if (result['floors']['status'] != 'PASS' or result['ceilings']['status'] != 'PASS'
        or any(r['missing'] for r in result['routes'])
        or any(g['status'] != 'PASS' for g in result['geometry'])):
    sys.exit(1)
