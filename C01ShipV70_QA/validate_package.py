from pathlib import Path
import hashlib
import json
import tarfile

root = Path(__file__).resolve().parent
package = root / 'C01_Ship_Multideck_v7.0.unitypackage'
with tarfile.open(package, 'r:gz') as archive:
    members = {m.name: m for m in archive.getmembers()}
    paths = {archive.extractfile(m).read().decode('utf8'): n[:-len('/pathname')]
             for n, m in members.items() if n.endswith('/pathname')}
    required = ['Assets/C01ShipV70/Scenes/C01_Ship_Multideck_v70.unity',
                'Assets/C01ShipV70/Prefabs/C01_SHIP_MASTER_V70.prefab',
                'Assets/C01ShipV70/Data/wall_repair.json',
                'Assets/C01ShipV70/Data/roof_repair.json',
                'Assets/C01ShipV69/Prefabs/C01_SHIP_MASTER_V69.prefab',
                'Assets/C01ShipV68/Prefabs/C01_SHIP_MASTER_V68.prefab',
                'Assets/C01ShipV5/Runtime/ShipExplorerV5.cs',
                'Assets/C01ShipV5/Runtime/ShipGateV5.cs',
                'Assets/C01ShipV70/README.md']
    assert all(p in paths for p in required), [p for p in required if p not in paths]
    roof = json.loads(archive.extractfile(members[paths[required[3]] + '/asset']).read())
    modules = [p for p in paths if p.startswith('Assets/C01ShipV70/Prefabs/Modules/') and p.endswith('.prefab')]
    assert len(modules) == 11, modules
    assert len(roof['roofs']) == 504
report = {'status': 'PASS', 'bytes': package.stat().st_size,
          'sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
          'required_assets': required, 'shared_modules': len(modules), 'roof_tiles': len(roof['roofs'])}
(root / 'package_validation.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report, indent=2))
