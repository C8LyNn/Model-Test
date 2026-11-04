from pathlib import Path
import hashlib
import json
import tarfile

root = Path(__file__).resolve().parent
package = root / 'C01_Ship_Multideck_v7.2.unitypackage'
with tarfile.open(package, 'r:gz') as archive:
    members = {m.name: m for m in archive.getmembers()}
    paths = {archive.extractfile(m).read().decode('utf8'): n[:-len('/pathname')]
             for n,m in members.items() if n.endswith('/pathname')}
    required = ['Assets/C01ShipV72/Scenes/C01_Ship_Multideck_v72.unity',
                'Assets/C01ShipV72/Prefabs/C01_SHIP_MASTER_V72.prefab',
                'Assets/C01ShipV72/Data/logistics.json',
                'Assets/C01ShipV71/Prefabs/C01_SHIP_MASTER_V71.prefab',
                'Assets/C01ShipV70/Prefabs/C01_SHIP_MASTER_V70.prefab',
                'Assets/C01ShipV68/Prefabs/C01_SHIP_MASTER_V68.prefab',
                'Assets/C01ShipV5/Runtime/ShipLiftV5.cs',
                'Assets/C01ShipV72/Tests/PlayMode/ShipLogisticsV72Tests.cs',
                'Assets/C01ShipV72/README.md']
    assert all(p in paths for p in required), [p for p in required if p not in paths]
    plan = json.loads(archive.extractfile(members[paths[required[2]]+'/asset']).read())
    assert len(plan['moves']) == 14 and len(plan['swaps']) == 4
report = {'status':'PASS','bytes':package.stat().st_size,
          'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
          'required_assets':required,'moved_items':len(plan['moves']),'sectors':len(plan['swaps'])}
(root/'package_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
