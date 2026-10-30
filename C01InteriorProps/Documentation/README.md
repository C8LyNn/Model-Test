# C01-10 — Interior Props integration

**Current entrypoint (Wave 02, 2026-10-30):** [WAVE02_ACCEPTED_SHOWCASE.md](WAVE02_ACCEPTED_SHOWCASE.md) and [WAVE02_HANDOFF_C01-00_C01-02.md](WAVE02_HANDOFF_C01-00_C01-02.md).

**STATUS: BLOCKED**. Producer PRs exist (#12, #15–18) with real/provisional source assets and some Blender/FBX outputs, but the latest independently observed C01-02 report (#13/#8) approves **0 of 16** Wave 01 assets. Supplier updates require fresh per-SHA retests. Wave 02 adds 20 IDs, not new models owned by C01-10.

**Live Unity editor tool:** `Assets/C01InteriorProps/Editor/InteriorPropsAcceptedShowcaseBuilder.cs`. It only accepts SHA-pinned rows marked APPROVED in `Assets/C01InteriorProps/QA/approved_assets.csv`. That ledger currently contains only its header. Consequently it **refuses to build a scene**, instead of faking integration.

**Legacy W01 builder:** `InteriorPropsShowcaseBuilder.Build` has deliberately been disabled because it ignored C01-02 acceptance and allowed a 20cm dimensional deviation. Do not use it.

**Deliverables in PR #11:** new SHA and pivot gates, accepted-only prefab instance master, independent Showcase/Cabin/Bridge/Engineering/Cargo scene generation capability, updated QA state, C01-02/C01-00 handoff.

**NOT RUN:** Unity compilation, FBX imports, actual .prefab and .unity file generation, PlayMode, Blender, physical clearance and screenshots in the current C01-10 runtime. The output scene names are **targets**, not files that exist.

**Owner boundaries:** C01-15–19 own meshes, source Blend and FBX; C01-01 owns standards, C01-02 independently approves; C01-10 owns integration logic; C01-00 accepts. No ship source geometry, floor plan, gate or elevator is modified by this branch.
