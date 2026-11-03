# C01-02 — WAVE 29 / UNITY INTEGRATION & RELEASE CANDIDATE — independent execution report

**Date:** 2026-11-03. **Role:** C01-02 independent QA, not C01-10 Unity Integration Lead or a native model producer. **Existing Draft:** [PR #13](https://github.com/C8LyNn/Model-Test/pull/13), no merge. **HQ:** [#36](https://github.com/C8LyNn/Model-Test/issues/36), **QA:** [#8](https://github.com/C8LyNn/Model-Test/issues/8), **W27:** [#45](https://github.com/C8LyNn/Model-Test/issues/45).

## 0. W28 closure verified directly against current GitHub, NOT assumptions

- C01-03 canonical [36-row JSON](https://github.com/C8LyNn/Model-Test/blob/c01/props-03-library-wave02/C01InteriorProps_Library/Pass26/C01_03_W26_CANONICAL_36_QA_RELEASE.json) at read-back **blob `8f0db6c3069cb519ab47cd7dd677d8908623a0e1`**, latest Draft #27 HEAD `cd3d919b2b0c715191fdab44de443742ea7c00cb` was read in W29. All 36 current FBX/BLEND SHA-256 rows retained from verified W28 and P19-01 P1 is now accurately marked **independent static pass but assembly VISUAL FAIL / HOLD**; no erroneous P19-01 PASS transfer.
- W28 exact full-source C01-02 Blender4 signed independent [3 repaired current-SHA acceptance #41717112468](https://github.com/C8LyNn/Model-Test/actions/runs/41717112468) + [P18 focused corrected #41717691683](https://github.com/C8LyNn/Model-Test/actions/runs/41717691683); W28 [4 unchanged suspect source/FBX reimports #41722742476](https://github.com/C8LyNn/Model-Test/actions/runs/41722742476) and [P19-01 causal BVH/visible A/B #41724216356](https://github.com/C8LyNn/Model-Test/actions/runs/41724216356). W28 **36/36 live current original FBX LFS OIDs matched authority**, pointer readback != 36 new full physical imports.
- W29 actual producer commit comparisons: P18-03 PR43 `82e3269d…→e39232b5…`, P15 W02 PR25 `0032d313…→dbfc8eb4…`, P19 W02 PR29 `cf042fd3…→aeadaf51…`, C01-10 PR11 `8f4d79ff…→45699e04…` each **exactly one metadata/report document changed**, zero new native FBX/BLEND geometry. No redundant full Blender static reruns.
- New [C01-13 P19-03 current spatial test #41730728371 SUCCESS](https://github.com/C8LyNn/Model-Test/actions/runs/41730728371) tested 3 existing room layouts with exact FBX and 0 wall/floor contacts; this is *not Unity*.

## 1. W29 executed physical visual QA (new scope; never confuse with Unity)

**C01-02 generated genuine Blender 4.0.2 1920×1080 full FBX shaded/original indexed-wire visual evidence at verified unchanged full native BLEND+FBX SHA.** Existing no-defect mesh geometry unchanged.

- [First Action #41735420957 SUCCESS](https://github.com/C8LyNn/Model-Test/actions/runs/41735420957), [artifact #13278871411](https://github.com/C8LyNn/Model-Test/actions/runs/41735420957/artifacts/13278871411): P15-03 34 meshes/672T, P18-03 63/1780, P19-03 5/128; 9 real Workbench PNG, full source SHA/hashes and true original indexed-wire edges; fixed viewpoints / object materials inspected.
- QA camera discovered that **the first P18-03 WHOLE shot cropped the casters**. Corrected only the *orthographic camera 16:9 projected bounds* and ran **ONLY P18-03** [Action #41736031650 SUCCESS](https://github.com/C8LyNn/Model-Test/actions/runs/41736031650), [artifact #13279007246](https://github.com/C8LyNn/Model-Test/actions/runs/41736031650/artifacts/13279007246). The current corrected screenshot shows the whole cart and wheels. No geometry/UV/normal/fbx/export change, no other model reruns.
- These are actual independently produced original-FBX 1080p preview captures, **not `UNITY_ACCEPTED`**, **not** Editor GameView under URP, nor full game-camera readable/shadows and functional acceptance. Final VISUAL SIGNOFF still requires actual Unity and reviewer. No low-poly polygon increase authorized.

## 2. Exact SHA per highlighted model

| ASSET | OWNER | Actual signed FBX SHA256 | BLENDER | INDEPENDENT QA | VISUAL | UNITY | RC STATUS | BLOCKER |
|---|---|---|---|---|---|---|---|---|
| P15-03 | C01-15 | `ea25d2d7b47baa50fdca3000b101c65b19ba252994553ee6fe6691ca89d5c149` | W26 repaired, W27 true native+FBX PASS | STATIC/UV/MOTION PASS @ current SHA; 361+46 per source & FBX | Actual W29 1080p Workbench; URP NOT_RUN | NOT_RUN | BLOCKED | Real Unity import/material/pivot/PlayMode |
| P18-03 | C01-18 | `f932c5fb36624ef91c039b1de04367fff4e99da7c400bbcb4cadd4138f83618f` | W26 8 axle/hub repairs, real W27 import PASS | STATIC/UV/MOTION PASS @ current SHA; 8×73×2 tested | Actual W29 corrected 1080p whole cart/macro; URP NOT_RUN | NOT_RUN | BLOCKED | Real Unity wheel, collider, camera |
| P19-03 | C01-19 | `4a1ad590e79515b0a699f0fb643d9999b4d1726bd68fce97505f401bb8375967` | W26 10 n-gons triangulated, W27 import PASS | STATIC/UV PASS + W28 3-room spatial regression | Actual W29 1080p Workbench; URP NOT_RUN | NOT_RUN | BLOCKED | Real Unity room/shadow/material |
| **P19-01** | **C01-19** | `f3b9f806f4dcaafe00f24ac22b0805bf06a49d4216cb1339460ed1be9b26a2f2` | Current original Blender4 import STATIC PASS; visible fail | **17 real source+FBX Mattress↔AccentStripe BVH hits**, A/B same-camera orange streaks disappear only with *temporary QA-only stripe hide* | **VISUAL FAIL P1** | NOT_RUN | **BLOCKED** | C01-19 producer **surgical actual .blend/.fbx repair**, exact-new-SHA independent C01-02 retest |
| P19-07/P19-08 | C01-19 | `eb579a85…` / `9de76d29…` | W28 current physical import PASS | Tiny UV/micro endpoint warnings recorded; no independently visible repair trigger | W28 Workbench reviewed, final URP pending | NOT_RUN | BLOCKED | Unity, not speculative weld |
| P17-01 | C01-17 | `cd6a5787…` | W28 current physical import PASS | 32 tiny near-perpendicular bolt normals, 0 inverted; no proven unacceptable shading | Producer macro plus W28 signed shaded review | NOT_RUN | BLOCKED | URP/game camera, not forced normal reset |
| P18-07 | C01-18 / C01-01 standard | `858a24db…` | Signed source+FBX real proof same SHA | Static indexed scoped; latch prior 11-step motion measured | placement/clearance scope HOLD | NOT_RUN | BLOCKED | Formal individual 0.341 vs nominal 0.340m + 0.361m dynamic sweep rule |

Full per-model **36 canonical +8 separate architecture** current exact SHA / owner / source PR/commit / Blender / independent QA / visual / Unity / RC and blockers: **[JSON W29 RC](W29_C01_02_INDEPENDENT_RC_36_PLUS_8.json)**, **[44-row release matrix CSV](W29_RC_44_EXACT_SHA_ACCEPTANCE_MATRIX.csv)**. GitHub source readback **11/11 schema, exact SHA, complete IDs, exclusions and release-hold invariants PASS**: [machine QA](W29_RC_44_SOURCE_READBACK_INVARIANTS.json).

## 3. W29 current W01–03 architecture identity

W01 current curated `4260732720...` vs W26 independently tested historic candidate `c644e95d...`; W02 `7dfcf0fe...` vs `a23f602d...`; W03 `4c268d55...` vs `9dcc8fec...`. They are **version identity conflicts, not known topology failures**. Existing owner Draft #22 W29 [source declaration](https://github.com/C8LyNn/Model-Test/blob/c01/walls-11-wave02-native-export/Assets/C01Architecture/Walls_W01_W04/QA/WAVE29/C01_11_W29_NONDOOR_UNITY_INPUT_PROVENANCE.json) confirms no safe existing four-wall Unity builder (because old entrypoints include excluded W04). C01-02 explicitly prepared **real current curated SHA only W01/W02/W03 independent targeted Blender4 source import/FBX QA**, [Action #41736886141](https://github.com/C8LyNn/Model-Test/actions/runs/41736886141) — **RESULT_PENDING at this report snapshot**. Do not transfer candidate PASS across SHA, do not mark curated SHA accepted before this run’s actual reports are read. Five remaining auxiliary F01/F02/C01/RAI-01/RMP-01 retain same-current-SHA scoped historical static QA, no Unity.

## 4. Unity 6000.3.14f1 URP owner packet delivered — NO licensed Editor execution

**[C01-02 W29 exact full owner execution packet](W29_UNITY6_6000_3_14F1_URP_OWNER_EXECUTION_PACKET.md)** for C01-10 existing PR11 runbook, using isolated 4×4m room + 2×4m contiguous corridor only from permitted wall/floor/ceiling variants, 1m snap, controlled materials/pivots/normal/UV/collider/scale. Required 1920×1080 GameView, real prefab and Editor SHA, logged EditMode and PlayMode for P15 internal cabinet hinge, P18 cart wheels, available non-door lever/lid. **Do not use old C01-11 Unity entrypoints that load W04.** Avoid P19-01 until true producer repair+independent exact new-SHA pass. No scene generated by C01-02. Existing PR11 licensed Windows owner runbook remains the implementation authority; no counterfeit Unity PASS or fake off-engine Editor simulation.

`UNITY_6000_3_14f1_URP_EDITMODE_PLAYMODE_NOT_RUN / OWNER_ACTION_REQUIRED` for all 36+8; **0/36 FINAL_APPROVED**.

## 5. Five highest release blockers (W29)

1. **UNITY_LICENSED_EDITOR_OWNER_GATE:** C01-10 real 4×4+2×4 URP scene, non-door FBX, import materials/scale/pivot/colliders, true EditMode/PlayMode and GameView 1080p evidence absent.
2. **P19-01 P1 confirmed visible mattress stripe surface z-fighting:** original signed current SHA still defect; C01-19 PR15 producer surgical Blender4 .blend→FBX→real reimport and independently tested new SHA required.
3. **W01/W02/W03 curated source SHA identity:** unless current curated real signed independent W29 proof completes, do not transfer historic candidate static PASS, and never use forbidden W04.
4. **P18-07 formal C01-01 tolerance and clearance:** 0.341m locked (+1mm) vs nominal 0.340m plus 0.361m moving latch envelope; no general grid tolerance waiver.
5. **Final visual and per-part assembly intent:** current Blender Workbench 1080p does not sign URP gameplay visuals; P16 nested seated component intersect witnesses must be separately classified as intentional or visible failure (do not blanket weld).

## 6. Safety and non-negotiable stop

`CLAUDE_DOORS_EXTERNAL_HOLD`: D01/D02, all Claude-delegated doors and gates, W04 door-opening geometry and frozen PR #19/#32 **NOT inspected, tested, reexported, imported, modified or merged** by C01-02 W29. No new model IDs, ship layout changes, speculative geometry, general normals reset, or unauthorized merge. C01-02 never modified producer native FBX/BLEND; writes only own QA scripts/workflows, artifacts, RC gate/report. `RC_NOT_RELEASED / NO_UNITY_ACCEPTED`.
