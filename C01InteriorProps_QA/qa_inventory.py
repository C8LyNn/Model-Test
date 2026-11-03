#!/usr/bin/env python3
"""C01-02 static inventory gate. It does not approve Blender, FBX or Unity geometry."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

OWNERS={**{f'P15-{n:02}':'C01-15' for n in range(1,4)},
        **{f'P16-{n:02}':'C01-16' for n in range(1,4)},
        **{f'P17-{n:02}':'C01-17' for n in range(1,4)},
        **{f'P18-{n:02}':'C01-18' for n in range(1,4)},
        **{f'P19-{n:02}':'C01-19' for n in range(1,5)}}
FILES={'blend':'blend','fbx':'fbx','prefab':'prefab','preview':'png'}

def safe_path(root,relative):
    p=(root/relative).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError('path escapes package')
    return p

def check_asset(root,asset_id,owner):
    tests={k:'NOT RUN' for k in ('manifest','blend','fbx','prefab','preview','fbx_signature','blender_open','unity_import','geometry','pivot','materials','colliders','clearance','playmode')}
    defects=[];evidence={}
    manifests=list(root.rglob(asset_id+'.asset.json'))
    if len(manifests)>1:tests['manifest']='FAIL';defects.append('duplicate manifest')
    elif manifests:
        try:
            m=json.loads(manifests[0].read_text(encoding='utf-8'))
            if m.get('asset_id')!=asset_id or m.get('owner')!=owner or not m.get('version'):
                raise ValueError('asset_id, owner or version incorrect')
            tests['manifest']='PASS'
            for key,ext in FILES.items():
                rel=m.get('files',{}).get(key)
                if not isinstance(rel,str) or not rel:continue
                p=safe_path(root,rel)
                if not p.is_file() or p.stat().st_size==0:continue
                if p.suffix.lower()!='.'+ext and not (key=='preview' and p.suffix.lower() in ('.jpg','.jpeg','.webp')):
                    tests[key]='FAIL';defects.append('bad extension: '+key);continue
                raw=p.read_bytes()
                if key=='blend' and not raw.startswith(b'BLENDER'):
                    tests[key]='FAIL';defects.append('invalid Blender signature');continue
                if key=='fbx':
                    tests['fbx_signature']='PASS' if raw.startswith(b'Kaydara FBX Binary  \x00\x1a\x00') or raw.lstrip().startswith(b'; FBX') else 'FAIL'
                    if tests['fbx_signature']=='FAIL':defects.append('invalid FBX signature')
                if key=='prefab' and not raw.lstrip().startswith(b'%YAML'):
                    tests[key]='FAIL';defects.append('invalid Unity prefab YAML');continue
                tests[key]='PASS';evidence[key]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'path':rel}
        except (ValueError,TypeError,OSError) as exc:
            tests['manifest']='FAIL';defects.append('manifest: '+str(exc))
    # File signatures and manifest values never substitute for measured meshes, pivots or scene tests.
    status='FAIL' if 'FAIL' in tests.values() else 'BLOCKED'
    return {'asset_id':asset_id,'owner':owner,'overall':status,'tests':tests,'defects':defects,'evidence':evidence}

def audit(root):
    return [check_asset(root,i,owner) for i,owner in OWNERS.items()]

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv)
    if not args.root.is_dir():p.error('--root must exist')
    rows=audit(args.root);args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'inventory.json').write_text(json.dumps({'assets':rows},indent=2)+'\n')
    with (args.output/'inventory.csv').open('w',newline='',encoding='utf-8') as stream:
        w=csv.writer(stream);w.writerow(['asset_id','owner','overall','manifest','blend','fbx','prefab','preview','unity_import','geometry','clearance','playmode'])
        for a in rows:w.writerow([a['asset_id'],a['owner'],a['overall']]+[a['tests'][t] for t in ('manifest','blend','fbx','prefab','preview','unity_import','geometry','clearance','playmode')])
    fails=sum(x['overall']=='FAIL' for x in rows)
    print(f'C01-02 QA: {len(rows)} assets / {fails} FAIL / {len(rows)-fails} BLOCKED; 0 approved')
    return 1 if fails else 2
if __name__=='__main__':sys.exit(main())
