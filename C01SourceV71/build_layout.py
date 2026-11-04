"""Generate a candidate bridge layout in the isolated project copy."""
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'C01SourceV71/Tools'))
import scene_data_v6

data = scene_data_v6.build()
baseline = json.loads((ROOT / 'Assets/C01ShipV68/Data/ship_v68.json').read_text(encoding='utf8'))
old = {p['id']: p for p in baseline['placements']}
new = {p['id']: p for p in data['placements']}
changed = [key for key in old.keys() & new.keys() if old[key] != new[key]]
report = {'removed': len(old.keys() - new.keys()), 'added': len(new.keys() - old.keys()),
          'changed': len(changed),
          'removed_categories': dict(Counter(old[k]['category'] for k in old.keys() - new.keys())),
          'added_categories': dict(Counter(new[k]['category'] for k in new.keys() - old.keys())),
          'changed_categories': dict(Counter(new[k]['category'] for k in changed))}
out = ROOT / 'C01SourceV71/Data/bridge_candidate.json'
out.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
print(json.dumps(report, indent=2))
