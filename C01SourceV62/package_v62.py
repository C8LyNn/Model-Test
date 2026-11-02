"""Build and verify a portable Unity project archive without caches or Git state."""
import argparse
import hashlib
import json
import os
import zipfile
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def package(project, output):
    excluded={'.git','Library','Temp','Logs','UserSettings','obj','Obj','.vs','__pycache__'}
    extensions={'.csproj','.sln','.slnx','.blend1','.pyc','.tmp','.user','.log'}
    files=[]
    for folder, dirs, names in os.walk(project):
        dirs[:]=sorted(d for d in dirs if d not in excluded)
        for name in sorted(names):
            path=Path(folder)/name
            if name in excluded or path.suffix.lower() in extensions or name.endswith('.blend1.meta'):
                continue
            files.append((path,path.relative_to(project).as_posix()))
    output.parent.mkdir(parents=True,exist_ok=True)
    manifest=[]
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path, relative in files:
            data=path.read_bytes()
            if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
                raise RuntimeError('Unresolved Git LFS pointer: '+relative)
            manifest.append(dict(path=relative,size=len(data),sha256=digest(data)))
            archive.writestr('Model Test/'+relative,data)
        archive.writestr('CONTENTS_SHA256.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None: raise RuntimeError('ZIP CRC validation failed')
        for item in manifest:
            data=archive.read('Model Test/'+item['path'])
            if len(data)!=item['size'] or digest(data)!=item['sha256']:
                raise RuntimeError('ZIP content mismatch: '+item['path'])
    h=hashlib.sha256()
    with output.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''): h.update(chunk)
    report=dict(status='PASS',file=output.name,bytes=output.stat().st_size,sha256=h.hexdigest(),
                files=len(manifest),crc='PASS',every_entry_sha256='PASS',unresolved_lfs_pointers=0)
    output.with_suffix('.validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--project',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();package(args.project.resolve(),args.output.resolve())
