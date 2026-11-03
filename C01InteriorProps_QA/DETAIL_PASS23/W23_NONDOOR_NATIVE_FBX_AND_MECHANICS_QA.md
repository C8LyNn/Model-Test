# C01-02 — DETAIL PASS 23 / WAVE 23 — Independent non-door QA

**Executed:** 2026-11-03. **Existing isolated QA Draft:** [PR #13](https://github.com/C8LyNn/Model-Test/pull/13) / `c01/props-02-independent-qa`. **Freeze:** `CLAUDE_DOORS_EXTERNAL_HOLD`: ALL door/gate assets delegated to Claude, including D01/D02 (outside 36-ID denominator), old PR #19/#32, imported door prefabs, hinges, materials and tools. **No door file was read, retested, regenerated, changed, or touched by this wave.** Preserve old source/hashes for an explicit later authorized comparison. C01-13's **new non-door placement QA** is that lane's own new Draft, not this C01-02 branch.

## W23 newly executed, not merely producer reports: 5 native physical FBXs

Independent offline native binary parser **actually executed** against original hydrated Actions ZIPs: ZIP CRC, full original `BLENDER-v400` and `Kaydara FBX Binary 7400` file SHA-256, FBX v7400 compressed/uncompressed `Objects/Geometry/Vertices`, `PolygonVertexIndex` negative termination, real per-corner `LayerElementUV`, UV indexing and normal arrays, finite unit-length normals, per-mesh indexed edge incidence/winding, indexed triangle area and `Objects/Model` hinge node names. Exact producer Git LFS pointer OIDs independently retrieved at current producer PR heads. **10/10 current full physical native BLEND+FBX SHA match repo Git LFS; 2/2 ZIP CRC PASS.** No Blender executable or Unity Editor was run by this C01-02 local audit.

| Original GitHub artifact | Downloaded original ZIP SHA-256 | Physical contents re-read |
|---|---|---|
| [C01-15 #41536225400, artifact #13183049341](https://github.com/C8LyNn/Model-Test/actions/runs/41536225400) | `dd23be7e7ae202259fbd29eb99f00b99849dcf9376fd3b9f35f126f68aa20a52` | Signed current P15-01/02 BLEND+FBX |
| [C01-18 #41089810123, artifact #12994285353](https://github.com/C8LyNn/Model-Test/actions/runs/41089810123) | `03daa679d31714648fd6399f2f761e3db2b0f86ba5fe6e99d34fa1b5539c7dbf` | Signed current P18-04/05/06 BLEND+FBX. **Archive also includes stale P18-07 native bytes**; those are deliberately excluded, not accidentally counted as current P18-07. |

| ID | Full current FBX SHA-256 independently verified | Actual Geometry mesh / indexed T | STATIC QA |
|---|---|---:|---|
| **P15-01** | `bff1a07223b61762e4dcb27df7ff4c91dae11d42e0695163fe17bedc6b314c5a` | **25 / 636** | **STATIC_INDEXED_PASS** |
| **P15-02** | `470fdbdfad19d6b94ee227fc546053548b709da31115fd928f07790780066590` | **34 / 760** | **STATIC_INDEXED_PASS** |
| **P18-04** | `233253cea4a872052ef87c33f79c08794885dacac4caadf276e95701d0a70803` | **9 / 348** | **STATIC_INDEXED_PASS** |
| **P18-05** | `58e33516ead13e35e8a48228045c67bd53d6caf8de01883a11625fa2961957e5` | **10 / 120** | **STATIC_INDEXED_PASS**; actual `Lid_HingePivot` node exists, **dynamic hinge sweep NOT_RUN** |
| **P18-06** | `e83be5fac79ba0d4baf57f9a4c6050a978383da4f3bd95d046b38462fbabb220` | **11 / 132** | **STATIC_INDEXED_PASS** |

All **89 distinct indexed meshes / 1,996 indexed triangles** across the five actual FBX: **0** invalid indices, missing/bad UV0 or normal arrays, mesh boundary/nonmanifold edges, erroneous indexed winding, exactly zero-area triangles or local-area-under-`1e-10` triangles. This is **indexed-mesh-only QA**; it does not prove global inter-object z-fighting, all shading directions, actual motion/PhysX/Unity or final release. All five were previously SOURCE-SHA-only/scoped-not-audited in C01-03's QA reference status; five specific static intake holes are now closed without reexport.

## W23 P0 — P18-03 mechanical assembly classification based on actual physical FBX **and current Unity prefab source**

**Current unchanged native BLEND:** `ea1b4f5cc5612f8d8ff5c3c585b9b48843659972c2371204b5d3b5c4df3a3b56`; **FBX:** `f169ab74086ee3853c14b46ac6f6199cd255cfca15d8b7cbef32c3758cde7926`. Current PR #18 HEAD `4d167a5e610c2b905360ed472e30960b735ffad5`, LFS pointer pair 2/2 MATCH. The model is still the **genuine unchanged** 63 meshes/1,780 indexed triangles.

Previously independently executed C01-02 **W22 real FBX** triangle narrowphase: all **8 moving `Hub_In/Out` versus their eight stationary fork cheeks** have actual triangle surface crossings at **576/576** tested samples (8×72 axle orientations, 5° increments); **29–33 intersecting triangle-face pairs per sample**. Positive common-solid interior witnesses originate from C01-18 source (8/8) and are consistent with physical moving/fixed FBX overlap. Rubber wheel↔frame clearance **~2mm** is a separate previous PASS and cannot overrule hub overlap.

**New W23 independently executed source-contract audit** of actual `Assets/C01InteriorProps/C01-18/Editor/BuildWave01CargoPrefabs.cs` at current immutable PR18 head, **Git blob `56a289cbd050b40ada3b7e214a22d14f96c22def`**:
- For P18-03 the builder adds exactly **six** solid `BoxCollider` components: `Cart_Shelf_0`, `Cart_Shelf_1`, four `Cart_Upright_*`. None of the four rotating rubber `Wheel_*`, eight rotating `Hub_In/Out`, stationary `ForkInner/Outer` or four `Axle` are assigned **new** solid colliders by this code.
- The builder **does not add a Rigidbody or joint / wheel rolling physics** to P18-03. Imported FBX intrinsic or externally added colliders cannot be excluded without actual Unity inspection. This is a code inspection, **not** successful runtime loading/compilation.
- **Precise classification:** P18-03 has genuine overlapping *rendered mechanical mating surfaces*, but the six-collider W01 builder itself does **not** define mutually-colliding hub↔fork physics solids. Thus those mesh overlaps are **NOT proof of a PhysX runtime wheel lock** for this builder. They also are **NOT proof of invisible/no clipping** or real functional wheel ground contact. **`STATIC_PASS / BEARING_RENDER_MATING_REVIEW / UNITY_PHYSX_HOLD` (P1).**
- **Owner C01-18:** choose and document either (A) `HUBS_RENDER_ONLY_INTENTIONAL_PRESS_FIT` with exact requirement to exclude `Hub_In/Out, ForkInner/Outer, Axle` from mutually blocking solid colliders and verify wheel Spin+Game view; or (B) a true moving-solid bearing requiring **localized axial/radial clearance fix only**, true new BLEND→FBX SHA, independent new-SHA QA. For real cart movement, supply actual wheel-ground collider/joint plan; current six frame colliders alone do not prove rolling. Do not rebuild geometry for a physics collision absent from the intended collider setup.

## W23 P0 — P18-07 state machine vs visual lock: independently confirmed **source-only visual release defect**

**Current physical BLEND** `5fd990d8153430dd4f1a8893ebef0097465a404d1b2c6bbd77777de695b3e87d`, **FBX** `858a24db4338804ee3a3a70c310cd4936e3c45f559b9c4ab81c6037add564554`; current PR #26 HEAD `7eb56b5a474b025fa4ab153e08da583404f8f080`, current LFS pointer pair 2/2 verified, **no physical changes**.

Prior independent W22 native FBX actual surface-test: fixed visible `Front_Lock`↔moving `Bin_Lid` **13 crossing triangle pairs at 0°**, **9 at 5°**, 0 at ≥10° across 23 poses (0–110°). Lock is a fixed **rendered mesh**, not merely a collider.

**New W23 inspected LIVE CURRENT actual code, with exact Git blob IDs**:
- `Assets/C01InteriorProps/C01-18-Wave02/Editor/BuildWave02CargoPrefabs.cs` blob `90baf98b228c35a83ada757cd5d7fde95f4e5775`: checks signed exact P18-07 SHA before prefab writes, demands real imported hinge + five native moving children and **4 solid colliders** (`Bin_Chassis/Bin_Lid/Base_Stiffener/Front_Lock`), adds `C01ToolBinLatchGate`. **Code existence only; native Unity prefab creation NOT_RUN.**
- `Assets/C01InteriorProps/C01-18-Wave02/Runtime/C01ToolBinLatchGate.cs` blob `ecd69c9e20b4b8cea7b1c1f8c1b3ff16dd168197`: `TryUnlock` disables `frontLockCollider.enabled`; `TrySetOpeningDegrees` requires unlocked; `TryRelock` requires fully closed (≤0.1°); `LateUpdate` restores collider according to state. A static source audit confirms these guards. **There is no `Renderer`/ `MeshRenderer` visibility toggle, `Transform.position` retraction, animation or mesh hide for `Front_Lock`.**
- **Independent result:** `LOCKED_PHYSICS_STATE_CODE_SCOPED_PASS`, **`UNLOCKED_VISUAL_LATCH_CLEARANCE_FAIL_SOURCE_ONLY`** because toggling collider cannot remove the existing visual geometry crossing at 0–5°. **It is not a claim of failed Unity PlayMode**; rather, a confirmed unimplemented visual-contract requirement in actual source.
- **C01-18 action:** add *source-only* visible latch-release (retraction animation or explicit justified hide/reveal) **before** applying hinge >0°, synchronize collider and visible state; relock only when closed and re-extend latch. Independently verify 0/5° geometry visibility and 0..110° sweep in actual Unity scene, and keep five native hinge children unchanged. Blender reexport is **not** necessary if visual release can be implemented by transform/renderer state correctly; do not change P18-04/05/06. **C01-01 +1.0mm depth tolerance owner signoff still required**; 0.341m measured vs 0.340m nominal, no documented auto-PASS tolerance.

## W22 independent model decisions inherited accurately (not falsely retested W23)

- **P17-03** `32d460d54a396d3171b639ef7656eb30fbae2c79023cdb510abeefe0428021f8`: W22 C01-02 **STATIC_PASS / 91/91 SAMPLED_MOTION_PASS**, min PivotAnchorVisual-Housing gap **6.433mm** on actual FBX. Historical P0 closed; no new producer export.
- **P15-07** `ffc0211cc73a2056b815f3a494c24ab97d3c808d7ad9eb5b472472c555fb47f2`: W22 C01-02 intentional 2×24 open one-sided front gauge faces, STATIC_PASS, no blind mesh cap.
- **P19-01** `f3b9f806f4dcaafe00f24ac22b0805bf06a49d4216cb1339460ed1be9b26a2f2`: W21 independent micro-sliver correction 2→0 on current physical FBX; STATIC_PASS, no reexport.
- **P19-07** `eb579a85355756c0d803f58ec96fac509e33788d8142390349aebbffdba50e81`: 18 vertex-on-edge candidates, visual severity REVIEW, no blind weld. **P19-08** `9de76d296482e2d302b5b0a14c30692dbdb6adacd90fcd4e022da9ab35ec658c`: near-endpoint ~0.0039mm precision review. **P17-01** `cd6a5787bb7b4c088f0af35382385e4274c85c415c60467f9a22e46fe33ef02c`: bolt normals localized shading review. No unjustified wholesale normal recalculation.

## Full 36-model release handoff and Unity

Own [36-row **W23 QA matrix**](W23_36_NONDOOR_SHA_INDEPENDENT_QA_MATRIX.csv) derived from C01-03 W22 immutable release matrix at `60714e8b7229aaee4aafa76a3bb945bbe44f8821`. **36 unique P15–P19 IDs preserved**, updated five real independent binary+SHA static results, reconciled W22 exact-SHA P17-03, P15-07, P18-03, P18-07, P19-01, and preserved earlier holdings. Current producer HEAD shifts P18 #18/#26 and P15 #25 are source/QA-only with independently checked exact unchanged native LFS pointer OIDs. C01-03 PR #27 must refresh its own canonical JSON+CSV using exact per-current-SHA decision; no declaration of global PASS.

**Unity 6000.3.14f1 URP 17.3:** `UNITY_NOT_RUN / OWNER_ACTION_REQUIRED`. The [C01-10 preflight #41540521732](https://github.com/C8LyNn/Model-Test/actions/runs/41540521732) authenticated P16-01/P17-02/P18-01 full binary bytes but **licensed Editor job SKIPPED**. No truthful Unity prefabs, actual scene, Editor.log, EditMode/PlayMode XML or screenshots. **One owner action, no CI repeat:** on licensed Windows activate Unity Hub/Editor 6000.3.14f1, isolated C01-10 PR #11 checkout, then `& .\\C01InteriorProps\\Pass20\\run_real_unity_windows.ps1 -Mode Execute -ProjectRoot (Get-Location).Path` per [existing runbook](https://github.com/C8LyNn/Model-Test/blob/c01/props-10-showcase-integration/C01InteriorProps/Pass20/UNITY6_WINDOWS_OWNER_RUNBOOK.md). Do not reveal any licensing credentials.

**Overall: `0/36 FINAL_APPROVED`, no merge/no new models/no producer edits/no ship changes/no door changes.** C01-02 release stays HOLD until full independent assembly/visual/runtime and real Unity proof.
