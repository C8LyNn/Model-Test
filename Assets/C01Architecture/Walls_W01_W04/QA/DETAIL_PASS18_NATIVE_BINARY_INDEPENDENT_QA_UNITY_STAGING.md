# C01-11 — DETAIL PASS18 / actual latest Blender4 FBX + independent binary QA + isolated Unity handoff

**Scope:** W01–W04 architectural models, **outside the 36 P15–P19 interior props**. All existing geometry unchanged, no redesign, no ship scene edits, no merge. Existing Draft [PR #22](https://github.com/C8LyNn/Model-Test/pull/22).

## Actual source / native producer receipt

Latest real Blender 4.0.2 producer output is from [successful run #41346578552](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552), GitHub artifact **#13098949702** (original artifact ZIP SHA-256 `52bcbcb53d08b587a21bcd582c1e216f640c4346518448537ebbc46cdc8e5e6c`). 4 actual `BLENDER-v400` source files, 4 real `Kaydara FBX Binary 7400`, 12 actual Blender Workbench previews and producer reimport receipt. Blender save/export/reimport **PASS 4/4** in that **executed** CI run. Not a new Blender execution in this PASS18 audit.

## NEW real Unity-preparation defect fixed in this pass

Previous `C01WallPrefabBuilder.cs` pins included only immutable original-r2 binaries and EARLIER candidate FBX SHA values. It would reject **the latest** real PASS17 Blender exports. Committed actual source change [`62fcf3752a64d735c0de680c3dd4478e3ee2a66b`](https://github.com/C8LyNn/Model-Test/commit/62fcf3752a64d735c0de680c3dd4478e3ee2a66b):
- Third explicit `Pass17Native` source variant, with **four exact new Blender-origin FBX SHA-256** pins (including **correct W02 572 triangles**).
- New isolated menu `Tools/C01/C01-11/QA Only/Build PASS17 Real Blender W01-W04 Prefabs` that imports ONLY `Assets/C01Architecture/Walls_W01_W04/QA_Candidates/PASS17_SourceRecovery/FBX/*.fbx` and writes ONLY `QA_Candidates/PASS18_Unity/Prefabs/*_QA_ONLY.prefab`.
- Fails closed before any prefab output on wrong/unhydrated SHA, triangle count (12/572/20/28), missing UV0/normals or material submesh slots. Preserves imported root/pivots, source mesh and FBX-assigned materials. Original 12-triangle W02 legacy candidate remains rejected.
- Native source/QA-only paths do not overwrite ship prefabs, existing QA output is never overwritten, preview scene used. Actual GitHub HEAD source readback **17/17 structural assertions PASS**; **Unity C# compilation/Editor execution NOT RUN** (no Unity runtime available in this executor).

## PASS18 independently executed real physical binary QA (NOT source-only)

An **independent FBX 7400 property-array decoder** reopened the actual latest 4 producer FBX bytes and 4 original immutable r2 FBX. At 1 µm spatial quantization, compared ALL real polygon surfaces using 3D coplanar surface-union symmetric differences; parsed UV0 layer / indices and per-corner split normals; reconstructed actual triangular faces, tested geometry watertightness, winding, degenerate area, bounds and source→native SHA. Read four `.blend` physical header bytes and exact SHA. Report/script are inside the attached executable ZIP, not an invented Blender or Unity test.

| Asset | Exact latest native BLEND SHA-256 | Exact latest Blender FBX SHA-256 | Original/native tris | 3D surface diff after 1µm | Normal max Δ | PASS18 offline gate |
|---|---|---|---:|---:|---:|---|
| W01 | `7918bea022a05b0676e97f1995a66cccc28745590941240f5c3efe6b4a5006dd` | `c644e95d548cafbac61cebe000d7b0fb4b584a1fe4527565ba55d4c8e0415a79` | 12/12 | 0 m² | 0 | PASS |
| **W02 detailed** | `28c71407f49d84d653a4844b82933599bf1a4083783bcd619804cdc75e9ed360` | `a23f602d8dd61a6dc61ee52af347e472f2e6f6ce546988f50409911d1b11a317` | **572/572** | 0 m² | **2.654e-6** | **PASS at 1e-5; strict 1e-6 FAIL** |
| W03 | `609c862ea8ee85c0b48a87547a37c442ab8840e3c26a8a0f7494dd7e2c7aac07` | `9dcc8feca9475626e393910b4176d8c2eadf9c645d34e32718a417a10214807a` | 20/20 | 0 m² | 0 | PASS |
| W04 | `57f62bcac28d9505d18b1f37a95f2e8494c0c0bc92a3696d3bdc5db478ef113e` | `6236dbb22a71d8ef0c8137ec263c14d59fbeda2a62eb299fe7cc05e1421dd51f` | 28/28 | 0 m² | 6e-8 | PASS |

All 4 decoded native meshes **watertight, consistent winding, nondegenerate faces, valid polygon indices and UV0 records, positive polygon area, 1 native FBX material assignment**; all 4 original-to-native 3D surfaces match at the explicit 1 µm quantization tolerance, no source-to-native silhouette loss. For W02 there are **30 bidirectional normal comparisons above 1e-6** but max Δ is ~2.654e-6; independent C01-02 must decide whether a 1e-5 tolerance is acceptable for final SHA acceptance. This is **NOT** an exhaustive inter-module junction, collider/Unity or vertex-by-vertex bitwise identity pass.

## Actually delivered physical PASS18 review package

`C01-11_DETAIL_PASS18_REAL_NATIVE_UNITY_HANDOFF.zip`: **6,263,082 bytes, 48 entries, full SHA-256 `4fcc35a9378d11b59b4b64492d4823611391e91edde41343b0991e92597af9fc`**. ZIP CRC PASS; every **47/47** manifest-listed file SHA256 checked. Freshly unpacked archive independently re-executed the FBX QA **4/4 PASS**. Contains:
- The **eight current** real producer native source/export binary files, not old candidate FBX for the active Unity stage; 4 original immutable FBX for read-only comparison.
- Four current FBX staged **at exact new Unity project paths** under `Assets/C01Architecture/Walls_W01_W04/QA_Candidates/PASS17_SourceRecovery/FBX/`.
- Twelve real Blender Workbench previews, genuine producer receipt, local numerical QA JSON and reproducible decoder.
- **Offline interactive HTML viewer** with actual current native FBX vertex/index arrays for W01–W04 ONLY, shaded/wireframe orbit/zoom/model switch; no external network, synthetic primitive or old FBX in interactive viewer. Headless Chromium UI smoke **4/4 model selections, shaded/wireframe, reset, spin, ZERO JS exceptions PASS**.
- Precisely labeled historical wrong W02 12T vs corrected native W02 572T **BEFORE/AFTER QA screenshots**, offline renderer not Blender; additional real-browser W02 shaded/wireframe screenshots. No new mesh has been authored in PASS18.

### Manual REAL UNITY6 URP gate (no false PASS)
Stage package `Assets/` into **disposable Unity 6 URP project** using matching updated C01-11 Draft PR #22 Editor source. Click `Tools > C01 > C01-11 > QA Only > Build PASS17 Real Blender W01-W04 Prefabs` (or batchmode `-executeMethod C01WallPrefabBuilder.BuildPass17NativeQaOnly`). Inspect exact SHA, imported topology, UV0, shaders/material slots, pivots, 4×4 m wall seams, W04 door opening and colliders, Editor/PlayMode logs; return evidence to C01-02 and C01-10 before integration. **Actual Unity6 C# compilation and real asset/prefab/PlayMode test: NOT RUN.** No active ship source modified.

**Release gate:** Real historical producer Blender4 export/roundtrip **PASS 4/4**; independent PASS18 local binary source geometry+UV/normal audit **PASS 4/4 at documented tolerance**, strict W02 1e-6 normal threshold **FAIL**; final C01-02 exact-native-SHA approval **PENDING**; Unity6 URP **NOT RUN**; PR22 Draft / **NO MERGE**. No impact on 36 P15–P19 acceptance denominator.
