# C01-03 — DETAIL PASS 24 / WAVE 24 — EXECUTED SOURCE-INTEGRITY & 36-MODEL QA LEDGER

**HQ:** https://github.com/C8LyNn/Model-Test/issues/36#issuecomment-6602639024
**Owner:** C01-03 — existing [Draft PR #27](https://github.com/C8LyNn/Model-Test/pull/27). **No merge, no source model edits, no export, no new model IDs.**

## What was actually performed
- Reconciled immutable 36-row canonical P15–P19 BLEND+FBX pair registry with latest current producer PR head snapshot (explicit in JSON), against C01-02 W23 independent exact-SHA evidence at `aad7ec98957e68a1cffa5f1cfe1492df7fd131a8`.
- Read **8/8** current real Git LFS pointer SHA256 OIDs + byte sizes of P17-03, P18-03, P18-05, P18-07 at producer branches, **all matched existing exact real binary SHA**. This was a **pointer readback**, NOT new hydration, BLEND editor execution or complete independent QA. Historical actual physical producer evidence remains 36 pairs / 72 file full-byte hashes.
- Read current repaired OPTIONAL **RMP-01** at C01-14 Draft #24: new BLEND `9c5a2628...`, FBX `3b47d12a...`, 2/2 live current LFS pointer matches. Prior producer physical Blender4 anti-slip 0.6mm floating-strip fix and 0.4mm embed recorded, **independent C01-02 new SHA acceptance PENDING**, optional model OUTSIDE canonical 36.
- C01-13 independently performed prior W23 actual FBX non-door grid study: P17-01/P18-01/P19-03, 4×4m room, 2×4m corridor, 24/24 single-prop rotated configurations, measured illustrated width 0.20–0.675m; **not an official accessibility or navigation PASS**. Existing isolated non-door Draft PR #39, multi-object W24 pending. **No door models**.
- C01-02 new W24 dedicated independent report has **not yet been published at this ledger snapshot**; newest accepted proof remains [C01-02 W23 report](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/DETAIL_PASS23/W23_NONDOOR_NATIVE_FBX_AND_MECHANICS_QA.md). No W24 QA promotion without exact current physical proof.

## Focused per-asset release states
| Asset | Latest immutable FBX SHA | Grounded latest state | Required next gate |
|---|---|---|---|
| P17-03 | `32d460d5...` | Independent STATIC_PASS / sampled 91/91 MOTION_PASS, previous P0 CLOSED | Unity actual animation |
| P18-03 | `f169ab74...` | Physical 576/576 rendered hub/fork intersections; W23 producer **render-only bearing** source plan 20/20 structural checks; no proven PhysX wheel lock, **no Unity** | C01-02/01 independent source semantics; real Unity wheel motion / collider check |
| P18-05 | `58e33516...` | C01-02 W23 physically hydrated real binary, STATIC_INDEXED_PASS (10 meshes/120T), hinge pivot exists; **hinge swept motion NOT_RUN** | C01-02 exact-FBX hinge sweep |
| P18-07 | `858a24db...` | Producer real Blender→FBX source signed **+20mm authored Unity local Z** visible Front_Lock retract candidate, 23/23 sampled lid angles zero producer contacts. Original locked visual collides 13@0°, 9@5°. Independent CURRENT-source motion accept **PENDING**, nominal 0.340 vs measured 0.341m dimensional tolerance **C01-01 decision PENDING**, real Unity NOT_RUN | C01-02/01 physical state acceptance + depth decision and Unity |
| P15-07 | `ffc0211c...` | Independent STATIC_PASS intentional 2×24 gauge border edges, CLOSED | Unity URP visual |
| P19-01 | `f3b9f806...` | Independent micro-sliver 2→0 STATIC_PASS, CLOSED | Unity visual only |

## Unity licensing gate and final status
C01-10 W24 [HQ report](https://github.com/C8LyNn/Model-Test/issues/36#issuecomment-6602799841) confirms **UNITY_NOT_RUN / OWNER_ACTION_REQUIRED**; real original 3 signed FBX staged, licensed Editor not run; actual prefabs 0/3, scene 0, EditMode/PlayMode not executed, no real Editor.log. ONE owner action on activated legal Windows Unity Hub 6000.3.14f1 in isolated PR11 checkout:
```powershell
& .\C01InteriorProps\Pass20\run_real_unity_windows.ps1 -Mode Execute -ProjectRoot (Get-Location).Path
```
No blocked CI repeated, no credentials exposed.

## Hard freeze: Claude doors
`CLAUDE_DOORS_EXTERNAL_HOLD` remains. D01/D02 and all owner-assigned door/gate geometry/prefabs/scripts/materials/pivots frozen, outside canonical denominator. Existing door PR #19/#32 untouched. No door files read/reexported; historic W23 SHA evidence retained without new W24 verification.

**Registry-only W24 source snapshot delivered; no declaration of independent W24 acceptance or Unity release. 0/36 final approved, 36 HOLD.**
