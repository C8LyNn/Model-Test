# C01-03 — TECHNICAL MESH INTEGRITY / PASS 03

**Main task:** https://github.com/C8LyNn/Model-Test/issues/30  
**Scope:** 36 model IDs / 16 Wave01 + 20 Wave02  
**Owner:** C01-03 — VERSIONING, SHA-256 and BEFORE/AFTER evidence integrity; **not mesh producer**.

## Actual deliveries

- `repair_ledger.json`: exactly 36 canonical IDs, six P0, ten immutable producer Git commit references and known original source/FBX paths.
- `validate_pass03.py`: validates identities, prevents premature APPROVED, refuses LFS pointers and untrusted file paths, checks actual Blender/FBX byte headers and SHA256; verifies checked-out Git HEAD equals pinned producer commit.
- `tests/test_pass03.py`: executable static registry tests; not an actual topology/Unity test.
- `.github/workflows/c01-pass03-snapshot.yml`: 10 pinned producer SHA checkouts with Git LFS; saves BEFORE byte receipts as run artifacts. Success of a checkout or SHA check never equals geometry PASS.
- This folder does **not** contain repaired mesh bytes or substitute geometry. AFTER revisions and QA evidence remain null/NOT_RUN.

## Six original P0 assets

| Asset | Owner PR | Original source (.blend) | Original FBX |
|---|---|---|---|
| P17-04 | #23 | `C01InteriorProps_W02/Blender/P17-04.blend` | `Assets/C01InteriorProps/W02/Models/P17-04.fbx` |
| P17-05 | #23 | `C01InteriorProps_W02/Blender/P17-05.blend` | `Assets/C01InteriorProps/W02/Models/P17-05.fbx` |
| P18-04 | #26 | `Assets/C01InteriorProps/C01-18-Wave02/Sources/P18-04.blend` | `Assets/C01InteriorProps/C01-18-Wave02/Models/P18-04.fbx` |
| P18-05 | #26 | `Assets/C01InteriorProps/C01-18-Wave02/Sources/P18-05.blend` | `Assets/C01InteriorProps/C01-18-Wave02/Models/P18-05.fbx` |
| P19-07 | #29 | `Assets/C01InteriorProps/C01-19-W02/Models/P19-07/P19-07.blend` | `Assets/C01InteriorProps/C01-19-W02/Models/P19-07/P19-07.fbx` |
| P19-08 | #29 | `Assets/C01InteriorProps/C01-19-W02/Models/P19-08/P19-08.blend` | `Assets/C01InteriorProps/C01-19-W02/Models/P19-08/P19-08.fbx` |

These paths were identified in the changed-file lists. **The old interactive gallery showed parametric reconstructions; no mesh defect can be inferred from them without reviewing actual source.**

## Required evidence per model before releasing

**BEFORE:** native .blend and binary FBX SHA-256; per-mesh Blender API counts for vertices/edges/faces/tris, connected components, loose or duplicated geometry, nonmanifold and boundary edges, T-junctions, overlaps and winding; real wireframe.

**AFTER:** new repair version with immutable Git commit and SHA-256 (do not overwrite BEFORE), matching real wireframe/shaded and defect detail PNG; same real-world scale, silhouette, pivots, materials and intentionally separated moving parts. Open surfaces and UV/sharp seam splits must be documented intentional exceptions, not blanket FAIL.

**Actual application tests:** Blender open, Blender FBX export + import (verify UV0, normals, materials and geometry) and Unity 6 URP if available. Separate PASS/FAIL/NOT_RUN for each, no claimed PASS without execution and exact byte evidence.

**QA release gate:** C01-02 signs the exact AFTER FBX SHA256 after reviewing topology and original files. C01-10 shows actual meshes in viewer (not reconstructed primitives). C01-00 authorizes release. Metadata tooling never supplies these approvals.

## Commands

```bash
python C01InteriorProps_Library/Pass03/validate_pass03.py validate
python -m unittest discover -s C01InteriorProps_Library/Pass03/tests -v
python C01InteriorProps_Library/Pass03/validate_pass03.py capture --asset P17-04 --checkout /path/to/pinned-producer-worktree --output reports/P17-04-before.json
```

`capture` requires the exact commit HEAD and actual checked-out Git LFS files. If original path is not yet determined in the producer PR, it returns a blocked receipt rather than fabricating a file or signature. Existing C01-03 Wave01 SHA receipts from earlier commits must **not** be attached as current revision hashes.

**Status:** Library snapshot and CI tools developed; independent topology repairs 0 confirmed; Blender/Unity NOT_RUN by C01-03; release BLOCKED. No ship geometry modified. No unauthorized merge.
