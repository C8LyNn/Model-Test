#!/usr/bin/env python3
"""C01-01 deterministic static mesh-attribute preflight for OBJ and glTF JSON.

Only checks presence/consistency of source streams; never asserts Blender/Unity import.
No external dependencies. Outputs FAIL if any required surface lacks UV or normals.
"""
import argparse
import json
import math
from pathlib import Path


def result(path, fmt, triangles, surfaces, errors, warnings):
    return dict(file=str(path), format=fmt, triangles=triangles, surfaces=surfaces,
                static='FAIL' if errors else 'PASS', errors=errors, warnings=warnings,
                blender='NOT_RUN', fbx_roundtrip='NOT_RUN', unity_import='NOT_RUN',
                clearance='NOT_RUN', independent_qa='NOT_RUN')


def inspect_obj(path):
    vertices, tex, normals, faces = [], [], [], []
    errors, warnings = [], []
    current_object = 'default'
    for line_no, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        fields = line.split('#', 1)[0].split()
        if not fields:
            continue
        kind, *values = fields
        if kind in ('o', 'g'):
            current_object = ' '.join(values) if values else 'unnamed'
        elif kind in ('v', 'vt', 'vn'):
            try:
                count = 3 if kind != 'vt' else 2
                nums = [float(s) for s in values[:count]]
                if len(nums) != count or not all(math.isfinite(n) for n in nums):
                    raise ValueError('invalid numeric coordinates')
                {'v': vertices, 'vt': tex, 'vn': normals}[kind].append(nums)
            except ValueError:
                errors.append(f'LINE_{line_no}:INVALID_{kind.upper()}')
        elif kind == 'f':
            if len(values) < 3:
                errors.append(f'LINE_{line_no}:FACE_TOO_SHORT')
                continue
            corners = []
            for corner in values:
                parts = corner.split('/')
                if len(parts) > 3:
                    errors.append(f'LINE_{line_no}:INVALID_FACE_TOKEN')
                    continue
                limits = (len(vertices), len(tex), len(normals))
                resolved = []
                for index, value in enumerate(parts + [''] * (3-len(parts))):
                    if not value:
                        resolved.append(None)
                        continue
                    try:
                        integer = int(value)
                        idx = (integer-1) if integer > 0 else limits[index]+integer
                        if integer == 0 or not 0 <= idx < limits[index]:
                            raise ValueError('index outside defined stream')
                        resolved.append(idx)
                    except ValueError:
                        errors.append(f'LINE_{line_no}:INVALID_INDEX_{index}')
                        resolved.append(None)
                corners.append(resolved)
            if len(corners) == len(values):
                faces.append((line_no, current_object, corners))
    if not vertices:
        errors.append('NO_VERTICES')
    if not faces:
        errors.append('NO_FACES')
    triangles = 0
    for line_no, obj, corners in faces:
        triangles += len(corners)-2
        if any(c[1] is None for c in corners):
            errors.append(f'LINE_{line_no}:MISSING_TEXCOORD_0')
        if any(c[2] is None for c in corners):
            errors.append(f'LINE_{line_no}:MISSING_NORMAL')
        # Reject collapsed face fan and zero-area primitives (geometry QA, not watertight QA).
        if all(c[0] is not None for c in corners):
            pts = [vertices[c[0]] for c in corners]
            for i in range(1, len(pts)-1):
                a, b, c = pts[0], pts[i], pts[i+1]
                ab = [b[j]-a[j] for j in range(3)]
                ac = [c[j]-a[j] for j in range(3)]
                cross = [ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0]]
                if sum(x*x for x in cross) < 1e-16:
                    errors.append(f'LINE_{line_no}:DEGENERATE_TRIANGLE')
    warnings.append('STATIC_ONLY: OBJ attributes do not prove FBX/Unity roundtrip or normal orientation')
    return result(path, 'obj', triangles, len(faces), sorted(set(errors)), warnings)


