# C01-17 — Blender/FBX Production Evidence

Task: https://github.com/C8LyNn/Model-Test/issues/5
PR: https://github.com/C8LyNn/Model-Test/pull/17
CI successful run: https://github.com/C8LyNn/Model-Test/actions/runs/40969058588
Artifact: C01-17-Real-Models-Blender-FBX-PNG; artifact id 12940310298; archive 4,538,623 bytes.
Generated binaries committed with Git LFS at 98b08fc3fe2c18785a06ad525b9161e975807656.

## Measured in actual Blender 4.0.2

| ID | Mesh objects | W x D x H (m) | Native BLEND | Binary FBX | PNG views | Status |
|---|---:|---|---|---|---|---|
| P17-01 | 17 | 1.6000 x 0.6500 x 1.1000 | PASS | PASS | 3 | PASS |
| P17-02 | 20 | 0.1800 x 0.0700 x 0.2800 | PASS | PASS | 3 | PASS |
| P17-03 | 12 | 0.4000 x 0.3000 x 0.5500 | PASS | PASS | 3 | PASS |

Static glTF QA: 652 triangles total, 0 degenerate, 0 inverted, dimensions PASS.
Downloaded ZIP inspected independently: all 15 files present, ZIP CRC PASS.
Native BLEND headers: BLENDER-v400. FBX headers: Kaydara FBX Binary.
GitHub Contents endpoint shows LFS pointers, not file payloads. Use Git LFS or Actions artifact.
Images are actual Blender Workbench renders, NOT Unity screenshots.

## Remaining blockers
- Unity 6 URP import and visual test: NOT RUN.
- Actual native Unity prefab creation: MISSING / NOT RUN. Run C01ControlsPrefabBuilder.Build in Unity.
- Lever movement in Unity, collisions and clearance: NOT RUN.
- Independent acceptance C01-02: PENDING.
- C01-10 integration and Showcase: PENDING.
- C01-01 pivot/mount specification approval: PENDING.

Overall: real geometry + Blender + FBX PASS; Unity integration remains BLOCKED.
No changes to ship architecture or layout. PR must remain draft.