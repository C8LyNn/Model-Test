"""Audit candidate geometry and route connectivity before touching the Unity scene."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'C01SourceV71/Tools'))
sys.path.insert(0, str(ROOT / 'C01SourceV71/Tools/v5_dependencies'))
import audit_routes_v6
from validate_ship_v5 import collision_audit

data = json.loads((ROOT / 'C01SourceV71/Data/bridge_candidate.json').read_text(encoding='utf8'))
geometry = collision_audit(data, 0)
routes = audit_routes_v6.audit(data)
report = {'geometry': geometry, 'routes': routes}
out = ROOT / 'C01SourceV71/Data/candidate_audit.json'
out.write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report, indent=2))
if geometry['status'] != 'PASS' or any(item['missing'] for item in routes):
    sys.exit(1)
