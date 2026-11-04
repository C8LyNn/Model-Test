"""Reconstruct the final v7.0 assembly from v6.8 plus the v6.9/v7.0 manifests."""
from copy import deepcopy
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
def read(path):return json.loads((ROOT/path).read_text(encoding='utf8'))

def build():
    data=read('Assets/C01ShipV68/Data/ship_v68.json')
    bridge=read('Assets/C01ShipV69/Data/bridge_layout.json')
    wall=read('Assets/C01ShipV70/Data/wall_repair.json')
    roof=read('Assets/C01ShipV70/Data/roof_repair.json')
    placements=data['placements'];ids={p['id']:p for p in placements}
    models={m['id']:m for m in data['models']}
    for q in bridge['placements']:
        if q['added']:
            if q['id'] in ids:raise ValueError('Duplicate bridge item '+q['id'])
            sample=next(p for p in placements if p['model']==q['model'] and p['zone']=='L1_BRIDGE' and p['category']=='CoreStations')
            item=deepcopy(sample);item.update(id=q['id']);placements.append(item);ids[item['id']]=item
        item=ids[q['id']]
        for name in ('x','y','z','yaw'):item[name]=q[name]
    for move in wall['moves']:
        p=ids[move['id']]
        if abs(p['y']-move['fromY'])>1e-6:raise ValueError('Incorrect wall position '+move['id'])
        p['y']=move['toY']
    single=deepcopy(models['W3_H3000']);single['id']='W3_H3000_V70_OneSeam'
    if single['parts'][1]['role']!='METAL':raise ValueError('Unexpected wall trim')
    single['parts'][1]['role']='PANEL';data['models'].append(single);models[single['id']]=single
    fascia=deepcopy(models['W3_H400_FASCIA']);fascia['id']='W3_H400_V70_TopSeam'
    if len(fascia['parts'])!=1:raise ValueError('Unexpected fascia model')
    lower=deepcopy(fascia['parts'][0]);upper=deepcopy(lower)
    lower['y1']=.34;upper['y0']=.34;upper['role']='METAL';fascia['parts']=[lower,upper]
    data['models'].append(fascia);models[fascia['id']]=fascia
    for ident in wall['singleSeamWalls']:ids[ident]['model']=single['id']
    for ident in wall['topBandFascias']:ids[ident]['model']=fascia['id']
    variants={}
    for item in roof['roofs']:
        p=ids[item['id']]
        if p['model']!=item['model']:raise ValueError('Incorrect roof model '+item['id'])
        key=json.dumps([item['model'],item['caps']],sort_keys=True,separators=(',',':'))
        if key not in variants:
            model=deepcopy(models[item['model']]);model['id']='C_V70_'+hashlib.sha1(key.encode()).hexdigest()[:12]
            if model['id']!=item['variant']:raise ValueError('Roof variant ID mismatch')
            for part in model['parts']:part['y1']=round(part['y1']+.4,7)
            for cap in item['caps']:
                model['parts'].append(dict(role='HULL',outline=cap['outline'],y0=.2,y1=.4))
            model['nominal'][1]=.6;data['models'].append(model);models[model['id']]=model;variants[key]=model['id']
        p['model']=variants[key]
    data['version']='C01.SHIP.7.0'
    return data

if __name__=='__main__':
    data=build();out=ROOT/'C01SourceV70/Data/ship_v70.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    print(json.dumps({k:len(data[k]) for k in ('placements','models','zones','gates','lifts')}))
