# C01-03 — WAVE01 updated handoff to C01-02 / C01-10 / C01-00

**Registry PR:** https://github.com/C8LyNn/Model-Test/pull/10 (draft)  
**Main issue:** https://github.com/C8LyNn/Model-Test/issues/2  
**QA:** https://github.com/C8LyNn/Model-Test/pull/13 (C01-02, draft)  
**Integration:** https://github.com/C8LyNn/Model-Test/pull/11 (C01-10, draft)  
**Byte-intake CI:** https://github.com/C8LyNn/Model-Test/actions/runs/41071526841 (SUCCESS; 5/5 jobs).

## Deliverables C01-03 (real changes)

- Reconciled 16 Wave01 assets to actual PRs #12 / #15 / #16 / #17 / #18.
- Pinned all five supplier head commit SHAs and verified **115 individual candidate file bytes** through GitHub Actions with LFS enabled. Recorded per-path SHA-256 and job provenance in the registry.
- Kept accepted local files/released versions empty: a producer path is not an accepted/approved Unity asset.
- Added metadata tests, real-byte intake scanner, test workflow, report and README.
- No producer mesh, source, prefab or ship scene was altered; C01-03 performed **no Blender/Unity Editor run**.

## Wave01 status by ownership

| Owner / PR | Assets | SHA256-verified candidate files | Native .blend | FBX | Unity prefab | Preview | Full set |
|---|---|---:|---|---|---|---|---|
| C01-15 / #16 | P15-01–03 | 17 | YES | YES | MISSING | 3 PNG/model | BLOCKED |
| C01-16 / #12 | P16-01–03 | 16 | MISSING | YES | YES | MISSING | BLOCKED |
| C01-17 / #17 | P17-01–03 | 21 | YES | YES | MISSING | >=3/model | BLOCKED |
| C01-18 / #18 | P18-01–03 | 12 | MISSING on PR (external native archive reported) | YES | YES | MISSING on PR | BLOCKED |
| C01-19 / #15 | P19-01–04 | 49 | MISSING | MISSING | MISSING | 3 SVG/model | BLOCKED |

**Actual independently accepted: 0/16.** No evidence of successful Unity 6 URP runtime import or corridor clearance signed by C01-02.

## Confirmed problems and obligations

- **P17-01:** previous C01-02 findings UV0 absent on glTF primitives. Retest current FBX SHA; do not auto-clear.
- **P18-01:** previous C01-02 findings absent FBX UV and normal layers. Retest new files.
- 14 other assets: BLOCKED pending completion and QA, not PASS.
- Producer files are still isolated on their own PR branches, not silently merged.
- PR #1 (ship) is separate; do not modify level layout, corridors, decks, doors or elevators.

## Integration / acceptance gates

1. Producers deliver missing original files and fixes on existing PRs (#3–#7), not in C01-03.
2. C01-03 refreshes pinned supplier SHAs, reruns GitHub Actions byte audit and updates registry hashes; new geometry requires new semantic version.
3. C01-02 independently verifies matching FBX SHA, UV, normals, pivots, materials, colliders, actual Blender/Unity import and clearance. QA status must be an explicit signed result.
4. C01-10 assembles showcase + master prefab, test cabin/bridge/engineering/storage with approved assets. Do not modify source ship scene.
5. C01-00 accepts before merge. No Wave01 or Wave02 final PASS without that signoff.

## Status

**C01-03 REGISTRY / SHA256 INTAKE: PASS.**  
**Independent geometry QA: 0/16 approved.**  
**Full Wave01 integration: BLOCKED.**

The machine-readable details, owner SHAs and hashes are in `catalog.json`. Full per-ID receipt summary: `WAVE01_HASH_AUDIT_2026-10-30.md`.
