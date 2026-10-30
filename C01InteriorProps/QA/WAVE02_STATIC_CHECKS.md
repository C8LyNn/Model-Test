# C01-10 — WAVE02 static integration tests (2026-10-30)

**Result: 26/26 STATIC SOURCE CHECKS PASS — 0 Unity/Blender tests run.**

These checks directly inspected GitHub branch files and compared the complete PR branch diff to `codex/c01-ship-integration`. They are contract/source inspections, **NOT Unity Editor compilation, physics, render validation, binary model import, or independent C01-02 QA**.

## Actual assertions performed
1. 16 unique Wave 01 slot IDs.
2. 20 unique Wave 02 slot IDs.
3. 36 ID parity with integration CSV.
4. 36 unique IDs.
5. C01-02 approved-assets ledger currently has header only.
6. No asset is misrecorded as APPROVED.
7. Only rows with exact APPROVED status are instantiated.
8. Zero approved models throws before generating any scene/prefab.
9. SHA-256 is read from actual FBX bytes.
10. Computed SHA must match QA-pinned approval.
11. Likely Git LFS pointer refused.
12. Prefab must contain a mesh referring to approved FBX.
13. Built-in primitive meshes rejected.
14. No generated geometry in accepted-only integrator.
15. No replacement colliders fabricated.
16. Source prefab must contain colliders.
17. Source prefab must contain a renderer.
18. Width/depth/height dimensional tolerance ±0.002m.
19. Pivot tolerance ±0.001m.
20. Root scale tolerance ±0.0001.
21. All five scene target names exist in code.
22. Master prefab target exists.
23. Empty family scenes are skipped.
24. Legacy non-QA-gated builder explicitly disabled.
25. Modified/added paths confined to C01InteriorProps namespace.
26. No ship or architecture files modified.

## Input state and blockers
- Latest independent C01-02 QA matrix: **0/16 APPROVED**, 2 representative source FAILs at previously observed SHAs (P17-01 UV0 and P18-01 FBX UV/normals; current producer heads require retesting), 14 BLOCKED.
- Producer WAVE01 PRs: #16/#12/#17/#18/#15 exist; source artifacts in producers/CI are not the same as QA approval.
- New WAVE02 IDs: P15-04..07, P16-04..07, P17-04..07, P18-04..07, P19-05..08; **not integrated**.
- No native Blender or Unity Editor executable in C01-10 runtime.
- Generated .prefab/.unity, in-engine screenshots, player capsule and corridor clearance are **NOT RUN / NOT CREATED**.
- C01-02 must perform actual editor and model checks and provide SHA-specific acceptance; no merging or release at this gate.

**Status: TOOLING STATIC PASS / SHOWCASE BUILD BLOCKED / UNITY NOT RUN / QA NOT APPROVED.**
