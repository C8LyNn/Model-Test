from pathlib import Path
import hashlib
import json
import tarfile

root=Path(__file__).resolve().parent
package=root/'C01_Ship_Multideck_v6.9.unitypackage'
with tarfile.open(package,'r:gz') as archive:
    members={m.name:m for m in archive.getmembers()}
    paths={}
    for name,member in members.items():
        if name.endswith('/pathname'):
            paths[archive.extractfile(member).read().decode('utf8')]=name[:-len('/pathname')]
    required=['Assets/C01ShipV69/Scenes/C01_Ship_Multideck_v69.unity',
              'Assets/C01ShipV69/Prefabs/C01_SHIP_MASTER_V69.prefab',
              'Assets/C01ShipV69/Data/bridge_layout.json',
              'Assets/C01ShipV68/Prefabs/C01_SHIP_MASTER_V68.prefab',
              'Assets/C01ShipV68/Prefabs/Modules/P_V68_CommandConsole.prefab',
              'Assets/C01ShipV68/Prefabs/Modules/P_V68_CommandChair.prefab',
              'Assets/C01ShipV68/Prefabs/Modules/P_V68_StatusDisplay.prefab',
              'Assets/C01ShipV5/Runtime/ShipExplorerV5.cs',
              'Assets/C01ShipV5/Runtime/ShipGateV5.cs',
              'Assets/C01ShipV69/Tests/PlayMode/ShipBridgeV69Tests.cs',
              'Assets/C01ShipV69/README.md']
    assert all(p in paths for p in required),[p for p in required if p not in paths]
    layout=json.loads(archive.extractfile(members[paths[required[2]]+'/asset']).read())
    assert len(layout['placements'])==19
    test_code=archive.extractfile(members[paths[required[-2]]+'/asset']).read()
    assert b'BridgeGateButtonAndPassengerLiftStillOperate' in test_code
report={'status':'PASS','bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
        'required_assets':required,'bridge_placements':19}
(root/'package_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
