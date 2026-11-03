# C01 W26 — Global non-door mesh audit / coordination-only master

**EXECUTE, evidence-first.** [Master task #41](https://github.com/C8LyNn/Model-Test/issues/41) · [HQ #36](https://github.com/C8LyNn/Model-Test/issues/36). This isolated Draft branch stores **registry and dispatch only**; mesh repairs belong on each existing producer Draft branch, not here.

## Current repo-scoped audit inventory

| Inventory | Provenance | Count | Limitations |
|---|---|---:|---|
| [Canonical + auxiliary native asset registry](NONDOOR_BASELINE_44.csv) | 36 C01-03 W25 exact current FBX/BLEND SHA records + 8 latest Git LFS pointer pairs confirmed from owner PRs | **44 unique declared assets** | 36 existing previous physical source/FBX reports reused; 8 pairs 16/16 SHA pointer+size checks this execution. This is not 44 new Blender tests or 44 Unity approvals |
| [Generated/legacy model-file discovery](REPO_GEOMETRY_DISCOVERY_CANDIDATES.csv) | Read-only [C01-10 Draft #11](https://github.com/C8LyNn/Model-Test/pull/11) historical integration tree `a41ca3f0630c97a25945abfeb1103c970bc1b143` | **538 candidate source/export file paths** | 24 legacy C01Modular + 152 generated ship V3 + 358 generated ship V4 + 4 combined/source files. These are **FILES, NOT 538 extra unique meshes or approved assets**. Ten protected door/gate/W04 path candidates explicitly excluded without content review; actual count of delegated Claude models may be different |

**Inventory is an opening scope, not proof that there are only 44 non-door models in the whole project.** C01-10/C01-11 must deduplicate generated geometry by *actual input source/parametric generator and immutable content*, determine whether V3/V4 are still used in the current ship, locate any other standalone non-door assets in all non-merged producer branches, and add real distinct assets/versions to #41 before asserting global completion. Generated V3/V4 should be audited using shared source/generator invariants rather than 510 blind per-file reexports; no ship rebuild or layout changes without owner permission.

## Owner lanes — current authoring PRs

- **C01-11:** W01/W02/W03 architectural wall modular mesh; [Draft #22](https://github.com/C8LyNn/Model-Test/pull/22). **W04/door-opening excluded**; collaborate on read-only generated architecture dedup with C01-10.
- **C01-12:** F01/F02/C01 native floor/ceiling [Draft #20](https://github.com/C8LyNn/Model-Test/pull/20).
- **C01-14:** RMP-01/RAI-01 structural models [Draft #24](https://github.com/C8LyNn/Model-Test/pull/24).
- **C01-15:** P15-01..07, [Draft #16](https://github.com/C8LyNn/Model-Test/pull/16)/[#25](https://github.com/C8LyNn/Model-Test/pull/25).
- **C01-16:** P16-01..07, [Draft #12](https://github.com/C8LyNn/Model-Test/pull/12)/[#28](https://github.com/C8LyNn/Model-Test/pull/28).
- **C01-17:** P17-01..07, [Draft #17](https://github.com/C8LyNn/Model-Test/pull/17)/[#23](https://github.com/C8LyNn/Model-Test/pull/23).
- **C01-18:** P18-01..07, [Draft #18](https://github.com/C8LyNn/Model-Test/pull/18)/[#26](https://github.com/C8LyNn/Model-Test/pull/26).
- **C01-19:** P19-01..08, [Draft #15](https://github.com/C8LyNn/Model-Test/pull/15)/[#29](https://github.com/C8LyNn/Model-Test/pull/29).
- **C01-13:** non-door object placement/clipping only, [Draft #39](https://github.com/C8LyNn/Model-Test/pull/39); **all Claude-transferred doors and frozen #19/#32 untouched**.
- **C01-01:** functional/open mesh construction standard, model-specific tolerance, modular interfaces; Draft #31. **C01-02:** independent actual geometry/UV/motion/QA on exact source+FBX bytes, Draft #13. **C01-03:** canonical registry, Draft #27. **C01-10:** actual Unity 6 licensed import/scene/render/physics or explicit `OWNER_ACTION_REQUIRED`, Draft #11.

## Urgent triage before ANY new geometry export

1. **P17-01**: inspect bolt normal/shading candidates under real hard-surface lighting; if intentionally hard edge, do not alter.
2. **P19-07**: classify 18 vertex-on-edge/T-junction candidates with shaded and wireframe proof. Do not indiscriminately merge.
3. **P19-08**: ~0.0039 mm near-endpoint candidate; explicit measured render/mechanical fault required.
4. **P18-03**: previous physical 576/576 hub↔fork render surface intersections; **source render-only visual bearing contract ACCEPTED**, six static cart body colliders, no solid moving wheel colliders. Validate actual visual z-fighting or functional impact before changing model, preserve wheel rotation semantics. No fake PhysX PASS.
5. **P18-07**: coordinate-correct 20 mm visible latch release source contract independent PASS on original FBX; **C01-01 formal +1 mm static vs +20 mm swept envelope acceptance needed**. No blind new FBX export.
6. **P18-05**: W25 actual native independent **23/23 corrected release/lift/hinge motion PASS** on unchanged signed FBX, source gate PASS; **keep current accepted fix**, Unity HOLD, do not repeat old W24 failure unqualified.
7. **P17-03 91/91**, **P19-01 slivers fixed**, **P15-07 purposeful open gauges**, **RMP-01 seated 0.4 mm antis lip**: retain previous PASS if exact SHA is unchanged; don't re-export just to generate another PASS report.

## Gate semantics

`DISCOVERED` != `AUDITED`. `LFS_SHA_POINTER_MATCH` != `FULL_BINARY_HASHED`. `STATIC_PASS` != `MOTION_PASS`. `OFFLINE_CSHARP_PASS` != `UNITY_EDITOR_PASS`. `PRODUCER_PASS` != `INDEPENDENT_QA_PASS`. `INDEPENDENT_PASS` != `RELEASE_APPROVED`.

For a confirmed defect, owner changes only its own real native file; runs physical Blender4 native save→FBX export→FBX reimport with old/new exact SHA and mesh/UV/pivot/material/animation parity; publishes before/after shaded and wireframe evidence; C01-02 independently verifies current bytes and signs. If no defect, record exact SHA and prior evidence; no gratuitous rebuild. Full Unity acceptance only through **authorized Unity 6000.3.14f1 Editor**, not a mock or CI skip. No unapproved merge.

## Explicit restrictions

**CLAUDE_DOORS_EXTERNAL_HOLD:** do not modify, QA, import, test, export or alter D01/D02/any doors or gates entrusted to Claude; do not touch frozen PR #19 and #32, W04 door-opening, production gate interfaces or ship redesign. **No new models. No edits to source geometry on this coordination branch.**

**Current honest W26 milestone:** 44 exact known asset row baselines + 538 unclassified historical model-file paths discovered, no new mesh fixes claimed and no Unity execution claimed. Next: owner targeted Blender/FBX tests and repairs, independent QA, source dedup and Unity owner run.
