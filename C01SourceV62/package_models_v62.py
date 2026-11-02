"""Package the editable Blender source and independently exported FBX modules."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

source=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
output=parser.parse_args().output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
files=[source/'C01_Ship_v62_NewModules.blend',source/'blender_export_v62.py',source/'verify_fbx_v62.py',
       source/'blender_export_report.json',source/'fbx_roundtrip_report.json']+sorted((source/'Models').glob('*.fbx'))
if len(files)!=23: raise RuntimeError('Expected source plus 18 FBX modules')
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for path in files: archive.write(path,path.relative_to(source).as_posix())
with zipfile.ZipFile(output) as archive:
    if archive.testzip() is not None: raise RuntimeError('Corrupt archive')
    for path in files:
        if archive.read(path.relative_to(source).as_posix())!=path.read_bytes():
            raise RuntimeError('Archive content mismatch: '+str(path))
print(json.dumps(dict(status='PASS',file=output.name,bytes=output.stat().st_size,
                      sha256=hashlib.sha256(output.read_bytes()).hexdigest(),fbx=18),indent=2))
