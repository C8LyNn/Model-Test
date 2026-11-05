import json
from pathlib import Path
import sys
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'C01SourceV71/Tools'))
sys.path.insert(0,str(root/'C01SourceV71/Tools/v5_dependencies'))
from audit_floor_v77 import audit as floors
from audit_ceiling_v77 import audit as ceilings
from audit_routes_v77 import audit as routes
from validate_ship_v5 import collision_audit
data=json.loads((root/'C01SourceV77/Data/ship_v77.json').read_text(encoding='utf8'))
result={'floors':floors(data),'ceilings':ceilings(data),'routes':routes(data),'geometry':[collision_audit(data,x) for x in (0,.5,1)]}
(root/'C01ShipV77_QA/source_audit.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
if result['floors']['status']!='PASS' or result['ceilings']['status']!='PASS' or any(r['missing'] for r in result['routes']) or any(g['status']!='PASS' for g in result['geometry']):sys.exit(1)
