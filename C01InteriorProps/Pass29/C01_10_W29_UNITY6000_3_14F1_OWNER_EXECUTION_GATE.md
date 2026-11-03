# C01-10 — W29 owner-executable Unity 6000.3.14f1 URP non-door RC validation gate

**Current result: `UNITY_NOT_RUN / OWNER_ACTION_REQUIRED`.** This is a precise owner handoff, **not** an Editor scene, successful import, screenshot, PlayMode run, or a Unity acceptance. PR #11 stays **DRAFT / NO MERGE**.

## Verified upstream immutable inputs

- C01-03 [W29 36+8 RC metadata manifest](https://github.com/C8LyNn/Model-Test/blob/c01/props-03-library-wave02/C01InteriorProps_Library/Pass29/C01_03_W29_RELEASE_CANDIDATE_36_PLUS_8.json), exact producer SHA, all 44 `RC_STATUS=BLOCKED`, 0 Unity accepted.
- C01-02 [W27 genuine 3 changed SHA independent Blender4 import acceptance](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/W27/W27_EXECUTED_EXACT_SHA_ACCEPTANCE.md) — 3/3 STATIC+UV PASS, two movable motion PASS. **Not visual/Unity PASS**.
- C01-02 [W28 independent visual findings](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/W28/W28_INDEPENDENT_FINAL_MESH_ACCEPTANCE_HANDOFF.md): P19-01 visible mattress stripe z-fighting P1, no current producer fix; P17-01/P19-07/P19-08 current numerical warnings without actionable visible defect.
- Existing tested **3-FBX first-slice Windows execution script** and exact output rules: [PASS20 runbook](https://github.com/C8LyNn/Model-Test/blob/c01/props-10-showcase-integration/C01InteriorProps/Pass20/UNITY6_WINDOWS_OWNER_RUNBOOK.md). Previous source preparation run #41540521732 did **not** execute Unity Editor (license gate). **Do not rerun blocked hosted CI.**

| Phase | Asset | Real current FBX SHA256 | Existing evidence / hold |
|---|---|---|---|
| Existing 3-FBX licensed pilot | P16-01 | `c0a782a17a0047e0d578a41e42ac714c0fa0f86c7c4960f4bc10e21a24a278fd` | stage and use existing PASS20 script |
| Existing 3-FBX licensed pilot | P17-02 | `db49121a520f16ca636626795550b83e8a4df94ded56a7ccb76308520bb7c3f6` | stage and use existing PASS20 script |
| Existing 3-FBX licensed pilot | P18-01 | `f541d502ba9eaaf5c7a0a7279c44f71f36dd482e3aed3ba0734058dcf1045f6c` | source static scoped PASS, lid sweep pending |
| Follow-on exact-new-SHA native import | P15-03 | `ea25d2d7b47baa50fdca3000b101c65b19ba252994553ee6fe6691ca89d5c149` | C01-02 static/UV/motion PASS; only internal cabinet mechanism, not externally assigned doors |
| Follow-on exact-new-SHA native import | P18-03 | `f932c5fb36624ef91c039b1de04367fff4e99da7c400bbcb4cadd4138f83618f` | C01-02 static/UV/1168 wheel-clearance samples PASS; six frame-only collider contract requires actual PhysX test |
| Follow-on exact-new-SHA native import | P19-03 | `4a1ad590e79515b0a699f0fb643d9999b4d1726bd68fce97505f401bb8375967` | C01-02 static/UV PASS; C01-13 current physical placement test #41730728371 PASS, not Unity |

**Exclude P19-01 from positive visual QA until C01-19 fixes its verified defect, provides new SHA and C01-02 independent retest.** P18-07 must **not** be signed off before C01-01's written locked-depth +1mm and 0.361m latch swept-envelope clearance ruling.

## One authorized Windows owner step: real editor first, then door-free layout

1. On a licensed Windows 11 host with Unity Hub signed in and **Unity Editor exactly 6000.3.14f1**, use a fresh isolated checkout of **existing Draft PR #11** and Git LFS. Follow [PASS20 runbook](https://github.com/C8LyNn/Model-Test/blob/c01/props-10-showcase-integration/C01InteriorProps/Pass20/UNITY6_WINDOWS_OWNER_RUNBOOK.md); stage original full-byte signed P16-01/P17-02/P18-01 (not their text LFS pointers). Preflight only checks source, **not Unity**.
2. Execute the existing real Editor script in PowerShell (once, not on every PR commit):
   ```powershell
   & .\C01InteriorProps\Pass20\run_real_unity_windows.ps1 -Mode Execute -ProjectRoot (Get-Location).Path -UnityExe 'C:\Program Files\Unity\Hub\Editor\6000.3.14f1\Editor\Unity.exe'
   ```
   Require actual Unity-generated 3 model prefabs, QA scene, sanitized `Editor.log`, **EditMode and PlayMode XML passed >0 and failed=0**, exact full FBX SHA, Unity process success, real GameView and SceneView PNG. If any is missing: `UNITY_NOT_RUN` (no execution) or `UNITY_FAIL` (actual bad test); never `UNITY_PASS`.
3. **Only after pilot** stage the independently approved P15-03/P18-03/P19-03 binaries from exact original producer Draft HEAD via Git LFS into an *isolated QA-only location*, ensuring SHA256 and v7400 binary header. Do not overwrite other agents' producer/ship source. Run the same real Unity importer and scene tests, now with the new signed 3 sources, separate QA receipts.
4. **Non-door modular room/corridor scene, only when architecture version identities are pinned:** room footprint **4m × 4m** (`x=0..4, z=0..4`); adjoining 2m × 4m corridor (`x=4..8, z=1..3`), contiguous open passage at `x=4, z=1..3`, **no door or gate object**. Use original F01 1m floor modules: 16 room + 8 corridor = **24**; use original C01 ceiling modules: 16 + 8 = **24**; perimeter 1m wall modules = **24** (external footprint only, no wall across shared 2m opening). Position actual imported prefab **by measured pivot/mesh bounds**; the given coordinate convention specifies footprint extents, *not unverified pivot locations*.
5. **Architecture identity gate:** do not substitute curatorial W01/W02/W03 FBX with historical independent QA candidate silently. C01-03 current curated SHA **W01 `4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f`**, W02 `7dfcf0fe84952e607a74845ad193acfbb9f4fc029e7f168a94a7bac2edacb78b`, W03 `4c268d554d4e5948ea1927e29b0d32fc581a6f9f14f41fd070bf116a8eb7864c`, while independent tested variants have different SHA. C01-11/C01-03 must choose exact approved source version; **no claim of arch exact-SHA PASS until this decision**. F01 signed `46acac987ca3f8387472b2dc8b611cd871c90cd3e7d4773568c9005c84cb5c09`, C01 signed `632135269d3ac8893a273b364e23aac088c09494011d1d79dc2ca511394344e6`.
6. Perform real Unity **EditMode + PlayMode**, checking 1m module alignment, 24 floor/24 ceiling tiling, 2m connection with no wall at opening, scale/orientation/pivots, Unity URP material and normals under directional + point lighting, `MeshRenderer` visibility, actual collider components and contact without clipping, actual wheel movement for P18-03 and hinge/latch for P18-05/P18-07 **only when their own scoped contracts are ready**. Record pixel-real **1920×1080 GameView + SceneView shaded/wireframe** from player-height camera, plus overview and mechanical closeups. Check unintended coplanar flicker, shadows, floating parts and visual budget; no proxy cube substitute for the actual imported signed FBX.
7. Archive results in **existing C01-10 Draft PR #11** under a QA-only output path, e.g. `C01InteriorProps_QA/Pass29/WindowsUnity/`: actual Unity-generated QA scene/prefabs, sanitized Editor logs, EditMode/PlayMode XML, screenshots, source SHA table, version and build settings, explicit deviations. **Never commit Unity license files, serials, passwords, .ulf, GitHub tokens, local sensitive paths.** Send exact proof to QA #8 and HQ #36. If scene creation was manual, state manual and show original .unity file SHA; this handoff document is **not** that scene.

## Current gate classification (before any owner Windows run)

- `STATIC_ACCEPTED`: C01-02's scoped static/UV/native motion proof only for signed same-SHA models.
- `UNITY_ACCEPTED`: **NONE**, until real authorized Editor + tests + visual acceptance.
- `BLOCKED`: P19-01 visible defect; P18-07 dimension/sweep decision; W01/W02/W03 curated version mismatch; other current-source assembly/visual holds.
- `NOT_RUN`: all Unity 6000.3.14f1 URP Editor/prefab/scene/EditMode/PlayMode, entire 44 asset final release.

**CLAUDE_DOORS_EXTERNAL_HOLD:** no D01/D02, W04 opening or any Claude-assigned door/gate test/import/export/edit; old PR #19/#32 remain untouched. No ship layout change, no new 3D model IDs, no merge, no unauthenticated license workaround.
