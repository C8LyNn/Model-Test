"""C01-16 PASS06 native BLEND header regression (Python stdlib; NO Blender runtime).
Usage:
    python test_native_blend_header.py
    python test_native_blend_header.py --real-blend /path/to/actual.blend

The optional --real-blend test reads actual source bytes; it does NOT
execute Blender, FBX roundtrip or certify geometry.
"""
from __future__ import annotations
import argparse
import hashlib
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).with_name("ci_pass04_native.py")


def is_blender_header(raw: bytes) -> bool:
    return raw.startswith(b"BLENDER-")


class BlenderHeaderRegression(unittest.TestCase):
    def test_valid_blender_40_header(self):
        self.assertTrue(is_blender_header(b"BLENDER-v400"))
    def test_valid_blender_42_header(self):
        self.assertTrue(is_blender_header(b"BLENDER-v420"))
    def test_reject_seven_byte_prefix(self):
        self.assertFalse(is_blender_header(b"BLENDER"))
    def test_reject_git_lfs_pointer(self):
        self.assertFalse(is_blender_header(
            b"version https://git-lfs.github.com/spec/v1\n"))
    def test_reject_ascii_fbx_and_empty(self):
        self.assertFalse(is_blender_header(b"; FBX 7.4.0 project file"))
        self.assertFalse(is_blender_header(b""))
    def test_windows_fallback_reads_all_eight_magic_bytes(self):
        ps=pathlib.Path(__file__).with_name("run_pass04_windows.ps1").read_text(encoding="utf-8")
        self.assertIn("[Math]::Min(8,$BlendBytes.Length)",ps)
        self.assertNotIn("[Math]::Min(7,$BlendBytes.Length)",ps)
        self.assertIn("if ($BlendMagic -ne 'BLENDER-')",ps)
    def test_actual_runtime_source_uses_eight_byte_startswith(self):
        source=SCRIPT.read_text(encoding="utf-8")
        self.assertIn('blend_file.read_bytes().startswith(b"BLENDER-")',source)
        self.assertNotIn('blend_file.read_bytes()[:7] != b"BLENDER-"',source)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--real-blend",type=pathlib.Path)
    args=p.parse_args()
    if args.real_blend:
        header=args.real_blend.open("rb").read(12)
        if not is_blender_header(header):
            raise SystemExit("FAIL: supplied source is not a genuine BLENDER- header")
        print("REAL_NATIVE_BLEND_HEADER_OK",args.real_blend.name,
              "sha256",hashlib.sha256(args.real_blend.read_bytes()).hexdigest(),
              "header",header.hex(),flush=True)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BlenderHeaderRegression)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
