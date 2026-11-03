# C01-11 — W28 FINAL MESH ACCEPTANCE / NON-DOOR VERSION SPLIT

**Owner:** C01-11 (W01 full wall, W02 panel wall, W03 corner 90° ONLY). Existing [Draft PR #22](https://github.com/C8LyNn/Model-Test/pull/22), input HEAD `6f33626cd29b7181d4e9d12f9eeaa5cdbe8b1ab9`, still open/unmerged. This is an evidence receipt and release dependency, **not a new physical QA PASS**. Canonical 36 P15–P19 props tracked separately by C01-03/02.

## New W28 independent intake finding

[C01-03 W28 eight-architecture ledger](https://github.com/C8LyNn/Model-Test/blob/c01/props-03-library-wave02/C01InteriorProps_Library/Pass28/C01_03_W28_ARCHITECTURE_8_STATUS.csv) and [C01-02 W28 independent matrix](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/W28/W28_36_CANONICAL_CURRENT_SHA_QA_MATRIX.json) both explicitly confirm **three version-SHA conflicts** for W01/W02/W03. W28 separately fetched current PR22 original tracked FBX pointer file text on pinned head and independently parsed all three **entire 64-digit Git LFS sha256 OIDs and Git pointer blob hashes**: **3/3 exact current matches to curated ledger**. GitHub commit comparison W26 head→W28 PR branch: **IDENTICAL / 0 new commits / 0 changed files** before this receipt. These are pointer identity validations, not new full binary imports.

| ASSET | ORIGINAL / CURATED PR22 FBX SHA-256 (CURRENT tracked LFS OID) | W26 C01-02 FULL-BINARY AUDITED PASS17 QA CANDIDATE FBX SHA-256 | MATCH? |
|---|---|---|---|
| W01 | `4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f` | `c644e95d548cafbac61cebe000d7b0fb4b584a1fe4527565ba55d4c8e0415a79` | **NO** |
| W02 | `7dfcf0fe84952e607a74845ad193acfbb9f4fc029e7f168a94a7bac2edacb78b` | `a23f602d8dd61a6dc61ee52af347e472f2e6f6ce546988f50409911d1b11a317` | **NO** |
| W03 | `4c268d554d4e5948ea1927e29b0d32fc581a6f9f14f41fd070bf116a8eb7864c` | `9dcc8feca9475626e393910b4176d8c2eadf9c645d34e32718a417a10214807a` | **NO** |

| ASSET | ORIGINAL / CURATED PR22 BLEND LFS SHA-256 | PASS17 physically validated QA CANDIDATE BLEND SHA-256 | SOURCE VERSION MATCH? |
|---|---|---|---|
| W01 | `80a8999cc0a039eb4f5f907c38c492ec4c4ed49c22a66d44f36fbe14cb1356b2` | `7918bea022a05b0676e97f1995a66cccc28745590941240f5c3efe6b4a5006dd` | **NO** |
| W02 | `ba135eac38faa8d76f70282b8c1613013b64450a9e4f7b72368ade3df8ae4372` | `28c71407f49d84d653a4844b82933599bf1a4083783bcd619804cdc75e9ed360` | **NO** |
| W03 | `77e1a52db293d4fc6b27b27e151c89865eb4473465bfeafefcc85935b810f9cc` | `609c862ea8ee85c0b48a87547a37c442ab8840e3c26a8a0f7494dd7e2c7aac07` | **NO** |

**Why this matters:** Actual [W26 independent non-door full binary audit](https://github.com/C8LyNn/Model-Test/blob/c01/walls-11-wave02-native-export/Assets/C01Architecture/Walls_W01_W04/QA/WAVE26/C01_11_W26_REAL_BINARY_NON_DOOR_MESH_AUDIT.md) and C01-02 44 physical model QA tested the **PASS17 native QA candidate** full-byte FBX set from genuine [Blender4.0.2 Actions #41346578552](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552), [artifact #13098949702](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552/artifacts/13098949702), original archive SHA256 `52bcbcb53d08b587a21bcd582c1e216f640c4346518448537ebbc46cdc8e5e6c`. That evidence: W01 12T, **W02 detailed 572T**, W03 20T, full physical binary source geometry no confirmed actionable defects in tested scopes. The **curated PR22 LFS FBX files are different** and their exact current bytes have **not** acquired equivalent C01-02 current-file final acceptance. Do not transfer a physical PASS from a mismatched candidate SHA to curated SHA. Do not silently overwrite curated W02 with 572T source (12T legacy is not correct for detailed QA variant, but choosing official release identity is an owner decision).

## Required identity decision and gates (not a geometry repair)

1. **C01-00 / C01-10 + C01-03:** formally choose which of the two original sets is an intended *curated production release* versus *isolated QA-only native candidate*, with explicit source path and full SHA for BLEND+FBX. Either preserve both as separately labeled versions or authorize a controlled, documented source promotion after C01-02 physical-byte revalidation. **No automatic promotion in W28.**
2. **C01-02 independent QA:** once target exact source identity is decided, reproduce/approve the matching real full-byte source/FBX, with W02 source→native normal max discrepancy `2.654e-6` (historical strict 1e-6 fails; 1e-5 passes) and UV0/shading criteria explicitly dispositioned. A pointer SHA check is **NOT independent full binary QA**.
3. **Unity 6000.3.14f1 URP C01-10:** actual authorized Unity Editor import, material, scale 1m, pivot and collider checks, prefabs and PlayMode remain `UNITY_NOT_RUN / OWNER_ACTION_REQUIRED`. Existing four-wall PR22 editor smoke includes frozen W04 door-opening: **do not run that path in W28**. Use a future explicitly approved isolated **non-door-only** test. No unlicensed CI rerun.
4. **CLAUDE_DOORS_EXTERNAL_HOLD:** D01/D02/all externally delegated doors/gates, W04 opening, frozen #19/#32 stay entirely out of scope; no reexport, import, test, script or prefab modification and no ship-layout change.

## W28 asset release statuses (format requested by HQ)

| ASSET | SHA | DEFECT | REPAIR | BLENDER QA | INDEPENDENT QA | UNITY | STATUS |
|---|---|---|---|---|---|---|---|
| W01 | curated `42607327…`; native candidate `c644e95d…` | **VERSION_SHA_MISMATCH**, not confirmed mesh fault | NOT_NEEDED/NOT_AUTHORIZED | historical source candidate Blender4 PASS [#41346578552](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552) | candidate static PASS scoped; **curated exact SHA PENDING** | NOT_RUN | **RELEASE_HOLD** |
| W02 | curated `7dfcf0fe…`; detailed candidate `a23f602d…` | **VERSION_SHA_MISMATCH**, normal threshold needs C01-02 ruling; no independently confirmed visible mesh fault | NOT_NEEDED/NOT_AUTHORIZED | historical detailed 572T source candidate Blender4 PASS | candidate static PASS scoped; **curated exact SHA PENDING** | NOT_RUN | **RELEASE_HOLD** |
| W03 | curated `4c268d55…`; native candidate `9dcc8fec…` | **VERSION_SHA_MISMATCH**, not confirmed mesh fault | NOT_NEEDED/NOT_AUTHORIZED | historical source candidate Blender4 PASS | candidate static PASS scoped; **curated exact SHA PENDING** | NOT_RUN | **RELEASE_HOLD** |

**W28 execution in own lane:** current GitHub PR/issue/release/Actions readback, source SHA crosswalk + exact three current pointer file reads. **No new Blender, no geometry edit, no reexport, no QA runner, no Unity, no CI, no merge.** This documentation-only commit records a genuinely new cross-version blocker surfaced by C01-03/C01-02 W28. For canonical 36, independently verified [C01-02 W28 complete 36-row matrix](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/W28/W28_36_CANONICAL_CURRENT_SHA_QA_MATRIX.json) reports `36/36 current FBX LFS OIDs matched / 0/36 FINAL_APPROVED / UNITY_NOT_RUN`, separate from these three architectural assets.
