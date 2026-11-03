# C01-02 — DETAIL PASS25 / WAVE25 — Independent non-door QA

**Executed:** 2026-11-03. Existing isolated [Draft PR #13](https://github.com/C8LyNn/Model-Test/pull/13). **STRICT:** all Claude-owned D01/D02/doors/gates and frozen old PRs #19/#32 completely untouched, including testing, exports, assets, scripts, materials, prefabs and history. **No native geometry edits / no new models / no unauthorized merge.**

## Scope and method (what really ran)
- Independent **read-only full-byte BLEND/FBX7400** SHA verification from previously downloaded *actual* original Blender Actions ZIPs (not Git LFS pointer content), followed by decoding actual indexed FBX7400 mesh geometry, real model hierarchy and transformations. Native sources remained unchanged.
- Independently executed **world-space triangle–triangle crossing** tests at physically reconstructed hinge angles, with precise root-to-parent axis math of latest production C# `TransformVector` then `InverseTransformVector`, not only producer 50/50 offline tests.
- W25 independent P18-05 staged-candidate motion test on the exact original FBX, **23 actual 5° hinge configurations** and separate negative controls; 0-release untouched FBX previously independently failed W24. A Blender4 authoring search by C01-18 has separately actually run, but **no P18-05 correction was committed to native or runtime** as of inspected PR26 HEAD `5a90dab4d98ec600b95a56ee0d4006d24b87fa66`.
- Local exact 3-FBX + 3-BLEND source bytes, Python source and detailed per-pose JSON packaged in `C01_W25_INDEPENDENT_QA_EVIDENCE.zip` SHA256 **`3f1c1039276765a5a8cb10a5d5c6d57d94e01061c27c2d130154ab007ab907ef`**; no Unity Editor or Blender executable was invoked by independent C01-02. Original source proof from [P18 W01 Blender Action #41344872313](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313), [P18 W02 Blender #41089810123](https://github.com/C8LyNn/Model-Test/actions/runs/41089810123), [P18-07 Blender #41536767833](https://github.com/C8LyNn/Model-Test/actions/runs/41536767833).

## P18-07 — new independent current-source axis contract ACCEPTED (scoped)

**Exact unchanged full binary FBX SHA256:** `858a24db4338804ee3a3a70c310cd4936e3c45f559b9c4ab81c6037add564554`. **BLEND:** `5fd990d8153430dd4f1a8893ebef0097465a404d1b2c6bbd77777de695b3e87d`. Latest producer #26 HEAD `5a90dab4d98ec600b95a56ee0d4006d24b87fa66`; **latest actual production code blob `568e7eb2b8f3f54284d01c3e452ceb96a93122c7`** is byte-identical to producer's offline-compiled [50/50 PASS #41631548847](https://github.com/C8LyNn/Model-Test/actions/runs/41631548847). Producer test is Mono + UnityEngine doubles, explicitly NOT licensed Unity runtime.

**Independently reconstructed true FBX model parent**: `Front_Lock` direct child of `P18-07_Root`, original root X rotation **−90°**, no new native mesh. Component on Unity prefab wrapper root uses:

```csharp
Vector3 worldRelease = transform.TransformVector(rootSpaceReleaseOffset);
retractedDeltaInLockParent = originalLockParent.InverseTransformVector(worldRelease);
```

For wrapper root identity and true signed FBX root −90°: `rootSpaceReleaseOffset=(0,0,+.020)m` maps to **actual `Front_Lock` parent local `(0,−.020,0)m`**, exactly previous independent physical release witness. This mapping is also mathematically frame-invariant for arbitrary rigid wrapper/parent rotation if Unity represents those transforms consistently. **Independent actual signed FBX 23-pose negative-X lid test:** at fully retracted correct delta **0/23 positions intersect `Bin_Lid` and visible `Front_Lock`** over 0→110°. Old buggy direct child-local +Z has **13 pairs @0° + 11 @5°**; current corrected mapping has **zero**. External sender's previous P0 **source-axis issue CLOSED at current executable code blob**.

**Staged retraction** (lid stationary, exact original physical FBX): 0/2/4mm → 13 triangle contacts, 6/8/10mm → 11, **12/14/16/18/20mm → 0**. Current `TryUnlock` delays lid rotation until complete 20mm visible retraction; `Tick` keeps latch solid during partial travel; `TryRelock` requires closed lid. Actual visual sliding and full Unity scene collision remain **UNTESTED**, and the resting/partial *engaged* contacts should not be misrepresented as an already clear intermediate mechanical passage.

**Scoped verdict:** `STATIC_PASS / SOURCE_AXIS_CONTRACT_PASS / NATIVE_FULLY_RELEASED_HINGE_CLEARANCE_PASS / UNITY_EDITOR_NOT_RUN`. **C01-01 per-asset dimensional exception still pending**: actual closed depth **0.341m** vs nominal **0.340m** (+1mm); full unlocked latch swept depth **0.361m**. Both distinct envelopes must be considered in real non-door placement clearances; no project-wide tolerance waiver and no final release.

## P18-03 — wheel physical source geometry consistent with latest visual-only code, actual rendering remains HOLD

**Exact original full FBX SHA256:** `f169ab74086ee3853c14b46ac6f6199cd255cfca15d8b7cbef32c3758cde7926`; **BLEND:** `ea1b4f5cc5612f8d8ff5c3c585b9b48843659972c2371204b5d3b5c4df3a3b56`. PR18 HEAD `6f178a17a566294ef0be7654b2dee516062bb9b1`. Runtime C# exact blob **`f7a9bface308f94f01d0d805d8cd53163fd8d4a1`** matches the version producer executed in non-Unity [39/39 offline mock #41630296188](https://github.com/C8LyNn/Model-Test/actions/runs/41630296188).

**Independent native FBX physically measured all four rubber wheel meshes:** `Wheel_LB/LF/RB/RF` each has **48 triangles**, axial local-X thickness ≈**0.060m** and exact Y/Z diameter ≈**0.210m** → **radius 0.1049999967m**, matches source `radiusMeters=0.105f` and local X spin. Source `LateUpdate` projects root delta onto `transform.forward`, ignores side slide and teleport (>2m/step), records signed accumulated roll; `Configure` validates four original named pivots and nested two hub children; builder exact signed FBX SHA preflight and six cart shelf/upright body colliders, no wheel/fork/hub colliders. **Current source-contract radius/axis/collider mapping STATIC_PASS**, not a simulation of game wheels or actual imported FBX.

The previously confirmed **8 metal hubs ×72 angles = 576/576 real triangle crossings into fixed fork seats** remain, by intentional visual-only design. They can visibly clip or z-fight; absence of hub colliders in builder does NOT prove visual appearance, rolling PhysX or independent 360° in-engine tests. **Verdict:** `VISUAL_ONLY_BEARING_SOURCE_CONTRACT_PASS / RENDER_CLIPPING_REVIEW / UNITY_PHYSX_NOT_RUN`. Do not reexport original correct wheel mesh solely for a non-existent wheel PhysX collision.

## P18-05 — actual original Blender/FBX search gives a clean candidate, NOT an implemented repair

**Exact unchanged full FBX SHA256:** `58e33516ead13e35e8a48228045c67bd53d6caf8de01883a11625fa2961957e5`; **BLEND:** `5f98b9e34f346df3ef133e30243aee5b26dc45032c415d643490d00dbdd22f21`. 10 mesh/120 indexed triangles, actual `Lid_HingePivot`. C01-18 physically executed **[real Blender4+original FBX hinge search #41634071887, artifact #13230031707](https://github.com/C8LyNn/Model-Test/actions/runs/41634071887)**, result under producer PR26 `QA/Pass25/P18-05_ORIGINAL_NATIVE_BLENDER_FBX_HINGE_RELEASE_SEARCH.json`; no native/source fix, FBX exports=0, mesh changes=0. Producer's Blender vs FBX BVH *baseline triangle pair counts differ* (e.g. 44 vs 42 at rest), so source/FBX counts must not be treated as numerically identical.

**Independent C01-02 strict indexed FBX narrowphase reproduced** source proposal on the original FBX, all actual 23 hinge positions `0°,−5°,...,−110°`:
1. Move **fixed `Front_Latch_L/R` 8mm along original Blender −Y**, before lid movement.
2. Move `Case_Lid`, `Lid_Accent` **plus all THREE actual original `Carry_Handle_Rail/Stem_L/Stem_R`** together with **+2mm Blender Z lift**, then rotate the FIVE mesh parts rigidly about `Lid_HingePivot` around authored **−X**.
3. Result: **0/23 sampled configurations with any moving↔stationary actual strict triangle crossing**. The 8mm latch retract has a margin: at rest with handle moved together, 0–4mm latch retract still shows 20 indexed contact pairs against the lid, while ≥6mm shows 0 (tested 2mm increments).
4. Negative control: move **lid alone** while leaving handle stationary: **20 pairs at 0°, 26 @−5°, 18 @−10°**. Moving **latches with lid** is also wrong: causes 20 latch↔Case_Bottom strict pairs at 0° and −5°. The handle MUST move with lid, but the latches MUST retract separately.

**Verdict:** `NATIVE_GEOMETRIC_FIX_CANDIDATE_PASS` only, **`P1_HINGE_IMPLEMENTATION_HOLD`** until C01-18 commits an executable and time-ordered locked→latches retract→2mm lid/handle lift→hinge open→close→lower→latches relock contract in existing PR #26 (correct transformed coordinate frames, imported pivot/parent hierarchy checks, true full-binary SHA). A 23-pose test of a *hypothetical displaced mesh* is NOT evidence the current Unity scene makes that displacement. If fix is solely source animation, no Blender reexport; if native geometry altered, demand genuine new BLEND/FBX SHA then independently repeat. No automatic prefab/Unity PASS.

## Release and minimal handoffs

- [W25 3-model **delta-only** evidence matrix](W25_CHANGED_QA_GATES.csv): do **not** regenerate 36 native exports or re-audit 36 unchanged rows. C01-03 may update per-SHA canonical 36-row statuses only for **P18-07 current-source axis PASS**, P18-03 verified radius-source, P18-05 **proposed** geometric candidate but implementation still HOLD. The remainder retain exact prior SHA and statuses.
- Formal dimension decision remains C01-01 `ACCEPT_P18-07_SCOPED_EXCEPTION` vs `REJECT_WITH_MEASURED_CLEARANCE_WITNESS`, needs BOTH 0.341m closed and 0.361m swept. C01-13 is separately responsible for room/corridor layouts in Draft PR #39.
- **UNITY6:** `UNITY_NOT_RUN / OWNER_ACTION_REQUIRED`. Initial P16-01/P17-02/P18-01 pilot lacks real licensed Editor artifacts. Single owner action: activate authorized **Unity 6000.3.14f1** using Unity Hub on Windows, then run `& .\C01InteriorProps\Pass20\run_real_unity_windows.ps1 -Mode Execute -ProjectRoot (Get-Location).Path` in C01-10 isolated PR11 checkout per [project runbook](https://github.com/C8LyNn/Model-Test/blob/c01/props-10-showcase-integration/C01InteriorProps/Pass20/UNITY6_WINDOWS_OWNER_RUNBOOK.md). No repeat blocked CI/no license content disclosure.
- **36/36 registered original non-door FBX, 0/36 FINAL_APPROVED**. All producer and QA PRs Draft; no merge, no doors, no ship layout edits.
