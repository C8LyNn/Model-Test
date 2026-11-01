# C01-03 — DETAIL PASS17 / FINAL SOURCE INTAKE, VERIFIED BLENDER RUNS AND NATIVE QA HOLD

**Snapshot:** 2026-11-01 · **HQ:** https://github.com/C8LyNn/Model-Test/issues/36  
**Library Draft:** https://github.com/C8LyNn/Model-Test/pull/27  
**Exact-machine receipt:** [C01_03_INCREMENTAL_SOURCE_NATIVE_QA.json](./C01_03_INCREMENTAL_SOURCE_NATIVE_QA.json)

## Execution completed (C01-03)

1. Fetched immutable, latest authored sources and recomputed actual source-file SHA-256 (NIST empty+abc vector 2/2 PASS) for P15 shared spec v0.1.6, P17-03 glTF revision, P16-06 OBJ revision, and P18-01/02/03 OBJ revisions. All 6 pinned Git blob IDs matched the current exact source revisions and 6/6 hashes were recorded in machine QA receipt. **36 asset IDs unchanged.**
2. Verified **two actual Blender 4 workflow successes**: C01-15 [run #41344475164](https://github.com/C8LyNn/Model-Test/actions/runs/41344475164), C01-18 [run #41344872313](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313). Producer jobs report genuine Blender scene save, binary FBX export and producer reimport/validation passing, with LFS commits on isolated producer branches. These are six native **candidates**, NOT six independent final asset approvals.
3. Independently fetched **12 Git LFS text pointers** for P15-01/02/03 and P18-01/02/03 (6 BLEND + 6 FBX), read matching complete SHA-256 OIDs and sizes, and matched each to the corresponding producer workflow/metadata. The C01-03 GitHub connector returned **pointer TEXT, not hydrated binary payloads**, so do not falsely report local binary SHA recalculation or independent native mesh QA.
4. Reconstructed offline preview from **10 immutable REAL OBJ/glTF before/after source snapshots**, then detected producer commits and updated four affected after-snapshots plus added P17-03 BEFORE, for **11 versions: 6 AFTER (5384 triangles), 5 BEFORE, 9704 source triangles total**. Self-contained offline [REAL_SOURCE_INTERACTIVE_VIEWER.html](./REAL_SOURCE_INTERACTIVE_VIEWER.html), WebGL, model/part selection, orbit, zoom, shaded/wireframe/both. Coordinates quantized to **0.01 mm** for preview only. Uses no legacy FBX, stand-in meshes, CDN or external downloads. **Browser rendering runtime QA NOT_RUN**; do not promote to pixel-perfect Unity/Blender visual evidence.
5. GitHub Actions formerly failed to allocate runners; reran C01-16 W02 job [41138429511 attempt 2](https://github.com/C8LyNn/Model-Test/actions/runs/41138429511). This time Blender 4.0.2 executed, but FBX exporter raised `ModuleNotFoundError: No module named 'numpy'`; one preliminary P16-04.blend was saved in a failed run artifact, **no validated FBX**. Prepared isolated CI-only [Draft PR #37](https://github.com/C8LyNn/Model-Test/pull/37) based on C01-16 W02; adds `python3-numpy` to apt install and a Blender Python smoke test. **No producer PR merge or patch deployment** — fix must be explicitly integrated and retested before C01-16 can claim native output.

## Current geometry and independent QA differences

| Existing asset | Newest real authored source evidence | Native state |
|---|---|---|
| **P15-01/02/03** | Shared spec v0.1.6, source SHA-256 `9394e90c72b78ce8d33e0629e383fe32b9faafb0a1cbf3fcb817281623cf05f3`; P15-02 now 34 parts | Real Blender4 producer workflow success; BLEND+FBX LFS OIDs verified; **independent binary QA pending** |
| **P16-06** | OBJ SHA-256 `63ab5763d2a5b711a94275f86e6ca5c693a43d1a0e9fd041b9784389fdaf7283` | CI exporter missing NumPy, isolated fix #37 unmerged, **FBX release BLOCKED** |
| **P17-01** | PASS16 actual guide repair retained, 380 instanced triangles | Blender final binary revalidation and Unity still pending |
| **P17-02** | Unmodified glTF, 536 instanced triangles | Final native QA pending |
| **P17-03** | Source glTF SHA-256 **`4949558f7eb03d9c70aee938acb2942fe21fc50b772d8412041fa9c521ad9abb`**, 424 triangles; producer adjusted Base and SocketRetainer coplanar planes without changing pivot count | **Independent SOURCE retest needed**: prior C01-02 PASS17 found four open boundary edges in each of LeverShaft and LeverGrip; moving-pivot/Unity sweep NOT_RUN |
| **P18-01** | SHA-256 `4fd8fc54e37f9941142aed85559ecef077cdfc97e2326b153dfb2ca91fa7b566`, 47 parts / 980 triangles | Blender exported candidate, independent binary QA pending |
| **P18-02** | SHA-256 `b7ee7803f625c2ec48901a0ad6739248e22a59ac56d7dada5e20847604e4d2fc`, 59 / 1284 | Same, inspect opposite-facing internal faces and real materials |
| **P18-03** | SHA-256 `4446cfc77a6c4a9de4cf7c172ae06395b9dad9e39941566046d952eab0f16a6a`, 63 / 1780 | Same, recheck caster/axle sweep and Unity floor contact |

**P18 total: 169 source parts, 4044 triangles** (prior PASS16: 159 parts, 3764 triangles). Earlier independent C01-02 PASS17 report inspected exactly these P18 source blobs, checked source topology and reported new functional contact checks but **did not approve new hydrated native FBX**. The report may refer to old FBX OIDs because it predates successful producer export; treat that binary observation as historical, not an indication the newer LFS OIDs are absent.

**P19-07 visual vertex-on-edge HOLD persists**. Existing P19-01 offline-format candidate cannot be promoted to Blender-application export without actual verified evidence. No new model IDs and no ship geometry modifications.

## What blocks release

| Gate | Current outcome |
|---|---|
| Latest authored SHA-256 from real UTF-8 source (6 freshly computed) | **6/6 PASS** |
| P15/P18 new BLEND and FBX Git LFS pointer paths | **12/12 verified OID references** |
| Blender application native producer execution | **6 models in 2 successful runs** |
| P16 Blender FBX export workflow | **FAIL — NumPy missing; Draft fix #37 not yet integrated** |
| Current preview offline source data fidelity | **11/11 immutable Git blob matches; 9704 triangles** |
| Viewer WebGL browser runtime/pixel comparison | **NOT_RUN** |
| Genuine Blender shaded/wireframe **AFTER** for all updated models | **NOT_FULLY_VERIFIED** (P15 producer preview candidates exist) |
| C01-02 independent exact hydrated BLEND/FBX geometry, UV, shading, pivots and moving clearance | **NOT_RUN for 6 candidates** |
| Unity 6000.3.14f1 URP actual model/prefab import | **NOT_RUN** |
| Production release, all 36 models | **0/36 approved — BLOCKED** |
| PR merging | **NONE; all work remains Draft** |

## Actions for assigned owners

- **C01-00:** review [Draft PR #37](https://github.com/C8LyNn/Model-Test/pull/37), coordinate C01-16 to integrate missing NumPy CI fix into its own W02 branch without unrelated changes, and have it rerun genuine exporter. DO NOT merge producer branches into ship layout before QA.
- **C01-01 / independent C01-02:** fetch hydrated LFS BYTES for the six newly exported candidates, recompute SHA-256 on physical bytes, perform exact Blender/FBX topology, UV0/normals/material, coplanar/oblique intersection, supporting contacts and pivot QA. Pay attention to P17-03 open boundaries, P18-02/03 opposite-facing mating planes and P19-07. The CI producer PASS alone is not independent QA.
- **C01-10:** run actual Unity6 URP tests of imported FBX, shared pivots/doors/wheels/rotors and gameplay colliders, then report exact imported FBX SHA and tests. Do not alter vessel architecture.
- **C01-03:** update canonical approved SHA only **after** independent native QA and actual Unity import. Archive current source snapshot rather than rewriting baseline statuses without a final signed gate.

**Copyright:** Existing manufacturer references remain link-only, never copy external vendor CAD/images/product dimensions 1:1.
