"""Check actual walkable footprint coverage against the six gate sockets."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'C01SourceV71/Tools/v5_dependencies'))
from validate_ship_v5 import solids,difference
from ship_geometry import polygon_area

def audit(data):
    plan=json.loads((ROOT/'Assets/C01ShipV74/Data/pursuit.json').read_text(encoding='utf8'))
    ground=[s for s in solids(data,1) if s['category'] in ('Floors','Walls','Nodes') and abs(s['hi']-3.4)<1e-6]
    gaps=[]
    for route in plan['routes']:
        for x in range(route['x0'],route['x1'],3):
            z=route['z0'];remaining=[[[x,z],[x+3,z],[x+3,z+3],[x,z+3]]]
            for part in ground:
                if part['x1']<=x or part['x0']>=x+3 or part['z1']<=z or part['z0']>=z+3:continue
                remaining=[r for poly in remaining for r in difference(poly,part['poly'])]
                if not remaining:break
            area=sum(polygon_area(p) for p in remaining)
            if area>1e-5:gaps.append({'sector':route['name'],'x':x,'z':z,'missingArea':round(area,6)})
    return {'status':'PASS' if not gaps else 'FAIL','tiles':24,'gaps':len(gaps),'examples':gaps[:20]}

if __name__=='__main__':
    data=json.loads((ROOT/'C01SourceV74/Data/ship_v74.json').read_text(encoding='utf8'))
    result=audit(data);out=ROOT/'C01ShipV74_QA/catwalk_coverage.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2));sys.exit(result['status']!='PASS')
