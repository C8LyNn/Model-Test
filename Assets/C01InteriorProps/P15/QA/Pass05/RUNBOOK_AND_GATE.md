# C01-15 PASS05 — Real-asset, fail-closed execution status (W01)

Owner: C01-15. PR: https://github.com/C8LyNn/Model-Test/pull/16. No new mesh; no geometry/pivot/UV/material rewrite; no merge.

## Measured and unmeasured gates
1. **Previous PASS03** real Blender 4.0.2 native .blend open, binary FBX re-export and reimport PASS for all 3 pinned assets, documented under QA/Pass03.
2. **Current PASS05 source provenance** — actual GitHub LFS OID receipts match archived PASS03 native source SHA on all 3/3 model IDs. Exact FBX SHA256 receipts below. These are verified pointer/OID records, NOT newly hydrated file bytes or runtime proof.
3. **PASS04 new native test** — NOT RUN. Retry of https://github.com/C8LyNn/Model-Test/actions/runs/41094609379 succeeded as a GitHub API request, but runner assignment failed, 0 steps executed. Other independent project jobs fail before allocation. Cause unknown; GitHub Actions usage/budget/payment blocker plausible on a private repository, no owner billing access exposed via this connector.
4. **PASS05 local Blender** — NOT RUN. Current execution container has no Blender, no working package/index DNS resolution and no hydrated private Git LFS .blend/.fbx files. No QA can be claimed from this environment.
5. **Unity 6 URP** — NOT RUN. **Independent C01-02** — NOT RUN.

## Exact model receipts

| Model | Native .blend SHA256 | Production binary FBX SHA256 | Past native FBX check | PASS05 native Blender |
| --- | --- | --- | --- | --- |
| P15-01 | `4109a4734a58ef905cebb49229138957a00657b6cddf41249f855eefeec3973a` | `657836b58af85c6bcc3ecfe7fa59d32b4ae4dbd8ceb259fb375c8c3ce4d17274` | PASS | NOT RUN |
| P15-02 | `ed6d25c498b47a7bc259262cf23f2fe6cf07a10996087197306d56bef54dc116` | `16f099e6821e41cee2c7079f736261caef481456ded2b469fdc01df55592a742` | PASS | NOT RUN |
| P15-03 | `c76b4911e885234f18756669c4492a195ab9fde2ea2b3911683f241c5e7b503e` | `95d2730197a7c86bd3a59c1748a1df6df2a276ef9a9554d0df3ad0b769f6f414` | PASS | NOT RUN |

## To execute (real Blender 4.x, from checked-out correct private PR branch)

```powershell
git lfs pull
python Tools/C01MeshPass05/P15/local_blender_gate.py --wave W01 --blender "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
```

The CLI locates Blender from PATH/BLENDER_BIN automatically if --blender is omitted. It rejects:
- wrong branch, LFS pointers instead of real `.blend`/`.fbx`, missing files or mismatched SHA256,
- Blender version other than 4.x, nonzero Blender exit code, incomplete asset results, or report digests that differ from the source and actual FBX binary hashes.

Successful real execution writes `QA/Pass04/PASS04_SUMMARY.json`, `QA/Pass04/PASS05_EXECUTION.json`, `PASS05_BLENDER_STDOUT.txt`, `PASS05_BLENDER_STDERR.txt` and per-ID genuine native Blender audit reports. It does **not** rewrite original .blend or .fbx assets. Commit reports to this existing PR only after inspecting, and request C01-02 exact SHA retest.

Native BVH overlap and exact coplanar triangle contacts are candidates requiring review, never silently welded and never automatically independent-QA-approved. PASS05 native and Unity currently **NOT RUN / BLOCKED**.
