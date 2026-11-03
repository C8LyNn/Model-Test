# C01-02 — Interior Props Wave 01 retest / Wave 02 intake (2026-10-30)

**Repo:** `C8LyNn/Model-Test` · **QA branch:** `c01/props-02-independent-qa` · **PR:** #13 · **Issue:** #8  
**Verdict:** **0 ACCEPTED / 3 FAIL / 33 BLOCKED** across 36 target IDs (Wave01: 16, Wave02: 20).  
**IMPORTANT:** FAIL applies to repository ASCII FBX UV/normal streams (P18-01–03), not to the separate Blender binary FBX deliverables, which were not opened in this QA environment.

## Actual checks executed independently (source-level)

| IDs | Performed | Result | Limitations |
|---|---|---|---|
| P15-01–03 | Git tree, manifest and LFS pointer inventory | BLOCKED | .blend/FBX/PNG LFS pointers present; no committed final Unity prefabs; Blender/Unity import NOT RUN |
| P16-01–03 | Parsed 3 real OBJ: 60 triangles each, 0 invalid/degenerate triangles, 0 UV-less faces, 0 normal-less faces, consistent face-normal alignment; reviewed prefab YAML | BLOCKED (source OBJ check PASS) | No native .blend in producer branch; Unity import/render/clearance NOT RUN |
| P17-01 | Independently decoded source glTF buffer: 204 tris, 17 primitives, 0 UV-less primitives, 0 degenerates, 0 bad normals, 0 invalid indices | BLOCKED (source glTF check PASS) | LFS .blend/.fbx pointers not independently opened; actual prefabs not available |
| P17-02 | Same: 240 tris, 20 primitives, 0 UV-less, 0 degenerates/bad normals | BLOCKED (source glTF check PASS) | Same |
| P17-03 | Same: 208 tris, 12 primitives, 0 UV-less, 0 degenerates/bad normals | BLOCKED (source glTF check PASS) | Same; lever pivot/runtime NOT RUN |
| P18-01 | OBJ: 180 tris, UV and normals present, 0 degenerates. Repo ASCII FBX: no `LayerElementUV` or `LayerElementNormal` | **FAIL P1 (repo ASCII FBX)** | Blender binary FBX and Unity prefab fidelity NOT RUN |
| P18-02 | OBJ: 204 tris, UV and normals present, 0 degenerates. Repo ASCII FBX lacks both streams | **FAIL P1 (repo ASCII FBX)** | Same |
| P18-03 | OBJ: 348 tris, UV and normals present, 0 degenerates. Repo ASCII FBX lacks both streams | **FAIL P1 (repo ASCII FBX)** | Four wheel pivots/animations and Unity NOT RUN |
| P19-01–04 | Sampled one actual OBJ mesh per asset (Mattress, Door_Leaf, Desktop, Seat): 8 vertices/12 triangles per sample, 0 UV/normal records; reviewed 37-part source inventory | BLOCKED (P1 source follow-up) | Not all parts inspected; Blender sources, FBX and prefabs absent from this branch |

**Wave 02 P15-04–07 / P16-04–07 / P17-04–07 / P18-04–07 / P19-05–08:** no matching source .blend, .fbx or .prefab files in the five pinned supplier branch trees; all 20 **BLOCKED / geometry NOT RUN**. This does not prove creators are not working elsewhere.

## Important correction to previous QA

Prior QA reported missing UV0 for all P17 glTF primitives and missing UV/normal streams in P18 OBJ. **Those statements are no longer true for current supplier SHAs:** current P17 glTF contains UV0 in all 49 primitives; current P18 OBJ contains both streams in all 732 triangles. The separately committed P18 *ASCII FBX* still lacks serialized UV/normal layers, however. Do not apply outdated failures to corrected source files.

## Native/export evidence (not independent mesh QA)

