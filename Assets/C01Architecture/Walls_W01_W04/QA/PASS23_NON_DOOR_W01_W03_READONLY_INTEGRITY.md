# C01-11 — DETAIL PASS 23 / WAVE 23 — non-door legacy wall integrity

**Repository:** C8LyNn/Model-Test · **Owner:** C01-11 WALLS & ARCHITECTURE · **Existing [Draft PR #22](https://github.com/C8LyNn/Model-Test/pull/22)** · frozen input HEAD `c096c6c7d0b8154c4ae9ff02f85ac8f1b75b01a3` · **HQ [#36](https://github.com/C8LyNn/Model-Test/issues/36)**.

## Owner handoff and scope restriction

The owner assigned door and gate model production to Claude: `CLAUDE_DOORS_EXTERNAL_HOLD`. **Do not touch D01/D02, door/gate assets, door-opening W04, door/gate prefabs/colliders/hinges/pivots/materials/scripts, or ship layout.** W23 C01-11 activity was limited to a **read-only** Git LFS pointer / Git object identity check of non-door **W01 full wall, W02 wall panel, W03 90° corner**. No changes to Blender/FBX sources or import tools; no new mesh, export, runner rerun, Unity test or merge.

## Actual W23 checks against exact immutable PR22 HEAD

Performed six real GitHub `fetch_file` reads for `.fbx` + `.blend` entries on pinned commit `c096c6c7...`. Parsed exact `git-lfs.github.com/spec/v1` text, `oid sha256` (64 hex digits) and `size`. Compared each exact LFS SHA256 against the previous W22 GitHub record **and** Git blob SHA-1 for the pointer object. Result: **6/6 SHA pointer and Git blob identity checks PASS**, all six unchanged. This proves source references stable, **NOT a fresh full-byte hydrated native binary hash or geometry inspection**.

| Asset | Format | Current Git LFS SHA-256 OID | Pointer Git blob SHA-1 | LFS size (bytes) | W23 result |
|---|---|---|---|---:|---|
| W01 | FBX | `4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f` | `200ecae7566bdd280385d41bb636d15bb86c2ec6` | 15452 | EXACT MATCH |
| W01 | BLEND | `80a8999cc0a039eb4f5f907c38c492ec4c4ed49c22a66d44f36fbe14cb1356b2` | `8209e7ff7428e70e74a0bb2ccdc5c4cc9c414b0d` | 862816 | EXACT MATCH |
| W02 | FBX | `7dfcf0fe84952e607a74845ad193acfbb9f4fc029e7f168a94a7bac2edacb78b` | `b6e1f3cec151eefebf02d99b1a66c6f310b9e5eb` | 15452 | EXACT MATCH |
| W02 | BLEND | `ba135eac38faa8d76f70282b8c1613013b64450a9e4f7b72368ade3df8ae4372` | `1dff3b985bbd8402ca3e5b987cf058cb250226ec` | 884120 | EXACT MATCH |
| W03 | FBX | `4c268d554d4e5948ea1927e29b0d32fc581a6f9f14f41fd070bf116a8eb7864c` | `43d583ad0a50fc999ee1ef49535200234dbee993` | 15612 | EXACT MATCH |
| W03 | BLEND | `77e1a52db293d4fc6b27b27e151c89865eb4473465bfeafefcc85935b810f9cc` | `0eaf120848c2ec6100c164b62377355899d5c83c` | 906016 | EXACT MATCH |

## Historic physical Blender evidence — not newly executed

Previous actual [Blender 4.0.2 GitHub Actions #41346578552](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552) completed success; original artifact #13098949702, 4,771,746 B, `sha256:52bcbcb53d08b587a21bcd582c1e216f640c4346518448537ebbc46cdc8e5e6c`, was reported unexpired at W23 query. Prior PASS17 actual native generated outputs are **different bytes** from current tracked *legacy/prototype* FBX pointers, notably detailed W02 572 triangles native FBX `a23f602d8dd61a6dc61ee52af347e472f2e6f6ce546988f50409911d1b11a317` versus tracked legacy W02 pointer `7dfcf0fe...`. The detailed model is **not** auto-promoted to production. Previous normal-parity observation for detailed W02 at 1e-6 strict versus 1e-5 relaxed tolerance is still awaiting C01-02 approval. W23 did not download or re-parse the artifact bytes and does not claim renewed PASS17 motion, topology or Blender coverage.

## Release gate

- Non-door W01/W02/W03 tracked Blender/FBX pointer identity: `6/6 MATCH` at exact commit. **No new model or geometry defect confirmed**.
- Door-related W04 and all Claude-assigned D01/D02/gates: `EXTERNAL_OWNER_FREEZE / NOT_TESTED / UNCHANGED_BY_C01_11`.
- C01-02 final non-door walls QA and W02 native normal tolerance: `PENDING`.
- Actual Unity Editor compile/import/prefab/scene/EditMode/PlayMode: `UNITY_NOT_RUN`. C01-10's separate licensed non-door P16-01/P17-02/P18-01 slice remains P0 and requires owner's authorized Unity workstation, not repeated CI.
- W01/W02/W03 are **outside 36 P15–P19 prop IDs**; release count remains `0/36 FINAL_APPROVED` until canonical independent/runtime gates.
- Existing Draft PR #22 retained, **NO MERGE/NO RELEASE**.

**Handoff:** `C01-11 | W01/W02/W03 | tracked Git LFS BLEND+FBX OIDs unchanged 6/6 | source refs PASS (not hydrated binary QA) | Unity NOT_RUN | Claude door freeze respected | independent C01-02 still PENDING | no modifications to native models`.
