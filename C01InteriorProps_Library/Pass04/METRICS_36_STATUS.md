# C01-03 — PASS04 / 36-model source-reported mesh metrics and QA status

**SOURCE:** Issue #33 / #30. **Owner:** C01-03 asset-library versioning only. **Base:** existing Draft PR #27.

**CAUTION:** All V/E/F/T and local error counts below are transcribed from **producer JSON in actual PR branches**, not independently rerun by C01-03. Independent C01-02 did verify subsets of binary FBX in PR #13, and its tri-gate FAIL has precedence. A check here is not a mesh-repair acceptance.

**Notation:** V/E/F/T = vertices/edges/faces/triangles. `local defects*` sums only local degenerate/duplicate/loose/zero-area categories present in a given producer report. It does **not** include all T-junction, overlap, interpart or FBX triangulation candidates and therefore is not a universal topology error score.

| ID | Owner | BEFORE V/E/F/T | AFTER V/E/F/T | Local defects* | Producer Blender FBX roundtrip | Unity | Independent C01-02 QA |
|---|---|---|---|---|---|---|---|
| P15-01 | C01-15 | 288/432/178/508 | 288/432/178/508 | 0→0* | PASS | NOT RUN | BLOCKED |
| P15-02 | C01-15 | 176/264/120/288 | 176/264/120/288 | 0→0* | PASS | NOT RUN | BLOCKED |
| P15-03 | C01-15 | 192/288/144/288 | 192/288/144/288 | 0→0* | PASS | NOT RUN | BLOCKED |
| P15-04 | C01-15 | 918/1722/852/1740 | 918/1722/852/1740 | 0→0* | PASS | NOT RUN | BLOCKED |
| P15-05 | C01-15 | 2274/4494/2238/4512 | 2274/4494/2238/4512 | 0→0* | PASS | NOT RUN | BLOCKED |
| P15-06 | C01-15 | 3744/7308/3630/7356 | 3744/7308/3630/7356 | 0→0* | PASS | NOT RUN | BLOCKED |
| P15-07 | C01-15 | 2794/5400/2646/5460 | 2770/5376/2642/5420 | 0→0* | PASS | NOT RUN | BLOCKED |
| P16-01 | C01-16 | 120/150/60/60 | 40/90/60/60 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P16-02 | C01-16 | 120/150/60/60 | 40/90/60/60 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P16-03 | C01-16 | 120/150/60/60 | 40/90/60/60 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P16-04 | C01-16 | 168/210/84/84 | 56/126/84/84 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P16-05 | C01-16 | 168/210/84/84 | 56/126/84/84 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P16-06 | C01-16 | 216/270/108/108 | 72/162/108/108 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P16-07 | C01-16 | 120/150/60/60 | 40/90/60/60 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P17-01 | C01-17 | 408/510/204/204 | 136/306/204/204 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P17-02 | C01-17 | 480/600/240/240 | 160/360/240/240 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P17-03 | C01-17 | 456/540/208/208 | 128/312/208/208 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P17-04 | C01-17 | 696/870/348/348 | 232/522/348/348 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P17-05 | C01-17 | 480/600/240/240 | 160/360/240/240 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P17-06 | C01-17 | 312/390/156/156 | 104/234/156/156 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P17-07 | C01-17 | 456/570/228/228 | 152/342/228/228 | 0→0* | NOT_RUN | NOT RUN | BLOCKED |
| P18-01 | C01-18 | 120/270/180/180 | 120/270/180/180 | 0→0* | SEE_PRODUCER_FBX_ROUNDTRIP_REPORT | NOT RUN | BLOCKED |
| P18-02 | C01-18 | 136/306/204/204 | 136/306/204/204 | 0→0* | SEE_PRODUCER_FBX_ROUNDTRIP_REPORT | NOT RUN | BLOCKED |
| P18-03 | C01-18 | 208/522/348/348 | 208/522/348/348 | 0→0* | SEE_PRODUCER_FBX_ROUNDTRIP_REPORT | NOT RUN | BLOCKED |
| P18-04 | C01-18 | 192/288/114/348 | 192/288/114/348 | 0→0* | SEE_PRODUCER_FBX_ROUNDTRIP_REPORT | NOT RUN | BLOCKED |
| P18-05 | C01-18 | 80/120/60/120 | 80/120/60/120 | 0→0* | SEE_PRODUCER_FBX_ROUNDTRIP_REPORT | NOT RUN | BLOCKED |
| P18-06 | C01-18 | 88/132/66/132 | 88/132/66/132 | 0→0* | SEE_PRODUCER_FBX_ROUNDTRIP_REPORT | NOT RUN | BLOCKED |
| P18-07 | C01-18 | 80/120/60/120 | 80/120/60/120 | 0→0* | SEE_PRODUCER_FBX_ROUNDTRIP_REPORT | NOT RUN | BLOCKED |
| P19-01 | C01-19 | 88/132/66/132 | 133/205/78/254 | 0→0* | PASS | NOT RUN | BLOCKED |
| P19-02 | C01-19 | 72/108/54/108 | 118/194/86/216 | 0→0* | PASS | NOT RUN | BLOCKED |
| P19-03 | C01-19 | 64/96/48/96 | 72/112/48/128 | 0→0* | PASS | NOT RUN | BLOCKED |
| P19-04 | C01-19 | 72/108/54/108 | 72/108/54/108 | 0→0* | PASS | NOT RUN | BLOCKED |
| P19-05 | C01-19 | 88/132/66/132 | 88/140/66/148 | 0→0* | PASS | NOT RUN | FAIL_P1_TRIANGULATION |
| P19-06 | C01-19 | 56/84/42/84 | 56/84/42/84 | 0→0* | PASS | NOT RUN | BLOCKED |
| P19-07 | C01-19 | 104/156/78/156 | 136/204/78/252 | 0→0* | PASS | NOT RUN | FAIL_P1_TRIANGULATION |
| P19-08 | C01-19 | 96/144/72/144 | 149/241/100/282 | 0→0* | PASS | NOT RUN | FAIL_P1_TRIANGULATION |