Verified GitHub Actions run status=completed / conclusion=success:
- C01-15: [Blender exporter CI run 40969827124](https://github.com/C8LyNn/Model-Test/actions/runs/40969827124)
- C01-17: [Blender exporter CI run 40969058588](https://github.com/C8LyNn/Model-Test/actions/runs/40969058588)
- C01-18: [Blender exporter CI run 40970297098](https://github.com/C8LyNn/Model-Test/actions/runs/40970297098)

CI success is evidence of producers' pipeline execution, **not** evidence of independent physical verification of native FBX normals, UV, Unity importer, collider/clearance, or the final package. In Git tree, 130–131 byte blobs are Git LFS pointers; they are not real binary Blender/FBX/PNG bytes in this inspection.

## Reproducibility and artifacts

- `C01InteriorProps_QA/wave02_branch_snapshot.json` — actual Git-tree paths, sizes, blob hashes and pinned producer heads.
- `C01InteriorProps_QA/reports/WAVE02_STATIC_EVIDENCE.json` — per-source blob SHA and measured source metrics.
- `C01InteriorProps_QA/reports/WAVE02_STATUS.csv` — all 36 IDs with release-gate outcome.
- `C01InteriorProps_QA/qa_wave02.py` — fail-closed 36-ID inventory scanner, NOT a source of asset PASS.
- `C01InteriorProps_QA/tests/test_qa_wave02.py` — seven deterministic synthetic tests: **7/7 PASS locally**.
- `Assets/C01InteriorProps/QA/Editor/C01InteriorPropsQa.cs` — 36-ID Unity Editor inspector, updated but **NOT COMPILED / NOT RUN**.

## Defects and owner actions

**QA-P18-W01-FBX-UV-NORMAL (P1; C01-18):** re-export P18-01–03 ASCII FBX with explicit UV and normal layer arrays, OR replace these declared export files with validated binary Blender FBX and update manifests, avoiding ambiguous dual FBX. Repro: inspect `Assets/C01InteriorProps/C01-18/Models/P18-0{1,2,3}.fbx` for `LayerElementUV` and `LayerElementNormal`; both absent, while source OBJ has UV/normals. The binary FBX in Drive/Actions may already be correct but **has not been independently checked**. Keep FAIL on the repository export gate.
**QA-P19-W01-UV (P1; C01-19):** sampled source OBJ parts lack `vt`/`vn`; produce explicit UV0 and consistent normals in the finalized export or document verified importer-generated equivalents. Samples alone do not prove all submeshes are defective.
**QA-P15-W01-PREFAB (P0; C01-15):** generated Blender/FBX claimed with CI evidence, Unity prefabs not committed; build and verify real Unity YAML prefabs plus colliders.
**QA-P16-W01-BLEND (P0; C01-16):** native Blender sources absent from inspected branch; supply Blender-native and verified FBX roundtrip.
**QA-P17-W01-PREFAB (P0; C01-17):** native .blend/.fbx pointers present, final Unity prefabs absent; Unity build and lever test needed.
**QA-P19-W01-EXPORT (P0; C01-19):** Blender-native, FBX and final Unity prefab outputs missing.
**QA-W02-INVENTORY (P1; C01-15..19):** no Wave 02 asset outputs in inspected producer branch heads; run independent QA when PR artifacts exist.

## Release gate / handoff to C01-00 and C01-10

- Blender executable: **not available** in QA runtime. Native .blend opening: NOT RUN.
- Unity 6 URP executable: **not available** in QA runtime. Prefab import, rendering, materials, colliders, door/stair/lift/3 m corridor clearance, PlayMode and screenshots: **NOT RUN**.
- Ship geometry or producer branches: **not edited**. Only independent QA PR #13 updated.
- Required next step: owners update existing Wave01 PRs with real native sources, unambiguous exported FBX, built prefabs and evidence. C01-10 assembles separate showcase, then C01-02 independently inspects exact immutable versions and records engine-level results. **Do not merge / do not mark issue #8 complete.**
