from pathlib import Path
import hashlib
import json
import tarfile

root=Path(__file__).resolve().parent;package=root/'C01_Ship_Multideck_v7.4.unitypackage'
with tarfile.open(package,'r:gz') as archive:
    members={m.name:m for m in archive.getmembers()}
    paths={archive.extractfile(m).read().decode('utf8'):n[:-len('/pathname')] for n,m in members.items() if n.endswith('/pathname')}
    required=['Assets/C01ShipV74/Scenes/C01_Ship_Multideck_v74.unity',
              'Assets/C01ShipV74/Prefabs/C01_SHIP_MASTER_V74.prefab','Assets/C01ShipV74/Data/pursuit.json',
              'Assets/C01ShipV74/Prefabs/Modules/G_V74_Frame.prefab','Assets/C01ShipV74/Prefabs/Modules/G_V74_Leaf.prefab',
              'Assets/C01ShipV73/Prefabs/C01_SHIP_MASTER_V73.prefab','Assets/C01ShipV5/Runtime/ShipGateV5.cs',
              'Assets/C01ShipV74/Tests/PlayMode/SectorPursuitV74Tests.cs','Assets/C01ShipV74/README.md']
    assert all(p in paths for p in required),[p for p in required if p not in paths]
    plan=json.loads(archive.extractfile(members[paths[required[2]]+'/asset']).read())
    assert len(plan['gates'])==6 and len(plan['routes'])==3
    assert sum('_FLOOR_' in p['id'] for p in plan['added'])==24
report={'status':'PASS','bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
        'required_assets':required,'gates':len(plan['gates']),'routes':len(plan['routes']),'tiles':24}
(root/'package_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
