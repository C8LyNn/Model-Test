# C01-03 — MESH REPAIR PASS09 / actual source changes and final SHA gates

**Repo:** Model-Test · **Issue:** [#33](https://github.com/C8LyNn/Model-Test/issues/33) · **Library:** existing [Draft PR #27](https://github.com/C8LyNn/Model-Test/pull/27) · **No merge or architecture/model redesign**.

## What actually changed in existing original model source

| ID | Authored source edit (actually committed by owner) | Current authored source SHA256 | Source check | New Blender `.blend`/binary FBX |
|---|---|---|---|---|
| P17-05 | Corrected glTF LowerDisplayRail +1 mm Z in PR #23 | `cc4b0e9a7b7a78c461baca467f0ca433b81c0c60d14895531af9ddf556371378` | single JSON node transform, all other data identical PASS | NOT RUN |
| P18-01 | PR #18: 180 tris→90 equivalent quads; four corner trims receded 1 mm at caps, 32 original vertices edited | `e7eae0ca915d265d8f41676b3e6d390de5396e4eaa9ef72ded0d5ad8d92a0283` | exact face/UV coverage and targeted vertex deltas PASS | NOT RUN |
| P18-02 | PR #18: 204 tris→102 equivalent quads; six shelf lips receded ±3 mm on source Z, 48 vertices edited | `d8623bb0fe51388fe25ead63703b0868dac2549c32b14cb20f1757aa41e541a2` | source faces/UV unchanged, original triangle coverage PASS | NOT RUN |
| P18-03 | PR #18: 348 authored triangles→78 equivalent planar quads + 192 retained wheel triangles = 348 resulting triangles | `4565e7f3c38c154a28b8494c163619bbfa0883371dfe66515b6ee36d66743ef8` | 0 vertex, UV, normal, material changes; source quad equivalence PASS | NOT RUN |
| P18-05 | PR #26: producer Python Case_Bottom bounds synced to separately audited old native export | `430766db66a207034e2997fb29834d6947056ed1f7b43dfa6aefd6135d83b564` | changed source definition; native not reexported | NOT RUN |
| P18-06 | PR #26: producer Python Safety_Lid bounds synced to earlier FBX | `430766db66a207034e2997fb29834d6947056ed1f7b43dfa6aefd6135d83b564` | changed source definition; native not reexported | NOT RUN |
| P18-07 | PR #26: producer Python Front_Lock +1 mm depth separation; also chassis/handle dimensions synced to existing FBX | `430766db66a207034e2997fb29834d6947056ed1f7b43dfa6aefd6135d83b564` | source lock plane 0.170→0.171m vs lid 0.170m; actual old FBX still at 0.170m | NOT RUN |

**These seven source revisions are not seven newly repaired native Blender files.** P18-05/06 generator definition was matched to previously audited native bounds; do not automatically mark their existing FBX mismatched until exact component geometry is independently compared.

## Real SHA / version evidence

- [PASS09 36-ID machine ledger](./asset_registry_36.json): exact current producer heads, immutable prior native source SHA, actual independently hydrated historical FBX SHA where known, recent source_sha256 and quarantine flags.
- [P18 quad and lock source diffs](./verified_P18_source_changes.json): exact original OBJ SHA before/after 180→90, 204→102, 348→270 source faces, no accidental vertex/UV/normal changes in quad conversion; initial P18-07 Front_Lock 1mm generator edit.
- [P18 further updated source HEADs](./verified_P18_latest_heads.json): current P18-01/02 vertex delta source sha, newer Wave02 producer generator sha, companion parts spec sha.
- [16/16 metadata/source integrity checks](./VALIDATION_RESULT.json) PASS. **NOT** Blender/Unity execution.

## Quarantined binary proposals — DO NOT PROMOTE

- P17-05 owner-produced offline byte-level `.blend` candidate SHA `16ad0dffa17f5918e64b009086d16efc7c998703b14f2d43f6fa258bb084d440` and FBX candidate SHA `c2b8f049de4e84697980e53d0f443a77b19ce930ea6b159a10fb5b3df8695c71`. Authentic binary source editing and detailed structural tests were reported by C01-17, but Blender open/save and FBX Blender export/reimport **NOT RUN**. Draft #23 original native LFS binaries remain unchanged.
- P19-01 original FBX polygon #59 offline surgical repair candidate SHA `9dc4d6b724c4a5a4b45a04412dc5a61fe732fa1b4423a9f0c27889053960163b`. Its static parsed fan-zero count is reported 12→0; actual original `.blend` still old, no Blender save/export or independent QA.
- P19-02, P19-05, P19-07, P19-08: four existing offline FBX candidates from PASS05, still QUARANTINED. Do not replace original Blender source/export with offline byte-patched files unless rebuilt and approved.

## Independent QA and engine gates

| Test | PASS09 outcome |
|---|---|
| Source authoring changes checked | 7 asset IDs; includes generator syncs, not all are mesh edits |
| Actual native Blender `.blend` newly saved with repairs | 0/36 |
| Newly Blender-exported binary FBX validated via Blender reimport | 0/36 |
| Independently hydrated historical binary FBX available to C01-02 | 22/36 prior-source versions |
| P19 export triangulation-risk FAIL (current original FBX) | P19-01, P19-02, P19-05, P19-07, P19-08 (5) |
| P15 native FBX not independently hydrated | 7 |
| P16 absent native `.blend` and Blender binary FBX | 7 |
| Independent fully approved final model | 0/36 |
| Unity 6 URP real import/prefab PASS | 0/36, NOT RUN |

## CI diagnostic and exact owner action

- RoboRougelike B01 Blender actual workflow [ENV03 #40968934658](https://github.com/C8LyNn/RoboRougelike/actions/runs/40968934658) completed SUCCESS and **10 actual steps**; [ENV04 #40969369152](https://github.com/C8LyNn/RoboRougelike/actions/runs/40969369152) SUCCESS and **11 actual steps**.
- C01 [#41108063941](https://github.com/C8LyNn/Model-Test/actions/runs/41108063941) and [#41103820326](https://github.com/C8LyNn/Model-Test/actions/runs/41103820326) both FAILURE **0 steps**. No Blender / Git LFS / Unity installed in C01-03 executor. Account/repository-specific runner root cause unconfirmed; never automatically change budget/billing.
- **NEEDS_OWNER_ACTION:** in C01 GitHub repo owner checks Settings → Actions (General, Runners) and Actions billing/usage or provides authorized real Windows Blender 4.x + Git LFS workspace. Then producers execute genuine native Blender save/export/FBX reimport for exact source SHA and commit authentic binary output. C01-02 signs all final hashes; C01-10 real Unity import on those versions; C01-00 approves release.

## ENV01–ENV05 methodological collaboration

Read five B01 v002 Draft PRs #288/#290/#291/#289/#293. [Read-only cross-project lessons](./ENV01_ENV05_CROSS_PROJECT_LESSONS.md) cover actual Blender generation, hashes, source reopen, UV/normals/contact, modular seams, independent B01 QA and Unity gates. **No file/asset/license/permission crosses between repos.**

**Final:** 36 assets catalogued; 7 model IDs with new authoring-source changes, 6 offline binary candidate sets quarantined; 0 new Blender roundtrips, 0 full QA approvals, 0 Unity PASS; no unauthorized merge.
