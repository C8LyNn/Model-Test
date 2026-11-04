"""Align deck-zero engineering and storage with the rooms they serve."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
source = ROOT / 'C01SourceV71/Data/ship_v71.json'
data = json.loads(source.read_text(encoding='utf8'))
swap = {'L0_ENGINE_ROOM': 'L0_PURIFICATION', 'L0_PURIFICATION': 'L0_ENGINE_ROOM',
        'L0_CARGO': 'L0_FOOD_RESERVE', 'L0_FOOD_RESERVE': 'L0_CARGO'}
shift = {'L0_ENGINE_ROOM': 42, 'L0_PURIFICATION': -42,
         'L0_CARGO': 84, 'L0_FOOD_RESERVE': -84}
labels = {'L0_ENGINE_ROOM': 'MASZYNOWNIA', 'L0_PURIFICATION': 'OCZYSZCZALNIA',
          'L0_CARGO': 'LADOWNIA', 'L0_FOOD_RESERVE': 'ZAPASY ZYWNOSCI'}
moves = []
for p in data['placements']:
    old = p['zone']
    if old not in swap:
        continue
    if p['category'] == 'Props':
        oldx = p['x']
        p['x'] += shift[old]
        moves.append({'id': p['id'], 'model': p['model'], 'zone': old,
                      'fromX': oldx, 'toX': p['x'], 'y': p['y'], 'z': p['z']})
    else:
        p['zone'] = swap[old]
for z in data['zones']:
    if z['id'] in swap:
        old = z['id']
        z['id'] = swap[old]
        z['label'] = labels[z['id']]
for gate in data['gates']:
    gate['zones'] = [swap.get(x, x) for x in gate['zones']]
for link in data['links']:
    for key in ('a', 'b'):
        link[key] = swap.get(link[key], link[key])
data['version'] = 'C01.SHIP.7.2'
assert len(moves) == 14
delta = {'version': data['version'], 'swaps': [{'original': a, 'replacement': b, 'label': labels[b]}
                                                for a,b in swap.items()],
         'moves': moves}
out = ROOT / 'Assets/C01ShipV72/Data/logistics.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(delta, indent=2), encoding='utf8')
(ROOT / 'C01SourceV72/Data/ship_v72.json').write_text(
    json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
print('moved props:', len(moves), 'remapped zones:', len(swap))
