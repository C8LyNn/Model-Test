# C01-11 / MESH REPAIR PASS 04 — source truth handoff

**Scope:** architectural W01–W04, outside the 36 P15-01…P19-08 props in #33. The three P19 P1 failures belong to C01-19 / PR #29. **No other producer asset or ship geometry was modified.**

## Repeatable original binary FBX topology audit — independent local rerun

The October 28 detailed r2 FBX exports were **decoded directly**, and their exact vertex/triangle arrays matched against the archived authored `mesh_data.json`. This is not a parametric visualization or simplified replacement. A repeat execution of `audit_original_fbx.py` on PASS04 produced:

| ID | Original FBX SHA-256 | Vertices B→A | Edges B→A | Faces B→A | Triangles B→A | Detected errors B→A | Action |
|---|---|---|---|---|---|---|---|
| W01 | `7cc73ea116aa82cab5aa4833db2e6d3ce58888b47907402169d13ac2d7a7ff10` | 8→8 | 18→18 | 12→12 | 12→12 | 0→0 | no edit |
| W02 detailed r2 | `3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037` | 288→288 | 858→858 | 572→572 | 572→572 | 0→0 | no edit |
| W03 | `3f6d37472239fe2ab61be27eaafb928ee9cf0253c9783d465d81ec649a9b2ee2` | 12→12 | 30→30 | 20→20 | 20→20 | 0→0 | no edit |
| W04 | `c492539f3d33f65c90e0a0ac5279a6feded45d7cb14c3fefc147358dc9d7ecfe` | 16→16 | 42→42 | 28→28 | 28→28 | 0→0 | no edit |

Metrics: no unintended loose/coincident vertices, zero-length edges, boundary/non-manifold edges, incompatible edge winding, degenerate/duplicate triangles, T-junction candidates, coplanar overlaps or strict-interior noncoplanar intersections at documented numeric tolerances. UV0 and FBX normals were present. **This is static geometry QA, not an independent C01-02 approval.** No blanket weld or retopology is justified without a reproducible defect. The source is retained byte-for-byte, so BEFORE and AFTER mesh identities and counts deliberately match.

## Important correctness barrier

**Do not use candidate W02 from PR #22 as W02 r2 production source**: candidate has 12 triangles; authentic detailed r2 has 572. PR #22 only contains provisional greybox architecture assets, not approved replacements for the ship. The Unity Editor preflight now refuses to create ANY prefabs when the W02 imported triangle count differs from 572; it checks all four counts **before any .mat/.prefab writes**. This guard is SOURCE CODE ONLY; execution in Unity 6 URP has not occurred.

## CI and source provenance

- [CI run 41072466328](https://github.com/C8LyNn/Model-Test/actions/runs/41072466328) succeeded in generating actual Blender .blend / FBX / previews for PR22 candidate models. Do not infer that the detailed r2 W02 was validated by it.
- [CI run 41088902223](https://github.com/C8LyNn/Model-Test/actions/runs/41088902223) passed real Blender source audit and FBX import for PR22 candidates, but whole workflow FAILED on non-fast-forward push. Later attempts failed at push/rebase or runner setup; no final green PASS04 CI claimed.
- PASS04 workflow was changed to **read-only**: it no longer regenerates/commits meshes or uses git push, to prevent accidental source substitution or Git LFS conflicts. Latest read-only CI result must be inspected and not assumed PASS.
- Original detailed r2 native `.blend` source: **MISSING**. Original r2 Blender export/reimport: **NOT RUN**. Unity 6 URP import, real D01 frame fit and corridor clearance: **NOT RUN**. C01-02 independent topology acceptance: **PENDING**.

## Disposition

**W01–W04 original binary FBX local topology STATIC PASS UNCHANGED / 0 repairs. Full technical acceptance BLOCKED.** Keep PR22 DRAFT and do not merge. W01–W04 are not part of the 36-model acceptance numerator. Priorities from issue #33 (P19 fixes, P16 native exports, then 36 SHA-pinned independent checks) remain with their designated owners.
