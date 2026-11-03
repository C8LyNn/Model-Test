# C01-02 — WAVE 01 independent QA follow-up (2026-10-29)

Parent #2; QA #8; supplier issues #3–7. **Audited source state only; do not merge or mark completed.** 0/16 APPROVED. No change to ship architecture, source scenes, or producer geometry.

## Latest supplier PR heads observed
| Owner | PR | Head SHA |
|---|---|---|
| C01-15 | #16 | `2ed37ba58c25f5b03223668c1f3502869f2d13a8` |
| C01-16 | #12 | `e9cd92831c41ebd5fa2da026326831e524d08458` |
| C01-17 | #17 | `e3b50cddca7a151b6d88b162042e885731958e15` |
| C01-18 | #18 | `f024aa4dfda43c5b0b23183cde4b694a3851b451` |
| C01-19 | #15 | `f3bccbf2fef5265e7cd37d094968d76bdc7b5192` |

## Independent retest of two representative current source files

- **P17-01**: parsed `Assets/C01InteriorProps/Models/P17-01.gltf` at PR #17 head. Blob SHA `87d914c88c8265bed4320f95bc7190e244b37ae8`. Exactly **17 mesh primitives**, **0 with TEXCOORD_0**. **FAIL P1 / C01QA-P1-17-UV0** persists. Other P17 files are not retested here; see prior audit for their older-SHA findings.
- **P18-01**: fetched `Assets/C01InteriorProps/C01-18/Models/P18-01.fbx` at PR #18 head. Blob SHA `e6ed41a3c00066fcfd9a1534b7ba89f0c8795620`. Text FBX 7.4.0 contains neither `LayerElementUV` nor `LayerElementNormal` record. **FAIL P1 / C01QA-P1-18-UV-NORMAL** persists. FBX import was not executed; remaining two P18 files were not independently retested this time.

## Delivery status per asset

| Asset | Static status | Blender native source + FBX roundtrip | Unity 6 URP prefab and clearance | Overall |
|---|---|---|---|---|
| P15-01 | Generator/spec found; output unverified | NOT RUN | NOT RUN | BLOCKED |
| P15-02 | Generator/spec found; output unverified | NOT RUN | NOT RUN | BLOCKED |
| P15-03 | Generator/spec found; output unverified | NOT RUN | NOT RUN | BLOCKED |
| P16-01 | Previous OBJ static evidence (PR #12) | NOT RUN | NOT RUN | BLOCKED |
| P16-02 | Previous OBJ static evidence (PR #12) | NOT RUN | NOT RUN | BLOCKED |
| P16-03 | Previous OBJ static evidence (PR #12) | NOT RUN | NOT RUN | BLOCKED |
| P17-01 | **FAIL P1: UV0 absent in 17/17 primitives** | NOT RUN | NOT RUN | FAIL |
| P17-02 | Previous FAIL P1; not retested at current SHA | NOT RUN | NOT RUN | BLOCKED |
| P17-03 | Previous FAIL P1; not retested at current SHA | NOT RUN | NOT RUN | BLOCKED |
| P18-01 | **FAIL P1: FBX UV/normal layers absent** | NOT RUN | NOT RUN | FAIL |
| P18-02 | Previous FAIL P1; not retested at current SHA | NOT RUN | NOT RUN | BLOCKED |
| P18-03 | Previous FAIL P1; not retested at current SHA | NOT RUN | NOT RUN | BLOCKED |
| P19-01 | OBJ parts present; independent native source check pending | NOT RUN | NOT RUN | BLOCKED |
| P19-02 | OBJ parts present; independent native source check pending | NOT RUN | NOT RUN | BLOCKED |
| P19-03 | OBJ parts present; independent native source check pending | NOT RUN | NOT RUN | BLOCKED |
| P19-04 | OBJ parts present; independent native source check pending | NOT RUN | NOT RUN | BLOCKED |

No Blender or Unity executable available in QA execution environment. Preview files are not substituted for actual engine screenshots. Full 3m corridor and door arc clearance cannot be certified until scene is assembled with actual prefabs. All suppliers retain ownership of their meshes.

## Handoff and repair requests

- **C01-17 / #5:** provide UV0 per glTF mesh primitive, export native .blend and FBX, then demonstrate Unity import; request retest by C01-02.
- **C01-18 / #6:** populate UV/normal layers in final Blender FBX; ensure prefab mesh references point to actual source models rather than built-in Unity cube mesh; provide import evidence.
- **C01-15 / #3:** make generated Blender/FBX artifacts accessible and prove identity by SHA256; do not substitute CI workflow definition for output.
- **C01-16 / #4, C01-19 / #7:** provide native Blender sources and verified FBX/Unity import for all assets.
- **C01-10 / #9:** integrate only actual supplied prefabs in an isolated showcase; run 3m clearance, door swing and mounting tests.
- **C01-00:** no release approval until 16 actual Unity prefabs and independent retest evidence.

**Final: BLOCKED for complete package, 2 currently independently reconfirmed source FAIL; 0/16 APPROVED.**