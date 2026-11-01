# C01-10 — DETAIL PASS 18 / 36-ID native provenance + Unity 6 URP diagnostic handoff

**Date:** 2026-11-01  
**Role:** C01-10 — SPACE HORROR INTERIORS — COORDINATION  
**HQ:** https://github.com/C8LyNn/Model-Test/issues/36  
**Own isolated Draft PR:** https://github.com/C8LyNn/Model-Test/pull/11  
**Release status:** **0/36 FULL APPROVED — HOLD. NO MERGE.**

## Actual PASS18 results

- The previous C01-10 36-entry manifest was stale: real Blender 4.0.2 / Git LFS runs succeeded after PASS17 for C01-15, C01-16, C01-17, C01-18 and C01-19. Do **not** repeat the older erroneous statement that Blender remains universally unavailable.
- Read GitHub **current native .blend and FBX pointer records for 24/24 real producer assets**, each with full 64-hex Git LFS OID and declared byte size. Current reports and matching producer run references where available:
  - **C01-15** P15-01/02/03 — run [41344475164](https://github.com/C8LyNn/Model-Test/actions/runs/41344475164); 3 native .blend + FBX pairs, cabinet P15-03 separate Body/Door outputs also exist, canonical combined P15-03 is for quarantine; [producer binary report](https://github.com/C8LyNn/Model-Test/blob/c01/props-15-installations/Assets/C01InteriorProps/P15/QA/blender_mesh_roundtrip.json).
  - **C01-16** P16-01..07 — real *successful* runs [41348140241](https://github.com/C8LyNn/Model-Test/actions/runs/41348140241) and [41348144803](https://github.com/C8LyNn/Model-Test/actions/runs/41348144803) (prior publish failure superseded); 7 native pairs, 116 meshes / 2052 T producer report. [Exact manifest](https://github.com/C8LyNn/Model-Test/blob/c01/props-16-lighting-wave02/C01Source/LightingW02/MeshRepairPASS17/GENUINE_BLENDER_SHA_AND_QA.json).
  - **C01-17** P17-01/02/03 — [41347796593](https://github.com/C8LyNn/Model-Test/actions/runs/41347796593); 25/380,38/536,20/424 part/triangle current native outputs. Native source/FBX normal/UV topology producer receipts under `C01InteriorProps_Source/QA/PASS04/`; P17-03 original eight boundary edges require independent functional rationale and moving sweep, even though current Blender source/FBX source-triangle parity passed.
  - **C01-18** P18-01/02/03 — [41344872313](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313); **169 meshes / 4044T**. C01-10 previous actual independent binary-byte QA is [PASS17 report](../Pass17/C01_10_INDEPENDENT_NATIVE_P18_FBX_QA.md). Four wheels, moving hubs and static mount parentage structurally preserved. Unity physics/motion NOT RUN.
  - **C01-19** P19-01..08 — actual Blender4 PASS04 runs [41345661916](https://github.com/C8LyNn/Model-Test/actions/runs/41345661916) and [41345672118](https://github.com/C8LyNn/Model-Test/actions/runs/41345672118); detailed current P19-01/02/05 renders and roundtrip [41346465283](https://github.com/C8LyNn/Model-Test/actions/runs/41346465283) and [41346471952](https://github.com/C8LyNn/Model-Test/actions/runs/41346471952). **P19-07 remains explicitly blocked** on historical visible T-junction / vertex-on-edge QA until independent current full-mesh verification.
- These 24 current native pairs are 48 **Git LFS pointer** records. Their OIDs and producer run receipt matches do not mean C01-10 independently hydrated and parsed all 48 full binary files. That separate C01-02 gate is pending. **Neither pointer integrity nor a green producer Blender run establishes Unity or release acceptance.**

## Own executed integration changes

1. Updated `C01InteriorProps/Pass04/source_stage_36.json` to immutable *current* producer commits, current canonical .blend/.fbx paths and exact LFS SHA-256 pins for 24 IDs. Reused existing 36 IDs, all `independent_qa=NOT_APPROVED`. 23 of the 24 can enter **SHA-gated QA-only quarantine**, while P19-07 remains hard-blocked.
2. Added [36-ID current native release matrix](./C01_10_NATIVE_36_SHA_QA_MATRIX.csv). The global count is now **23 signed QA hydration eligible; 10 candidates missing at least one signed Blender+FBX pair; 3 source/QA BLOCKED**. Note that `native_export_sync=CANDIDATE` alone does NOT permit staging if either signed SHA is missing.
3. Hardened `stage_real_fbx.py`: before copying any eligible FBX, require exact current **.blend source path + 64-character SHA**, hydrate the source .blend via LFS in the same immutable detached producer worktree, reject text LFS pointers, verify BLENDER binary magic and entire native source SHA, verify entire FBX magic/SHA, then copy only to `Assets/C01InteriorProps/Pass04Incoming`. No automatic merge, no ship or producer edits, no fallback to old FBX.
4. Added [read-only current producer LFS pointer check](./verify_producer_lfs_pins.py) for immutable 24 source pairs / 48 pointers. This is a **source code test** until an actual GitHub Actions runner executes it. It checks current source-branch HEAD and exact pointer SHA at pinned commit, without LFS hydration.
5. Added `Assets/C01InteriorProps/Editor/Pass18NativeUnityBatchAudit.cs`, a **real Unity Editor batch entrypoint** reading the signed staging paths (not old FBX). It verifies actual hydrated FBX bytes, exact SHA, real imported MeshFilter components, minimum triangles where known, zero degenerate geometry, UV0, imported normals, URP shader compatibility, original named rotor/wheel/lever/door hierarchy, and emits 36 records. It only modifies **QA copy importer settings** when necessary, never ship scenes. Collider, animated swept collisions, PhysX PlayMode clearance and independent final acceptance remain explicit non-passing gates. **Unity executable unavailable in this C01-10 tool runtime: UNITY_NOT_RUN, no fabricated prefab, playtest, shaded/wireframe screenshot or QA PASS**.

## Exact remaining blockers

- `P17-05`: authored rail/glTF changed after old FBX. Current matching signed .blend + binary FBX and independent QA pending; keep BLOCKED.
- `P18-07`: authored lock offset newer than historical FBX. Current native pair and exact SHA missing; keep BLOCKED.
- `P19-07`: real current Blender native pair exists but historical visible T-junction / mesh contact issue not independently resolved; keep BLOCKED regardless of binary file presence.
- `P15-04..07, P17-04/06/07, P18-04/05/06`: legacy QA candidates without **both** current signed native .blend and FBX source pair; fail closed pending actual latest verification. P17-05 and P18-07 are separate blocked entries.

## Unity 6 URP on the authorized Windows editor machine

On a clean worktree of **this C01-10 Draft branch**, with Python3, Git LFS and actual Unity 6000.3.14f1 or project-selected Unity 6 installed:

```powershell
# First validate manifests/producer pointers (read-only aside from git refs):
py -3 C01InteriorProps/Pass18/verify_producer_lfs_pins.py
# Stage selected exact signed real binaries and corresponding native Blender sources:
py -3 C01InteriorProps/Pass04/stage_real_fbx.py --repo . --apply --ids P16-06 P17-03 P18-03
# Actual native importer inspection: runs in REAL Unity Editor, not Python/JS:
$UNITY = 'C:/Program Files/Unity/Hub/Editor/6000.3.14f1/Editor/Unity.exe'
& $UNITY -batchmode -nographics -projectPath (Get-Location).Path -executeMethod C01.InteriorProps.Editor.Pass18NativeUnityBatchAudit.RunBatch -logFile 'C01_PASS18_UNITY.log' -quit
# Optional: existing isolated QA prefab/scene builder (not ship edits):
& $UNITY -batchmode -nographics -projectPath (Get-Location).Path -executeMethod C01.InteriorProps.Editor.Pass04SourceImportAudit.RunBatch -logFile 'C01_PASS18_QUARANTINE_PREFABS.log' -quit
```

Read outputs `C01InteriorProps_QA/PASS18/UNITY_ACTUAL_FBX_IMPORT_36.csv`, `C01InteriorProps_QA/PASS04/staged_sources.csv` and actual Unity log. After these runs, **do not claim PlayMode/motion/whole-scene clearance PASS** until targeted tests with physical collision evidence are performed. C01-02 must issue **individual final QA** by exact same SHA, then C01-10 may integrate with accepted-only showcase tooling; ship layout remains untouched.

## Existing actual current geometry previews (no fabricated replacement)

- Producer actual current P18 authored OBJ: [interactive](https://github.com/C8LyNn/Model-Test/blob/c01/props-18-cargo/Assets/C01InteriorProps/C01-18/QA/Pass17/C01_18_REAL_OBJ_INTERACTIVE_BEFORE_AFTER.html).
- Own [P17 source geometry viewer](../Pass17/PREVIEW_P17_SOURCE_INTERACTIVE.html) and [P18 source geometry viewer](../Pass17/PREVIEW_P18_SOURCE_INTERACTIVE.html) are **source viewers**, not certified Unity/FBX renders and may predate current native exporter files; do not present as definitive latest native material preview.
- P19-01/02/05 actual Blender shaded/wireframe BEFORE/AFTER stored in current producer Draft branches under `Assets/C01InteriorProps/C01-19*/QA/PASS17/`.

**Gate conclusion:** 36 IDs intact; SHA and native candidate provenance updated; **C01-02 full QA PENDING, real Unity Editor NOT RUN, final approved 0/36. HOLD.**
