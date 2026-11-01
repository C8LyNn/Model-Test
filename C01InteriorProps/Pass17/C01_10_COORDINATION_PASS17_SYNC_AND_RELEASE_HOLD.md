# C01-10 — DETAIL PASS17 / coordination, SHA-pinned QA staging and Unity release HOLD

**Date:** 2026-11-01. **Owner:** C01-10 SPACE HORROR INTERIORS — COORDINATION. **HQ:** https://github.com/C8LyNn/Model-Test/issues/36 . **Own Draft:** https://github.com/C8LyNn/Model-Test/pull/11 . No merge, new asset IDs, structural spaceship edits, or producer-model edits.

## P0 — Actual producer build evidence, not Unity certification

| Ownership / IDs | Actual evidence observed | Coordinator disposition |
|---|---|---|
| C01-18 P18-01/02/03 | Successful Blender4.0.2 source-to-native FBX and independent actual-byte QA, 47/980, 59/1284, 63/1780 named meshes/triangles; see [C01-10 real binary report](./C01_10_INDEPENDENT_NATIVE_P18_FBX_QA.md) and [run 41344872313](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313) | Immutable final FBX SHA already pinned in manifest; **QA-only quarantine candidates**, C01-02 approval and Unity6 NOT RUN |
| C01-19 P19-01/02 | [run 41346465283](https://github.com/C8LyNn/Model-Test/actions/runs/41346465283) SUCCESS and [native summary](https://github.com/C8LyNn/Model-Test/blob/c01/props-19-furniture/Assets/C01InteriorProps/C01-19/QA/PASS17/SUMMARY.json); 4 meshes/470T and 5 meshes/292T; actual Blender BEFORE/AFTER images plus reimport reports | Exact current Git LFS pointer SHA256 **matches producer summary for both**; hydrated native FBX independent C01-02 QA **PENDING**, do not promote from older manifest until new immutable source pins + actual bytes independently checked |
| C01-19 P19-05 | [run 41346471952](https://github.com/C8LyNn/Model-Test/actions/runs/41346471952) SUCCESS and [native summary](https://github.com/C8LyNn/Model-Test/blob/c01/props-19-furniture-wave02/Assets/C01InteriorProps/C01-19-W02/QA/PASS17/SUMMARY.json); 7 meshes/252T | Git LFS pointer SHA256 matches producer summary; independent C01-02 full native/hierarchy/render QA PENDING, Unity NOT RUN |
| C01-16 P16-01/02/03 | [run 41346888455](https://github.com/C8LyNn/Model-Test/actions/runs/41346888455) executed genuine Blender4.0.2 export + reimport 3/3 and uploaded [artifact 13099492261](https://github.com/C8LyNn/Model-Test/actions/runs/41346888455/artifacts/13099492261) | Workflow overall FAIL at git rebase; binary outputs in CI artifact, **not pushed to own producer branch**. No promotion or independent hydrated bytes attestation |
| C01-16 P16-04/05/06/07 | [run 41346809918](https://github.com/C8LyNn/Model-Test/actions/runs/41346809918) executed real Blender4.0.2 export + reimport 4/4 and uploaded [artifact 13099537034](https://github.com/C8LyNn/Model-Test/actions/runs/41346809918/artifacts/13099537034) | Workflow overall FAIL at git rebase; binary outputs in CI artifact, **not pushed**. No promotion |
| C01-17 P17-01/02/03 | [PASS17 real-source interactive viewer](./PREVIEW_P17_SOURCE_INTERACTIVE.html), previous exact P17-01 +1mm guide correction intact; independent C01-02 also flags 8 P17-03 lever boundary edges | Await exact latest Blender native source+FBX, producer rationale for intentional lever open ends, C01-02 and Unity pivot sweep |

## C01-16 exact root cause and ownership

Both P16 workflow logs show: Blender install **SUCCESS**, actual native .blend and FBX 7400 write+roundtrip **SUCCESS**, uploaded CI artifacts **SUCCESS**, local CI commit **SUCCESS**, and Git LFS smudge/checkout left tracked asset changes after `git reset --hard HEAD`. The subsequent `git rebase origin/<producer branch>` fails with `cannot rebase: You have unstaged changes`. This is a producer workflow/Git LFS cleanup defect; C01-10 must not modify C01-16 producer models or force-push. C01-16/C01-03 to preserve immutable artifact IDs, fix CI checkout/index cleanup on a disposable worktree, and republish with exact full object SHA-256. Do not silently copy local CI commits `9a53ba5` and `63430e7` as published source.

## QA staging defect found and fixed by C01-10

The existing 36-entry manifest had **19 BLOCKED + 17 QA-only candidates**. Of those 17 candidates, exactly **10 had a valid full 64-hex final FBX SHA-256 pin**, while **7 were unpinned**: P15-02, P15-04/05/06/07, P19-03/04. Previously `stage_real_fbx.py --apply` could hydrate an unpinned candidate and trust the found binary instead of comparing it with an immutable approved candidate SHA. This was unacceptable for the QA staging provenance gate (even though it did not imply independent approval).

**Executed repo changes in this own Draft PR:**
- `C01InteriorProps/Pass04/stage_real_fbx.py`: unpinned/malformed pin now produces `BLOCKED_UNPINNED_BINARY_SHA256` before any fetch, LFS hydration or copy; for eligible candidates, **exact final SHA equality is mandatory**.
- `.github/workflows/c01-pass04-integrator-static.yml`: regression preflight simulates a known P18-01 candidate with missing/malformed final SHA, checks dry-run + apply stay blocked and no FBX appears in staging; also confirms valid SHA remains a diagnostic dry-run candidate. This is **test code committed, GitHub Actions execution NOT RUN**.
- The 36 model IDs and original statuses remain unchanged; this hardening affects **staging eligibility**, not asset QA approval or source authoring.

## C01-19 exact integrity receipts checked on live current branches

| Asset | Producer reported FBX SHA-256 | Current Git LFS pointer OID (read in this coordination pass) | Native receipt |
|---|---|---|---|
| P19-01 | `e2e0bb9e095c1daed87e407814e88f8788cf503ab705d3e34513879038bcd559` | EXACT MATCH; pointer claims 36,796 bytes | Blender4 / producer FBX roundtrip PASS |
| P19-02 | `b0d68ce917a938b4bdaa32f4b2d48dcab5275c752c141260cabd3d82a5c9374f` | EXACT MATCH; pointer claims 34,316 bytes | Blender4 / producer FBX roundtrip PASS |
| P19-05 | `d07b4884cfe1de2c48a96dc9407c2eccdfbdbdf703551c71ae195bd3fd8c9d87` | EXACT MATCH; pointer claims 37,404 bytes | Blender4 / producer FBX roundtrip PASS |

**Limitation:** SHA matching a Git LFS *pointer* is metadata verification, not independent hydration and parse of the final binary. No C01-02 full-byte PASS asserted for these three models.

## Unity 6 URP handoff (unchanged GO/NO-GO)

1. C01-03 freeze a 36-entry exact source/native inventory **only after** real immutable binary SHA evidence (including P16 CI recovery and P19 fresh hashes); no trust in historical FBX or screenshots alone.
2. C01-02 independently inspect **hydrated** final FBX: all triangles, UV0, normal loops, hierarchy/pivot, new mechanical attachment, coplanar overlap and intentional assembly boundaries, then authorize QA intake by exact source SHA. In particular P17-03 eight boundary edges and P19-07 visual HOLD remain open.
3. C01-10 stage only SHA-pinned candidates in `Assets/C01InteriorProps/Pass04Incoming`, run existing editor audit in separate quarantined Unity 6 URP scene (not the ship), inspect material slots, emissive signals, rotor and wheel pivots, physics/sweep and prefab GUIDs.
4. C01-02 final acceptance and C01-10 Unity EditMode/PlayMode screenshots are required **before** any release GO. Existing interactive source viewers: [P17 actual glTF](./PREVIEW_P17_SOURCE_INTERACTIVE.html), [P18 actual OBJ](./PREVIEW_P18_SOURCE_INTERACTIVE.html), not substitutes for Blender/Unity engine tests.

**Runtime inspected here:** `blender`, Unity executable and `git-lfs` unavailable. No Blender GUI save/export, no Unity 6 compilation, scene load/import, prefab build, visual shader QA or PlayMode executed by C01-10 in this new pass. The Python regression was committed for CI but **NOT RUN**, so no runtime PASS claimed. **Current release decision: 0/36 final approved; HOLD; no merge**.
