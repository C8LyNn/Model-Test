"""C01-12 PASS05: deterministic SHA and binary-header evidence gate.
Usage: python verify_sha_manifest.py <repository root>
Actual mesh geometry test is in compare_pass05.py (requires numpy).
"""
import json
import hashlib
import sys
from pathlib import Path


def main(repo):
    root = repo / 'C01StandaloneKits' / 'FloorCeiling'
    report = json.loads((root / 'QA' / 'PASS05_binary_fbx_pair_report.json').read_text())
    names = {'F01': 'C01_SHI_F01_FLOOR_BASIC', 'F02': 'C01_SHI_F02_FLOOR_MARKED',
             'C01': 'C01_SHI_C01_CEILING_BASIC'}
    for key, stem in names.items():
        row = report['models'][key]
        assert row['geometry_signature_same'] is True
        assert row['uv0_degenerate_triangles_before'] == 4 and row['uv0_degenerate_triangles_after'] == 0
        assert row['v_e_f_t_before'] == row['v_e_f_t_after'] == [16, 28, 14, 28]
        files = [
            (root / 'FBX_Blender_Export' / (stem + '_v002.fbx'), row['fbx_sha256_before']),
            (root / 'RepairPass03' / 'FBX' / (stem + '_v003.fbx'), row['fbx_sha256_after'])
        ]
        for path, expected in files:
            raw = path.read_bytes()
            assert raw.startswith(b'Kaydara FBX Binary  ' + bytes((0, 26, 0))), path
            actual = hashlib.sha256(raw).hexdigest()
            assert actual == expected, (key, path.name, actual, expected)
        print(key, 'PASS: binary FBX headers and exact before/after SHA256')
    assert report['unity_pass05'] == 'NOT_RUN' and report['independent_qa'] == 'PENDING'
    print('PASS05 SHA evidence 6/6 PASS; Blender/Unity not inferred')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python verify_sha_manifest.py <repo root>')
    main(Path(sys.argv[1]))
