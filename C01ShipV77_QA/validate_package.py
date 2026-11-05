from pathlib import Path
import hashlib
import json
import tarfile

root=Path(__file__).resolve().parent;package=root/'C01_Ship_Multideck_v7.7.unitypackage'
with tarfile.open(package,'r:gz') as archive:
    members={m.name:m for m in archive.getmembers()}
    paths={archive.extractfile(m).read().decode('utf8'):n[:-len('/pathname')] for n,m in members.items() if n.endswith('/pathname')}
    required=['Assets/C01ShipV77/Scenes/C01_Ship_Multideck_v77.unity',
              'Assets/C01ShipV77/Prefabs/C01_SHIP_MASTER_V77.prefab','Assets/C01ShipV77/Data/two_decks.json',
              'Assets/C01ShipV77/Prefabs/Modules/P77_ShaftPassenger.prefab','Assets/C01ShipV77/Prefabs/Modules/P77_ShaftCargo.prefab',
              'Assets/C01ShipV77/Prefabs/Modules/F77_LaunchEdge.prefab','Assets/C01ShipV76/Prefabs/C01_SHIP_MASTER_V76.prefab',
              'Assets/C01ShipV77/Tests/PlayMode/ShipTwoDecksV77Tests.cs','Assets/C01ShipV77/Tests/PlayMode/CargoTwoDecksV77Tests.cs',
              'Assets/C01ShipV5/Runtime/ShipLiftV5.cs','Assets/C01ShipV6/Cargo/Runtime/CargoLiftController.cs','Assets/C01ShipV77/README.md']
    assert all(p in paths for p in required),[p for p in required if p not in paths]
    plan=json.loads(archive.extractfile(members[paths[required[2]]+'/asset']).read())
    assert len(plan['moves'])==30 and len(plan['removedGates'])==39 and len(plan['added'])==36
report={'status':'PASS','bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
        'required_assets':required,'transferred':len(plan['moves']),'removedGates':len(plan['removedGates'])}
(root/'package_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
