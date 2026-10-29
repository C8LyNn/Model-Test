# Three-deck C01 Implementation Plan

> Agent workers: use subagent-driven-development; one implementation worker at a time while primary owns generator integration. Do not create further subagents.

Goal: Deliver the confirmed 3 m-square ship with 6/12 m clearances, 24 equipped square cabins and bathrooms, three decks, button gates, real elevators, lower service spaces, verified Unity and actual Blender exports, uploaded to Drive.

Architecture: shared prism/placement manifest per contract.md, independent native Unity modules, separate v4 namespace preserving v3.1, no transform scaling of architecture. Tech: Python, Blender 5.2, Unity 6000.3.14f1 URP 17.3 and Input System 1.19. Spec: spec.md.

Global constraints: all user dimensions are floor-square counts; 3 m corridor widths; cabin/bath/stern dimensions 9×9 / 6×3 / 12 m; heights 6/12 m; moving elevators and gate buttons; no deletion of previous versions or user settings.

- [ ] T1 Primary: write failing dimensions/content/coverage tests, build manifest and geometry with global wall interval merging, clipping decks/shafts and gate pockets; independent collision/gap checks and mutations.
- [ ] T2 Runtime worker: gate/button/airlock/lift/explorer behavior and focused Unity PlayMode tests per contract; only Runtime and Tests/PlayMode files.
- [ ] T3 Fresh Unity worker after T2: build native meshes, prefabs, master, scene, validator, asynchronous batch runner and meaningful EditMode QA. Own Editor and Tests/Editor only.
- [ ] T4 Primary while T3 runs: actual Blender exports and FBX round trips, Python audit, prepare integration preserving v3 data/settings.
- [ ] T5 Primary + fresh reviewer: import/build in Model Test, actual Unity tests including clicked controls and moving platform ride, screenshots each deck/room/core, repair failures, final broad spec/code review.
- [ ] T6 Primary: complete source/project ZIP and Unity package with verification manifest; update PR #1; Drive folder/upload/metadata readback and final download links.

Review focus: elevator landing gate safety under repeated calls; all 96 beds and 192 lockers fit clear cabin space; 6×3 bathrooms have real traversable gates; tall-sector walls must not penetrate deck2 slabs; lower and upper decks must both have actual reachable access via each vertical core; navigation transport links cannot substitute for physical elevator tests.
