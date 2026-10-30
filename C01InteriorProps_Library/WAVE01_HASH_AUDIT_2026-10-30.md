# C01-03 — WAVE01 Supplier SHA-256 Audit (2026-10-30)

**GitHub Actions evidence:** https://github.com/C8LyNn/Model-Test/actions/runs/41071526841

Five jobs checked out immutable producer commit SHAs using Git LFS. All 115 candidate file paths were read successfully; format signatures and SHA-256 were checked and recorded in catalog.json. Those are file-byte provenance checks, **not** Blender, Unity, or independent geometry QA. No producer files were merged into this library branch.

| Asset | Producer PR | .blend | FBX | prefab | preview | QA C01-02 | Full set |
|---|---|---:|---:|---:|---:|---|---|
| P15-01 | [#16](https://github.com/C8LyNn/Model-Test/pull/16) | 1 | 1 | 0 | 3 | BLOCKED | INCOMPLETE |
| P15-02 | [#16](https://github.com/C8LyNn/Model-Test/pull/16) | 1 | 1 | 0 | 3 | BLOCKED | INCOMPLETE |
| P15-03 | [#16](https://github.com/C8LyNn/Model-Test/pull/16) | 1 | 3 | 0 | 3 | BLOCKED | INCOMPLETE |
| P16-01 | [#12](https://github.com/C8LyNn/Model-Test/pull/12) | 0 | 1 | 1 | 0 | BLOCKED | INCOMPLETE |
| P16-02 | [#12](https://github.com/C8LyNn/Model-Test/pull/12) | 0 | 1 | 1 | 0 | BLOCKED | INCOMPLETE |
| P16-03 | [#12](https://github.com/C8LyNn/Model-Test/pull/12) | 0 | 1 | 3 | 0 | BLOCKED | INCOMPLETE |
| P17-01 | [#17](https://github.com/C8LyNn/Model-Test/pull/17) | 1 | 1 | 0 | 4 | FAIL | INCOMPLETE |
| P17-02 | [#17](https://github.com/C8LyNn/Model-Test/pull/17) | 1 | 1 | 0 | 4 | BLOCKED | INCOMPLETE |
| P17-03 | [#17](https://github.com/C8LyNn/Model-Test/pull/17) | 1 | 1 | 0 | 4 | BLOCKED | INCOMPLETE |
| P18-01 | [#18](https://github.com/C8LyNn/Model-Test/pull/18) | 0 | 1 | 1 | 0 | FAIL | INCOMPLETE |
| P18-02 | [#18](https://github.com/C8LyNn/Model-Test/pull/18) | 0 | 1 | 1 | 0 | BLOCKED | INCOMPLETE |
| P18-03 | [#18](https://github.com/C8LyNn/Model-Test/pull/18) | 0 | 1 | 1 | 0 | BLOCKED | INCOMPLETE |
| P19-01 | [#15](https://github.com/C8LyNn/Model-Test/pull/15) | 0 | 0 | 0 | 3 | BLOCKED | INCOMPLETE |
| P19-02 | [#15](https://github.com/C8LyNn/Model-Test/pull/15) | 0 | 0 | 0 | 3 | BLOCKED | INCOMPLETE |
| P19-03 | [#15](https://github.com/C8LyNn/Model-Test/pull/15) | 0 | 0 | 0 | 3 | BLOCKED | INCOMPLETE |
| P19-04 | [#15](https://github.com/C8LyNn/Model-Test/pull/15) | 0 | 0 | 0 | 3 | BLOCKED | INCOMPLETE |

**Totals:** 16 assets, 115 signed candidate file references, 0 complete file sets, 0 APPROVED.

**Observed gaps:** P15 no checked-in Unity prefabs; P16 native Blender and preview files missing; P17 saved Unity prefabs missing; P18 native Blender/PNG previews not in producer PR branch (some external CI archives may exist); P19 FBX/Blend/prefab missing (OBJ and SVG prototypes are present). Several variants and submeshes increase total file count above asset count.

**QA findings:** independent QA PR #13 reports P17-01 UV0 FAIL and P18-01 FBX UV/normal layer FAIL at earlier sampled revisions; current candidate hashes still require per-hash retest. Remaining 14 assets BLOCKED; no independent approval. QA matrix: https://github.com/C8LyNn/Model-Test/pull/13

**Required:** producer repair and updated pinned SHA -> repeat byte audit -> independent Blender/Unity inspection with FBX SHA -> C01-10 test scene and clearance -> C01-00 approval. Blender, Unity rendering, material/pivot and clearance tests were NOT RUN by C01-03.

**Status:** Byte-level registry PASS / finished interior model package BLOCKED.
