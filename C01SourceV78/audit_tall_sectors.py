"""Audit ceilings and structural overlaps in the v7.8 assembly data."""
import json, sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'C01SourceV71/Tools'))
sys.path.insert(0,str(root/'C01SourceV71/Tools/v5_dependencies'))
sys.path.insert(0,str(root/'C01SourceV77'))
from audit_floor_v77 import audit as floors
from audit_routes_v77 import audit as routes
from validate_ship_v5 import collision_audit
source=(root/'C01SourceV77/audit_ceiling_v77.py').read_text(encoding='utf8')
source=source.replace('planes[6.0 if deck==1 and kind=="sector"','planes[9.0 if deck==1 and kind=="sector"')
scope={'__name__':'ceiling_v78'};exec(compile(source,'ceiling_v78','exec'),scope)
data=json.loads((root/'C01SourceV78/Data/ship_v78.json').read_text(encoding='utf8'))
result={'floors':floors(data),'ceilings':scope['audit'](data),'routes':routes(data),'geometry':[collision_audit(data,x) for x in (0,.5,1)]}
(root/'C01SourceV78/audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
if result['floors']['status']!='PASS' or result['ceilings']['status']!='PASS' or any(r['missing'] for r in result['routes']) or any(g['status']!='PASS' for g in result['geometry']):sys.exit(1)
