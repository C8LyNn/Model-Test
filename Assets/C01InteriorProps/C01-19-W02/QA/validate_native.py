#!/usr/bin/env python3
import json,hashlib,pathlib
R=pathlib.Path(__file__).resolve().parent.parent
models=json.loads((R/'Source'/'wave02_parts.json').read_text())
report={'scope':'native Blender outputs + UV/normal indexed OBJ','models':[],'Unity_import':'NOT RUN','independent_QA':'NOT RUN'}
for m in models:
  mfiles=[]
  for ext,magic in [('.blend',b'BLENDER'),('.fbx',b'Kaydara FBX Binary  \x00\x1a\x00')]:
    f=R/'Models'/m['id']/(m['id']+ext)
    b=f.read_bytes()
    assert b.startswith(magic) and len(b)>500,('invalid native file',f)
    mfiles.append({'path':str(f.relative_to(R)),'size':len(b),'sha256':hashlib.sha256(b).hexdigest()})
  for p in m['parts']:
    slug=''.join(c if c.isalnum() or c=='_' else '_' for c in p['name'])
    f=R/'Models'/m['id']/(m['id']+'__'+slug+'.obj')
    data=f.read_text().splitlines()
    actual=[sum(s.startswith(k+' ') for s in data) for k in ('v','vt','vn','f')]
    assert actual==[8,24,6,12],(f,actual)
    assert all(len(token.split('/'))==3 for line in data if line.startswith('f ') for token in line.split()[1:]),f
  for view in ('iso','front','side'):
    f=R/'Previews'/(m['id']+'_'+view+'.png')
    b=f.read_bytes()
    assert b.startswith(b'\x89PNG\r\n\x1a\n'),f
    mfiles.append({'path':str(f.relative_to(R)),'size':len(b),'sha256':hashlib.sha256(b).hexdigest()})
  report['models'].append({'id':m['id'],'status':'PASS','native_files':mfiles})
report['status']='PASS'
(R/'QA'/'blender_native_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
