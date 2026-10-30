# C01-03 PASS09 — Lessons from B01 ENV01–ENV05 v002 (QA only)

**STRICT PROJECT ISOLATION:** No B01 files, model binaries, GLBs, licenses, permissions, Git refs or QA approvals are transferred into C01. Only quality-assurance methodology is shared.

| B01 asset | Existing Draft PR | Grounded Blender QA lesson | Not yet complete |
|---|---|---|---|
| ENV01 protective barrier | [#288](https://github.com/C8LyNn/RoboRougelike/pull/288) | True Blender geometry QA, scale and scene bounds, distinguish intentional contact from overlap, collider box is a proposal only | B01 independent G1 + Unity |
| ENV02 ramp v002 | [#290](https://github.com/C8LyNn/RoboRougelike/pull/290) | Real native BLEND reopen; GLB visual/collider proposal separate; correct ramp profile, UV and normal verification | B01 independent G1 + Unity |
| ENV03 wall v002 | [#291](https://github.com/C8LyNn/RoboRougelike/pull/291) | [Blender Actions PASS #40968934658](https://github.com/C8LyNn/RoboRougelike/actions/runs/40968934658), **10 real steps**; immutable before/after, tile end-profile consistency, deterministic GLB twice, previews do not change source | B01 G1 + Unity |
| ENV04 vent grate v002 | [#289](https://github.com/C8LyNn/RoboRougelike/pull/289) | [Blender Actions PASS #40969369152](https://github.com/C8LyNn/RoboRougelike/actions/runs/40969369152), **11 real steps**; avoid interpenetrating contacts and over-welding; independent geometry/UV hash rather than equating all render byte hashes | B01 G1 + Unity |
| ENV05 light bollard v002 | [#293](https://github.com/C8LyNn/RoboRougelike/pull/293) | Mechanical part seating, native Blender/GLB source & SHA evidence, actual emissive material settings vs artistic preview | B01 G1 + Unity |

### CI difference established, root cause not established

- B01 ENV03 #40968934658: SUCCESS, 10 executed job steps.
- B01 ENV04 #40969369152: SUCCESS, 11 executed job steps.
- C01 [#41108063941](https://github.com/C8LyNn/Model-Test/actions/runs/41108063941): FAILURE, zero steps.
- C01 [#41103820326](https://github.com/C8LyNn/Model-Test/actions/runs/41103820326): FAILURE, zero steps.
- B01 runner success does not prove C01 billing/permission/runner policy diagnosis. No spending, account settings or visibility changed.

### What C01 can reuse technically

1. Immutable source and binary hashes attached to exact producer commit, preserving all previous revisions.
2. Real Blender source reopen, triangulation/winding/non-manifold validation per mesh part with intentional openings and disconnected moving parts exempted where justified.
3. Before and after actual wireframe and material-shaded previews, not primitive reconstructions.
4. Exact source topology, UV0, normals, scale and pivots across export/import; distinguish true coplanar face overlap from valid geometry seams and triangle diagonals.
5. Separate producer (G0), independent binary QA (G1), Unity import/prefab (G2), HQ release. Green Python or B01 GLB CI does not satisfy C01 native binary FBX or Unity.

**Status:** five ENV v002 PRs inspected read-only; no B01 files in C01; no cross-project permission or merge operation.
