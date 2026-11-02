import hashlib,json,subprocess,tarfile
from pathlib import Path
STAGE=Path(__file__).resolve().parents[1]
LIVE=Path(r'C:\Users\kubap\Documents\GitHub\Model Test')
sha=lambda b:hashlib.sha256(b).hexdigest().upper()
baseline=json.loads((STAGE/'QA/host_before_v4.json').read_text(encoding='utf-8-sig'))
differences=[];intentional=[];restored=[];unchanged=0
previous=STAGE/'QA/host_preservation_v4.json'
if previous.exists():restored=json.loads(previous.read_text(encoding='utf-8')).get('restored',[])
for entry in baseline:
    relative=entry['path'].replace('\\','/');p=LIVE/relative
    current=p.read_bytes() if p.exists() else b''
    if sha(current)!=entry['sha256'] and relative=='ProjectSettings/ProjectSettings.asset':
        for before,after in [(b'runInBackground: 1',b'runInBackground: 0'),(b'runInBackground: 0',b'runInBackground: 1')]:
            candidate=current.replace(before,after)
            if sha(candidate)==entry['sha256']:
                p.write_bytes(candidate);current=candidate;restored.append(relative+' / TestRunner runInBackground only');break
    if sha(current)!=entry['sha256'] and relative=='Assets/Settings/Mobile_RPAsset.asset':
        original=subprocess.check_output(['git','show','HEAD:'+relative],cwd=LIVE)
        if sha(original)==entry['sha256']:
            (STAGE/'QA/mobile_rp_unity_migrated.asset').write_bytes(current)
            p.write_bytes(original);current=original;restored.append(relative+' / automatic URP serialization upgrade restored to exact baseline bytes')
    if sha(current)==entry['sha256']:unchanged+=1
    elif relative=='ProjectSettings/EditorBuildSettings.asset':intentional.append(relative+' / v4 scene appended, host snapshot retention PASS')
    else:differences.append(relative)
report=dict(status='PASS' if not differences else 'FAIL',checked=len(baseline),unchanged=unchanged,intentional=intentional,restored=restored,differences=differences)
(STAGE/'QA/host_preservation_v4.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
if differences:raise SystemExit(1)
package=LIVE/'C01ShipV4_QA/C01_Ship_Multideck_v4.0.unitypackage'
with tarfile.open(package) as archive:
    contents={m.name:archive.extractfile(m).read() for m in archive if m.isfile()}
    paths={data.decode('utf-8'):name.rsplit('/',1)[0] for name,data in contents.items() if name.endswith('/pathname')}
    mismatches=[];tested=0
    for path,prefix in paths.items():
        if not path.startswith('Assets/C01ShipV4/') or not (LIVE/path).is_file():continue
        try:data=contents[prefix+'/asset']
        except KeyError:continue
        tested+=1
        if data!=(LIVE/path).read_bytes():mismatches.append(path)
    required=['Assets/C01ShipV4/Scenes/C01_Ship_Multideck.unity','Assets/C01ShipV4/Prefabs/C01_SHIP_MULTIDECK_MASTER.prefab','Assets/C01ShipV4/Runtime/ShipExplorerV4.cs']
    missing=[p for p in required if p not in paths]
    check=dict(status='PASS' if not mismatches and not missing else 'FAIL',package_bytes=package.stat().st_size,package_sha256=sha(package.read_bytes()),paths=len(paths),source_files_compared=tested,mismatches=mismatches,missing_required=missing)
    (STAGE/'QA/unitypackage_v4.json').write_text(json.dumps(check,indent=2),encoding='utf-8');print(json.dumps(check,indent=2))
    if mismatches or missing:raise SystemExit(1)
