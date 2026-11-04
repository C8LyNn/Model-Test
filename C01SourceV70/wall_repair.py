"""Plan modular wall and slab-edge adjustments without modifying the ship source."""
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent.parent

def build(data):
    placements=[deepcopy(p) for p in data['placements'] if p['category'] in ('Walls','Nodes')]
    groups=defaultdict(list)
    for p in placements:groups[(p['category'],p['x'],p['z'],p['yaw'])].append(p)
    floors=[d['y'] for d in sorted(data['decks'],key=lambda d:d['id'])]
    slab_bottom=round(floors[1]+3,7);slab_top=floors[2];roof=round(slab_top+3,7)
    thickness=round(slab_top-slab_bottom,7)
    if abs(thickness-.4)>1e-6:raise ValueError('Unexpected slab thickness')
    moves=[]
    for group in groups.values():
        for short in group:
            if short['model'] not in ('W3_H400','N_H400') or abs(short['y']-(roof-thickness))>1e-6:continue
            expected='W3_H3000' if short['category']=='Walls' else 'N_H3000'
            matches=[p for p in group if p['model']==expected and abs(p['y']-slab_bottom)<1e-6]
            if len(matches)!=1:raise ValueError('Ambiguous upper module '+short['id'])
            full=matches[0]
            moves.extend([dict(id=full['id'],fromY=full['y'],toY=slab_top),
                          dict(id=short['id'],fromY=short['y'],toY=slab_bottom)])
            full['y']=slab_top;short['y']=slab_bottom
    single=[];tops=[]
    for group in groups.values():
        for wall in group:
            if wall['category']!='Walls' or wall['model']!='W3_H3000':continue
            short=[p for p in group if p['model'].startswith('W3_H400') and abs(p['y']-wall['y']-3)<1e-6]
            if not short:continue
            if len(short)!=1:raise ValueError('Ambiguous fascia '+wall['id'])
            single.append(wall['id']);fascia=short[0]
            if not any(p['model']=='W3_H3000' and abs(p['y']-fascia['y']-thickness)<1e-6 for p in group):tops.append(fascia['id'])
    return dict(version='C01.SHIP.7.0',slabThickness=thickness,moves=moves,
                singleSeamWalls=sorted(single),topBandFascias=sorted(tops))

if __name__=='__main__':
    data=json.loads((ROOT/'Assets/C01ShipV68/Data/ship_v68.json').read_text(encoding='utf8'))
    result=build(data);out=ROOT/'Assets/C01ShipV70/Data/wall_repair.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:len(result[k]) for k in ('moves','singleSeamWalls','topBandFascias')}))
