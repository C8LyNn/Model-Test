import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'Assets/C01InteriorProps/P15'
expected=[P/'Sources/Blender'/f'{i}.blend' for i in ('P15-01','P15-02','P15-03')]
expected += [P/'Models/FBX'/f'{i}.fbx' for i in ('P15-01','P15-02','P15-03','P15-03_Body','P15-03_Door')]
expected += [P/'Previews/Blender'/f'{i}_{view}.png' for i in ('P15-01','P15-02','P15-03') for view in ('front','iso','side')]
out=[]
for p in expected:
    b=p.read_bytes() if p.is_file() else b''
    valid=(p.suffix=='.blend' and b.startswith(b'BLENDER') or
           p.suffix=='.fbx' and b.startswith(b'Kaydara FBX Binary') or
           p.suffix=='.png' and b.startswith(bytes([137,80,78,71,13,10,26,10])))
    out.append(dict(path=str(p.relative_to(ROOT)),status='PASS' if valid and len(b)>200 else 'FAIL',
                    size=len(b),sha256=hashlib.sha256(b).hexdigest() if b else None))
report={'scope':'file signatures/hash only; not Blender geometry QA or Unity import','files':out,
        'result':'PASS' if all(v['status']=='PASS' for v in out) else 'FAIL',
        'unity':'NOT RUN','independent_qa':'NOT RUN'}
(P/'QA').mkdir(parents=True,exist_ok=True)
(P/'QA/blender_export_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['result'],'signatures checked:',len(out))
if report['result']!='PASS':raise SystemExit(1)
