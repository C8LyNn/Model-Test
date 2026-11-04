from pathlib import Path
import hashlib
import json
import tarfile

root=Path(__file__).resolve().parent;package=root/'C01_Ship_Multideck_v7.6.unitypackage'
with tarfile.open(package,'r:gz') as archive:
    members={m.name:m for m in archive.getmembers()}
    paths={archive.extractfile(m).read().decode('utf8'):n[:-len('/pathname')] for n,m in members.items() if n.endswith('/pathname')}
    required=['Assets/C01ShipV76/Scenes/C01_Ship_Multideck_v76.unity',
              'Assets/C01ShipV76/Prefabs/C01_SHIP_MASTER_V76.prefab','Assets/C01ShipV76/Data/operations.json',
              'Assets/C01ShipV76/Prefabs/Modules/G76_LaunchLeft.prefab','Assets/C01ShipV76/Prefabs/Modules/G76_LaunchRight.prefab',
              'Assets/C01ShipV76/Prefabs/Modules/G76_LaunchLeaf.prefab','Assets/C01ShipV75/Prefabs/C01_SHIP_MASTER_V75.prefab',
              'Assets/C01ShipV76/Tests/PlayMode/ShipOperationsV76Tests.cs','Assets/C01ShipV76/README.md']
    assert all(p in paths for p in required),[p for p in required if p not in paths]
    plan=json.loads(archive.extractfile(members[paths[required[2]]+'/asset']).read())
    assert len(plan['moves'])==15 and len(plan['labels'])==6 and len(plan['added'])==24
report={'status':'PASS','bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
        'required_assets':required,'moved':len(plan['moves']),'rooms':len(plan['labels'])}
(root/'package_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
