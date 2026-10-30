"""PASS06: regression of the ACTUAL C01-16 production Blender signature checks.

No bpy dependency. The 12-byte BLENDER-v400 sample is the authentic
Blender 4.0 file-HEADER format, not a complete .blend project.
"""
import ast
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
PY_EXPORTER = HERE.parent / "MeshRepairPASS04" / "ci_pass04_native.py"
PS_EXPORTER = HERE.parent / "MeshRepairPASS04" / "run_pass04_windows.ps1"

def production_rejects(path):
    """Execute only the signature-related Python AST expression from production."""
    source = PY_EXPORTER.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(PY_EXPORTER))
    matches = [
        node.test for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and "BLENDER-" in ast.unparse(node.test)
        and "blend_file" in ast.unparse(node.test)
    ]
    if len(matches) != 1:
        raise AssertionError("Expected exactly one active Blender file signature gate")
    code = compile(ast.Expression(matches[0]), str(PY_EXPORTER), "eval")
    return bool(eval(code, {"blend_file": path}))

class NativeSignatureRegression(unittest.TestCase):
    def test_canonical_blender40_header(self):
        self.check(b"BLENDER-v400", expected_rejection=False)

    def test_valid_header_with_payload(self):
        self.check(b"BLENDER-v400" + b"\x00" * 32, expected_rejection=False)

    def test_old_seven_byte_bug_reproduced(self):
        header = b"BLENDER-v400"
        self.assertNotEqual(header[:7], b"BLENDER-")  # old erroneous comparison
        self.assertTrue(header.startswith(b"BLENDER-"))
        self.check(header, expected_rejection=False)

    def test_invalid_magic(self):
        self.check(b"NOTBLEND-v400", expected_rejection=True)

    def test_truncated_seven_byte_prefix(self):
        self.check(b"BLENDER", expected_rejection=True)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(production_rejects(pathlib.Path(d) / "missing.blend"))

    def test_powershell_reads_complete_eight_byte_magic(self):
        ps = PS_EXPORTER.read_text(encoding="utf-8")
        self.assertIn("Min(8,$BlendBytes.Length)", ps)
        self.assertIn("if ($BlendMagic -ne 'BLENDER-')", ps)
        self.assertNotIn("Min(7,$BlendBytes.Length)", ps)

    def check(self, raw, expected_rejection):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "fixture.blend"
            p.write_bytes(raw)
            self.assertIs(production_rejects(p), expected_rejection)

if __name__ == "__main__":
    unittest.main(verbosity=2)
