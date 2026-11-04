"""Unify the sector ownership using the same horizontal room footprint."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent.parent
data=json.loads((root/'C01SourceV75/Data/ship_platforms.json').read_text(encoding='utf8'))
sectors=[z for z in data['zones'] if z['deck']==1 and z['kind']=='sector']
upper=[z for z in data['zones'] if z['deck']==2 and z['kind'] in ('void','gallery')]
mapping={}
for s in sectors:
    matches=[z for z in upper if z['bounds']==s['bounds']]
    if len(matches)!=1 or s['floor']!=0 or s['height']!=6:raise ValueError('Invalid sector '+s['id'])
    mapping[matches[0]['id']]=s['id'];s['spansDecks']=True
if len(mapping)!=6:raise ValueError('Expected six sector pairs')
for p in data['placements']:
    p['zone']=mapping.get(p['zone'],p['zone'])
for g in data['gates']:
    g['zones']=[mapping.get(z,z) for z in g['zones']]
for l in data['links']:
    l['a']=mapping.get(l['a'],l['a']);l['b']=mapping.get(l['b'],l['b'])
data['zones']=[z for z in data['zones'] if z['id'] not in mapping]
data['version']='C01.SHIP.7.5'
plan={'version':data['version'],'mapping':[{'upper':u,'owner':o} for u,o in mapping.items()]}
owners=set(mapping.values())
expected={'placements':[p for p in data['placements'] if p['zone'] in owners and p['category']!='GateLeaves']}
(root/'C01SourceV75/Data/ship_v75.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
(root/'Assets/C01ShipV75/Data/sectors.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
(root/'Assets/C01ShipV75/Data/sector_placements.json').write_text(json.dumps(expected,separators=(',',':')),encoding='utf8')
print('Unified sector pairs:',mapping)
