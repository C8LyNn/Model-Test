# C01-10 — Interior Props WAVE 02 / accepted-only Unity integration

Repo: C8LyNn/Model-Test, PR #11; base: `codex/c01-ship-integration` (draft ship PR #1). Parent issue #2, integration issue #9, QA issue #8. 2026-10-30.

## Real state, not intent

**0/16 approved by C01-02 at latest observed independent QA report** (`c01/props-02-independent-qa`, PR #13). Source supplier PRs #12/#15/#16/#17/#18 exist, but **do not** treat producer-run Blender FBX exports as independent C01-02 acceptance. Source-level QA lists P17-01 UV0 absent in GLTF and P18-01 FBX missing UV/normal layers; supplier heads have moved since earlier QA, so retest exact current SHA.

**Nothing is currently instantiated or captured in Unity**. No Unity/Blender executable in this C01-10 runner. Model binary source and screenshots belong to supplier PRs, not this integrator. No source-ship file modified; no merge and no release request.

## Deliverable: actual Unity Editor C# implementation

`Assets/C01InteriorProps/Editor/InteriorPropsAcceptedShowcaseBuilder.cs` includes:
- Acceptance list for Wave 01 (16) and Wave 02 (20) IDs; Wave 02 size/mount/family details must come from the independent QA ledger.
- SHA-256 verification on real FBX bytes (also rejects short Git LFS pointer), required prefab import and live mesh bounds.
- C01-01 v0.2.1 dimensional tolerance ±0.002m, pivot tolerance ±0.001m, scale ±0.0001; expects local front -Z and verified mounting profile.
- Requires at least one actual `APPROVED` row in the ledger and matching 64-digit SHA, a QA evidence link, and actual imported Unity prefab containing meshes, renderers and colliders.
- Never scales, edits, recenters, repaints or rewrites supplier geometry.
- Creates a separate master prefab with **nested supplier prefab instances**, plus up to five scenes, only if accepted inputs pass.
- Empty themed scenes are **not** generated; source ship remains unchanged.

The older `InteriorPropsShowcaseBuilder.cs` builder is explicitly disabled: it permitted ±0.20m deviation and did not require formal QA approval.

## Required QA-approved ledger

Path: `Assets/C01InteriorProps/QA/approved_assets.csv`.

Current file contains **header only**, because 0 models are accepted. This is intentional, not a delivery claim. Fill only after the C01-02 independent process records PASS on the exact model and import.

Columns:
`asset_id,approval,owner,family,mount,width_m,depth_m,height_m,prefab_path,fbx_path,fbx_sha256,qa_reference`

Example (ILLUSTRATIVE — DO NOT COMMIT AS APPROVED):
`P19-01,APPROVED,C01-19,Furniture,floor,0.95,2.1,0.65,Assets/C01InteriorProps/.../P19-01.prefab,Assets/C01InteriorProps/.../P19-01.fbx,<64 hex SHA>,https://github.com/C8LyNn/Model-Test/issues/8#issuecomment-...`

The ledger does not itself prove independent approval: C01-02 must explicitly verify and sign the corresponding evidence. The generator checks fields and SHA, not the human reviewer's identity.

## How to execute in Unity 6 URP

1. Merge *reviewed* source PR files from C01-15–19 into an **integration test branch**; retain `.meta`, LFS content, materials, real FBX, native `.blend`, separate movable part pivots and per-model source manifest.
2. Confirm independent C01-02 approvals for each exact file SHA and prefab version; add only corresponding rows to the accepted ledger.
3. Open Unity 6000.3.14f1 / URP 17.3.0, wait for import. Menu **C01 > Interior Props > Wave 02 > Preflight Approved SHA**. Examine `C01InteriorProps_QA/integration/ACCEPTED_PREFLIGHT.csv` created by Unity.
4. If preflight returns BLOCKED, return the defect to C01-15–19/01 and do not compensate by scaling, renaming missing GUIDs or editing meshes.
5. Menu **C01 > Interior Props > Wave 02 > Build Approved Showcase** (requires at least one accepted model); writes `Assets/C01InteriorProps/AcceptedShowcase/Prefabs/C01_InteriorProps_Showcase_MASTER.prefab` and 1–5 independent scenes under `AcceptedShowcase/Scenes`:
   - `C01_InteriorProps_Showcase.unity` (all accepted IDs).
   - `C01_InteriorProps_Cabin.unity` (accepted furniture, if any).
   - `C01_InteriorProps_Bridge.unity` (accepted controls, if any).
   - `C01_InteriorProps_Engineering.unity` (accepted installations + lighting, if any).
   - `C01_InteriorProps_Cargo.unity` (accepted cargo, if any).
6. Inspect all actual prefabs/rendering, collider contact and movable parts. Snapshot render, Inspector bounds, SHA evidence, assembly log and manual/PlayMode test. Commit generated .prefab/.unity/.meta only AFTER actual run.
7. Test real ship v4 passage and doors at minimum navigable 3m, player capsule, gate sweep, lift, stairs, fire exits, without writing changes to ship scenes. The standalone gallery only includes a notional 3m lane and **does not prove ship clearance**.
8. C01-02 signs final independent review; C01-00 approves release. Do not merge PR #11 before that.

## Important implementation caveats / to resolve

- This tool is authored and statically inspected but **NOT COMPILED IN UNITY**. Its output paths are target paths, not present generated files.
- Standalone gallery positions are inspection positions, not measured real ship anchors, so wall/ceiling alignment must be tested manually on actual completed surfaces.
- Prefab validation verifies local bounds/colliders/source hash, not UV normals/URP shaders, moving sweeps, penetration, or walkability. C01-02 must test those separately.
- Wave 02 targets 20 additional IDs, but C01-10 does not author those meshes. Separate producer PRs are required for P15-04..P19-08.
- The accepted ledger is empty by design until C01-02 explicitly approves source identity and renderer/collider behavior.
