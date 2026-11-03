# C01-10 / PASS10 — ACTUAL RECOVERED REAL BLEND + BINARY FBX QUARANTINE

**Execution evidence, not another script-only handoff.** On 2026-10-30, C01-10 downloaded actual ZIP bytes of six PREVIOUSLY successful native Blender CI artifacts (five new ZIP downloads + one existing W01), unpacked them locally, verified zip CRC, and independently parsed real FBX 7400 structures. The ten allowed existing assets were copied byte-for-byte to a newly written user-downloadable quarantine ZIP: `C01_PASS10_VERIFIED_10_REAL_BLENDER_FBX_QUARANTINE.zip` (1,035,886 bytes), **ZIP SHA-256 `b18f4154d5dbbfc27b6b43f182e661b56f7cd2ee62b1f05d1954d6f6e19806e7`**. It is a chat-delivered attachment, **NOT committed into GitHub or a producer PR**, and its sandbox link should not be guessed by GitHub.

### The REAL source files actually recovered

One original native `BLENDER-v400...` `.blend` file and one genuine `Kaydara FBX Binary` file for **each** of: P17-01, P17-02, P17-03, P17-04, P17-06, P17-07, P18-04, P18-05, P18-06, P19-06. **10 BLEND + 10 FBX**; real FBX content = **147 Geometry Mesh nodes / 2,068 estimated indexed triangles**. Every FBX SHA-256 was calculated from its actual full binary bytes and exactly matches the current FBX Git LFS `oid sha256:` at the pinned producer revision. Native `.blend` byte SHA computed, header checked, original GitHub Actions provenance pinned. Per-asset full hashes, mesh parts and triangle counts: [`REAL_NATIVE_RECOVERY_10.csv`](REAL_NATIVE_RECOVERY_10.csv).

Prior successful original runtime sources used:

- C01-17 W01 Blender [run 41089779966](https://github.com/C8LyNn/Model-Test/actions/runs/41089779966), ZIP artifact `12992848775`.
- C01-17 W02 Blender [run 41088800979](https://github.com/C8LyNn/Model-Test/actions/runs/41088800979), ZIP artifact `12991739268`.
- C01-18 W02 Blender [run 41089810123](https://github.com/C8LyNn/Model-Test/actions/runs/41089810123), ZIP artifact `12994285353`.
- C01-19 W02 Blender [run 41088782744](https://github.com/C8LyNn/Model-Test/actions/runs/41088782744), ZIP artifact `12993051362`.

**Independently executed C01-10 on actual binaries:** original ZIP integrity 4/4 used sources plus two other recovered producer archives; all ten FBX actual 7400 file headers/size/hash/parsed `Geometry`/`Vertices`/`PolygonVertexIndex` present; **10/10 0 out-of-range polygon indices**, 10/10 UV0 and normal layer headers present for every counted mesh, and 10/10 no naive-fan zero-area candidates. This is a preliminary structural import preflight, **NOT independently approved C01-02, and does NOT check appearance, fully validate UV value correctness, or substitute a genuine Blender/Unity run**.

### Contents of chat ZIP

- Ten true FBX files: `Assets/C01InteriorProps/Pass04Incoming/<ID>/<ID>.fbx`, with no source geometry modifications.
- Ten corresponding original native `.blend`: `C01_PASS10_REAL_NATIVE_REFERENCE/<ID>/<ID>.blend`, as historical reference only.
- A real file-derived `C01InteriorProps_QA/PASS04/staged_sources.csv` containing 10 exact source commit IDs, real binary FBX SHA and paths, plus per-asset complete provenance JSON and clear qualifications.

Unpack into a **checkout of existing Draft PR #11** when a computer has Unity 6000.3.14f1 URP; run menu `C01/Mesh Repair PASS04/00` then `01` then `02` to inspect and create QA-only prefabs and scene. **No real Unity runtime was available in this conversation; those files were not generated, the importer not compiled in Unity.** A staging receipt does not grant production approval.

### Strict block/acceptance semantics

The upstream manifest remains **36/36**, of which 17 `BLOCKED`: 7× P16 no native source/binary, 5× P19 export topology P1 risks, 1× P17-05 old FBX vs changed glTF, 4× P18-01/02/03/07 old FBX vs edited sources. The other 19 remain QA-only candidates, but only **ten** matching real binary+native source pairs have been hydrated here. The **remaining nine candidate sources** (P15-01..07, P19-03/04) were NOT downloaded and are **not included** in the ZIP. Some P18-05/06 authoring generator dimensions were synchronized to the previous genuine FBX, not newly re-exported; final native QA still applies.

**NEW repaired mesh count in C01-10: 0. NEW Blender-produced source exports: 0. Actual archived binary sources recovered: 10. Actual Unity import/test/prefabs: NOT RUN. Full C01-02 acceptance: 0/36.** This is a real-file recovery and SHA-verification output, not a claim of completed PASS10 repairs.

No Wave03, no copied B01 assets, no new 3D models, no ship geometry or prefab edits, no PR merge.
