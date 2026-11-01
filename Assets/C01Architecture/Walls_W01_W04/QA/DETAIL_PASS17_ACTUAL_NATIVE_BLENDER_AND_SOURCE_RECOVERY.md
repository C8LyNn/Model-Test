# C01-11 / DETAIL PASS 17 — ACTUAL W02 original detailed recovery and Blender4 outputs

## Ownership / immutable design
C01-11 W01–W04 architecture are outside 36 P15–19 props. **No ship modification, no new asset ID, no redesign and NO merge.** Existing [Draft PR #22](https://github.com/C8LyNn/Model-Test/pull/22), real native outputs isolated in `QA_Candidates/PASS17_SourceRecovery/`, not on protected production binary paths.

## Actual source mesh correction (W02)
- Earlier `Sources/build_wall_models.py` authoring generator produced a 12-triangle cuboid under the W02 name, discarding the original r2 technical panel. **ACTUAL FIX COMMITTED**, source generation now uses genuine r2 geometry, **288 vertices, 572 oriented triangles**, 0.2m thick and unchanged original pivot and 1×3m silhouette.
- Frozen lossless source module `Sources/original_r2_w02.py`: original r2 typed-number canonical topology SHA256 `1a0a3a6fb40902876102f7a6d6b0d4742c9b9ec852fa4a8ae79e49fc711de6e8` (corrected after real CI identified a `0` vs `0.0` JSON representation issue). Every vertex and triangle index matches original immutable authoring source **288/288 and 572/572**.
- Actual new source OBJ committed in same Draft PR: [W02 full real OBJ](https://github.com/C8LyNn/Model-Test/blob/c01/walls-11-wave02-native-export/Assets/C01Architecture/Walls_W01_W04/Sources/OriginalR2/W02_TECH_PANEL_WALL_1M_R2_AUTHORING.obj), **Git blob `37dbdf2f828c6efabce0da22bc85d26a2c8c228c`**, exact byte match against local source file SHA256 `7235114e7b41bf5a20b1d9014eddce35d7ef15c39a58fb6649b10fa69f49a965`. OBJ includes UV0/normal loops; authoring OBJ source reimport PASS, GLB preview exported from this OBJ and independently reimported with 572 triangles.
- Numerical source QA: 288 indexed vertices, 858 unique edges / **858 with incidence exactly two**, manifold/winding consistent, signed volume 0.5463396m³, **zero degenerates and zero positive-area same-facing coplanar overlaps in 41,128 candidate tests**. Re-derived source OBJ vs original immutable r2 full FBX 1716/1716 position+UV0+normal face-corner matches at 1e-6.

## Real native Blender 4.0.2 execution and artifact
**REAL GITHUB ACTIONS PASS** [workflow run #41346578552](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552), commit `808602f908e35e97fb4a3f25431030b39111d558`; `apt install blender` (v4.0.2) and Git LFS executed on assigned Ubuntu runner. Actual Blender `.blend` save, binary FBX export, source `.blend` reopen, FBX reimport, positions and vertex UV pair checks **PASS 4/4**, producer native QA output `QA/PASS17_REAL_BLENDER_ROUNDTRIP.json` result PASS, no empty steps. **No production binaries were changed.**

Actual downloaded real GitHub artifact ZIP: `C01-11_PASS17_ACTUAL_BLENDER_4_NATIVE_QA.zip`, **23 files**, exact file SHA256 **`52bcbcb53d08b587a21bcd582c1e216f640c4346518448537ebbc46cdc8e5e6c`**, ZIP CRC PASS. GitHub artifact ID `13098949702` in run #41346578552. Contains four actual BLENDER-v400 native sources, four Kaydara FBX Binary 7400 exports, twelve actual Blender workbench PNG shaded front/iso/side and all SHA+native reimport JSON. Uploaded as conversation download, not merged.

| ID | Triangles actual Blender/reimport | Actual BLEND SHA256 | Actual Blender-origin binary FBX SHA256 |
|---|---:|---|---|
| W01 | 12 / 12 | `7918bea022a05b0676e97f1995a66cccc28745590941240f5c3efe6b4a5006dd` | `c644e95d548cafbac61cebe000d7b0fb4b584a1fe4527565ba55d4c8e0415a79` |
| **W02 detailed** | **572 / 572** | `28c71407f49d84d653a4844b82933599bf1a4083783bcd619804cdc75e9ed360` | `a23f602d8dd61a6dc61ee52af347e472f2e6f6ce546988f50409911d1b11a317` |
| W03 | 20 / 20 | `609c862ea8ee85c0b48a87547a37c442ab8840e3c26a8a0f7494dd7e2c7aac07` | `9dcc8feca9475626e393910b4176d8c2eadf9c645d34e32718a417a10214807a` |
| W04 | 28 / 28 | `57f62bcac28d9505d18b1f37a95f2e8494c0c0bc92a3696d3bdc5db478ef113e` | `6236dbb22a71d8ef0c8137ec263c14d59fbeda2a62eb299fe7cc05e1421dd51f` |

## Additional independent parser numerical precision receipt (explicit limitation)
After native Blender output, additionally re-parsed original W02 r2 binary FBX versus new native PASS17 binary FBX with independent Python FBX 7400 readers. **Exact source geometry preserved, 572/572 triangles**, 1716 corresponding source corners, 360 unique position+UV groups. Recalculated Blender float normal differences **max Euclidean 2.6543168623e-6**, p99 1.37613e-6; maximum corresponding position and UV numerical delta **8.58306883e-8**. Of 1716 corners, **21** exceed normal delta 1e-6 but **none** exceed 1e-5. Consequently *strict 1e-6 normal identity FAIL*, tolerant 1e-5 numerical geometry+UV+normal **PASS** (to be reviewed independently). Coplanar surface numerical symmetric-difference 4.88496e-7m² from roundtrip quantization. Not a confirmed geometric defect or permission to call independent C01-02 full PASS; the exact tolerance decision belongs to C01-02.

## Interactive preview and other gates
- The portable source ZIP `C01-11_PASS17_W02_REAL_AUTHORING_OBJ_INTERACTIVE_QA.zip` (650,524B, SHA256 `b8c0ef67a18b93e2fa410ff025c88fd001b6b3c7efe9e05b3312d836a5256282`) contains actual current authored OBJ+glTF, source shaded/wireframe BEFORE/AFTER, an **interactive offline Canvas2D W02 viewer**, provenance and exact source-level QA. Viewer uses newly authored OBJ, NOT old FBX, synthetic user-facing substitute or remote network. Real Chromium headless visual check: zoom/rotate/mode switching, **zero JavaScript errors**, 288V/572T model visible.
- The real Blender native ZIP separately contains actual Blender workbench shaded renders, source+FBX and new binary QA.
- Unity 6 URP native prefab build and PlayMode: **NOT RUN**. Independent **C01-02 final SHA approval PENDING**. Source Blender/native producer PASS is not Unity or C01-02 final acceptance.
- Request C01-02 recheck the four **exact new FBX SHA256** and floating-point normal tolerance, then request C01-10 quarantined Unity 6 URP import; do not integrate W02 into the active spaceship or merge. W01–W04 do not increase 36-prop approval numerator.

## Actual commits (existing Draft only)
- Real exact source module: `94472811a20c79596661b3553fc57c31bad62ee5`
- Blender generator corrected & QA_ONLY: `413b986413ae954e897767db2938b96cd3f0ab24`, import safety `c84c74a2271f66948f54dadb2cab97cc5b643b06`
- Original true OBJ: `78b2311079ebbdefe9d57cc161e48dd7d4b11285`
- Checker current outputs: `23e68526619fe71dabf702b1f9837918fa1523cd`
- True Blender native reimport check: `c14f78a3839e4b6c331ed9c8b8702fd2c9742a17`
- Native workflow execution: `28ccffec9592a983eeda4cd56b796aaccf7d640a`
- Correct typed-number source identity: `808602f908e35e97fb4a3f25431030b39111d558`

**Release state: NATIVE_BLENDER_PRODUCER_PASS / C01-02_PENDING / UNITY_NOT_RUN / PR_DRAFT / NO_MERGE.**