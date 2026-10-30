# C01-17 PASS05 — actual binary FBX contacts, runner diagnosis, producer handoff

Scope issue #33 (parent #30), only seven owned models P17-01–07. NO new models, NO repair-by-proxy, NO redesign, NO ship changes, NO merge.

## Evidence ACTUALLY EXECUTED outside GitHub Actions

Hydrated authentic native Blender PASS03 **binary FBX 7400**, SHA-256 verified from real ZIP bytes. Local Python parser read Geometry/Vertices/PolygonVertexIndex, Connections and Model transforms (including FBX root orientation/scale). Per-polygon triangular coordinates transformed to meters. Tested convex triangle-plane coplanarity and Shapely polygon intersection across separate mesh objects. Representative intersection point ray-cast outward through actual FBX triangles (not renderer, not reconstructed cubes).

**Results: 7/7 binary FBX parsed; 1624 triangles, 130 distinct parts; 12 coincident-plane part-pair candidates, 0 P17-02. Five models have at least one outward-ray-unobstructed overlap sample; does NOT prove visible z-fighting in Unity.** Increased candidate count from earlier PASS04 six results is sensitivity/transform processing, not a model change. Detailed actual branch-specific SHA matrix follows.

| ID | BEFORE Blender V/E/F/T | PASS03 AFTER Blender/FBX V/E/F/T | Coplanar part-pairs | SHA256 FBX |
|---|---|---|---:|---|
| P17-01 | 408/510/204/204 | 136/306/204/204 | 1 | `fca67dad3e35e7070575c7d7d141fab3e6756eecb0d618d325ec36266eca2772` |
| P17-02 | 480/600/240/240 | 160/360/240/240 | 0 | `af858385a0abae9c623ee4002bcf22bcbc401b5687024acd8df142eb1b848147` |
| P17-03 | 456/540/208/208 | 128/312/208/208 | 3 | `749c0a6e3df59e927fc448e01ae233504b46d0caed1d6ecd1768be8c926a412c` |
| P17-04 | 696/870/348/348 | 232/522/348/348 | 3 | `093be5df6e600764528c68368441e5c83a2cc020def2f5e4b03c99cbc659b968` |
| P17-05 | 480/600/240/240 | 160/360/240/240 | 1 | `3fa314481f87d66f9a878936028b809cd78440d781146a058594e28f3f4e1740` |
| P17-06 | 312/390/156/156 | 104/234/156/156 | 3 | `d9fcaf1a5b0f77ef375b96bdbf17d9a4731156c13880a26647aa481ee59723fb` |
| P17-07 | 456/570/228/228 | 152/342/228/228 | 1 | `c9e4b221c96ddb9ecd137946ec6043a6c11af21934ad21699c5dedfa1b750285` |

Each pair below: `mesh A` / `mesh B`, candidate summed same-facing projected triangle overlap surface m², outward ray samples not blocked by another real triangle. Counts are **diagnostic flags, not proven defects**.

- P17-01 Backbone ↔ Plinth: 0.047970006 m²; unoccluded outward samples=3
- P17-03 Base ↔ WarningBar: 0.00372 m²; unoccluded outward samples=0
- P17-03 Base ↔ FootR: 0.0112 m²; unoccluded outward samples=3
- P17-03 Base ↔ FootL: 0.0112 m²; unoccluded outward samples=2
- P17-04 CableBar ↔ Underframe: 0.003750003 m²; unoccluded outward samples=0
- P17-04 Keyboard_L ↔ WarningStrip: 0.01475 m²; unoccluded outward samples=0
- P17-04 Keyboard_R ↔ WarningStrip: 0.01475 m²; unoccluded outward samples=0
- P17-05 DisplayBezel ↔ LowerDisplayRail: 0.059199984 m²; unoccluded outward samples=6
- P17-06 CoverBottomLip ↔ Housing: 0.000275 m²; unoccluded outward samples=4
- P17-06 Actuator ↔ SwitchPlate: 0.000156 m²; unoccluded outward samples=0
- P17-06 Actuator ↔ SwitchBlack: 0.00468 m²; unoccluded outward samples=0
- P17-07 RemovableCore ↔ RemovableHandle: 0.002274999 m²; unoccluded outward samples=3

Potentially externally visible or assembly-exposed contacts warranting C01-02 visual inspection first: P17-05 DisplayBezel–LowerDisplayRail (six ray samples); P17-07 RemovableCore–RemovableHandle (three); P17-06 CoverBottomLip–Housing (four). P17-01/P17-03 may be intentional base-to-foot contact but are not silently approved. P17-04 overlaps have all ray samples occluded; do not change without a visual defect.

## GitHub Actions diagnostic PASS05

Dedicated minimal no-Blender smoke workflow `.github/workflows/c01-17-pass05-runner-diag.yml` triggered: https://github.com/C8LyNn/Model-Test/actions/runs/41098559165. Two independent jobs `ubuntu-latest` and `ubuntu-22.04` BOTH failed before runner assignment, steps=[]; no echo/python executed. PASS04 workflows #41094361604 and #41094377349 also failed before allocation, including re-runs. This rules out the Blender Python code as the immediate cause of these no-step failures, but **exact root cause is unknown**: check Actions permissions, plan/billing/spending, runner assignment and GitHub incident/account status. GitHub Status listed a multi-service incident on 2026-10-30 resolved 15:02 UTC, which does not confirm causation for later failures.

Local execution environment: no blender binary, no `bpy` module; pip registry did not offer bpy and apt-get update timed out. **NO Blender 4.x PASS05 run**, new .blend/.fbx generation **NOT RUN**. Previous genuinely executed Blender 4.0.2 repair/export/reimport PASS03 remain verified: W01 https://github.com/C8LyNn/Model-Test/actions/runs/41089779966; W02 https://github.com/C8LyNn/Model-Test/actions/runs/41088800979.

## Gates

- Existing mesh source and LFS binaries remain unchanged in PASS05; all 7 had source-local topology repaired in PASS03. Local FBX geometry check PASS (binary/parser) but new Blender-specific export or Unity tests NOT RUN.
- PASS05 discovered 12 cross-part **candidates**; do not weld/join separate moving/control parts automatically, do not reinterpret deliberate contacts as defects.
- C01-02 independent QA **PENDING** for all P17 models; no signed FULL PASS.
- Unity 6 URP FBX import, native prefab creation/clearance **NOT RUN**.
- C01-02: inspect actual source geometry/wireframe and close-ups for 12 candidates, confirm which are visible z-fighting; if confirmed assign a surgical localized repair to C01-17; then re-export source .blend/.fbx and pin new SHA. P17-05 is most important.

## Reproduce

Download previous successful native Blender PASS03 Actions artifacts above; local self-contained forensic Python script (`fbx_binary_parser.py` + `contact_audit.py`) is supplied in the separately delivered PASS05 evidence pack. Dependencies: numpy, scipy, shapely. In-repo `pass04_strict_fbx.py` also remains available on both PR branches for Blender execution once runner permits. Actual source screenshots in QA/PASS03/Previews, not reconstructed.

No PR merge and no new family of assets.
