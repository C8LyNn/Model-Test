# C01-18 PASS04 — final producer crosscheck, 2026-10-30

**Scope:** Seven original C01-18 meshes, P18-01…P18-07. Existing Draft PR #18 (Wave01), #26 (Wave02). Parent #30, wave #33. No new models, geometry reconstruction, redesign, or ship changes.

## Actual binary FBX v7400 validation
A standalone Python binary FBX parser directly inspected the hydrated *actual* FBX geometry and polygon index arrays from the post-PASS03 archive (not OBJ, GLB, mock or gallery). Compared each file SHA256 to its **current PR Git LFS pointer** — 7/7 exact matches. All 89 mesh parts PASS on indexed face topology, direct face winding, 0 missing/non-finite UV0 or normals, 0 invalid indices, 0 duplicates, 0 boundary/nonmanifold edge-use defects, 0 zero-area triangulation, 0 concave complex n-gons, and 0 non-unit normals.

Normal-vs-face orientation: **3516 actual FBX polygon corners inspected**, 0 opposite/wrong-facing normals.

P18-04 contains ten regular convex cap n-gons with no degenerate fan triangulation. This is **not** the P19-05/07/08 complex concave-n-gon issue.

Source .blend and binary FBX SHA256, V/E/F/Tris pre/post, n-gon counts and all model-specific results are in `QA/Pass04/binary_fbx_index_audit.json` of both producer branches.

### Actual FBX moving hierarchy, from `Objects/Model` and `Connections`
- P18-03: four distinct wheel mesh model nodes `Wheel_LB`, `Wheel_LF`, `Wheel_RB`, `Wheel_RF`.
- P18-05: `Case_Lid` and `Lid_Accent` parented under `Lid_HingePivot`, parented under `P18-05_Root`.
- P18-07: `Bin_Lid` and `Lid_Label` parented under `Toolbox_LidHinge`, parented under `P18-07_Root`.

## Source repairs inherited from PASS03
- P18-02: 6 shelf lip contacts locally shifted; cross-part coplanar candidates 50→18.
- P18-05: 1 local face-plane correction; coplanar candidates 6→4.
- P18-06: 1 local correction; coplanar candidates 6→6.
- P18-07: 3 local corrections; coplanar candidates 7→5.
- P18-01: 12→12 assembly contact candidates; P18-03 0→0; P18-04 2→2.

These **candidates are not automatically topology defects**. Contact-face overlap must be checked visually on exact source surfaces, especially where hardware, lids and corner trim meet. Do not weld separate moving parts. No further topology edit was justified by the direct FBX binary audit.

## Execution / blockers
- Historical real Blender 4.0.2 FBX source roundtrips **PASS**: [W01](https://github.com/C8LyNn/Model-Test/actions/runs/41090212132), [W02](https://github.com/C8LyNn/Model-Test/actions/runs/41089810123).
- New PASS04 Blender source-vs-FBX CI workflow files committed in each producer PR, but GitHub-hosted job execution **FAILED BEFORE STARTING STEPS** (no job logs) even on rerun: [W01](https://github.com/C8LyNn/Model-Test/actions/runs/41094151991), [W02](https://github.com/C8LyNn/Model-Test/actions/runs/41094163356). **BLENDER PASS04: NOT RUN.**
- Unity 6 URP geometry import, real FBX-linked saved Unity prefabs, collider/interaction/clearance **NOT RUN**.
- Independent C01-02 SHA-pinned audit **PENDING**: 0 claims of full QA approval. PR #18 and #26 remain Draft/unmerged.
- The direct binary parser checked indexed FBX geometry; it is *not* a replacement for Blender import and independent Unity results.

**Next explicit action for C01-02:** consume exact FBX SHA256 in the JSON, run independent final-binary topology and UV/normals checks. **C01-10:** import verified binaries into actual Unity 6 URP and save editor-produced .prefab; test original ship clearance in staging only.
