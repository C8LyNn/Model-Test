# C01-03 / WAVE 27 — SOURCE-SHA READBACK & QA HOLD
**2026-11-03 | Own Draft PR #27 | master issue #45 | No source/mesh edits, no merge**

## Executed
- Read the existing 36-row authoritative W26 release JSON (Git blob `78dcfe0c7345806ceb8b5b6179bb7c5154289b50`), W26 independent 44-row original FBX polygon audit (Git blob `bc184f3db943aef422b5d85d7d3bd9d8d03829ab`) and original 44 logical source register (Git blob `64d2d320fb5ded5a4d0c0c1ad27f043a903510e1`).
- Inspected **6/6 current producer-branch Git LFS pointer OID SHA256 and sizes** for the three repaired .blend/.fbx pairs. Values exactly equal the W26 current native SHA inventory. This is **pointer metadata readback**, not a W27 full-byte Blender or mesh retest; prior W26 physical receipts remain the evidence base.
- Crosswalk: **33/36 unchanged exact FBX SHA** have previously performed W26 original scoped static QA; **3/36 new repaired SHA** are different from W26's previously inspected old bytes and are **INDEPENDENT_NEW_SHA_PENDING**, not PASS.
- **36/36 canonical release HOLD; 0/36 approved; Unity 6000.3.14f1 URP Editor NOT_RUN / OWNER_ACTION_REQUIRED.** W26 44 logical non-door audited models include eight architecture/structural models outside the canonical 36. W26 **1420 primary + 9 historical versioned path records** are not 1429 unique models/QA results.

## Current signed producer versions — awaiting independent acceptance
| Model / owner PR | Current FBX SHA256 | Current BLEND SHA256 | C01-03 W27 evidence | C01-02 verdict | Unity |
|---|---|---|---|---|---|
| P15-03 / #16 | `ea25d2d7b47baa50fdca3000b101c65b19ba252994553ee6fe6691ca89d5c149` | `e787a9455baa08d5e6b198b4c47d236376b240e08781792020b93be899ca38de` | LFS pointer OIDs read back | **INDEPENDENT_NEW_SHA_PENDING** | **NOT_RUN** |
| P18-03 / #43 | `f932c5fb36624ef91c039b1de04367fff4e99da7c400bbcb4cadd4138f83618f` | `1c8086b048ac1c62a6791bea5df22a22168b5aea4bc17008a2ce233d86ede41e` | LFS pointer OIDs read back | **INDEPENDENT_NEW_SHA_PENDING** | **NOT_RUN** |
| P19-03 / #15 | `4a1ad590e79515b0a699f0fb643d9999b4d1726bd68fce97505f401bb8375967` | `ce43931f9116fe3aef6f795c98e505665c921e6c1080c7d61c5cd518e7f7f5b8` | LFS pointer OIDs read back | **INDEPENDENT_NEW_SHA_PENDING** | **NOT_RUN** |

**No old-SHA static PASS promoted to current new-SHA acceptance.** P15-03 is restricted solely to internal technical-cabinet model as authorized in issue #45; Claude-delegated ship door/gate models and PR #19/#32 remain completely untouched.

## Targeted open risks, not automatic defects
- P19-07: eight collapsed microscopic UV polygons / 17–18 T-junction candidates; visible-game-resolution witness required before edit.
- P19-08: two ~0.0039mm endpoint candidates; no blind weld.
- P17-01: 32 hard-normal corner suspects, 0 inverted; shading witness needed before change.
- P18-07: static depth **0.341m** vs **0.340m** nominal and **0.361m** dynamic latch envelope; C01-01 explicit scoped dimensional policy decision pending.
- P19-01: one microscopic UV face under review; P18-05 23/23 motion, P17-03 91/91 retained on unchanged exact SHA.

## Gate before next C01-03 canonical ledger mutation
C01-02 writes per-new-SHA independent native BLEND/FBX Blender QA verdict with true geometry/UV/normals/motion/visual witnesses and full SHA, posted to #8/#45 and producer PR. Only then update **the affected rows** of canonical 36 ledger; preserve unchanged 33. C01-10 actual licensed Unity6 Windows Editor intake remains a separate gate; mock/editor-source tests do not satisfy it. No model IDs, ship layout changes, door tests, export, or merge.

**Machine-readable scoped 36+8 reconciliation**: `C01InteriorProps_Library/Pass27/C01_03_W27_READONLY_SHA_QA_CROSSWALK_36.json`. Existing authoritative W26 release ledger remains unchanged.
