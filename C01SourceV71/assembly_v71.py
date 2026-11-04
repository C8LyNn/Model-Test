"""Combine the bridge-shaft candidate with the v6.9 stations and v7.0 surfaces."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'C01SourceV70'))
from wall_repair import build as wall_repair
from roof_repair import build as roof_repair


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf8'))


def build():
    data = read('C01SourceV71/Data/bridge_candidate.json')
    bridge = read('Assets/C01ShipV69/Data/bridge_layout.json')
    ids = {p['id']: p for p in data['placements']}
    models = {m['id']: m for m in data['models']}
    for q in bridge['placements']:
        if q['added']:
            sample = next(p for p in data['placements'] if p['model'] == q['model']
                          and p['zone'] == 'L1_BRIDGE' and p['category'] == 'CoreStations')
            item = deepcopy(sample)
            item['id'] = q['id']
            data['placements'].append(item)
            ids[item['id']] = item
        for field in ('x', 'y', 'z', 'yaw'):
            ids[q['id']][field] = q[field]
    # A central command surface and paired outer operations stations use the
    # existing kit and leave the main fore/aft passage open on both sides.
    for ident, model, x, z in (
        ('BRIDGE_COMMAND_TABLE', 'P_V68_CommandConsole', -26.5, 42.6),
        ('BRIDGE_PORT_OPS', 'P_V68_CommandConsole', -25, 27.6),
        ('BRIDGE_STARBOARD_OPS', 'P_V68_CommandConsole', -25, 57.6),
        ('BRIDGE_PORT_OPS_CHAIR', 'P_V68_CommandChair', -22.5, 27.9),
        ('BRIDGE_STARBOARD_OPS_CHAIR', 'P_V68_CommandChair', -22.5, 57.9),
    ):
        sample = next(p for p in data['placements'] if p['model'] == model
                      and p['category'] == 'CoreStations' and p['zone'] == 'L1_BRIDGE')
        item = deepcopy(sample)
        item.update(id=ident, x=x, y=0, z=z, yaw=0)
        data['placements'].append(item)
        ids[ident] = item
    wall = wall_repair(data)
    roof = roof_repair(data)
    for move in wall['moves']:
        ids[move['id']]['y'] = move['toY']
    single = deepcopy(models['W3_H3000'])
    single['id'] = 'W3_H3000_V70_OneSeam'
    single['parts'][1]['role'] = 'PANEL'
    data['models'].append(single)
    fascia = deepcopy(models['W3_H400_FASCIA'])
    fascia['id'] = 'W3_H400_V70_TopSeam'
    lower = deepcopy(fascia['parts'][0])
    upper = deepcopy(lower)
    lower['y1'], upper['y0'], upper['role'] = .34, .34, 'METAL'
    fascia['parts'] = [lower, upper]
    data['models'].append(fascia)
    for ident in wall['singleSeamWalls']:
        ids[ident]['model'] = single['id']
    for ident in wall['topBandFascias']:
        ids[ident]['model'] = fascia['id']
    variants = {}
    for item in roof['roofs']:
        p = ids[item['id']]
        key = json.dumps([item['model'], item['caps']], sort_keys=True, separators=(',', ':'))
        if key not in variants:
            model = deepcopy(models[item['model']])
            model['id'] = 'C_V70_' + hashlib.sha1(key.encode()).hexdigest()[:12]
            assert model['id'] == item['variant']
            for part in model['parts']:
                part['y1'] = round(part['y1'] + .4, 7)
            for cap in item['caps']:
                model['parts'].append(dict(role='HULL', outline=cap['outline'], y0=.2, y1=.4))
            model['nominal'][1] = .6
            data['models'].append(model)
            variants[key] = model['id']
        p['model'] = variants[key]
    data['version'] = 'C01.SHIP.7.1'
    return data


if __name__ == '__main__':
    data = build()
    (ROOT / 'C01SourceV71/Data/ship_v71.json').write_text(
        json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
    print('placements', len(data['placements']), 'models', len(data['models']))
