# C01-14 — PASS 05 / Genuine binary FBX verification and CI failure isolation

**30 Oct 2026.** Production owns only two *non-approved, optional* existing C01-14 structural reference meshes: RMP-01 and RAI-01. They are **NOT** part of the 36 P15–P19 interior meshes in #30/#33. No model created, no retopology/forced welding, no ship scene edited, no merge. Draft PR #24 continues.

## Actual executed tests, with evidence scope

Existing original Blender 4.0.2 producer execution [41089475908](https://github.com/C8LyNn/Model-Test/actions/runs/41089475908) successfully opened real native BLEND files, generated binary FBX 7400, imported FBX into Blender, and compared surface triangles at 1e-4. Its real before/after images and source files remain committed to `Pass03/`.

**NEW PASS05 executed locally (outside Actions):** read-only Python binary parser on the exact bytes of both Blender-origin binary FBX 7400 downloaded from run 41089475908, verified file SHA-256, fully parsed every `Objects/Geometry` / `PolygonVertexIndex` and the `LayerElementNormal` and UV/UVIndex streams. This is direct FBX evidence (not GLB or viewer reconstruction) and a static parser test, **NOT a new Blender/Unity engine run**. Reproducer `Tools/C01Structures14/fbx_raw_pass05.py`; local proof is delivered as a downloadable ZIP in the C01-14 conversation.

| Model | Before→after V | E | Faces | Tris | FBX parts | 0-area triangles | Duplicate faces | Nonmanifold edges | Normal-vs-face mismatch | UV0 missing/degenerate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RMP-01 | 48→48 | 108→108 | 72→72 | 72→72 | 6 (one invisible collider proxy) | 0 | 0 | 0 | 0 | 0 |
| RAI-01 | 32→32 | 72→72 | 48→48 | 48→48 | 4 (independent rails/posts) | 0 | 0 | 0 | 0 | 0 |

Both 120/120 actual FBX triangles are **explicit triangles**, no original n-gons; 0 loose vertices, unexpected boundaries or inconsistently oriented shared edges. All per-loop normals finite and aligned to triangles (cosine approximately 1), UV indices in range, no degenerate UV triangles. Unchanged source topology has 0 defects before and after in documented per-object checks, **0 repairs actually required or performed**. Separate intentional rail/post volume contacts and dedicated ramp collision proxy remain as declared in PASS04.

## Exact verified native binary SHA-256

- RMP-01 `.blend`: `7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa`
- RMP-01 `.fbx`: `97f0b125313057f4ecf601dd60a02b4d3f0d55b87c1713d71a0adbedcc6d1443`
- RAI-01 `.blend`: `8a2f16205874f8485adb87c5251f6adbba3f51816936c0bf1964ad40a47850a5`
- RAI-01 `.fbx`: `b51c3c012f5680de2d02c2deaf5c67c4ae9a12bb7e8347f179ed08d181a7e103`

## CI runner failure diagnostics — P0

Observed PASS04 run [41094351876](https://github.com/C8LyNn/Model-Test/actions/runs/41094351876) and its rerun: **job failed before allocation**. Actual REST evidence:
- `runner_id=0`, `runner_name=""`, `steps=[]`; 2 failed jobs.
- GitHub billing timing: **total_ms=0**, run duration 5000 ms.
- Job check-run `conclusion=failure`, no output summary or executed step logs.
- Control run [41089475908](https://github.com/C8LyNn/Model-Test/actions/runs/41089475908): `runner_id=1000012662`, 11 actual steps and SUCCESS.
- PASS05 switched one workflow runner label `ubuntu-24.04` → `ubuntu-latest` as an allocation diagnostic: [41099050445](https://github.com/C8LyNn/Model-Test/actions/runs/41099050445) also failed before any steps. This is **not** a Blender failure or a geometry failure; exact infrastructure root cause (account limits vs service/runner allocation) cannot be determined from available run data. C01-00 reports the same in multiple distinct repo workflows.

**Local alternate execution:** available conversation container lacks the Blender and Unity executables; apt/PyPI downloads were attempted and cannot resolve public domains, so native Blender PASS05 execution is **NOT RUN**, not claimed. A Windows PowerShell reproducible native runner can be executed on a workstation with Blender 4.x and checked-out branch. GitHub-side producer already has real earlier Blender PASS03 evidence. A static FBX parser does not replace an in-engine or Blender run.

## Remaining gates

- PASS05 SHA-pinned actual binary FBX indexed mesh/normal/UV0 audit: **PASS static** for RMP and RAI.
- Actual Blender 4.x FBX roundtrip: **PASS earlier PASS03**, **NOT RUN in PASS05 due to runner/unavailable local Blender**.
- Exhaustive mesh-mesh BVH/overlap beyond PASS04, Unity 6 URP import, controller/headroom clearances: **NOT RUN**.
- Independent C01-02 QA / C01-00 structural approval: **BLOCKED**. Draft PR #24 remains open, no merge.
- **No impact on 36-asset QA matrix**, P19 and P16 repairs belong to their assigned owners.

**Next actual unblocker:** investigate repo/account Actions billing / hosted-runner allocation and check status notifications; then run `Tools/C01Structures14/verify_pass04_exact_sources.py` in actual Blender 4.x against the exact committed `Pass03` source tree, or use the Windows local runner. Submit resulting exact SHA-pinned logs to C01-02 for independent review.
