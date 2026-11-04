"""Align the level-one cargo and technical sectors with deck-zero logistics."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
data=json.loads((ROOT/'C01SourceV72/Data/ship_v72.json').read_text(encoding='utf8'))
swap={'L1_CARGO':'L1_TECH','L1_TECH':'L1_CARGO'}
shift={'L1_CARGO':84,'L1_TECH':-84}
labels={'L1_CARGO':'MAGAZYN LADUNKOWY','L1_TECH':'SEKTOR TECHNICZNY'}
support={'L1_S_SUPPORT_03':'WARSZTAT','L1_S_SUPPORT_04':'CZESCI ZAMIENNE',
         'L1_S_SUPPORT_11':'EWIDENCJA LADUNKU','L1_S_SUPPORT_12':'NARZEDZIA LADUNKOWE'}
moves=[]
for p in data['placements']:
    old=p['zone']
    if old not in swap:continue
    if p['category']=='Props':
        x=p['x'];p['x']+=shift[old]
        moves.append(dict(id=p['id'],model=p['model'],zone=old,fromX=x,toX=p['x'],y=p['y'],z=p['z']))
    else:p['zone']=swap[old]
for z in data['zones']:
    if z['id'] in swap:
        z['id']=swap[z['id']];z['label']=labels[z['id']]
    elif z['id'] in support:z['label']=support[z['id']]
for gate in data['gates']:gate['zones']=[swap.get(z,z) for z in gate['zones']]
for link in data['links']:
    for key in ('a','b'):link[key]=swap.get(link[key],link[key])
data['version']='C01.SHIP.7.3'
assert len(moves)==8
plan={'version':data['version'],'swaps':[dict(original=a,replacement=b,label=labels[b]) for a,b in swap.items()],
      'relabels':[dict(id=a,label=b) for a,b in support.items()],'moves':moves}
out=ROOT/'Assets/C01ShipV73/Data/zoning.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(plan,indent=2),encoding='utf8')
(ROOT/'C01SourceV73/Data/ship_v73.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('moved',len(moves),'sector swaps',len(swap),'support relabels',len(support))