## P0 independent FBX export failure — remains open

- **P19-05**: 3 polygons >4 vertices; 1 degenerate fan triangle candidate, 1 nonmanifold fan edge candidate.
- **P19-07**: 16 polygons >4 vertices; 19 degenerate fan triangles, 2 nonmanifold fan edge candidates; additional reported T-junction candidates require classification.
- **P19-08**: 35 polygons >4 vertices; 7 degenerate fan triangles, 3 nonmanifold fan edge candidates; additional reported T-junction candidates require classification.
- C01-02's independent finding concerns unsafe triangulation under a conservative fan method; this is not a demonstrated Unity-import failure. The current producer PR #29 FBX LFS OIDs match the same independently failed binary export hashes. No corrected post-PASS04 binary is verified.

## Current release blockers

- P16-01–07: native .blend paths still missing from producer PRs #12/#28; binary Blender-derived export/reimport not independently demonstrated.
- GitHub Actions for new C01-03 PASS04 candidate byte capture currently fail before returning any executable steps/logs. Do **not** claim 36/36 AFTER bytes were downloaded or SHA verified. Read-only static ledger checks were performed separately.
- No new C01-02 signed after-FBX QA hash; all 36 release_status BLOCKED.
- Blender executable and Unity executable are unavailable in C01-03's runtime. Native Blender reimport/Unity editor = NOT RUN here.

## Provenance

- BEFORE source/export SHA and pinned producer commits: `Pass03/repair_ledger.json`.
- PASS04 pinned current producer commits + LFS expected OIDs for three P19 failures: `Pass04/repair_ledger.json`. Expected LFS OID is *not* a byte-hydration verification.
- Per-group producer report paths and Git blob SHAs: `Pass04/producer_metrics_15_16.json`, `_17.json`, `_18.json`, `_19.json`.
- QA independent binary-FBX triangulation verdict: `C01InteriorProps_QA/PASS03/INDEPENDENT_TOPOLOGY_HANDOFF_2026-10-30.md` in Draft PR #13.

## Next authorization gates

1. C01-19 explicitly triangulates original Blender n-gons in P19-05/07/08 and reexports binary FBX, keeping silhouette, UV0, normals, moving pivots and transforms unchanged; publishes new SHA + actual Blender roundtrip.
2. C01-16 delivers seven genuine .blend and binary FBX with Blender import evidence on existing PRs.
3. C01-03 repins new producer commits and verifies actual hydrated AFTER bytes (not pointer text); retains PREVIOUS SHA as immutable BEFORE.
4. C01-02 independently retests exact AFTER FBX SHA for all 36; C01-10 tests Unity real prefabs and clearance; C01-00 accepts. No merge before approval.
