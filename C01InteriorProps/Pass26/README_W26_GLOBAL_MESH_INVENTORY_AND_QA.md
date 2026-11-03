# C01-10 — WAVE 26 | GLOBAL NON-DOOR 3D MESH INVENTORY & EXECUTED QA

**HQ:** [#36](https://github.com/C8LyNn/Model-Test/issues/36) · **Master audit tracker:** [#41](https://github.com/C8LyNn/Model-Test/issues/41) · **Authoritative 44 source model IDs:** [C01-00 Draft #42](https://github.com/C8LyNn/Model-Test/pull/42) · **C01-10 integration:** [existing Draft #11](https://github.com/C8LyNn/Model-Test/pull/11)

## Absolute invariant: doors under Claude external hold
`CLAUDE_DOORS_EXTERNAL_HOLD`. D01/D02, all G_/gate/door models assigned to Claude, door-opening W04, door/gate scripts/prefabs and old PR #19/#32 cannot be tested, modified, reimported, re-exported, rebased or merged. This register lists their **Git tree filenames only** for quarantine; no model bytes or geometry were inspected. Ambiguous lift-adjacent `SILL_LIFT_*` paths are **SCOPE_CONFIRM_FIRST**, not authorized to test. The G_* filename exclusion is a conservative safeguard, NOT proof of exact Claude ownership; C01-00 can resolve without touching mesh.

## What the new 1513 rows DO and DO NOT mean
The following THREE read-back-validated, 17-column CSV files contain **1513 file/path/version entries**, **NOT 1513 distinct canonical models**:
- [Ship V3/V4/V5 + modular historical FBX: 629 paths](W26_SHIP_MESH_REGISTER_V3_V5.csv).
- [Ship V6/V62/V64 and source mirrors: 825 paths](W26_SHIP_MESH_REGISTER_V6_V64.csv).
- [36 canonical P15–P19, 4 wall versioned paths, 9 floor/ceiling versions, 4 rail/ramp versions and 6 scene-master BLEND sources: 59 entries](W26_CANONICAL_AND_STANDALONE_REGISTER.csv).

**Immutable Git snapshots used:**
- Draft ship/compact-decks PR #40: `e6ea04ebcc249188d9fabd7cb7ac0b1ffc4711fb` — **NOT MERGED, no ship geometry change authorized**; scan includes historical V3/V4/V5 FBXs, current V6/V62/V64 source-mirror paths. 1454 `.fbx` path entries and companion `.obj` relationship where present.
- C01-11 Draft #22: `7e6b159d0742f082e836bc7a4c6b12aee75b312e`; C01-12 Draft #20: `91275215a98a8eabb2079025162ee64785953f27`; C01-14 Draft #24: `d8dec92974921855db7def9e67c19884f29f9fbe`.
- C01-03 W25 36 exact SHA ledger pinned to `e029ad5339964b496b8627ea0137564845f52492`; 8 non-door legacy canonical LFS source+FBX SHA pairs reconciled from C01-00's [W26 44-ID tracker](https://github.com/C8LyNn/Model-Test/blob/c01/w26-global-nondoor-mesh-qa-master/C01MeshQA/W26/NONDOOR_BASELINE_44.csv).

**Protection and coverage:** 64 entries labelled frozen door/gate across all three CSV, 24 lift-threshold/door-adjacent entries `SCOPE_CONFIRM_FIRST`, and 36 canonical source-identity entries. These are **path-level** counts. Generated ship FBX files have Git blob SHA-1 of their LFS pointer and a pinned commit, **NOT** a newly verified physical FBX SHA-256. Spot-checked examples show `version https://git-lfs.github.com/spec/v1` pointers; remaining generated mesh bytes and full LFS SHA are pending actual hydration. All such entries retain `MESH_AUDIT_PENDING_NOT_YET_HYDRATED`; source path enumeration alone does not prove manifoldness, UV, clearance or normal quality.

## W26 ACTUALLY RUN — real native binary QA, not a synthetic mesh test
[W26 machine receipt for 19 latest-SHA FBXs](W26_19_CURRENT_SHA_PHYSICAL_BINARY_QA.json). Reran the physical FBX7400 auditor from the earlier C01-10 archived QA work on six actual local Blender4 producer ZIPs. ZIP CRC+SHA and embedded file SHA checked. Of the available 21 signed models, **19 FBX match current C01-03 W25 full SHA exactly**: 393 genuine FBX mesh instances, 8410 diagnostic triangle equivalents, 0 malformed vertex index / repeated per-face vertex index / zero-area triangular FBX polygon / missing UV0 / missing corner normal / invalid UV0 index in the tested subset. 1414 nontriangle source polygons exist (quad/ngon-compatible source faces are **not** automatically defects). **P17-03** and **P19-01** archived copies are stale and were explicitly rejected for current-SHA signoff; the current repaired sources instead have their own existing C01-02 producer/independent QA.

These results are strictly **SCOPED_RAW_BINARY_PASS**, not independent C01-02 final, not full inter-mesh/coplanar/self-intersection audit, not image/UV stretch/shading clearance QA. Blender executable and licensed Unity Editor are unavailable in this execution host: **no new Blender edit, FBX export/reimport, render or Unity run**. No modified meshes in this C01-10 branch.

## Exact current confirmed/remaining defect queue (reuse, do not regress)
| Model | Current disposition | Correct owner/action |
|---|---|---|
| **P18-03** | Actual original hub↔fork render geometry intersects at 576/576 motion samples. Prior C01-02 accepts only **render-only bearing collider contract**, not a claim there is no visual clipping | **C01-18** real shaded/Game View z-fighting confirmation; if truly visible defect, surgical geometry correction + true Blender/FBX new SHA; **C01-02** independent QA |
| **P18-07** | True FBX latch release and corrected root/parent axis source contract PASS. **Static +1 mm depth** and **0.361 m retracted sweep** still require formal C01-01 decision; Unity untested | **C01-01** tolerance/envelope owner decision; **C01-18** maintain runtime source; **C01-02** exact SHA QA |
| **P19-07** | 18 vertex-on-edge proximity candidates, no confirmed visible mesh crack | **C01-19 + C01-02** real before/after workbench comparison and contact classification **before** any topology edit |
| **P19-08** | Two ~0.0039 mm endpoint near-hits; unknown visual effect | **C01-19 + C01-02** threshold/visual check; **no blind weld** |
| **P17-01** | Bolt corner normals shading REVIEW, not independently visible artifact confirmed | **C01-17 + C01-02** real shaded proof before editing |
| **P18-05** | **Closed for scoped native release motion**: after staged 8 mm latch retract + 2 mm lid lift, genuine FBX 23/23 and independent C01-02 23/23 swept samples PASS; original native SHA unchanged | **No unnecessary reexport**; retain Unity PlayMode HOLD |
| **P17-03, P15-07, P19-01, RMP-01** | Prior independent geometry fixes/specific intent accepted on exact current native SHA | **Do not reopen** unless a new current-SHA visual/functional defect is documented |

## Delegation without overwriting other owners' branches
- **C01-11** non-door W01/W02/W03 and generated hull/walls/junction/cabin structural variants; **C01-12** floors, ceilings, modular grids including historical export-version dedup.
- **C01-14** ramps, stairs, safety rails, lift structural pieces **only after scope confirmation if door-adjacent**; **C01-15** installations and technical props; **C01-16** lighting P16, **C01-17** controls P17, **C01-18** cargo P18, **C01-19** furniture P19. Generated V3–V64 source-path owners are **provisional by filename**, not permission to edit live ship.
- **C01-13** non-door room/corridor placement only, existing Draft #39. **C01-01** intent/tolerance and 1 m grid, **C01-02** independent actual-FBX new/current-SHA signoff, **C01-03** canonical 36/44 registration, **C01-00** triage of historical generated variants and any case involving existing live ship geometry.
- **C01-10** safe export-intake checks, URP testing only with genuine licensed Unity. First signed P16-01/P17-02/P18-01 stay SHA locked. Do not rerun previously license-blocked CI.

## Required evidence transition per asset
`INVENTORIED` → physical original BLEND/FBX SHA+Blender importer/audit `AUDITED_SCOPED` → explicit `NO_CONFIRMED_DEFECT` **OR** named measured `DEFECT_CONFIRMED` → if needed `REPAIRED_NATIVE_WITH_NEW_SHA` (true Blender save → binary FBX export → reimport + before/after shaded/wire + vertex/edge/triangle deltas) → **C01-02 independent exact-SHA test** → actual Unity Editor evidence or `UNITY_NOT_RUN`. Intentional decorative open surfaces, same-volume assembly mating, purposeful materials/UV seams and render-only bearings require separate classification, never auto-weld/decimate. Historical/unhydrated rows remain `INVENTORIED`, not `AUDITED`.

**Unity owner action only:** after authorized Unity Hub activation of Unity **6000.3.14f1** on Windows and exact signed 3 native FBX staging, run `& .\C01InteriorProps\Pass20\run_real_unity_windows.ps1 -Mode Execute -ProjectRoot (Get-Location).Path` from isolated PR11 per [owner runbook](../Pass20/UNITY6_WINDOWS_OWNER_RUNBOOK.md). No credentials in QA reports, and no Unity claims until real prefab/scene + EditMode/PlayMode XML/Editor.log/screenshot evidence. **0/36 FINAL APPROVED / NO MERGE**.

