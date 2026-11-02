# C01-02 — DETAIL PASS 19 / physical independent FBX QA

**Date:** 2026-11-02 · **Own branch / Draft PR:** `c01/props-02-independent-qa` / [#13](https://github.com/C8LyNn/Model-Test/pull/13) · **HQ dispatch:** [#6589035504](https://github.com/C8LyNn/Model-Test/issues/36#issuecomment-6589035504)

**Verdict:** **21 real Blender4 .blend + binary FBX pairs independently hydrated, SHA-256 compared and parsed; 21/21 index/topology/UV0/normal core checks PASS; targeted mechanical defects HOLD; Unity NOT RUN; 0/36 FINAL RELEASE APPROVED.** See [36-row exact-SHA QA matrix](INDEPENDENT_NATIVE_36_MATRIX.csv). No producer edits, no native reexports, no merges.

## Real binary provenance, no Git LFS pointer confusion

Downloaded *original GitHub Actions artifact ZIPs* (not source proxies) with official authenticated GitHub connector. Reopened and CRC tested all ZIPs, SHA256 hashed both actual `BLENDER-v400` source and `Kaydara FBX Binary` contents, then parsed actual FBX binary node properties (FBX 7400, array decompression, PolygonVertexIndex end-of-face decoding, indexed LayerElementUV and LayerElementNormal). All **42 native physical binaries** SHA256 match the exact corresponding PASS18 C01-10 matrix LFS OIDs.

| Original artifact | Actual models | Full ZIP SHA256 independently measured |
|---|---|---|
| [#13099778112](https://github.com/C8LyNn/Model-Test/actions/runs/41348140241) | P16-01..03 | `59a216c1cfb25b959510d8348ec6cd90544b29bd2f58388022f785bd42465205` |
| [#13100396298](https://github.com/C8LyNn/Model-Test/actions/runs/41348144803) | P16-04..07 | `c8b8754b40842baf81b174a6296b17de8bab29acc3190ddf3acf37d17d31a09a` |
| [#13099877855](https://github.com/C8LyNn/Model-Test/actions/runs/41347796593) | P17-01..03 | `2ddab5c829475d29a8e22cdde37861de43e4e2eaf9f67f2dc46c25f86afccd51` |
| [#13099325067](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313) | P18-01..03 | `24ecf87d774e9ff3de87f22f34a59564a4668f926c7813b9f3ae2ea0b35683b0` |
| [#13099591414](https://github.com/C8LyNn/Model-Test/actions/runs/41346465283) | P19-01..04 | `eaa2b68dbdfb635ebad2184e41fb46941f585a3bf9f14e2fa98487da39455fe9` |
| [#13099890315](https://github.com/C8LyNn/Model-Test/actions/runs/41346471952) | P19-05..08 | `1dea85635e67b95038225abdb02fa91ca88837ad60c24c1db1bf6006b9005b88` |

**Measured 21 FBX:** 386 unique Geometry meshes, **8,712 triangles** after triangulating indexed polygons, 5,168 control points. All 386 geometry nodes have UV0 and normal layers with finite values, valid mapping/reference index bounds, normal vectors within 1e-3 of unit length. **Zero** invalid geometry indices, zero exact zero-area faces, zero index-boundary/nonmanifold/winding errors, **two positive-area sub-1e-10 m² near-degenerate triangles (P19-01 only)**. No claim of global inter-object BVH, full self-intersection, visual pixel-perfect inspection or Unity-level acceptance. Instanced P17 meshes have fewer unique binary Geometry triangle primitives than authored OBJ instance counts; do not flag as export loss solely on primitive counts (P17-02 21 unique meshes/272T, 38 authored instances/536T).

## Exact individual QA decisions for the first integration vertical slice

| ID | Full original binary FBX SHA-256 | Verified source QA | Independent decision |
|---|---|---|---|
| **P16-01** | `c0a782a17a0047e0d578a41e42ac714c0fa0f86c7c4960f4bc10e21a24a278fd` | 12 meshes / 220 T; native closed indexed geometry, UV0/normals valid | **STATIC_PASS**. URP and lighting materials `UNITY_NOT_RUN` |
| **P17-02** | `db49121a520f16ca636626795550b83e8a4df94ded56a7ccb76308520bb7c3f6` | 21 unique meshes / 272 T; valid native indices/UV0/normals; instanced detail hierarchy exists | **STATIC_PASS**. Actual prefab/collider `UNITY_NOT_RUN` |
| **P18-01** | `f541d502ba9eaaf5c7a0a7279c44f71f36dd482e3aed3ba0734058dcf1045f6c` | 47 meshes / 980 T, no static topology errors | **STATIC_PASS**, lid/hinge motion `NOT_RUN`, Unity `NOT_RUN` |

These three can be **SHA-gated QA-quarantine imported by C01-10**, not released without real Unity Editor proof.

## Physical motion / geometry review, exact latest FBX

**P17-03 / `a48c9dde921c25f61cef175896c5b7fde997392fc898784e16bb9612f39a4520` — ASSEMBLY FAIL, owner C01-17, P0.** Binary closed meshes and UV0/normal index tests PASS (13 unique Geometry meshes, 240T). However **TopCap is a closed 8-vertex, 12-triangle solid box with no central hole**, and LeverSocket also a closed 12-triangle cuboid. Actual FBX model transforms and complete parent chain, including the 100x FBX unit conversion and X-axis root rotation, were used for diagnostic pivot samples **0,5,10,...45°**. At *every sampled angle*, **12 LeverShaft mesh vertices lie strictly inside TopCap**. LeverSocket encloses 3–5 LeverShaft vertices at samples 15–45°. This establishes current solid-solid penetration, including at rest, independent of Unity physics. **Do not rotate/move functional LeverPivot to mask error.** C01-17 to cut/reshape real solids, preserve mechanical hierarchy, publish new Blender4 save+FBX+SHA; C01-02 retest exact new bytes. Full continuous triangle swept volume/Unity PhysX **NOT_RUN**; the sampled penetration already blocks release.

**P18-03 / `f169ab74086ee3853c14b46ac6f6199cd255cfca15d8b7cbef32c3758cde7926` — STATIC WHEELS PASS, DYNAMIC HOLD; owner C01-18.** Actual binary 63 Geometry meshes/1780T, source dimensions preserved. FBX parent hierarchy: four `Wheel_LB/LF/RB/RF` each has its own `Hub_In/Hub_Out` mesh children. World-transformed four wheel mesh minima relative to floor Y=0 are within **±1.6e-8 m**, consistent four-wheel ground contact. Each rubber wheel AABB stands ~**0.0020000 m** away from corresponding upright in vertical separation at rest. This is only an exact resting-geometry check, NOT wheel rolling/steering or PhysX swept collision. No new export justified from this result alone.

**P19-01 / `e2e0bb9e095c1daed87e407814e88f8788cf503ab705d3e34513879038bcd559` — HOLD MICROSLIVER, owner C01-19.** Current physical FBX contains two near-collinear but **positive** triangles in `Cube.001` (faces corresponding to indices `[3,106,107]` and `[88,87,13]`), actual areas **6.9917405e-12 m²** and **2.4334534e-11 m²**, minimum geometric triangle altitudes **2.518e-9 m** and **7.456e-10 m**. These are precision-collapse slivers, *not exactly zero-area* polygons and not evidence of a broken manifold. Target only their local original surfaces if producer confirms relevance; do not blindly weld all co-located meshes. Physical Blender/Unity screenshot comparison of their visibility NOT RUN.

**P19-07 / `eb579a85355756c0d803f58ec96fac509e33788d8142390349aebbffdba50e81` — HOLD T-JUNCTION, owner C01-19.** Real binary native FBX has 6 meshes/252T; all individual mesh edge windings/manifold indexes PASS, but **18** actual vertex-on-unrelated-edge geometric relations within 0.1 µm in `Cube.019` (8 relation pairs have disjoint face sets, 10 also occur on face-adjacent geometry). Positions run along long 2.13–2.20 m split-frame support edges. This is **genuine geometric contact / candidate partitioning**, not automatically a visible gap or guaranteed shader crack. See [producer's current P19-07 real Blender closeup / wireframe run](https://github.com/C8LyNn/Model-Test/actions/runs/41352494944) for context; independent geometry is not sufficient to authorize unconditional weld. Request producer classification of each T candidate as intentional support subdivision vs real unjoined seam, with targeted fix + exact native retest if required. No GO before visual/Unity acceptance.

**P19-08 / `9de76d296482e2d302b5b0a14c30692dbdb6adacd90fcd4e022da9ab35ec658c` — STATIC_PASS WITH TOLERANCE REVIEW.** Two physically observed vertex-on-edge candidates at normalized edge parameter **0.999921994**, distance to 50 mm edge endpoint about **0.0039 mm**; not interior 4 mm or 40 mm T-junction, no open/nonmanifold edges. At a proposed 0.01 mm proximity tolerance, classify as near-endpoint imprecision rather than *proven* structural defect. No automated weld, monitor after Unity import.

## 36-ID release matrix and practical handoff

- **21/36 physical binary BLEND/FBX pairs independently hydrated+SHA-verified and static-index-audited.** These were genuine producer files, not old source-only models.
- **3/36** P15-01/02/03 have signed matching LFS pair OIDs in C01-10 register but no original full physical archive accessible in this QA run. **POINTER_ONLY / NOT INDEPENDENTLY HYDRATED.**
- **12/36** P15-04..07, P17-04..07, P18-04..07 lack a complete current signed native pair in current registry. Among them **P17-05 and P18-07** explicitly require source→native re-export. **P19-07** has real native pair but remains geometric HOLD.
- **Final release 0/36**, Unity Editor `NOT_RUN` across all 36, no final product GO. Do not confuse **STATIC_PASS** with full model approval.

**Owners:** C01-10 to stage exactly P16-01/P17-02/P18-01 verified SHA in a disposable Unity 6 URP workspace, run actual Unity Editor, produce three real prefabs + scene, EditMode/PlayMode results and `Editor.log`, then return evidence for C01-02 independent final acceptance. C01-03 to reuse this 36-ID hash matrix and hunt the **three currently unhydrated + 12 unsigned** pairs without rerunning successful exporters. C01-17 to fix P17-03 full solid penetration first; C01-19 to classify P19-01/07/08 without bulk destructive weld. C01-18 to test full rotation clearance; C01-16 rotor dynamic sweep still `NOT_RUN`.

**No source/model/ship change, no PR merge. Source archive inputs from GitHub Actions are producer artifacts; independent analysis was performed offline in a separate QA-only workspace, not on producer worktrees.**
