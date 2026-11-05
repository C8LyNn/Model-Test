import json,sys
from pathlib import Path
r=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(r/'C01SourceV71/Tools'),str(r/'C01SourceV71/Tools/v5_dependencies'),str(r/'C01SourceV77')]
from audit_floor_v77 import audit as floors
from audit_routes_v77 import audit as routes
from validate_ship_v5 import collision_audit
source=(r/'C01SourceV77/audit_ceiling_v77.py').read_text(encoding='utf8').replace('planes[6.0 if deck==1 and kind=="sector"','planes[9.0 if deck==1 and kind=="sector"')
scope={'__name__':'ceiling_v79'};exec(compile(source,'ceiling_v79','exec'),scope)
p=json.loads((r/'C01SourceV79/Data/ship_v79.json').read_text(encoding='utf8'))
res={'floors':floors(p),'ceilings':scope['audit'](p),'routes':routes(p),'geometry':[collision_audit(p,x) for x in (0,.5,1)]}
(r/'C01SourceV79/surfaces_audit.json').write_text(json.dumps(res,indent=2),encoding='utf8')
print('floors:',res['floors']['status'],res['floors']['gaps'],'ceilings:',res['ceilings']['status'],res['ceilings']['gaps'],'routes missing:',sum(len(x['missing']) for x in res['routes']),'penetrations:',[x['penetrations'] for x in res['geometry']])
if res['floors']['status']!='PASS' or res['ceilings']['status']!='PASS' or any(x['missing'] for x in res['routes']) or any(x['status']!='PASS' for x in res['geometry']):sys.exit(1)
