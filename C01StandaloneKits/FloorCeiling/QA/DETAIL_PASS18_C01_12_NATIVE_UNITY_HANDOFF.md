# C01-12 — DETAIL PASS18 / NATIVE QA & UNITY HANDOFF

**Owner:** C01-12 Floors & Ceilings · **HQ:** https://github.com/C8LyNn/Model-Test/issues/36 · **Draft PR:** https://github.com/C8LyNn/Model-Test/pull/20

## Scope

Read-only PASS18 on the three existing historic F01, F02 and C01 modular floor/ceiling assets. They are **NOT** among 36 P15–P19 interior props and must not be substituted for current ship architectural prefabs. **No new models, ship edits or merge.** Current exact native sources, Blender-generated FBX, GLB and 12 true BEFORE/AFTER shaded/wireframe previews remain unmodified in C01StandaloneKits/FloorCeiling/DetailPass17.

## Verified final PASS18 execution and current test statuses

- **Actual Blender 4.0.2 & headless Chrome:** [GitHub Actions run #41352753090](https://github.com/C8LyNn/Model-Test/actions/runs/41352753090) **SUCCESS, every job step completed**.
- [Artifact #13102410237 — PASS18 three native QA receipts/screenshots/offline HTML](https://github.com/C8LyNn/Model-Test/actions/runs/41352753090/artifacts/13102410237) — download ZIP, SHA and PNG evidence. Includes 6 files: Blender QA JSON, Chrome QA JSON, 3 genuine screenshots and self-contained HTML.
- **F01 / F02 / C01 native Blender checks:** **PASS 3/3** on current original-vs-current native sources, real FBX and real GLB imports, exact SHA256. Each 16 vertices, 28 edges, 14 quads, 28 triangles; 0 checked degenerates/UV collapses/nonmanifold and 0 same-facing planar interior overlap. Full producer QA JSON in the Actions artifact.
- **Chrome actual real-data smoke:** **PASS 3/3**. All three pinned genuine GLBs loaded in browser, 28 triangles each, matching source SHA. F01 screenshot 149,958 bytes (SHA256 16bd75a9277654a8373ba1d895981876c671f857074c6e0210c602d373bb355c), F02 152,866 bytes (SHA256 f2e3c510869dd2418132defe035a3c712451f248497592e156e270731838d874), C01 150,495 bytes (SHA256 ca8fc18bed9412f0a7409f53038e38c05a12d753339555b76df64c2ab99bdd8a).
- Browser loading and screenshot existence are proven; detailed human visual review of every render remains **NOT RUN**.
- **Unity 6 Editor compilation, imported prefab/collider/URP PBR visual/PlayMode tests NOT RUN; C01-02 final acceptance PENDING**. Not a replacement for the 36 asset QA matrix.

## Current true binary SHA256 pins

| Asset | .blend v004 | FBX v004 | GLB v004 |
|---|---|---|---|
| F01 | ea75f1c8b4f039b3d58569b483955b24f5d891df4f1f543180fb7af16f136525 | 46acac987ca3f8387472b2dc8b611cd871c90cd3e7d4773568c9005c84cb5c09 | d29a5705e44f36839c5d40cc2897ed3fd65712917cd7040b8ae89e8bb6f51992 |
| F02 | 073eed0c5f150a09067c9797bff6be6af90a5596ae99ed8d71359039ea5113de | 229d88a2471fb27e48e62a7c81396f935b45e6ae548ce9d2540908ef63932782 | 6fafcfd1612f9de6931ac16bd30608a87f38d759fb1caf07106130cea9fafa7b |
| C01 | 70715084bd5917b10916d33d5ff2224cd79878677e19e39b312b207d1cc82fb6 | 632135269d3ac8893a273b364e23aac088c09494011d1d79dc2ca511394344e6 | 87f5b7a390e0c5b52be79893291d90453a3459a28f881d24bec6528fbed7a1b3 |

Full original source/output and PNG SHA: C01StandaloneKits/FloorCeiling/DetailPass17/QA/DETAIL_PASS17_NATIVE_SHA256.json. Genuine native source export proven on https://github.com/C8LyNn/Model-Test/actions/runs/41349568211 (SUCCESS).

## PASS18 actual Blender 4.x QA methods

Tool: Tools/C01Floors12/pass18_native_readonly_qa.py; CI .github/workflows/c01-floors12-pass18-readonly.yml.

- Hydrate genuine LFS binaries, check full SHA, open actual v003 and v004 .blend, reimport actual v004 binary FBX and GLB.
- Verify three materials and embedded 512² basecolor/normal/roughness PNG with source color-space choices.
- Verify 16 vertices / 28 edges / 14 quad faces / 28 triangles each, UV0 positive area, normal/winding orientation, manifold and quad material selection.
- Detect actual same-facing coplanar interior overlap on 14 rectangular planes. Distinguish same quad surface with different triangulation diagonal (importer may choose either). Compare exact original quad 3D corners and matching UV0/material ids. Accept only bounded numeric float error below 1e-5 m (C01 FBX near 1e-7 m is confirmed).
- Blender QA is **producer preflight, NOT C01-02 independent 36-model final QA**.
- Offline viewer generator uses only current real embedded GLB files; Chrome checks F01/F02/C01 individually with actual screenshots. HTML and JSON evidence published as PASS18 Actions artifact after a fully successful run. A static HTML file alone never counts as browser PASS.

## UNITY 6 URP — unexecuted explicit quality gate

Source: Assets/C01Floors12Pass18/Editor/RealNativeUnityAudit.cs, with committed .meta GUID. This is an isolated editor-stage/test utility, NOT an already executed Unity test. Project expected version 6000.3.14f1 and URP 17.3.0.

To execute on a licensed Unity host, hydrate Git LFS and open the project, then use Tools > C01 > Floors & Ceilings > PASS18 Stage QA-only FBX prefabs and validate, or Unity batch -executeMethod C01.Floors12Pass18.Editor.RealNativeUnityAudit.Run. The tool fails closed on source SHA mismatch, imports only F01/F02/C01 into isolated Assets/C01Floors12Pass18/Generated, checks actual Unity mesh triangles/UV0/normals/bounds and staged collider, and writes Library/C01Floors12/PASS18_REAL_UNITY_IMPORT_QA.json on actual execution.

**NOT RUN**: Unity C# compile, actual Editor import, generated prefab QA, PBR normal orientation/URP Lit texture appearance, active collisions/PlayMode, ship clearance. Do not claim release PASS or change the ship even if producer Blender QA passes.

**FINAL GATE:** C01-02 independent final approval PENDING, C01-10 Unity integration NOT RUN, NO MERGE, no replacement of latest ship floor geometry.