def inspect_gltf(path):
    errors, warnings = [], []
    try:
        doc = json.loads(path.read_text(encoding='utf-8-sig'))
    except (ValueError, UnicodeError) as exc:
        return result(path, 'gltf', 0, 0, [f'INVALID_JSON:{type(exc).__name__}'], [])
    accessors = doc.get('accessors', [])
    meshes = doc.get('meshes', [])
    if not isinstance(accessors, list) or not isinstance(meshes, list):
        return result(path, 'gltf', 0, 0, ['INVALID_ACCESSORS_OR_MESHES'], [])
    triangles, surfaces = 0, 0
    for mi, mesh in enumerate(meshes):
        for pi, primitive in enumerate(mesh.get('primitives', [])):
            surfaces += 1
            tag = f'MESH_{mi}_PRIMITIVE_{pi}'
            mode = primitive.get('mode', 4)
            if mode != 4:
                errors.append(f'{tag}:UNSUPPORTED_NON_TRIANGLES_MODE_{mode}')
            attrs = primitive.get('attributes', {})
            if not isinstance(attrs, dict):
                errors.append(f'{tag}:INVALID_ATTRIBUTES')
                continue
            for sem in ('POSITION', 'NORMAL', 'TEXCOORD_0'):
                if sem not in attrs:
                    errors.append(f'{tag}:MISSING_{sem}')
            counts = []
            for sem in ('POSITION', 'NORMAL', 'TEXCOORD_0'):
                idx = attrs.get(sem)
                if idx is None:
                    continue
                if type(idx) is not int or not 0 <= idx < len(accessors):
                    errors.append(f'{tag}:INVALID_ACCESSOR_{sem}')
                    continue
                n = accessors[idx].get('count')
                expected = 'VEC2' if sem == 'TEXCOORD_0' else 'VEC3'
                if type(n) is not int or n <= 0 or accessors[idx].get('type') != expected:
                    errors.append(f'{tag}:INVALID_ACCESSOR_SHAPE_{sem}')
                else:
                    counts.append(n)
            if counts and len(set(counts)) != 1:
                errors.append(f'{tag}:STREAM_COUNT_MISMATCH')
            idx = primitive.get('indices')
            if idx is not None:
                if type(idx) is not int or not 0 <= idx < len(accessors):
                    errors.append(f'{tag}:INVALID_INDICES_ACCESSOR')
                else:
                    count = accessors[idx].get('count', 0)
                    if type(count) is not int or count <= 0 or count % 3:
                        errors.append(f'{tag}:INVALID_INDEX_COUNT')
                    else:
                        triangles += count // 3
            elif counts:
                triangles += counts[0] // 3
                if counts[0] % 3:
                    errors.append(f'{tag}:UNINDEXED_NOT_TRIANGULATED')
    if not surfaces:
        errors.append('NO_PRIMITIVES')
    warnings.append('STATIC_ONLY: JSON semantic check, does not verify external/embedded buffers, tangent winding or Unity import')
    return result(path, 'gltf', triangles, surfaces, sorted(set(errors)), warnings)


def inspect(path):
    if not path.is_file():
        return result(path, path.suffix.lower().lstrip('.'), 0, 0, ['FILE_MISSING'], [])
    if path.suffix.lower() == '.obj':
        return inspect_obj(path)
    if path.suffix.lower() == '.gltf':
        return inspect_gltf(path)
    return result(path, path.suffix.lower().lstrip('.'), 0, 0, ['UNSUPPORTED_FORMAT'], [])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--json-out', type=Path)
    args = parser.parse_args()
    report = dict(contract='C01-PROP-INTERFACE-0.2.1', checks=[inspect(path) for path in args.files])
    report['status'] = 'FAIL' if any(x['static'] == 'FAIL' for x in report['checks']) else 'PASS'
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload+'\n', encoding='utf-8')
    raise SystemExit(1 if report['status'] == 'FAIL' else 0)


if __name__ == '__main__':
    main()
