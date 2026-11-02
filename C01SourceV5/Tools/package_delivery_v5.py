"""Package the real project bytes, source and QA without caches or Git credentials."""
import argparse, hashlib, json, os, zipfile
from pathlib import Path

def sha(data):
    return hashlib.sha256(data).hexdigest()

def package(project, output):
    excluded = {'.git', 'Library', 'Temp', 'Logs', 'UserSettings', 'obj', 'Obj', '.vs', '__pycache__'}
    extensions = {'.csproj', '.sln', '.slnx', '.blend1', '.pyc', '.tmp', '.user'}
    files = []
    for folder, dirs, names in os.walk(project):
        dirs[:] = sorted(d for d in dirs if d not in excluded)
        for name in sorted(names):
            path = Path(folder) / name
            if path.suffix in extensions:
                continue
            if name.startswith('InitTestScene') or name.endswith('.blend1.meta'):
                continue
            files.append((path, path.relative_to(project).as_posix()))
    manifest = []
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, relative in files:
            data = path.read_bytes()
            if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
                raise RuntimeError('Unresolved Git LFS pointer: ' + relative)
            manifest.append(dict(path=relative, size=len(data), sha256=sha(data)))
            archive.writestr('Model Test/' + relative, data)
        archive.writestr('CONTENTS_SHA256.json', json.dumps(manifest, indent=2))
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP CRC validation failed')
        for entry in manifest:
            data = archive.read('Model Test/' + entry['path'])
            if len(data) != entry['size'] or sha(data) != entry['sha256']:
                raise RuntimeError('ZIP byte validation failed: ' + entry['path'])
    report = dict(status='PASS', file=output.name, bytes=output.stat().st_size,
                  sha256=sha(output.read_bytes()), files=len(manifest),
                  crc='PASS', every_entry_sha256='PASS', unresolved_lfs_pointers=0)
    output.with_suffix('.validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    package(args.project.resolve(), args.output.resolve())
