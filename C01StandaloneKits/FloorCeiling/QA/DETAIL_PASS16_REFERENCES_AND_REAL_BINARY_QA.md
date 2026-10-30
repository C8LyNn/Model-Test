# C01-12 — DETAIL PASS16 / Floor & ceiling construction references and strict native QA

**Owner:** C01-12, Draft PR #20. **Date:** 2026-10-30. No model ID, ship-architecture, geometry, native FBX, pivot, or merge changes. This file is *actual technical research & material candidate documentation*; there are new independently generated PNG material candidates in the ChatGPT handoff ZIP, **not** yet assigned in Blender/Unity.

## 5 primary manufacturer references — construction principles (no geometry/CAD/image copied)

1. **Tate Access Floors** — https://www.tateinc.com/content/dam/tate/products/access-floors/tate-accessfloors-installguide.pdf — Panels, load-transferring edge stringers, locating tabs and fastened pedestal head. For the EXISTING floor F01/F02: keep 1×1×0.2m envelope. Do not add physical raised pedestals or alter ship geometry without a new design approval.
2. **Grating Pacific metal grating fastening** — https://gratingpacific.com/product/fasteners/ — Saddle clips, countersunk lands, weld lugs, nonfloating mounting. For C01-12: retain flush walking face; captive fixing impressions are **NORMAL-MAP-ONLY** visual candidates (not an assertion that functional screws physically exist).
3. **USG DONN DX/DXL accessible ceiling grid** — https://www.usg.com/content/dam/USG/pdpmovedocuments/donn-dx-dxl-concealed-acoustical-suspension-system-installation-guide-en-AC3335.pdf — Main/cross tees, wall molding and removable panel splines. For existing C01: panel-edge access marking concept only; no new fictional hangers/spacecraft structural changes.
4. **McNICHOLS steel plank-grating fasteners** — https://www.mcnichols.com/resources/plank-grating/getting-started — Mid-span clips and splice plates; panel connection and anti-slip surface material logic. For F01/F02: restrained brushed-steel microdetail in roughness/normal, no physical bumps that would disrupt walking clearance.
5. **USG DONN DX/DXL ceiling system** — https://assemblies-tools.usg.com/content/usgcom/en/products/ceilings/grids-trim/acoustical-suspension-systems/donn-dx-dxl-concealed-acoustical-suspension-system.html — Main tee/cross tee/wall profile load path. Model any *actual* hardware only after matching the receiving architecture & obtaining approval.

**IP and interpretation:** use technical construction principles only. No vendor CAD, mesh, branded product graphic, licensed photo, or 1:1 design copied.

## EXECUTED physical native-binary recheck (unchanged PASS03 source, not new Blender render)

In PASS16 re-extracted 3 existing verified real .blend + 3 real Kaydara FBX Binary 7400 from prior original Blender 4.0.2 PASS03 archive. Re-ran exact physical-byte FBX parser for indexed geometry, per-corner UV0, normals, normals-vs-winding, connectedness, manifoldness, triangulation, material IDs, and SHA256. **3/3 TRUE HISTORIC FBX STATIC PASS**: each 16V/28E/14 quads/28 tris, watertight, one connected component, 0 UV0/normal/degenerate/winding/edge failures.

| ID | Original real Blender .blend SHA256 | Original real binary FBX SHA256 | Envelope local FBX |
|---|---|---|---|
| F01 | `98d5713e35d60de427ff63d7917b8af6d592dd76180ea1166b45a093b724ffb1` | `077a2b04520b116d0a28f62d78f8a75b67354a59f528a8814417207d077f24aa` | X 0..1 Y -1..0 Z -.2..0m |
| F02 | `1110a109d3a4580bd472d0cb415eb48c555dc249d947b17f2fc7335fec04adf4` | `c0bb15467d3657d501e8d7516457bdba08cea6addace9079a1fa291a45c31346` | SAME geometric vertices/faces as F01; 1 face differs by material ID |
| C01 | `3dfde4463b3eddae61f275bedccdbafd24bb804a5621830b46f6e050a4c90e2f` | `28a6af0913dc18b787b2833a1e9d0b62260917c92765abc586e6e501600de164` | X 0..1 Y -1..0 Z 3..3.2m |

