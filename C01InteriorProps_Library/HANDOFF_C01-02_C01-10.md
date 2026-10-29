# C01-03 → C01-02 / C01-10 / C01-00 — Interior Props PASS 01 WAVE 01

**Registry owner:** C01-03  
**Master issue:** https://github.com/C8LyNn/Model-Test/issues/2  
**Producer issues:** #3 (C01-15), #4 (C01-16), #5 (C01-17), #6 (C01-18), #7 (C01-19)  
**Independent QA:** #8 (C01-02)  
**Scene integration:** #9 (C01-10)  
**Ship base branch:** `codex/c01-ship-integration` (PR #1 in Draft)

## C01-03 actual deliverables

- `catalog.json`: exactly sixteen stable asset IDs P15-01–P19-04, producer owner and links, proposed sizes W×D×H, mounting guidance; actual measurements all null.
- `tools/registry.py`: real-file validation with SHA-256 and blocked release until all delivered and verified.
- `tests/test_registry.py`: automated unit tests, distinct from Blender/Unity tests.
- `README.md`: isolated, version-safe intake procedure.
- `.github/workflows/c01-interior-props-registry.yml`: static CI workflow.

No Blender, FBX, prefab or preview file has been authored, imported, or claimed by C01-03. Actual model geometry must come from the owning specialists.

## Current intake matrix

| Owner | Asset IDs | Expected deliverables | C01-03 verified binaries | QA | Unity |
|---|---|---|---|---|---|
| C01-15 / #3 | P15-01–03 | .blend .fbx prefab/meta 3 PNG | 0 | NOT RUN | NOT RUN |
| C01-16 / #4 | P16-01–03 | .blend .fbx prefab/meta 3 PNG | 0 | NOT RUN | NOT RUN |
| C01-17 / #5 | P17-01–03 | .blend .fbx prefab/meta 3 PNG | 0 | NOT RUN | NOT RUN |
| C01-18 / #6 | P18-01–03 | .blend .fbx prefab/meta 3 PNG | 0 | NOT RUN | NOT RUN |
| C01-19 / #7 | P19-01–04 | .blend .fbx prefab/meta 3 PNG | 0 | NOT RUN | NOT RUN |

## Test distinctions

1. Manifest integrity: structurally testable by `registry.py audit` and `unittest`.
2. Byte integrity: NOT RUN on production model files until owner commits real inputs.
3. Blender native import/render: NOT RUN, no Blender editor execution by C01-03.
4. Unity 6 URP import/prefab & clearance: NOT RUN, no Unity editor execution by C01-03.
5. Independent C01-02 QA: NOT RUN.
6. C01-10 showcase scene: BLOCKED until 16 actual assets have been delivered.
7. C01-00 acceptance: BLOCKED.

## Defects / blockers

- BLOCKER C01-03-001: no producer asset branch/delivery was visible when this registry branch was created. Without bytes, QA cannot examine source geometry, and .blend/.fbx/.prefab hashes must remain unpopulated.
- BLOCKER C01-03-002: C01-01's final prop mounting/pivot conventions must be applied by owners before approvals.
- BLOCKER C01-03-003: ship PR #1 is still Draft; keep showcase independent and do not modify master ship.
- No structural ship edits were made here.

## Handoff procedure

1. C01-15–19: deliver to respective issue/PR, including source mesh files, Unity prefab/meta, three preview angles, measured dimensions, material and collider specifications, and export evidence.
2. C01-03: inspect real file paths, run `register` for each required role in version-isolated asset folders; verify byte hashes and regenerate report.
3. C01-02: run independent Blender/Unity validation, cite FBX SHA-256 and version, produce QA evidence. Return per-asset PASS/FAIL/NOT RUN and defects to owners.
4. C01-10: after QA, produce standalone showcase scene and master prefab; keep architecture unchanged; test corridor and door clearance.
5. C01-00: review evidence and approve release separately. Do not merge this Draft PR or other producer changes without review.

**Current overall result:** C01-03 registry implemented; end-to-end INTERIOR PROPS delivery BLOCKED until physical assets and independently verified QA. Do not interpret a passing registry unit test as game-ready geometry.
