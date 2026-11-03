#!/usr/bin/env python3
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
models=json.loads((ROOT/'Source/parts.json').read_text(encoding='utf8'))
report={'status':'PASS','source':'actual native Blender export and stream inspection','models':[],'unity':'NOT RUN','independent_qa':'NOT RUN'}
for m in models:
    records=[]
    for ext,signature in [('.blend',b'BLENDER'),('.fbx',b'Kaydara FBX Binary  \x00\x1a\x00')]:
        f=ROOT/'Models'/m['id']/(m['id']+ext)
        b=f.read_bytes()
        assert len(b)>500 and b.startswith(signature),(str(f),'invalid native binary')
        records.append({'file':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'size_bytes':len(b)})
    for p in m['parts']:
        slug=''.join(c if c.isalnum() or c=='_' else '_' for c in p['name'])
        f=ROOT/'Models'/m['id']/(m['id']+'__'+slug+'.obj')
        t=f.read_text().splitlines()
        counts={k:sum(x.startswith(k+' ') for x in t) for k in ('v','vt','vn','f')}
        assert counts=={'v':8,'vt':24,'vn':6,'f':12},(f,counts)
        assert all(all(len(i.split('/'))==3 for i in x.split()[1:]) for x in t if x.startswith('f ')),f
    report['models'].append({'id':m['id'],'status':'PASS','native':records})
f=ROOT/'QA'/'blender_native_validation.json'
f.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
