# C01-02 — DETAIL PASS 21 / WAVE 21 — independent real FBX QA handoff

**Date:** 2026-11-02 (Europe/Warsaw)  
**Scope:** independent C01-02 read-only QA on real, original GitHub Actions 4.x Blender saves + binary FBX; no reexports / merges / producer edits.  
**Own existing Draft:** [#13](https://github.com/C8LyNn/Model-Test/pull/13) / `c01/props-02-independent-qa`.  
**Overall:** 36 existing IDs, **0/36 FINAL_APPROVED**, Unity6 URP actual Editor **NOT_RUN**; no prefab, Game View screenshot or test XML has passed actual Editor yet.

## Original real physical artifacts and integrity

All listed original ZIPs physically downloaded via authenticated GitHub, ZIP CRC checked, original `BLENDER-v400` / `Kaydara FBX Binary 7400` full bytes SHA256 recomputed, independently compared to **14/14 current original producer Git LFS pointer OIDs at immutable heads**. The following full ZIP hash values are measured directly from ZIP bytes, not from a producer receipt:

| Native producer immutable reference | Genuine Action + artifact | ZIP SHA256 (original ZIP physical bytes) |
|---|---|---|
| P15-04..07 PR #25 `52649126eaf23ee9861c0351ecbfbc56a2470ba8` | [run #41536480455](https://github.com/C8LyNn/Model-Test/actions/runs/41536480455), **#13184477294** | `ca235e721e1284acf2a8267f94fb408839c14cf1d5656ff4fef0b6d0aa2c4189` |
| P18-07 PR #26 `361d2a3642e38e99e1c7d4b540a8ad2748453b98` | [run #41536767833](https://github.com/C8LyNn/Model-Test/actions/runs/41536767833), **#13184427833** | `08c7c62a18b52ee2edf83a6a1e01fdf0337991f5640e5007349989166750b74e` |
| P19-01 PR #15 `dece710d3672d8eb4ef4183eb3f8657ea6790b21` | [run #41537471598](https://github.com/C8LyNn/Model-Test/actions/runs/41537471598), **#13184379191** | `c3236d8c86863e440ff8f691b9b3c0cf31ad0e4ba229cf889947cc57cb35c350` |
| P17-03 PR #17 `ece6f7ea79bf531fa9c4500121d51701cea0cc6b` | [run #41532763700](https://github.com/C8LyNn/Model-Test/actions/runs/41532763700), **#13182807424** | `18870843652d600212079c82e10b746a6f07c84ec3d4a49dcd552b96fb09e08e` |

## Individual real FBX SHA + independent geometry outcome

Independent decoded FBX7400 `Objects/Geometry/Vertices`, `PolygonVertexIndex`, `LayerElementUV`/UVIndex, `LayerElementNormal`, mesh/Model Connections and parent hierarchy; checked polygon winding, mesh-level closed/boundary/nonmanifold, finite normals / UV indexes and strict sub-`1e-10m2` micro-area triangles. **FBX Geometry objects != Model mesh instances** when instancing: report the correct denominator.

| ID | EXACT measured current binary FBX SHA-256 | Unique Geometry / instances / indexed triangles | Independent QA / disposition |
|---|---|---|---|
| P15-04 | `58252505554c65354f9ebce7e3264868d3ff7a57c850d16323e71e6356c5ce04` | 24 / 24 / 1740 | **STATIC_TOPOLOGY_PASS**, no moving element; Unity HOLD |
| P15-05 | `5d254249234c100ca2e7c0b4d65fe8ed8bc366f275d4718b4d90bac416d3da5e` | 9 / 9 / 4512 | **STATIC_TOPOLOGY_PASS**, no moving element; Unity HOLD |
| P15-06 | `e48b943e7926a3d62e3f956f1b1bc59218dbe310837d179dfbbfee435001f448` | 33 / 33 / 7356 | **STATIC_TOPOLOGY_PASS**, no moving element; Unity HOLD |
| P15-07 | `ffc0211cc73a2056b815f3a494c24ab97d3c808d7ad9eb5b472472c555fb47f2` | 21 / 21 / 5420 | **STATIC_TOPOLOGY_PASS_WITH_GAUGE_SURFACE_REVIEW**, 48 boundary edges on two decorative face meshes; Unity HOLD |
| P18-07 | `858a24db4338804ee3a3a70c310cd4936e3c45f559b9c4ab81c6037add564554` | 10 / 10 / 120 | **STATIC_TOPOLOGY_PASS / LATCH_MOTION_HOLD**; see exact motion below |
| P19-01 | **`f3b9f806f4dcaafe00f24ac22b0805bf06a49d4216cb1339460ed1be9b26a2f2`** | 4 / 4 / 470 | **STATIC_TOPOLOGY_PASS**, historical micro-sliver HOLD **CLOSED for current SHA**; Unity HOLD |
| P17-03 | `775b1e6a0024c69285d9fb9e885f35bc2a55deb4be787acc9ad3c2d3ebe8408f` | 13 reusable Geometry / 20 mesh instances / 280 unique, 464 instanced triangles | **STATIC_TOPOLOGY_PASS / P0 MOTION_FAIL**; new post-repair anchor defect still exists |

**Static integrity details:** Zero invalid triangle indices, UV0 index errors, nonunit/malformed normal arrays, nonmanifold mesh edges, bad index-edge windings or exact degenerate triangles in 7 tested FBX. **P15-07 exception:** `Gauge_Face_0_MESH` + `Gauge_Face_1_MESH` each has precisely **24 boundary edges**; other 19 meshes have zero. Flat open gauge dial surfaces may be *intentional single-sided decals*, not proved broken manifold. Do not indiscriminately weld. **Owner C01-15** to confirm explicit front-face/backface visibility policy in URP before complete static visual approval.

### P19-01 real microscopic repair independent comparison

Old authentic producer FBX SHA `e2e0bb9e095c1daed87e407814e88f8788cf503ab705d3e34513879038bcd559` (previous genuine original Action artifact) versus latest physical FBX `f3b9f806f4dcaafe00f24ac22b0805bf06a49d4216cb1339460ed1be9b26a2f2`:

- Same 4 geometries / 470 triangles, zero invalid indexes/UV0/normals/boundaries after.
- `Cube.001` old triangles `[3,106,107]` area `6.9917405199e-12 m²`; `[88,87,13]` `2.4334534388e-11 m²`, both below `1e-10 m²`.
- Current `Cube.001` minimum triangle area **`6.2553072722e-9 m²`**; **0/470** under that threshold. Fix verified, no new export necessary.
- Genuine source artifact actual **950×740 Blender Workbench before/after SHADED and WIREFRAME PNG** read via PNG decoder; each respective before vs after has **pixel-identical image content** (while PNG byte hashes differ). This is evidence no visible change at those captures, **not Unity visual QA** and not evidence that geometry was unchanged.
- Current BLEND SHA `b4c695f3731ba1cfc575134f41ac795faedbf23ec4cfb58daaeb8bc44b8d8e98`; exact current FBX matching LFS verified.

### P18-07 real hinge / latch discrete motion audit

New native BLEND SHA `5fd990d8153430dd4f1a8893ebef0097465a404d1b2c6bbd77777de695b3e87d`. Current FBX Model graph now **actually contains** a named `Toolbox_LidHinge` Null transform; its five actual moving mesh children: `Bin_Lid`, `Lid_Label`, `Handle_Post_L`, `Handle_Post_R`, `Handle_Grip`. The W20 **missing hinge/housing handle** issue is closed at this new SHA — do not quote prior old FBX `38d93a…` verdict as current.

Independent world-space real FBX mesh narrowphase: apply full parent-local FBX transforms, root FBX -90° X rotation, 100× FBX unit scale and inverse cm→m, rotate hinge about its physical local **-X** axis for **23 positions at 0,5,10,...110 degrees**, count strict two-sided segment–triangle crossing pairs between `Bin_Lid` and static `Front_Lock` / `Bin_Chassis`:

| Hinge opening angle | Lid–Front_Lock intersection triangle pairs | Lid–Bin_Chassis pairs |
|---|---:|---:|
| 0° | **13** | **10** (closed seam) |
| 5° | **9** | 0 |
| 10°..110° | **0** | 0 |

**Actual dimension of current FBX** Unity-oriented bounds: 0.560m wide × 0.380m high × **0.341m depth**, versus nominal 0.340m depth; +1mm requires C01-01 explicit tolerance disposition. **Independent verdict `STATIC_PASS / MOTION_HOLD_LOCKED_LATCH`**. Contacts while latch is engaged at 0 and 5 degrees may be intentional *locked seam*, but user cannot open a mechanically engaged locked lid unless a clear **unlock/release state and ordering** is implemented/validated. No automatic weld, no blanket hinge PASS, Unity/PhysX NOT_RUN. Owner C01-18 for lock state/clearance policy if design requires moving while locked; C01-01 for 1mm tolerance.

### P17-03 actual moving visual anchor still FAILS after latest known repair

Same physical producer SHA `775b1e6a0024c69285d9fb9e885f35bc2a55deb4be787acc9ad3c2d3ebe8408f` on current PR17 immutable head (no later corrected native file in inspected W21). Independently decoded real FBX parented `PivotAnchorVisual` under functional `LeverPivot`, applied 19 physical X-axis positions from -45..45° with 5° steps, counted real segment-triangle crossing pairs versus fixed `Housing`. **8/19 sampled positions FAIL: ±30°, ±35°, ±40°, ±45°**, **7–9 crossing triangle pairs at each angle**. The repaired shaft+TopCap and shaft+LeverSocket clear for all 19 positions (0 crossings). **P0 MOTION_FAIL / producer C01-17 targeted reshape/reparent moving visual anchor without relocating functional LeverPivot**, Blender4 native save, binary FBX reimport, new SHA then exact recheck. Full continuous sweep and Unity PhysX NOT_RUN.

### Other previously open holds — conservative classifications

- **P19-07** current unchanged native FBX `eb579a85355756c0d803f58ec96fac509e33788d8142390349aebbffdba50e81`: W19 physically measured **18** vertex-on-nonadjacent-edge candidate relationships and no index-manifold defect. Actual producer Blender closeup PNG read: no unambiguous macroscopic open crack can be concluded from a single static shaded image. **REVIEW/HOLD**, do not automatically weld, request targeted visual overlay + Unity actual proof.
- **P19-08** native `9de76d296482e2d302b5b0a14c30692dbdb6adacd90fcd4e022da9ab35ec658c`: old W19 2 near-endpoint contacts at ~0.0039mm are precision screening observations, not proven real open gaps. No reason to rebuild from these alone; **static scoped PASS with Unity visual HOLD**.
- **P17-01** `cd6a5787bb7b4c088f0af35382385e4274c85c415c60467f9a22e46fe33ef02c`: prior W19 32/708 near-perpendicular corner normals in reused bolt Geometry, valid UV/normal indexes; actual original native Blender shaded closeup exhibits no indisputable macro bolt failure at that resolution. **Shading-specific REVIEW** (targeted inspection, no bulk normal recalculation).
- **P18-03** hub/fork/axle native mating contacts remain source-supported bearing/interference classification needing actual collider semantics. Rubber vs rigid frame independent prior positive 2mm gap scoped PASS; dense hub contact counts alone are not proof of faulty rolling geometry; Unity PhysX NOT_RUN.

## Exact 36-row gate and Unity handoff

[Own independent current 36-ID SHA/disposition matrix](W21_36_EXACT_SHA_C01_02_QA_GATES.csv), built from C01-03 latest pinned W20 36-ID source plus **corrected current P19-01 physical SHA**. C01-03 canonical W20 CSV at commit `3e4049195264f6c7bfa39336be447c08abda00c5` **still contained OLD P19-01 FBX `e2e0bb9e…` although latest producer FBX is `f3b9f806…`**. Own QA W21 entry uses the newly independently verified correct full source pair SHA and artifact; C01-03 must reconcile canonical matrix, not overwrite latest with older evidence. W21 checked 7 exact current .blend+FBX pairs / **14 full physical SHA + 14 pointer SHA**; prior C01-03 reported 36/36 physical native candidates overall, but that alone is not 36 independent functional QA PASS.

**Unity:** C01-10's latest actual Windows Actions checked 3 genuine signed FBXs P16-01/P17-02/P18-01, but only preflight. **No Unity licensed Editor run, no 3 actual prefabs/scene, EditMode/PlayMode, Editor.log/Unity screenshots**. The owner's **single required next action** is to activate authorized Unity 6000.3.14f1 in Unity Hub on the licensed Windows machine and execute the already prepared [owner Windows runbook](https://github.com/C8LyNn/Model-Test/blob/c01/props-10-showcase-integration/C01InteriorProps/Pass20/UNITY6_WINDOWS_OWNER_RUNBOOK.md); C01-10 must publish real Editor evidence before any final pass. Never post secrets/license.

**Final:** 0/36 FINAL_APPROVED. All producer PRs remain Draft / NO MERGE. No new model IDs, no ship layout changes, no redundant Blender exporters.
