# C01-11 — DETAIL PASS22 / WAVE22 — scoped architecture integration readiness

- **Owner:** C01-11 WALLS & ARCHITECTURE, existing Draft PR [#22](https://github.com/C8LyNn/Model-Test/pull/22), branch `c01/walls-11-wave02-native-export`.
- **Scope:** only legacy W01–W04 architectural modules. These are OUTSIDE the canonical 36 P15–P19 interior props. **No new models, no geometry/layout/ship changes, no merges, no redundant Blender exports or Unity CI reruns.**
- **Disposition:** `SOURCE_QA_PREFLIGHT_FIXED / STATIC_SOURCE_GUARDS_33_OF_33_PASS / C01_02_INDEPENDENT_PENDING / UNITY_NOT_RUN / RELEASE_HOLD`.

## Confirmed W22 safety defect and actual code repair

At W21 HEAD `b62dc79d7c5132c0554db618c5b57f60530d1462`, `C01WallPrefabBuilder.BuildSelected` executed `AssetDatabase.Refresh()` BEFORE validating SHA256 of staged FBX input files. Unity's refresh may import them and create sidecar `.meta` assets before the later byte-integrity rejection, contrary to the desired fail-closed no-unverified-import contract.

**Actual committed change:** [`338a15f5a19ad19239449c612c06a8b03e005f7b`](https://github.com/C8LyNn/Model-Test/commit/338a15f5a19ad19239449c612c06a8b03e005f7b), ONE C# file only: `Assets/C01Architecture/Walls_W01_W04/Editor/C01WallPrefabBuilder.cs`. New `PreflightSourceBytes(indices, variant)` verifies **ALL** requested physical FBX SHA before first `AssetDatabase.Refresh()`. `PreflightMeshes` retains post-import SHA check and geometry/UV0/normal/material validations; no hash pins or meshes changed. The previously written QA prefab rollback and smoke checks remain intact.

**Actually executed W22 tests:** fetched both C# files at that commit and executed **33/33 deterministic structural source-level assertions PASS**, including complete 4× SHA pins, guard ordering before `Refresh()`, subsequent source recheck, W02 rejection, UV/normals/submesh gates, isolated QA paths, no prefab overwrite, rollback, oriented collider logic, URP shader validation and fail-closed smoke result handling. Both fetched exact source Git blob IDs: builder `b0df9bb879bc53ae5e54fa2332cb2bb38c1b22e9` / smoke `87c289e9edeaae1ddfce84f211bab2ebd97b0544`. **These are STATIC checks, not compilation or actual Unity execution.** Code commit diff checked: only the intended C# file changed.

## Immutable native assets (do not duplicate export)

Genuine previous Blender 4.0.2 [Actions run #41346578552](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552) completed **SUCCESS**, 11 actual job steps; original artifact [#13098949702](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552/artifacts/13098949702) is currently listed **not expired**, 4,771,746 B, ZIP SHA256 `52bcbcb53d08b587a21bcd582c1e216f640c4346518448537ebbc46cdc8e5e6c`. Its prior documented real Blender4 source-save/export/reimport and independent local binary inspection are the historical evidence; **no new physical FBX hydration or Blender run was performed in W22**.

| ID | PASS17 genuine BLEND SHA256 | PASS17 genuine binary FBX SHA256 | Triangles | W22 |
| --- | --- | --- | ---: | --- |
| W01 | `7918bea022a05b0676e97f1995a66cccc28745590941240f5c3efe6b4a5006dd` | `c644e95d548cafbac61cebe000d7b0fb4b584a1fe4527565ba55d4c8e0415a79` | 12 | unchanged |
| W02 | `28c71407f49d84d653a4844b82933599bf1a4083783bcd619804cdc75e9ed360` | `a23f602d8dd61a6dc61ee52af347e472f2e6f6ce546988f50409911d1b11a317` | **572** | unchanged; normal Δ max ~2.654e-6, C01-02 tolerance signoff PENDING |
| W03 | `609c862ea8ee85c0b48a87547a37c442ab8840e3c26a8a0f7494dd7e2c7aac07` | `9dcc8feca9475626e393910b4176d8c2eadf9c645d34e32718a417a10214807a` | 20 | unchanged |
| W04 | `57f62bcac28d9505d18b1f37a95f2e8494c0c0bc92a3696d3bdc5db478ef113e` | `6236dbb22a71d8ef0c8137ec263c14d59fbeda2a62eb299fe7cc05e1421dd51f` | 28 | unchanged |

**Critical input distinction verified from current GitHub bytes:** PR22's tracked `FBX/W02_PANEL_WALL_1M.fbx` is a **legacy LFS pointer** (`7dfcf0fe84952e607a74845ad193acfbb9f4fc029e7f168a94a7bac2edacb78b`), NOT the PASS17 correct detailed W02 SHA `a23f602d...`. The four correct PASS17 FBX must be staged under `QA_Candidates/PASS17_SourceRecovery/FBX/` from the real handoff, not substituted by old tracked prototypes. The `Pass17Native` importer hard-pins these exact new FBX identities. Current PR22 tracked legacy Blender/FBX LFS pointers are unchanged in W22.

## Release gates / owner handoff

- **C01-11 static source / rollback readiness:** 33/33 structural source assertions PASS. No evidence of a new confirmed architecture geometry defect; **no model modification justified**.
- **Independent C01-02:** legacy W01–W04 final exact-SHA assessment and W02 normal tolerance signoff **PENDING**.
- **Unity 6000.3.14f1 URP:** real Editor compilation/import, generated native QA prefabs, scene, EditMode, PlayMode and Editor.log **NOT_RUN** in W22. Do not confuse previous Blender PASS with Unity. Legacy wall-smoke is optional after C01-10's P0 3-prop slice.
- **One owner P0 action for canonical props:** use authorized activated Windows Unity 6000.3.14f1 and run existing C01-10 command `& .\\C01InteriorProps\\Pass20\\run_real_unity_windows.ps1 -Mode Execute -ProjectRoot (Get-Location).Path` on isolated PR11 checkout as instructed by [runbook](https://github.com/C8LyNn/Model-Test/blob/c01/props-10-showcase-integration/C01InteriorProps/Pass20/UNITY6_WINDOWS_OWNER_RUNBOOK.md). No secrets in repo.
- **If C01-11 legacy smoke later explicitly authorized:** stage exact PASS17 native files from handoff into disposable Unity project and invoke `C01WallPass19UnitySmoke.RunPass19`, then preserve actual Editor log and `QA_Candidates/PASS19_Unity/Reports/C01-11_PASS19_UNITY_EDITOR_RESULT.json` for C01-02. Static code assertions do not substitute for this.

**Final:** Draft PR retained; no release, no change to 0/36 FINAL_APPROVED of canonical props. W22 owner scope completed only as isolated QA source repair and documented readiness.
