# C01-03 — DETAIL PASS 23 / WAVE 23 — EXECUTED CURRENT-SHA CATALOG HANDOFF

**HQ:** https://github.com/C8LyNn/Model-Test/issues/36#issuecomment-6601470988
**Own existing Draft PR:** #27. No merge, model repair, re-export, Unity claim, door activity or new IDs.

## Measured independent QA synchronized
- **36/36 native BLEND+FBX pairs** retain original full-byte producer evidence (72 hashed files in prior waves), native SHAs unchanged. Current producer PR18/25/26/29 changed metadata/scripts/reports only. **No new physical native byte downloads performed in C01-03 W23**.
- **36/36 current exact FBX SHA links to C01-02 independent QA records**, but **5 models P15-01/02 and P18-04/05/06 are only reference-linked; independent physical-binary examination NOT_RUN**. This is not 36/36 full QA PASS.
- W22 independent C01-02 current-SHA **P17-03** FBX `32d460d5...`: STATIC_PASS / **91/91 SAMPLED_MOTION_PASS** at -45..+45° every degree, 6.433mm minimum anchor/Housing clearance. Old `775b1e6a...` collision CLOSED. **P15-07** `ffc0211c...` decorative gauge open edges confirmed intentional, **STATIC_PASS**; 48 edges = 2 front dials×24, no welding.
- **P18-03** `f169ab74...`: static PASS but true **P1 ASSEMBLY_MOTION_HOLD**; 576/576 hub-to-fork rotation configurations have 29–33 indexed triangle crossings, possible mesh/render mating vs PhysX interference requires C01-01/02/C01-18 decision.
- **P18-07** `858a24db...`: static PASS, **P1 LOCK_STATE_MOTION_HOLD**; Front_Lock↔lid 13 crossings at 0° and 9 at 5°, also +1mm dimension tolerance. C01-18 has source-only collider and lock-state script, but no licensed Unity compilation or proof of retracting rendered latch geometry. Do not call it PlayMode PASS.
- **P19-01** `f3b9f806...`: previously independent micro-sliver correction confirmed, historical 2→0. No repeat Blender export. P19-07 18 T-junction candidate relations, P19-08 ~0.0039mm near-endpoint and P17-01 32/708 angled normal corners remain scoped visual REVIEW, not newly proved defects.
- C01-02 W22 CSV accidentally dropped **P15-04/05/06** signed W21 `c01_02_reference_sha`. C01-03 restored those exact SHA references from actual immutable W21 independent evidence, without transferring stale P17-03 W21 QA from former FBX SHA.
- **Unity 6000.3.14f1 actual Editor/URP, prefabs, scene, logs, EditMode, PlayMode = NOT_RUN**. C01-10 first-three-FBX preflight is not Unity runtime. Owner must activate authorized Unity Hub on Windows and run existing C01-10 runbook. **0/36 FINAL_APPROVED / all 36 HOLD.**

## Claude doors freeze
`CLAUDE_DOORS_EXTERNAL_HOLD` applies to D01/D02 plus all entrusted doors/gates; Draft PR #19/#32 frozen, outside the 36 models. **No door geometry, preview, materials, pivots, prefab, tools or scripts accessed or changed.** Last W22 historical D01/D02 SHA retained in JSON for later owner-approved comparison only, not a new W23 verification.

## Owner Unity next action
```powershell
& .\C01InteriorProps\Pass20\run_real_unity_windows.ps1 -Mode Execute -ProjectRoot (Get-Location).Path
```
Requires activated, authorized Unity 6000.3.14f1 in isolated C01-10 #11 Windows checkout. No secrets in logs.

**Artifacts:** [W23 JSON](C01_03_W23_36_CURRENT_SHA_QA_UNITY.json) / [W23 CSV](C01_03_W23_36_CURRENT_SHA_QA_UNITY.csv). Independent C01-02 [W22](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/DETAIL_PASS22/W22_NATIVE_INDEPENDENT_QA_FINDINGS.md), [W21](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/DETAIL_PASS21/W21_INDEPENDENT_FBX_QA_HANDOFF.md).

## P18-03/P18-07 — W23 new producer commits, unchanged native FBX/BLEND
- Producer PR #18 HEAD `b681c29b5f186bce6b6cc7afb57383a7b4bf967e`: **P18-03** added source-only six-chassis-collider vs render-only bearing/wheel policy and 20/20 reported static source checks. [Producer receipt](https://github.com/C8LyNn/Model-Test/blob/c01/props-18-cargo/Assets/C01InteriorProps/C01-18/QA/Pass23/P18-03_DECORATIVE_BEARING_COLLIDER_CONTRACT.json). Current FBX `f169ab740...` unchanged, independent W22 hub/fork 576/576 triangle penetrations **HOLD**. NOT a Unity compile or PlayMode PASS.
- Producer PR #26 HEAD `515d40bb81a1b0b267b50664e524ae7567c81eae`: **P18-07** added static producer receipt for 15mm Blender-WORLD retract candidate `[0,-0.015,0]m`, zero reported source/FBX intersections at 23 lid poses, plus uncompiled Unity source changes. [Real-source geometry receipt](https://github.com/C8LyNn/Model-Test/blob/c01/props-18-cargo-wave02/Assets/C01InteriorProps/C01-18-Wave02/QA/Pass23/P18-07_REAL_SIGNED_LATCH_RETRACT_BVH.json). Existing FBX `858a24db...` unchanged. Unity axis/render/physics/lock-state still **NOT_RUN**; independent C01-02 current geometry motion **HOLD** until state/retraction accepted.
- Verified GitHub changes from previous producer heads: 12 files changed, **zero .blend/.fbx/.obj/.glb changes**. The independent QA W22 release statuses were not upgraded. Doors remain strictly frozen.
