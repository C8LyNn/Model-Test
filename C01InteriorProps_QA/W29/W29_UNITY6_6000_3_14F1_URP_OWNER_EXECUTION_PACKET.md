# C01-02 W29 / Unity 6000.3.14f1 URP — exact-SHA owner execution packet

**Status:** `UNITY_NOT_RUN / OWNER_ACTION_REQUIRED`. This document is an execution checklist, **NOT** evidence that a scene or prefab was built or tested. **C01-10 owns Unity integration** in existing [Draft #11](https://github.com/C8LyNn/Model-Test/pull/11); reuse [actual Windows owner runbook](https://github.com/C8LyNn/Model-Test/blob/c01/props-10-showcase-integration/C01InteriorProps/Pass20/UNITY6_WINDOWS_OWNER_RUNBOOK.md), no parallel/competitive builder. C01-02 signs independent results after original Editor logs and per-asset current SHA are provided. No authorized merge.

## Sources and strict SHA scope

Use an isolated QA staging scene **inside existing Unity 6000.3.14f1 URP project** (not a replacement ship scene). Source material must come from original current owner Draft PR branches with Git LFS verified **FULL FBX SHA256 after checkout**; a pointer-only check isn't Unity import.

**Three current independent Blender4 accepted repaired models:**

| Asset | Producer PR / source commit | FBX full-content SHA256 | Independent Blender evidence |
|---|---|---|---|
| P15-03 | #16 / `880c3c6eaa199da3490a4ca66413a247bd08e78e` | `ea25d2d7b47baa50fdca3000b101c65b19ba252994553ee6fe6691ca89d5c149` | [W27 #41717112468](https://github.com/C8LyNn/Model-Test/actions/runs/41717112468) 361 hinge-critical + 46 whole motion samples each source/FBX |
| P18-03 | #43 / `e39232b52ca57759b654a3db9a39aa8f4ad3bd07` | `f932c5fb36624ef91c039b1de04367fff4e99da7c400bbcb4cadd4138f83618f` | [W27 corrected #41717691683](https://github.com/C8LyNn/Model-Test/actions/runs/41717691683) 8 hub/fork pairs ×73 angles on each source/FBX |
| P19-03 | #15 / `e053a786ffe8f08e5121c3ae5aa0f974a629660d` | `4a1ad590e79515b0a699f0fb643d9999b4d1726bd68fce97505f401bb8375967` | [W27 #41717112468](https://github.com/C8LyNn/Model-Test/actions/runs/41717112468), [additional current room-placement regression #41730728371](https://github.com/C8LyNn/Model-Test/actions/runs/41730728371) |

**Room/corridor modular sources separate from canonical 36:** F01 `46acac987ca3f8387472b2dc8b611cd871c90cd3e7d4773568c9005c84cb5c09`, F02 `229d88a2471fb27e48e62a7c81396f935b45e6ae548ce9d2540908ef63932782`, C01 `632135269d3ac8893a273b364e23aac088c09494011d1d79dc2ca511394344e6` — previous independent same-SHA scoped static pass, native composite placement still QA hold. W01/W02/W03 **CURRENT CURATED** exact FBX SHA are `4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f`, `7dfcf0fe84952e607a74845ad193acfbb9f4fc029e7f168a94a7bac2edacb78b`, `4c268d554d4e5948ea1927e29b0d32fc581a6f9f14f41fd070bf116a8eb7864c`. **Their prior independent W26 physical-tested FBX SHA differ** — do not inherit W26 candidate PASS; perform actual current-curated SHA independent Blender/FBX QA first or explicitly mark `ARCH_SHA_VERSION_HOLD`. Never use W04 opening or any delegated Claude door.

**P19-01**: BLOCKED and exclude from release staging until C01-19 exact corrected native FBX SHA and C01-02 new-SHA independent real Blender+visual retest. Existing `f3b9f806...` has proven mattress/stripe z-fighting ([#41724216356](https://github.com/C8LyNn/Model-Test/actions/runs/41724216356)).

## Isolated physical test scene, no ship layout changes

- Scene name suggestion: `C01_W29_QA_NonDoor_4x4_2x4` under existing project QA area; **do not overwrite the ship scene or import door/gate assets**.
- Assemble **one 4m × 4m room** and contiguous **2m × 4m corridor** on 1m world grid from allowed, SHA-pinned wall/floor/ceiling modules only. A room↔corridor passage may remain open (no door model or Claude-owned opening-interface part).
- Test room corners, wall/floor/ceiling seams, normal orientation, X/Y/Z conversion and 1m snapping, collider geometry vs imported visible meshes, cast/receive shadows, URP Lit materials and 1920×1080 GameView frames. Record each real used FBX file path/SHA as a sidecar.
- Place the three Blender-accepted P15-03/P18-03/P19-03 existing furnishing models into the room (no forced scale/rotation to hide faults). Check source pivot, parent hierarchy, hierarchy object count, import-axis matrices, material slots, UV0 and game-camera silhouettes. Retain original polygon budgets (34/672, 63/1780, 5/128).
- Real EditMode QA: check every current import for 1m unit, position/orientation, pivot and renderer/collider consistency, lighting/shadows, z-fighting, occlusion, 1080p screenshots and bounds. Measure spatial clearances and intentional vs accidental seams; do not treat an open corridor pass as proof of a separately frozen door interface.
- Real PlayMode QA on available *non-door* animated equipment: P15-03 internal cabinet hinge (not Claude ship door), P18-03 cart wheel rotations / axle vs fork, P17-03 lever ±45°, P18-05 movable lid (if included) with actual `Animator`/controller, runtime colliders/PhysX. Check signed real FBX motion/pivots/hierarchy, 0 forbidden penetrations, no floating supports. Do not claim Blender BVH == PhysX.
- P18-07 may be included *only* for dimensional clearance testing; signed stationary 0.341m (nominal 0.340m) and dynamic latch sweep 0.361m require formal C01-01 per-asset decision. No global grid tolerance change.
- P16-01..07 cross-part intersections: visually distinguish intentional seated fasteners/emitter overlays from unacceptable visible penetrations at real GameView. Never auto-weld or delete otherwise working models.

## Required physical receipts: all MUST be genuinely produced by the licensed Editor

`UNITY_ACCEPTED` may be assigned **per exact FBX SHA only after all applicable passes**:

1. `Editor.log` with **Unity 6000.3.14f1** version and URP active, Editor license available; import and prefab build errors 0.
2. Unity asset import SHA/size manifest plus Editor-side scale/pivot/axis/material/collider/renderer validation JSON or log (actual Editor APIs), scene and prefab revision SHA.
3. **EditMode** test results, real room+coridor screenshots at **1920×1080**, whole scene and details, scene camera and shadow/material witness.
4. **PlayMode** controller/moving props cases, collider/PhysX collisions, 0 invalid game runtime state, screenshots and logs.
5. Explicit no door/gate/W04/PR19/PR32 bytes accessed or moved; no ship layout change, no unauthorized merge.
6. Independent C01-02 review tied to current per-asset SHA, with clear separate `STATIC_ACCEPTED / UNITY_ACCEPTED / BLOCKED / NOT_RUN` fields.

**Until above: `UNITY_NOT_RUN / OWNER_ACTION_REQUIRED` for all 36 canonical + 8 auxiliary**, `0/36 FINAL_APPROVED`; no licensed Editor tool is connected to this C01-02 workflow, and GitHub Blender Actions **cannot** establish Unity pass.

## Ownership and next dependency

C01-10 → produce actual QA scene, logs, screenshots, Unity tests or explicit owner blocker; C01-11 → W01/W02/W03 identity before current-curated static acceptance; C01-19 → P19-01 surgical native repair/new SHA; C01-01 → P18-07 scope-only dimensional decision; C01-03 → synchronize RC manifest after matching this independent source. C01-02 only reaudits changed exact SHA. Existing Drafts remain open/unmerged. Absolute `CLAUDE_DOORS_EXTERNAL_HOLD`.
