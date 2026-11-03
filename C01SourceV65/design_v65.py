"""Single source for the v6.2 wall finish, lift cabins and bridge fixtures."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def stripe_centers(y, height):
    return [round(k * 3.0, 7) for k in range(math.floor((y - .06) / 3), math.ceil((y + height + .06) / 3) + 1)
            if y - .06 < k * 3 < y + height + .06]


def build():
    base = json.loads((ROOT / 'Assets/C01ShipV65/Data/ship_v65.json').read_text(encoding='utf-8'))
    walls = []
    for item in base['placements']:
        if item['category'] != 'Walls' or not item['model'].startswith('W3_H'):
            continue
        height = int(item['model'].split('_')[1][1:]) / 1000
        walls.append(dict(id=item['id'], y=item['y'], height=height,
                          stripeCenters=stripe_centers(item['y'], height)))

    lifts = []
    gates = {gate['id']: gate for gate in base['gates']}
    removed_buttons = []
    for source in base['lifts']:
        for landing in source['landings']:
            removed_buttons.append(gates[landing]['buttons'][1])
        x0, x1, z0, z1 = source['bounds']
        # Keep a real running clearance from the stationary shaft walls.
        hx, hz = (x1 - x0) / 2 - .04, (z1 - z0) / 2 - .04
        cargo = source['id'].startswith('STERN_CARGO')
        width = 2.25 if cargo else 2.15
        door_center = (1.5 if source['id']=='STERN_CARGO_N' else -1.5) if cargo else 0
        door_min, door_max = door_center - width/2, door_center + width/2
        thickness, wall_h, roof_t = .08, 2.7, .08
        panels = []

        def panel(role, center, size):
            panels.append(dict(id=source['id']+'_'+role+'_'+str(len(panels)), role=role,
                               center=[round(v, 5) for v in center],
                               size=[round(v, 5) for v in size]))

        def line(role, axis, start, end, fixed):
            count = math.ceil((end - start) / 2.85)
            for i in range(count):
                a, b = start + (end-start)*i/count, start + (end-start)*(i+1)/count
                if axis == 'x': panel(role, [(a+b)/2, wall_h/2, fixed], [b-a, wall_h, thickness])
                else: panel(role, [fixed, wall_h/2, (a+b)/2], [thickness, wall_h, b-a])

        line('side_s', 'x', -hx, hx-thickness, -hz+thickness/2)
        line('side_n', 'x', -hx, hx-thickness, hz-thickness/2)
        line('back', 'z', -hz, hz, hx-thickness/2)
        line('front', 'z', -hz+thickness, door_min, -hx+thickness/2)
        line('front', 'z', door_max, hz-thickness, -hx+thickness/2)
        nx, nz = math.ceil(2*hx/2.85), math.ceil(2*hz/2.85)
        for i in range(nx):
            for j in range(nz):
                sx, sz = 2*hx/nx, 2*hz/nz
                panel('roof', [-hx+sx*(i+.5), wall_h+roof_t/2, -hz+sz*(j+.5)], [sx, roof_t, sz])
        lifts.append(dict(id=source['id'], halfX=hx, halfZ=hz, doorMin=door_min,
                          doorMax=door_max, doorWidth=width, roofHeight=wall_h,
                          buttonZ=round(hz-thickness-.005, 5), panels=panels))

    bridge = [dict(id='COMMAND_CHAIR', kind='captain', position=[-19.5,0,45]),
              dict(id='OFFICER_CHAIR_A', kind='chair', position=[-19.5,0,41.5]),
              dict(id='OFFICER_CHAIR_B', kind='chair', position=[-19.5,0,48.5])]
    for i, z in enumerate((35,39,43,47,51,55)):
        bridge.append(dict(id=f'BRIDGE_CONSOLE_{i}', kind='console', position=[-24,0,z]))
    for i, z in enumerate((39,42,45,48,51)):
        bridge.append(dict(id=f'BRIDGE_VIEWSCREEN_{i}', kind='screen', position=[-31,0,z]))
    for p in bridge: p['position'][2] -= 1.5
    return dict(version='C01.SHIP.6.5', grid=3, wallStripeWidth=.12, walls=walls, lifts=lifts,
                removedLandingButtons=removed_buttons, bridge=bridge)


if __name__ == '__main__':
    result = build()
    dest = ROOT / 'Assets/C01ShipV65/Data/polish_v65.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, separators=(',', ':'), ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: len(result[k]) for k in ('walls', 'lifts', 'bridge')}))
