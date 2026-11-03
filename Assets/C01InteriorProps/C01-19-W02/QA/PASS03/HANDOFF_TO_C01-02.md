# C01-19 PASS03 Wave02: technical mesh before/after handoff
Producer PR: https://github.com/C8LyNn/Model-Test/pull/29
Blender 4.0.2 actual execution SUCCESS: https://github.com/C8LyNn/Model-Test/actions/runs/41088782744
Original .blend and FBX sources used; NOT an approximate mesh gallery.
Static same-material solids only joined when their AABBs overlap with positive volume; retain separate moving hierarchy/material boundaries; reviewer must check union appropriateness.

| ID | V before/after | E before/after | F before/after | T before/after | Unions | Degenerate before/after | Zero edges before/after | FBX reimport |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| P19-07 | 104/136 | 156/204 | 78/78 | 156/252 | 7 | 0/0 | 0/0 | PASS |
| P19-08 | 96/149 | 144/241 | 72/100 | 144/282 | 6 | 0/0 | 0/0 | PASS |
| P19-05 | 88/88 | 132/140 | 66/66 | 132/148 | 4 | 0/0 | 0/0 | PASS |
| P19-06 | 56/56 | 84/84 | 42/42 | 84/84 | 0 | 0/0 | 0/0 | PASS |

Per model true Blender evidence: QA/PASS03/<ID>/mesh_topology_before.json and mesh_topology_after.json; wireframe_before.png, wireframe_after.png, shaded_after.png, closeup_actual_mesh.png.
Blob SHA256 source-before / source-after and FBX-after in QA/PASS03/SUMMARY.json.
Producer static mesh topology checks: no new degenerate/zero/boundary/non-manifold edges in each tested mesh, postrepair; FBX roundtrip and UV0 4/4 PASS.
External appearance shape preserved by source bounds test; cross-material overlaps are manually reviewed exemptions, not automatically welded.
Full true T-junction topology across different objects and visual consistency QA: NOT RUN; independent review required.
Unity 6 URP import, saved prefabs, interactive hinge/clearance tests: NOT RUN.
Independent C01-02 acceptance: BLOCKED. Do not merge.
Next: C01-02 independently review native before/after and Unity importer at exact SHA; C01-10 integrate only approved props.
