# C01-03 / PASS03 — immutable BEFORE asset evidence

**Evidence run:** https://github.com/C8LyNn/Model-Test/actions/runs/41089950011 — ten producer LFS checkouts, byte header checks and SHA-256 receipts; all jobs SUCCESS.

**Inventory result:** 36 models, 36 verified original FBX hashes, 29 verified original Blender hashes, 7 unresolved native Blender sources (P16-01–07). **0 AFTER versions repaired or independently QA-approved.**

## First six (P0) — actual original bytes

| Asset | Origin PR | Blender SHA-256 | FBX SHA-256 | Before V/E/F/T | After V/E/F/T | Blender / Unity | Independent QA |
|---|---|---|---|---|---|---|---|
| P17-04 | [23](https://github.com/C8LyNn/Model-Test/pull/23) | `deec97aa786e3f2e6ce4f1f1eaaeb034da52bb9c3b8d8163e9836e50304f96f3` | `0b58f14caa2f6a4151430fd4457607061f6e5ad3a31978073f87e2301cb264c8` | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| P17-05 | [23](https://github.com/C8LyNn/Model-Test/pull/23) | `6b85a1e6b81b0aaf790cce83560658f4970062f853ed59337749c29993b427a3` | `b2ff6601d45e936ede795696e53aaf88c4805e4519222f59ecef86f720df73ac` | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| P18-04 | [26](https://github.com/C8LyNn/Model-Test/pull/26) | `4a0531a877df0cbbcc2078b02297efccd966611e736bf70480a7572c6602ec52` | `97298f0b49058f84eb2b746f8ac50af73f056f8bea43f11dde24fe9e550d1742` | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| P18-05 | [26](https://github.com/C8LyNn/Model-Test/pull/26) | `495260c299fa9afea63516549d50bcf3a581e1f3735409602e56859b41d23c5e` | `2f4dbc8e7077e15b12f37f9fca64a0bc08e3ebde05776e602542e6efb648295e` | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| P19-07 | [29](https://github.com/C8LyNn/Model-Test/pull/29) | `8d99c6286c6e28182742e69293eb393dc30c6abe9bb50fa77dee3a77fae9928a` | `2c180a3607c49b43c48a14e4cf58f2b825f44b56e2e86cc02b17e6d96d6c8d43` | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| P19-08 | [29](https://github.com/C8LyNn/Model-Test/pull/29) | `5b00c434831ef27f87e03b7716916b31893f8eb4f8733b7c95cc543510a27ce9` | `65bc32a8f280941b24e8070a706e5733b30fde25d042f4cdd4398022e2edaf44` | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

**Important:** the six images shown in the earlier interactive viewer were geometric reconstructions; those visuals cannot establish a defect in these original files. Actual BEFORE wireframe views, per-part topology counts and repair results must be produced in Blender against the hashes above.

## Reproducibility

- Baseline `repair_ledger.json` records exact producer branch + commit SHA, source and FBX paths, byte size, SHA-256, GitHub Actions run/job provenance per model.
- The original working revisions are frozen as Git refs. Repaired model must use a new, separate commit/version with its own hashes. No approved model may be overwritten.
- `mesh_topology_evidence.schema.json` describes actual Blender API per-part metrics and explicit intentional-open exceptions, but **does not constitute measured geometry**.
- No Blender UI/open or re-export was executed by C01-03. No Unity 6 URP import was executed by C01-03.
- Independent C01-02 must retest real AFTER files and sign their FBX hash; C01-10 must show original geometry, not reconstructed prisms.

## Missing source-path resolution

| Family | IDs | Known original FBX | Native Blender source | Action |
|---|---|---|---|---|
| C01-16 W01 | P16-01–03 | SHA verified | Unresolved in pinned PR #12 | Producer supply real `.blend`; new immutable commit |
| C01-16 W02 | P16-04–07 | SHA verified | Unresolved in pinned PR #28 | Producer supply real `.blend`; new immutable commit |

## Release state

**C01-03 SOURCE BYTE AUDIT: PASS (29 complete pairs / 7 partial).**

**MESH REPAIR / Blender roundtrip / Unity / QA: NOT RUN or BLOCKED.**

No ship geometry changes, no producer mesh edits, no merge.
