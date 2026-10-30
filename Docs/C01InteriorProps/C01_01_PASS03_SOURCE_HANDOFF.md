# C01-01 — MESH REPAIR PASS03: SOURCE TOPOLOGY HANDOFF / 2026-10-30

**Source ticket:** [#30](https://github.com/C8LyNn/Model-Test/issues/30). **C01-01 Draft PR:** [#31](https://github.com/C8LyNn/Model-Test/pull/31). **Scope:** technical standard, audited real original .blend, non-destructive before/after validator, selective reference repair on historical copies. Not an independent C01-02 QA sign-off.

## Actual six producer sources (Blender 4.0.2)
Run A (original source revision): https://github.com/C8LyNn/Model-Test/actions/runs/41088564219; source17 `fbef546fe446fe6845be4eb76a75b0e6916723eb`, source18 `80c86ee6697f2e92c5c3961e57fa5887498f7cd0`, source19 `a87fb0e9523cfe92d79d6b429cc6c4148a406f41`. Actual source .blend were Git LFS hydrated before Blender opened them, no surrogate mesh or gallery reconstruction.

Run B (producer branches advanced independently): https://github.com/C8LyNn/Model-Test/actions/runs/41089765717; source17 `3e232b774eb8159942083c05dc7885dc9724948f`, source18 `aee1837638e5eddef785e53af3ee310703d594a9`, source19 `91d5561a11cbac3dc6022198bf54b47fc01b7900`. **This is not a C01-01 repair**: the changed producer source was checked out fresh. The run's attempts to redundantly repair P17 correctly did not pass the strict preconditions, and produced no repair archive. A following update made Blender Python exit codes fail-closed.

| Asset | Run A V/E/F/tri | Run B V/E/F/tri | Run A components → Run B | B notable defect candidates |
|---|---:|---:|---:|---|
| P17-04 | 696/870/348/348 | 232/522/348/348 | 174 → 29 | 0 counted in basic topology |
| P17-05 | 480/600/240/240 | 160/360/240/240 | 120 → 20 | 0 counted in basic topology |
| P18-04 | 192/288/114/348 | unchanged | 9 → 9 | 0 basic topology |
| P18-05 | 80/120/60/120 | unchanged | 10 → 10 | 0 basic topology |
| P19-07 | 104/156/78/156 | 136/204/78/252 | 13 → 6 | 8 T-junction candidates in Exam_Leg_-0.4_-0.98 |
| P19-08 | 96/144/72/144 | 149/241/100/282 | 12 → 6 | 2 T-junction candidates in Mounting_Backplate |

P17-04 original had **696 boundary edges and 464 co-located vertex candidates**; P17-05 had **480 boundaries and 320 co-located vertex candidates**, six detached quad islands in each modeled box part. In later independent producer revisions these basic issues were **no longer present**. The derived change is real native source revision, not FBX importer proof. P19-07/08 have changed object/triangle counts; do not assume appearance/part hierarchy was preserved until producer documents this. Their T-junctions are candidates to inspect, not automatic FAIL.

### File evidence and tests
- `Tools/c01_mesh_repair/topology_audit.py` — Blender BMesh counts per real object, original .blend SHA, coincident positions, T-junction, self-overlap candidates, boundary, winding and degenerate checks; **never auto-weld**.
- `Tools/c01_mesh_repair/safe_box_weld_candidate.py` — strict source-only reference repair of exactly six disconnected quad-face islands per independent cuboid; refuses other meshes, moving parts preserved, compares source UV loops, normals, materials, dimensions and transforms; outputs separate `.blend` and binary FBX if native export succeeds. It does not overwrite producer branches.
- `Tools/c01_mesh_repair/compare_topology_reports.py` — checks before/after hashes, object hierarchy, bounds, scale, UV and material invariants; always `NOT_APPROVED` until independent QA.
- `Tools/c01_mesh_repair/inspect_existing_fbx.py` — reimports real producer binary FBX in native Blender and compares source triangles/mesh counts/UV0, records reference SHA.
- `Tests/c01_mesh_repair/test_topology_blender.py`: **5/5 actual Blender fixture tests PASS** at 4.0.2. `test_compare_reports.py`: **10/10 Python tests PASS** in CI.

## Stop conditions and QA states
Neither no-op clean audit nor synthetic tests amount to completed repair. Any intentionally open mesh needs object-specific exception reviewed by C01-02, and any T-junction candidate needs manual reproduction in real source. FBX import, Unity 6 import, topology before/after evidence, matching source binary SHA and C01-02 signature must be individually evidenced; report NOT RUN rather than inferred PASS. **No ship architecture changed and no producer PR updated by C01-01.**

**Handoff:** C01-17 inspect current P17-04/05 AFTER and its actual FBX, keep 29/20 independent parts. C01-19 validate P19-07/08 changed part counts and 8+2 T-junction candidates. C01-18 provide real FBX QA for P18-04/05; source topology is free of audited basic defects. C01-02 inspect actual source & native import independent of this audit; C01-10 only real GLB/FBX viewer. C01-03 store both source-revision SHAs and per-model evidence; C01-00 controls release.

**Status:** C01-01 standard PASS / six real source BEFORE audits EXECUTED / historical repair-copy validation and six FBX imports tracked by CI / Unity NOT RUN / independent C01-02 NOT RUN / whole 36-asset completion BLOCKED.


## Final actual Blender / FBX evidence (2026-10-30, same PASS03 execution)

- **FULL GREEN GitHub Actions:** https://github.com/C8LyNn/Model-Test/actions/runs/41091176065 ; native Blender 4.0.2, system numpy dependency installed, `--python-exit-code 13` fail-closed. Blender fixture tests **5/5 PASS**, report comparison Python tests **10/10 PASS**.
- **Current producer exported binary FBX directly imported back into Blender:** all six assets returned **static import PASS** for mesh count, triangle count, UV0 and world bounds (not Unity). Artifact name `C01-01-PASS03-SIX-FBX-NATIVE-BLENDER-REIMPORT`, ID `12993199406`.
- **Exact native source branch heads of that run:** source17 `1cc9eb8aaf9f44cb7c63741ad60ffd7d21b768c3`, source18 `95b8ef34b6ec61931473e390e9d351f1d46943fa`, source19 `e804786b94a1badb84f261f76f450f1e9500e43a`.

| ID | Actual Blender source triangle count | Actual imported FBX triangle count | Mesh objects source/import | UV0 on every imported render mesh | World AABB delta |
|---|---:|---:|---:|---|---:|
| P17-04 | 348 | 348 | 29 / 29 | YES | 0.0m |
| P17-05 | 240 | 240 | 20 / 20 | YES | 0.0m |
| P18-04 | 348 | 348 | 9 / 9 | YES | 0.0m |
| P18-05 | 120 | 120 | 10 / 10 | YES | 0.0m |
| P19-07 | 252 | 252 | 6 / 6 | YES | 0.0000001m |
| P19-08 | 282 | 282 | 6 / 6 | YES | 0.0m |

- **Historical real source repair** on immutable bad source17 SHA `fbef546fe446fe6845be4eb76a75b0e6916723eb` executed by Blender on separate COPIES. `P17-04`: V696→232, E870→522, boundary696→0, triangle348→348, mesh objects29→29. `P17-05`: V480→160, E600→360, boundary480→0, triangle240→240, mesh objects20→20. Exact UV loop coordinates, area, per-face normals and material indices were checked before/after; zero topology candidates in AFTER. Blender exporter produced genuine FBX **binary v7400**, native Blender reimport **PASS** triangle count and mesh objects/UV0. Artifact `C01-01-PASS03-P17-04-05-HISTORICAL-REPAIR-PROOF`, ID `12993468427`; contains 2 real repaired .blend, 2 binary .fbx, per-model before/after JSON, changes and verification reports. These are reference copies, **not** edits to producer PR #23, whose own newer source already passed the basic topology checks.
- Updated source-only six audit archive `C01-01-PASS03-SIX-ORIGINAL-BLEND-AUDITS`, ID `12994022362`.

**Not tested:** true shaded/wireframe BEFORE/AFTER screenshots of the reference repairs (the audited producer source may have its own preview), Unity 6 URP import/PlayMode/collision/clearance, independent QA C01-02 and 36-model completion. Normal direction and smoothing for all 36 still require scrutiny; self-BVH/T-junction candidates in P19-07/P19-08 need manual evaluation. Producer changed assets concurrently: all results bind exact inspected file SHA and PR source head.

**Final C01-01 status:** normative topological standard PASS, automated Blender source audit PASS (execution), six native FBX geometry import preflights PASS (bounded scope), two historical reference repairs PASS (geometry + FBX), C01-02 approval **PENDING**, Unity **NOT RUN**, global issue #30 **OPEN**. No auto-merge.
