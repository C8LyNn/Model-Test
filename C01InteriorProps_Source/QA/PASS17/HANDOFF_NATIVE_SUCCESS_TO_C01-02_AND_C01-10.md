# C01-17 — DETAIL PASS17 — REAL BLENDER4 SOURCE→FBX FIXED / QA HANDOFF

**No new model IDs, no vessel changes, no unauthorized merge.** Repaired real Blender export pipeline after diagnosed fail of C01-17 previously on `qa_gltf.py`'s invalid unique-mesh==instance assertion and single-buffer/index-only assumptions. Replaced with actual glTF parent-hierarchy T×R×S and buffer validation. **Success**: [real CI #41347796593](https://github.com/C8LyNn/Model-Test/actions/runs/41347796593) completed all 12 stages: glTF static, actual Blender 4.0.2 native saved .blend, real binary FBX, manifold topology PASS03, Blender-origin FBX reimport + UV0, strict PASS04 source triangle compare, original AFTER Blender shaded/wireframe renders, upload-artifact, Git-LFS push.

## Physical actual native outputs, verified against LFS and artifact

| Asset | Mesh objects | Source and FBX triangles | BLEND SHA256 | FBX SHA256 |
|---|---:|---:|---|---|
| P17-01 | 25 | 380 | `7e7fb3911d7f0d061dfa202804a42b18ef0d99510f95e6cc1b6b42d0c53c17eb` | `cd6a5787bb7b4c088f0af35382385e4274c85c415c60467f9a22e46fe33ef02c` |
| P17-02 | 38 | 536 | `9039029aece72ad4416ebe162c55141c8a3123572142423235e61e7865d1d756` | `db49121a520f16ca636626795550b83e8a4df94ded56a7ccb76308520bb7c3f6` |
| P17-03 | 20 | 424 | `c06f6388a948fa0264fae1278c7753587e7eae746b9e58748e642f458b65898d` | `a48c9dde921c25f61cef175896c5b7fde997392fc898784e16bb9612f39a4520` |

Downloaded original workflow [artifact #13099877855](https://github.com/C8LyNn/Model-Test/actions/runs/41347796593), as real physical user ZIP `C01-17_PASS17_BLENDER4_SOURCE_FBX_REIMPORT.zip` SHA256 `2ddab5c829475d29a8e22cdde37861de43e4e2eaf9f67f2dc46c25f86afccd51` (44 files, CRC PASS). Verified all six actual hydrated binary magic signatures (`BLENDER-v400`, Kaydara FBX Binary 7400), SHA-256 bytes equal both producer Blender report and all six current Git-LFS pointer OIDs. A **separate locally executed binary parser** independently counted 83 mesh instanced objects / 1340 indexed triangles, 0 index errors, 0 degeneracies, UV0/normal arrays present; noted 7+ FBX geometry instances may share one binary Geometry resource correctly. Blender-origin independent source FBX triangle compare 0 missing/extra/winding errors, 0 T-junctions, zero same-facing coplanar candidates. Existing P17-01 keyboard guides and Backbone remain repaired; P17-02 screws supported; P17-03 LeverPivot preserved in Blender and FBX.

## Real latest-source interactive 3D without stale FBX

[Current GLTF interactive viewer (embedded exact authored 3 binary-backed GLTF files)](../../Previews/PASS17_C01-17_INTERACTIVE_CURRENT_GLTF.html). Fully self-contained offline HTML; 25+38+20 mesh instances. Per-mesh shading/materials, drag orbit, wheel zoom, wireframe, bounds, select/pick real submesh, export PNG. The HTML directly embeds exact current GitHub `P17-01.gltf` blob `e0df06d260a955fe926f7e0279068bf2a2e6a6b5`, P17-02 `d80a67af140e434b983104aaec0078f9cf5bd66f`, P17-03 `0cf58dfd446c23f4077b59aea47d93f873d2db6e`, including original POSITION arrays + indices and parent quaternions. **No historical FBX, no proxy geometry, no remote CDN**. Download and open in browser if GitHub displays HTML source instead of executing it.

Also user-side `C01-17_PASS17_INTERACTIVE_SOURCE_VIEWER.zip` SHA256 `2d24531c27a6e76bd9bad76be1c16df581e45b8a602f4e39a3419c17b034d68c`, 10 physical files: interactive HTML of current source OBJ world-space meshes, 3 source world-OBJs, separate independent QA script/JSON and 3 actual old/new Blender SHADED+WIREFRAME side-by-side images.

## Required independent release handoff

**Blender native export COMPLETE / producer Blender QA PASS.** Exact native SHA assigned as above. **Independent C01-02 final signoff PENDING; Unity6 URP import + prefab/PlayMode NOT RUN**. C01-10 must import freshly Git LFS-hydrated new FBX for 25/380, 38/536, 20/424, verify moving `LeverPivot`, materials and colliders. No merge before separate C01-02 and actual Unity gates.

Machine receipt: `C01InteriorProps_Source/QA/PASS17/C01-17_NATIVE_BLENDER4_FBX_INDEPENDENT_VERIFY.json`.
