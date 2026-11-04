from pathlib import Path
import hashlib
import json
import tarfile

folder = Path(__file__).resolve().parent
package = folder / 'C01_Ship_Multideck_v6.8.1.unitypackage'
with tarfile.open(package, 'r:gz') as archive:
    members = {member.name: member for member in archive.getmembers()}
    names = {}
    for name, member in members.items():
        if name.endswith('/pathname'):
            names[archive.extractfile(member).read().decode('utf8')] = name[:-len('/pathname')]
    required = [
        'Assets/C01ShipV68/Scenes/C01_Ship_Multideck_v68.unity',
        'Assets/C01ShipV68/Prefabs/C01_SHIP_MASTER_V68.prefab',
        'Assets/C01ShipV5/Runtime/ShipGateV5.cs',
        'Assets/C01ShipV5/Runtime/ShipExplorerV5.cs',
        'Assets/C01ShipV61/Signage/ButtonSignage.cs',
        'Assets/C01ShipV6/Cargo/Runtime/CargoLiftController.cs',
    ]
    assert all(name in names for name in required), [n for n in required if n not in names]
    def content(name):
        return archive.extractfile(members[names[name] + '/asset']).read().decode('utf8')
    assert 'if (next == openness) return;' in content(required[2])
    assert 'climbable.ToArray()' in content(required[3])
report = dict(status='PASS', bytes=package.stat().st_size,
              sha256=hashlib.sha256(package.read_bytes()).hexdigest(),
              required_assets=required, optimized_code='PASS')
(folder / 'package_validation.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report, indent=2))
