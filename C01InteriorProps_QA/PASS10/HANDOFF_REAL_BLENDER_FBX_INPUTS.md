# C01-02 — PASS10 / Actual binary baseline delivery and independent release gate

**Date:** 2026-10-30. **Existing Draft:** [PR #13](https://github.com/C8LyNn/Model-Test/pull/13). **Scope:** 36 existing P15–P19 models. No new model, ship edits, producer asset merge, or fabricated native Blender PASS.

## Physical real binaries, independently recovered and verified

**22 real original native Blender `.blend` files + 22 real Blender-origin binary FBX** recovered byte-for-byte from previous successful producer PASS03 GitHub Actions archives. Extracted only authentic model files, not prior preview reconstructions or Git LFS pointers.

- Source groups: P17-01..07 (7), P18-01..07 (7), P19-01..08 (8).
- File signature: 22/22 `BLENDER-`; 22/22 `Kaydara FBX Binary`; ZIP CRC clean; all 22 FBX SHA256 recalculated and **identical** to PASS06 immutable independent source hashes. Counts and per-model original SHA in `PASS10/36_MODELS_PASS10.csv` and `PASS10/ACTUAL_BINARY_BASELINES_AND_P18_SOURCE_GATE.json`.
- Delivered physical file **C01_PASS10_GENUINE_22_BASELINE_BLEND_FBX.zip**, 2,339,947 bytes; **SHA256 `009fb4c6861a349c6c24f0c1496f97cdb66ecf8aa844dc5590ab091882a8f134`**. The actual ZIP contains 44 binary files, MANIFEST.json and explicit README release warning.
- Uploaded privately to owner's connected Google Drive; file metadata verified name, MIME and bytes, **not shared publicly:** [Download exact original BLEND+FBX ZIP from Drive](https://drive.google.com/file/d/11jx228y3rBRAIEDkNRKsnSleWkbG-NJT/view?usp=drivesdk). The download is also available in this C01-02 chat.
- **STRICT:** The 22 pairs are pre-repair **BASELINES**, **NOT final repaired versions** and must NOT overwrite current producer branches. This grants authentic native inputs for Windows repair even without Git LFS, but cannot replace need for new saved Blender outputs and independent QA.

## NEW source checks (actual current GitHub OBJ bytes)

Independently fetched and parsed current Producer #18 actual source at HEAD `ecfac25934a98985eca8222060e190f8d5cecd5c` vs prior `41d5f6a46bf9c4f6fb9a86f331a6214ec590387a`.

- **P18-01:** exactly 32 original positions changed, exclusively Y by +/−0.001m. Current OBJ 120V, 90 quads, 180 triangles, 15 separate parts; **0 invalid OBJ corner refs, 0 fan-degenerate triangles, 0 reversed recorded face-normal candidates**; full AABB unchanged exactly `[-.45,0,-.45] .. [.45,.90,.45]`. All face indices, UV0 records, normals, object/material membership unchanged. **STATIC SOURCE PASS / NATIVE EXPORT NOT RUN.** Current OBJ git blob `c6178ec0fe38d582eacddab4c342085f2a88afe1`.
- **P18-02:** exactly 48 original positions changed, exclusively Z by +/−0.003m. Current OBJ 136V, 102 quads, 204 triangles, 17 parts; **0 invalid corner refs, 0 fan-degenerates, 0 reversed recorded face-normal candidates**; full AABB unchanged `[-1.05,0,-.4] .. [1.05,2.1,.4]`. All face/UV0/normal/material data unchanged. **STATIC SOURCE PASS / NATIVE EXPORT NOT RUN.** Current blob `ec17212a2d60d1b39216c869b0a9706defa76c4d`.
- **P18-03:** unchanged actual source OBJ git blob `901959fa24658c9beb1439fc06805f3feb8aa069`, 208V/270F/348T, 17 parts, 0 fan-degenerates, 0 invalid references and 0 reversed face-normal candidates.
- **P18-05/06/07:** read latest Producer #26 `Sources/build_wave02.py` git blob `e78c6021a6b753c6d506176190ddcf0ac7adfc04`, compared exact old blob `8b6690d1274534f2ef358329a2d0c90cea82c0b8`; **exactly five changed generator lines** Case_Bottom, Safety_Lid, Bin_Chassis, Handle_Post_L/R (historical PASS03 fixes). The prior +1mm P18-07 Front_Lock source correction remains. These are *source generator synchronization*, not new Blender exports. The old source+FBX pair remains stale for P18-07.

## Reality of native and engine execution

- Local execution environment: Blender 4.x executable **missing**, `bpy` missing, Git LFS missing, Unity6 missing. Blender download DNS fails. There is no authorized connection to the owner's Windows Blender host.
- C01 Actions [41112264623](https://github.com/C8LyNn/Model-Test/actions/runs/41112264623), [41111446940](https://github.com/C8LyNn/Model-Test/actions/runs/41111446940), and [41110256127](https://github.com/C8LyNn/Model-Test/actions/runs/41110256127) fail before runner allocation: `runner_id=0,steps=0`. No repeated zero-runner execution, no billing/privacy/permission changes. **Root cause unknown**, although public B01 Actions were successful.
- Seven P15 authentic final FBX still unhydrated for C01-02 (current Actions PASS03 runs did not expose downloadable artifacts); seven P16 still lack native source+Blender-binary FBX. Existing P17-05 and P18-01/02/03/07 producer source changes not exported to updated native. Five P19 original FBX exporter-triangulation preflight risks persist; P19/P17 offline candidate binary edits are quarantined until actual Blender source matching and roundtrip.
- **FULL PASS10 QA: 0/36**. New Blender source save PASS 0, native Blender-origin new FBX PASS 0, Unity6 URP PASS 0. 22/36 exact **old** binary FBX hashes physically rechecked in this session.

**NEEDS_OWNER_ACTION**: Inspect private repository GitHub Settings → Actions → General/Runners/job annotations and Actions usage/budgets read-only; no spending without consent. OR run producer-owned native Blender 4.x scripts on authorized Windows with true source `.blend` (portable original 22 above) and where needed Git LFS; save NEW repaired `.blend` and binary FBX with source→FBX roundtrip and renders; publish exact new hashes for independent C01-02 QA; C01-10 then real Unity6 import and prefab tests.

Cross-project ENV01–ENV05 B01 knowledge exchange remains QA methodology only: authentic source save/reopen, degenerates, manifold exception, renderer front/back, SHA and engine NOT_RUN distinction; no C01 bytes uploaded into RoboRougelike.
