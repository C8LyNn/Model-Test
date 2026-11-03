# C01-14 — MESH REPAIR PASS 04 / exact source & cross-part QA

**Date:** 2026-10-30. **Scope:** RMP-01 and RAI-01 only, outside the 36 P15–P19 interior models in #33/#30. No ship-scene or mesh changes. Existing draft PR #24 remains unmerged.

## Baseline: real Blender PASS 03
Native v002 BLEND/FBX are committed to `Assets/C01StructuralPrototypes/P14/Pass03`; Blender 4.0.2 run [41089475908](https://github.com/C8LyNn/Model-Test/actions/runs/41089475908) **SUCCESS**, with true native source opening, binary FBX export, and real FBX import. Report `Pass03/REPORT.md` and QA JSON are authoritative for V/E/F/triangle counts. No topology defect was demonstrated in those two real native meshes, so the shapes were not changed.

| ID | Vertices before/after | Edges | Faces | Triangles | Internal defects before/after | SOURCE repair |
|---|---:|---:|---:|---:|---:|---|
| RMP-01 | 48→48 | 108→108 | 72→72 | 72→72 | 0→0 | not required |
| RAI-01 | 32→32 | 72→72 | 48→48 | 48→48 | 0→0 | not required |

RMP-01 has 60 visual triangles plus 12 triangles of a separate **intentionally duplicated, non-rendered collider proxy** `COL_RampDeck`. Do not count as visual z-fighting.

## PASS 04 additional independent static check
I loaded the actual v001 production GLB exported from the same original mesh family (not the earlier reconstructed 3D gallery), and evaluated each distinct visible convex component with `trimesh` + SciPy `ConvexHull` / `HalfspaceIntersection`. This is an **independent static cross-part volumetric analysis of GLB**, not another native Blender/FBX roundtrip. The original v001 geometry is verified unchanged by the Pass03 Blender FBX triangulated-surface comparison.

- RMP-01: 5 visible parts, 10 distinct visible-part pairs, **0 unexpected positive-volume intersections**. All four antislip strips are disjoint from the ramp deck and each other.
- RAI-01: 4 visible parts, 6 distinct pairs, 4 **INTENTIONAL** post/rail join volumes (each middle rail/post ≈0.000336 m³, each top rail/post ≈0.000192 m³), **0 unexpected** positive-volume intersections.
- A convex-hull calculation on separate parts does not establish absence of tangential coplanar triangles or face-level z-fighting at coincident boundaries. That limitation is explicit. The collider proxy is absent from v001 GLB and already separately evaluated in PASS03 Blender.
- GLB GPU stream vertex splits are **not** evidence of unwelded Blender topology.
- Exact SHA-256 of both PASS03 native v002 BLEND and binary FBX bytes were independently recalculated against the pass03 CI ZIP and matched:

| File | SHA-256 |
|---|---|
| RMP-01 v002 BLEND | `7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa` |
| RMP-01 v002 FBX | `97f0b125313057f4ecf601dd60a02b4d3f0d55b87c1713d71a0adbedcc6d1443` |
| RAI-01 v002 BLEND | `8a2f16205874f8485adb87c5251f6adbba3f51816936c0bf1964ad40a47850a5` |
| RAI-01 v002 FBX | `b51c3c012f5680de2d02c2deaf5c67c4ae9a12bb7e8347f179ed08d181a7e103` |

Offline PASS04 cross-part JSON and reproducer are supplied in the C01-14 conversation artifact. Native v002 BLEND, FBX and BEFORE/AFTER wire/shaded views were already committed in the **same PR**.

## Extra native audit CI attempted, not passed
`Tools/C01Structures14/verify_pass04_exact_sources.py` and workflow `.github/workflows/c01-14-mesh-repair-pass04.yml` were added to the existing branch. [Run 41094351876](https://github.com/C8LyNn/Model-Test/actions/runs/41094351876) concluded **FAILURE before any steps began** (runner job has no step records); rerun also concluded FAILURE before steps. Hence additional Blender v002 BVH/winding/material-source-to-FBX checks are explicitly **NOT RUN**, not PASS. The successful PASS03 Blender roundtrip remains valid.

## Gate
- Source topology (scope of PASS03): **PASS producer evidence, pending independent C01-02**.
- Extra static visible-part intersections PASS04: **PASS** with explicit intentional connections.
- PASS04 new Blender CI: **NOT RUN (runner/early-job failure)**.
- Actual Unity 6 URP import/renderer/colliders/play-mode clearance: **NOT RUN**.
- C01-02 independent technical QA / C01-00 structural acceptance: **BLOCKED**.
- **No merge. No new 3D models. No redesign.** Do not count these two prototypes among the 36 assets being repaired by C01-15–19.

Next action: C01-02 checks exact v002 native binary files and intentional post/rail contacts, C01-10 tests Unity only after scope approval. Dedicated P19-05/07/08 fixes remain C01-19 responsibility.
