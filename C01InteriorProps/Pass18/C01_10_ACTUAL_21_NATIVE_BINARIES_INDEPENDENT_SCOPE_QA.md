# C01-10 — DETAIL PASS18 / independent physical binary scope QA — **EXECUTED**

**Owner:** C01-10 / Space Horror Interiors Coordination. **2026-11-01.** Own Draft [PR #11](https://github.com/C8LyNn/Model-Test/pull/11), parent [HQ #36](https://github.com/C8LyNn/Model-Test/issues/36). **No merge, new models, ship geometry edits, producer source edits or false final QA.**

## Original immutable, actual files

Original GitHub Actions downloadable artifact ZIPs independently fetched and BYTE-OPENED, not only Git LFS pointers:

| Producer | Successful native run | Artifact | Existing models |
|---|---|---:|---|
| C01-16 W01 | [41348140241](https://github.com/C8LyNn/Model-Test/actions/runs/41348140241) | 13099778112 | P16-01–03 |
| C01-16 W02 | [41348144803](https://github.com/C8LyNn/Model-Test/actions/runs/41348144803) | 13100396298 | P16-04–07 |
| C01-17 W01 | [41347796593](https://github.com/C8LyNn/Model-Test/actions/runs/41347796593) | 13099877855 | P17-01–03 |
| C01-18 W01 | [41344872313](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313) | 13099325067 | P18-01–03 |
| C01-19 W01 | [41346465283](https://github.com/C8LyNn/Model-Test/actions/runs/41346465283) | 13099591414 | P19-01–04 |
| C01-19 W02 | [41346471952](https://github.com/C8LyNn/Model-Test/actions/runs/41346471952) | 13099890315 | P19-05–08 |

**ACTUALLY EXECUTED independent byte + limited geometry tests:** all 6 producer ZIP CRC PASS; all **21 actual BLENDER-v400 source files** and all **21 actual Kaydara FBX Binary 7400 files** byte-for-byte SHA256 match the immutable **42 current producer Git LFS SHA256 OIDs** already checked on live branches. Real FBX binary v7400 zlib arrays parsed; Geometry-to-Model instancing counted (do NOT confuse unique geometries with live mesh instances), per-polygon indices/UV0/normals/degenerate true triangle polygons and per-corner UV indices validated. Across 21 complete actual FBX **417 geometry/model instances** and **9304 diagnostic fan-triangulated triangles**. Zero missing UV0 arrays, normal arrays, invalid polygon indices, bad UV indices, repeated face indices or degenerate physically triangular polygons in this narrowly tested scope. No substitute primitives.

| Actual FBX | Instances | Diagnostic triangles | Scoped basic binary QA |
|---|---:|---:|---|
| P16-01 | 12 | 220 | PASS (scoped only) |
| P16-02 | 12 | 220 | PASS (scoped only) |
| P16-03 | 12 | 220 | PASS (scoped only) |
| P16-04 | 27 | 452 | PASS (scoped only) |
| P16-05 | 19 | 344 | PASS (scoped only) |
| P16-06 | 23 | 388 | PASS (scoped only) |
| P16-07 | 11 | 208 | PASS (scoped only) |
| P17-01 | 25 | 380 | PASS (scoped only) |
| P17-02 | 38 | 536 | PASS (scoped only) |
| P17-03 | 20 | 424 | PASS (scoped only) |
| P18-01 | 47 | 980 | PASS (scoped only) |
| P18-02 | 59 | 1284 | PASS (scoped only) |
| P18-03 | 63 | 1780 | PASS (scoped only) |
| P19-01 | 4 | 470 | PASS (scoped only) |
| P19-02 | 5 | 292 | PASS (scoped only) |
| P19-03 | 5 | 128 | PASS (scoped only) |
| P19-04 | 9 | 108 | PASS (scoped only) |
| P19-05 | 7 | 252 | PASS (scoped only) |
| P19-06 | 7 | 84 | PASS (scoped only) |
| P19-07 | 6 | 252 | HOLD / historical visible T-junction |
| P19-08 | 6 | 282 | PASS (scoped only) |

**Explicit limitations:** FBX n-gons are fan-triangulated **for diagnostic counting and offline preview only**, not the actual Unity or Blender tessellation. This does not clear any arbitrary cross-part self-intersection/z-fighting, hidden T-junction, welding, UV island quality, mesh tangent/normal shading appearance, material slots, moving pivots across whole swept volumes, physics or 3 m corridor. P19-07 remains a firm HOLD. Independent **C01-02 official 36-ID per-asset full release QA PENDING**, actual Unity 6 URP Editor/PlayMode/PBR/prefab import **NOT RUN**, **0/36 FINAL APPROVED**. Other 15 total IDs not in this exact 21-asset ZIP have no claim of full physical-byte QA by this pass, including C01-15 three pairs whose native LFS SHA OIDs were checked but run returned no downloadable artifact.

## Real binary interactive preview — executed, no remote dependencies

Built self-contained **21-model HTML** exclusively from freshly extracted original FBX geometry and FBX parent Transform hierarchy, with all 417 real named mesh instances. Canvas2D CPU depth buffer (no WebGL requirement), shaded/wireframe/shaded+wire, model and part picker, orbit/zoom, PNG export; actual viewport dimensions derived from native FBX geometry. **Actual Chromium headless smoke**: all 21 IDs populated; selected P18-03 shaded/wireframe, P17-03 wireframe, P19-07 HOLD, 3 actual screenshots saved, **zero JS errors**. Diagnostic material palette is NOT source PBR/URP asset material fidelity. Genuine C01-19 Blender Workbench shaded+wireframe BEFORE/AFTER for P19-01/P19-02/P19-05 preserved unchanged from original producer archive, other BEFORE renders not invented.

**Physically delivered user-chat ZIP**: `C01-10_DETAIL_PASS18_21_REAL_NATIVE_FBX_INTERACTIVE_QA.zip`, **23,652,688 bytes**, **114 ZIP members**, CRC/read-back plus **113/113 content SHA256 entries validated**, aggregate ZIP SHA256:

```
8f14f36f00a91d4b726eec550bb662c93ebcbce24dbd6e15b97c612ee13a0b62
```

It includes 21 x .blend, 21 x FBX original production bytes, original producer QA/Workbench source evidence, standalone actual FBX viewer, real PNG smoke captures, full per-asset Python QA JSON with exact original ZIP SHA/actual FBX SHA, reproducible offline audited script and per-file SHA list. The large binary ZIP was delivered **in this chat**, **NOT committed to Github**, and original producer SHA assets remain in own Draft PR source branches. Never relabel this as a new Blender export or Unity QA pass.

## Separately executed PASS18 GitHub Actions

[Integrator CI **SUCCESS #41352877495**](https://github.com/C8LyNn/Model-Test/actions/runs/41352877495) generated artifact **13102285937**, independently verified **24/24 native producer LFS pointer pairs / 48/48 current SHA OIDs** at immutable source commits, correctly allowed producer QA-only HEAD drift iff actual binaries remained identical; all Python compiler/static manifest checks and 4/4 negative SHA-preflight staging regressions PASS. This is POINTER integrity, distinct from the 21-asset full byte test above. Pass18 manifest: 23 diagnostic-only eligible, 10 unpaired, 3 blocked P17-05/P18-07/P19-07; zero final release.

## Unity 6 URP release gate

Actual import/prefab builder and signed validator are committed to own Draft [PR #11](https://github.com/C8LyNn/Model-Test/pull/11), but **not executed in Unity** in this runtime. The existing native editor QA `Assets/C01InteriorProps/Editor/Pass18NativeUnityBatchAudit.cs` must be invoked with a real Unity 6 Editor after SHA-gated staging; actual shader/material slots, hierarchies, colliders, PlayMode and clearance require in-editor evidence and independent C01-02 approval. No change to ship/corridors/doors, no merge, no final PASS.
