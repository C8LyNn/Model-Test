# C01-02 — Interior Props / WAVE 01 independent QA

**Issue:** #8 (parent #2). **Base:** `codex/c01-ship-integration`. QA does not edit producer geometry or ship architecture.

## Verified baseline (2026-10-29)

Recursive inspection of the source branch (5137 Git tree entries) found **no** `Assets/C01InteriorProps` catalog, no P15-01–P19-04 models, and no production branches for C01-15–19. The project PR #1 was still a draft. **All 16 actual production asset checks remain NOT RUN; overall BLOCKED.**

## Independent acceptance

Every asset requires real `.blend`, `.fbx`, Unity 6 URP `.prefab`, preview and a unique manifest (owner, version, size, mesh bounds, mounting interface, pivot, material slots, collision strategy). Screenshots and manifest assertions are not substitutes for actual mesh validation. Run geometry and exporter tests in Blender and imported prefab/clearance checks in Unity; issue-specific nominal dimensions are reference sizes, not automatic tolerance thresholds.

Required per-asset checks: dimensions/units, world-up and pivot, finite vertices, normals, UV, mesh/material counts, <=4 URP-compatible materials, collider correctness, separated movable parts and pivots, actual 3 m corridor and door clearance, screenshots from Unity, reproducible version/hash. Only complete evidence allows PASS; a verified defect yields FAIL; insufficient access yields BLOCKED, individual unperformed tests NOT RUN.

## Procedure

1. Producers (#3–7) deliver all sixteen real files and source manifests to their isolated PRs.
2. Run the included Python status checker against actual package manifests; it reports missing inputs honestly.
3. Unity QA inspector (in `Assets/C01InteriorProps/QA/Editor`) inspects actual prefabs without touching the ship scene.
4. C01-10 (#9) supplies the separate showcase and a 3 m corridor/door clearance test scene; QA observes actual walking/collision/door movement in PlayMode, logs results and screenshots.
5. C01-02 submits per-ID PASS/FAIL/NOT RUN, bugs to respective owner issues, and independent QA signoff only with evidence.

**Blocked:** no model-specific Blender/Unity tests have run. Local QA harness unit tests (12/12) validate checker behavior only; they are not asset acceptance.