## PASS16 MATERIAL detail candidates actually generated OFFLINE

New original procedural content: **9 physically saved 512×512 PNGs** = base color, OpenGL-style tangent-space normal, roughness for each F01/F02/C01, plus **3 new comparative technical preview boards**. Real archived Blender PASS03 shaded/wireframe views included for honest geometry reference; AFTER comparison shows **material sample only**, NOT a Blender AFTER render. Source generator and per-file SHA256 manifest bundled in ChatGPT-delivered 38-file ZIP (bytes **10,658,631**, archive SHA256 `bf19d6c0468849a60b598a7f44d22409ac768b7ff10a60e15968fceb87464880`, ZIP CRC PASS). No binary files have been committed to GitHub from this C01-12 turn; the handoff ZIP is a chat attachment.

**Gate HOLD:** actual UV0 face rotation and F02 mark semantic consistency, normal-map green-channel convention, correct sRGB/linear channels, mipmap edge seam, UV clipping, URP Lit import and render need **native Blender/Unity** review. No PBR map assigned to the real current .blend yet. 0 newly saved .blend / FBX, no fake native PASS.

## Independent current producer SOURCE graph and budget note

Current C01-18 Draft #18 commit `60c582cc74bf1401baed4f7d46c99d75dd3efab1`: direct full-OBJ v/vt/vn/f reparse and bi-directional triangle-edge intersection graph of all new parts **3/3 source static contact PASS**:
- P18-01 source Git blob `dc1ad53e6651a091f9bb193b9baed568a3a7aa60`, **43 parts / 868 triangles**, no detached parts; +6/+184 vs C01-12 pinned PASS15 producer source commit `681fc52d2159ac774abf1f48efd7b89965d1afe8`.
- P18-02 Git blob `f6ba1600294380416b567b443e328adccc29c270`, **55/1172**, no detached parts; +8/+160.
- P18-03 Git blob `259d3687a7968172f275410cf49e9d66d479c8ca`, **61/1724**, no detached parts; +8/+192.
- **TOTAL 159 parts / 3764 triangles; +22 parts / +536 tris** compared to the exact pinned prior SHA. Each *new* part touches an actual existing support triangle. **All original OBJ content is an exact byte-string prefix of the PASS16 source** (the new parts are appended). Any producer report citing +10 parts / +248 triangles must state a different intermediate baseline; don't mix reference commits.
- 0 invalid original OBJ v/vt/vn corner references, 0 triangle zero-area, 0 UV0 collapsed triangles, 0 detached new parts. These tests DO NOT certify absence of all overlapping hidden faces, z-fighting in the import, dynamic wheel pivot/collision or global Unity geometry.

**Floor-compatible footprint:** existing P18-03 local Y-up ground at 4 wheels; original F01/F02 FBX local Z-up floor top at Z=0. Must apply correct FBX/Unity axes/pivot; do not visually align raw coordinates. Reference-inspired details belong to owner C01-18, not C01-12.

## Strict acceptance status

- `REFERENCE_RESEARCH=PASS (5 verified manufacturer links)`
- `HISTORIC_REAL_NATIVE_BINARY_FBX_STATIC=PASS 3/3`
- `NEW_PROCEDURAL_PBR_TEXTURES=9 SAVED (OFFLINE candidate)`
- `C01_18_NEW_DETAIL_SOURCE_MECHANICAL_PREFLIGHT=PASS 3/3`
- `NATIVE_BLENDER4_AFTER_SAVE=NOT RUN`, `NATIVE_BLENDER_FBX_NEW_EXPORT=NOT RUN`
- `INDEPENDENT_FINAL_FBX_36=NOT APPROVED`, `UNITY6_URP=NOT RUN`
- `NO_NEW_MODEL_IDS, NO_SHIP_CHANGE, NO_UNAPPROVED_MERGE`.

**Execution blocker:** this accessible host has no `blender`, `bpy`, `git-lfs`, or Unity. Latest C01 workflow (#41138429511) failed without any executed test steps. **NEEDS_OWNER_ACTION** provide authorized Blender 4.x + Git LFS + Unity 6 host or restore C01 repository runner eligibility, with proper budget/security review. Don't rerun blind or claim a completed export.
