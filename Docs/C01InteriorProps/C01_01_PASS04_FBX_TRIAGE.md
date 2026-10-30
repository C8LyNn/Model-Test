# C01-01 — MESH REPAIR / PASS04 — REAL FBX TRIAGE

**Role:** C01-01 standards/technical interface. **Source:** #33 and parent #30.  
**No model authorship or ship changes. No merge.** Scope: three identified export blockers P19-05, P19-07, P19-08, then enforce same policy for all 36.

## Provenance and execution

Downloaded C01-19's **real binary FBX** from native Blender CI run [41088782744](https://github.com/C8LyNn/Model-Test/actions/runs/41088782744), artifact **12993051362**, not from the reconstructed viewer. Decoded FBX 7400 actual Geometry/Vertices/PolygonVertexIndex streams locally with read-only Python binary parser (no geometry replacement). Numeric results and exact binary SHA-256:

| Asset | Mesh objects | Original FBX polygon faces | Faces >4 corners | Maximum face corners | Degenerate naive-fan triangles | Original binary FBX SHA256 |
|---|---:|---:|---:|---:|---:|---|
| P19-05 | 7 | 66 | 3 | 16 | 1 | `64156363cb5007831c243aeea50d5e59c862cc98b27cb12dd2f8af5b3c019892` |
| P19-07 | 6 | 78 | 16 | 20 | 19 | `88b32fe2f5ddf981eecdc0469088f4e23e07c4c605a1db7bb9689a0b6011d585` |
| P19-08 | 6 | 100 | 35 | 12 | 7 | `cbbea5435f8326e06fb5f43237986594df044c0e3ff94100fc44f856dce35ae2` |

This independently reproduces the **triangulation ambiguity risk**, not a tested Blender/Unity failure: degenerates above arise from a conservative **naive triangle fan**, not Blender's actual tessellation. All three require source-side explicit triangulation and fresh export. Old binary hashes are locked to the archived artifact, **not** to the independently changing PR #29 branch head.

## Normative PASS04 acceptance, C01-01

Updated existing `MESH_TOPOLOGY_INTEGRITY_STANDARD_v1.0.md` with PASS04 amendment. For P19-05/07/08 only, every source Blender Mesh face and every reimported FBX face must have exactly 3 corners, valid winding, UV0, nonzero area and unchanged identity/shape/parenting/pivots/materials. `Tools/c01_mesh_repair/triangulation_gate.py` is the added **real Blender native source+FBX** check; it does not repair producer mesh, nor grant C01-02 QA approval.

C01-19 has independently committed native Blender triangulation script in its existing PR #29 (`Assets/C01InteriorProps/C01-19-W02/Source/pass04_triangulate.py`), with intended no-design-change assertions. Await actual successful execution, new SHA-pinned .blend and binary FBX, topology before/after, source wireframe screenshots, and independent C01-02 retest. Detect current 8 and 2 P19-07/08 T-junction **candidates**: review individually, not unconditional FAIL/weld.

## CI note — NO false PASS

New C01-01 GitHub Actions run [41094424733](https://github.com/C8LyNn/Model-Test/actions/runs/41094424733), including second attempt, failed **without executed steps/logs** in the first job. Thus **native PASS04 Blender tool execution is NOT_RUN**; no fabricated green CI. Previously successful native Blender run [41091176065](https://github.com/C8LyNn/Model-Test/actions/runs/41091176065) is PASS03 evidence for its narrower six assets, not a PASS04 triangulation proof. The independent binary FBX parser described above **was actually run locally on three real archival FBXs** and is source-static evidence only.

## Handoff / blockers

C01-19: keep #29 draft, produce explicit source triangles and binary FBX; verify UV0 and normals are not lost and preserve silhouette. C01-02: after real repaired file SHAs, independently run triangulation/UV/winding/geometry checks; hold three FAIL P1 until evidence. C01-10: Unity 6 URP actual prefab/collider/navigation tests remain NOT_RUN. C01-03: record old→new FBX/source SHA without accepting archived evidence as newest. C01-00: issue #33 / #30 remain OPEN; 0/36 final QA approved at latest verified independent QA baseline.

**C01-01 PASS04 technical standard: PUBLISHED. Native Blender PASS04 gate: NOT_RUN; actual old FBX binary scanner: EXECUTED (3/3 old failures reproduced); source repairs: OWNED BY C01-19; independent QA: PENDING; Unity: NOT_RUN.**
