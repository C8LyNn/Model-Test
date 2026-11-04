from pathlib import Path
import hashlib
import json
import tarfile

root=Path(__file__).resolve().parent;package=root/'C01_Ship_Multideck_v7.3.unitypackage'
with tarfile.open(package,'r:gz') as archive:
    members={m.name:m for m in archive.getmembers()}
    paths={archive.extractfile(m).read().decode('utf8'):n[:-len('/pathname')]
           for n,m in members.items() if n.endswith('/pathname')}
    required=['Assets/C01ShipV73/Scenes/C01_Ship_Multideck_v73.unity',
              'Assets/C01ShipV73/Prefabs/C01_SHIP_MASTER_V73.prefab','Assets/C01ShipV73/Data/zoning.json',
              'Assets/C01ShipV72/Prefabs/C01_SHIP_MASTER_V72.prefab','Assets/C01ShipV71/Prefabs/C01_SHIP_MASTER_V71.prefab',
              'Assets/C01ShipV70/Prefabs/C01_SHIP_MASTER_V70.prefab','Assets/C01ShipV5/Runtime/ShipLiftV5.cs',
              'Assets/C01ShipV73/Tests/PlayMode/ShipZoningV73Tests.cs','Assets/C01ShipV73/README.md']
    assert all(p in paths for p in required),[p for p in required if p not in paths]
    plan=json.loads(archive.extractfile(members[paths[required[2]]+'/asset']).read())
    assert len(plan['moves'])==8 and len(plan['swaps'])==2 and len(plan['relabels'])==4
report={'status':'PASS','bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
        'required_assets':required,'moved_items':len(plan['moves']),'sectors':len(plan['swaps']),'support_labels':len(plan['relabels'])}
(root/'package_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
