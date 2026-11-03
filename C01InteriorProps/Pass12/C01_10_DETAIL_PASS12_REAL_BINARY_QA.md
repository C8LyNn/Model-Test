# C01-10 — DETAIL PASS12 / executed real binary source diagnosis (2026-10-30)

**Owner role:** Unity 6 URP import/prefab QA only. C01-18 owns P18 source construction, C01-17 owns P17-02. No source mesh, Blender producer output, ship scene or B01 asset edited. Existing Draft PR #11 stays unmerged.

## What ACTUALLY RAN
- Downloaded original previously successful Blender PASS03 artifacts containing actual `BLENDER-` and `Kaydara FBX Binary` bytes for all four pilot models: P18-03/02/01 and P17-02. Recomputed full binary SHA-256, exactly matched live source FBX Git LFS pointers (not inferred from pointer content).
- Executed an independent Python FBX-7400 node/property/geometry reader on all four **real original binary byte streams**, extracting **69 actual Geometry Mesh objects** (P18-03 17 / P18-02 17 / P18-01 15 / P17-02 20), the original FBX `Model.Lcl Translation/Scale` and world-space mesh AABB. Tested source geometry symmetry, ground contact and cross-part AABB gaps (not a rendering/triangle intersection proof).
- Independently read current C01-18 producer `Assets/C01InteriorProps/C01-18/Sources/part_spec.json`, Git blob `3222abeca671f4e849823f2098a11c5946ad67c5`, to compare semantic naming and part dimensions.
- Generated an **authentic pre-DETAIL PASS12** 4-model Blender shaded/wireframe contact sheet from existing successful PASS03 CI PNGs (not artificially generated AFTER evidence). It is delivered in the assistant's chat, not GitHub (no binary asset duplication).
- A complete locally exported per-mesh AABB diagnostic JSON (27 KB, full SHA-256 `7e2e85c1db2a49ea6a386b74258c7c6cf5b325a3413d3e72f0d7d3d793bd1096`) is delivered in chat; original-before contact sheet SHA-256 `aada087209a5b34637ec59307cee9e2051c21f46d7e5a7436536040b5c848a99`.

## Grounded findings (BEFORE DETAIL12)
| Pilot | Real original binary FBX SHA-256 | Raw mesh parts | Exact mechanical issue to re-test |
|---|---|---:|---|
| P18-03 | `639fc09c39b804b9bf83de75a4096cdefe1229f58549662ee777537c19c5e165` | 17 | Four wheel axes at X±0.390, Y=0.105, Z±0.245m; upright axes at X±0.440, Z±0.290m. Each wheel offset is X=50mm, Z=45mm (67.268mm horizontally). All 4 wheels touch nominal ground Y≈0. Wheel/post AABBs intersect by 2.5mm X × 65mm Y × 45mm Z (REVIEW, not proven triangle collision); 4 distinct Wheel parts still present, but no part named Hub/Axle/Caster/Fork in these 17 archived mesh nodes. Require real supporting axle/fork and ground/rotation verification after native export. |
| P18-02 | `5ba3faf85a3ea57f755eeb51d0db832c1ce37aa64721d710a22db509f2c6d03f` | 17 | Both `Top_Label_±0.5` bottoms Y≈2.025m; top deck top Y=1.975m (50mm vertical gap), nearby upper lip top Y≈2.015m (10mm gap). Neither label AABB intersects any other source mesh. Native bracket/fastener geometry needed or reposition. |
| P18-01 | `84851387b58aeadc7f2ace49201077d847cfd294f82acfb2d0a7dce3e471a939` | 15 | Archival crate. Shell/corner contact is an actual mechanical assembly; AABB overlap alone not proven visible z-fighting. Need shaded contact review, hinges/latches and anchored structure. |
| P17-02 | `af858385a0abae9c623ee4002bcf22bcbc401b5687024acd8df142eb1b848147` | 20 | Archival access reader, not revised native output. Check button travel, service screws and panel clearance after producer new Blender export. |

**Important**: these are *old* exact producer FBX source bytes at PASS03 SHA, unchanged in latest inspected native pointers. The analytical findings neither claim new geometry source repair nor satisfy PASS12 native export, independent C01-02 signoff or Unity 6 runtime.

## Actual Unity integration code changes (this Draft PR #11)
1. `Assets/C01InteriorProps/Editor/Pass04SourceImportAudit.cs` now **enforces** `native_export_sync == CANDIDATE_BINARY_FBX_QA_NOT_APPROVED` when reading the current manifest, so even an existing valid file+receipt cannot circumvent a blocked detail source export.
2. `C01InteriorProps/Pass04/stage_real_fbx.py` recognizes `BLOCKED_DETAIL_PASS12_NATIVE_EXPORT` and excludes these source IDs *before* staging.
3. `C01InteriorProps/Pass04/source_stage_36.json` and `PASS04_36_MODEL_HANDOFF.csv` now mark all four pilots (P18-01/02/03/P17-02) blocked until real revised Blender .blend + binary FBX is published. Old P17-02 known FBX SHA is retained strictly as archived BEFORE provenance, not output acceptance.
4. Scope: 36 existing assets only; **18** currently marked BLOCKED (previous 17 + newly blocked P17-02). Remaining 18 are QA-only candidates, NOT automatically approved by C01-02.

## Native/Unity execution status and owner dependency
- **Genuine new DETAIL12 .blend written**: 0 by C01-10; **new binary FBX export**: 0; **new Blender save→FBX→reimport**: NOT RUN; **actual Unity 6 URP import**: NOT RUN; **native Unity prefabs**: 0; **real post-detail AFTER PNG**: NOT RUN.
- The available execution runtime has no Blender 4.x, `bpy`, git-lfs or Unity 6, and GitHub Actions private repo jobs continue to fail without runner steps. No billing/permissions changes, no repeated futile job reruns. Need **NEEDS_OWNER_ACTION**: run Blender 4.x+Git LFS/Unity 6 on user workstation, or restore real CI runner allocation with owner controls (no budget changes without explicit approval).
- Producer C01-18 (existing Draft PR #18) must actually save the 3 enhanced native .blend and real bin FBX, include before/after closeups at the exact mounts and C01-02 SHA; C01-17 (existing Draft PR #17) owns P17-02. C01-10 can then stage and test actual Unity import/material/UV0/mesh hierarchy/4-wheel movement/collider clearance. No merge without independent QA.
