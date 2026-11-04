"""Describe changes to apply to the verified v7.0 master without rebuilding it."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
old = json.loads((ROOT / 'C01SourceV70/Data/ship_v70.json').read_text(encoding='utf8'))
new = json.loads((ROOT / 'C01SourceV71/Data/ship_v71.json').read_text(encoding='utf8'))
before = {p['id']: p for p in old['placements']}
after = {p['id']: p for p in new['placements']}
removed = sorted(before.keys() - after.keys())
added = [after[k] for k in sorted(after.keys() - before.keys())]
changed = [after[k] for k in sorted(after.keys() & before.keys()) if after[k] != before[k]]
assert all(before[k]['category'] in ('Nodes', 'Walls', 'Railings', 'Floors') for k in removed)
assert all(p['category'] in ('Nodes', 'Walls', 'Railings', 'Floors', 'CoreStations') for p in added)
gates = [g for g in new['gates'] if g.get('lift') in ('BRIDGE_PASSENGER', 'BRIDGE_PASSENGER_N')]
lifts = [l for l in new['lifts'] if l['id'] in ('BRIDGE_PASSENGER', 'BRIDGE_PASSENGER_N')]
result = dict(removed=removed, added=added, changed=changed, gates=gates, lifts=lifts)
out = ROOT / 'Assets/C01ShipV71/Data/bridge_delta.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2), encoding='utf8')
print(json.dumps({'removed': len(removed), 'added': len(added),
                  'changed': len(changed), 'by_category': dict(Counter(p['category'] for p in changed)),
                  'gates': len(gates), 'lifts': len(lifts)}))
