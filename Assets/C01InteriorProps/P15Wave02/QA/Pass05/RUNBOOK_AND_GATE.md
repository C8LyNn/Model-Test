# C01-15 PASS05 — Real-asset, fail-closed execution status (W02)

Owner: C01-15. PR: https://github.com/C8LyNn/Model-Test/pull/25. No new mesh; no geometry/pivot/UV/material rewrite; no merge.

## Measured and unmeasured gates
1. **Previous PASS03** real Blender 4.0.2 native .blend open, binary FBX re-export and reimport PASS for all 4 pinned assets, documented under QA/Pass03.
2. **Current PASS05 source provenance** — actual GitHub LFS OID receipts match archived PASS03 native source SHA on all 4/4 model IDs. Exact FBX SHA256 receipts below. These are verified pointer/OID records, NOT newly hydrated file bytes or runtime proof.
3. **PASS04 new native test** — NOT RUN. Retry of https://github.com/C8LyNn/Model-Test/actions/runs/41094615625 succeeded as a GitHub API request, but runner assignment failed, 0 steps executed. Other independent project jobs fail before allocation. Cause unknown; GitHub Actions usage/budget/payment blocker plausible on a private repository, no owner billing access exposed via this connector.
4. **PASS05 local Blender** — NOT RUN. Current execution container has no Blender, no working package/index DNS resolution and no hydrated private Git LFS .blend/.fbx files. No QA can be claimed from this environment.
5. **Unity 6 URP** — NOT RUN. **Independent C01-02** — NOT RUN.

## Exact model receipts

| Model | Native .blend SHA256 | Production binary FBX SHA256 | Past native FBX check | PASS05 native Blender |
| --- | --- | --- | --- | --- |
| P15-04 | `54a4b2efdfe0cc3766ff1a04ce3bca24f1adcdf2e8d7812058fc000e297393cd` | `58252505554c65354f9ebce7e3264868d3ff7a57c850d16323e71e6356c5ce04` | PASS | NOT RUN |
| P15-05 | `4f30880643a17d97c9f7cfca4cd0a219e12fff6f8868fa1ba31017e9083f2c01` | `5d254249234c100ca2e7c0b4d65fe8ed8bc366f275d4718b4d90bac416d3da5e` | PASS | NOT RUN |
| P15-06 | `644b1fab278bf1694fc6eb61b6a1cfe0f4bcfce204ecfd25a6b4cb13221a82aa` | `e48b943e7926a3d62e3f956f1b1bc59218dbe310837d179dfbbfee435001f448` | PASS | NOT RUN |
| P15-07 | `00a456375c5fd731f811d61d1ae171330a5291d5669ae9fdcc752b174b72aa6e` | `ffc0211cc73a2056b815f3a494c24ab97d3c808d7ad9eb5b472472c555fb47f2` | PASS | NOT RUN |

## To execute (real Blender 4.x, from checked-out correct private PR branch)

```powershell
git lfs pull
python Tools/C01MeshPass05/P15/local_blender_gate.py --wave W02 --blender "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
```

The CLI locates Blender from PATH/BLENDER_BIN automatically if --blender is omitted. It rejects:
- wrong branch, LFS pointers instead of real `.blend`/`.fbx`, missing files or mismatched SHA256,
- Blender version other than 4.x, nonzero Blender exit code, incomplete asset results, or report digests that differ from the source and actual FBX binary hashes.

Successful real execution writes `QA/Pass04/PASS04_SUMMARY.json`, `QA/Pass04/PASS05_EXECUTION.json`, `PASS05_BLENDER_STDOUT.txt`, `PASS05_BLENDER_STDERR.txt` and per-ID genuine native Blender audit reports. It does **not** rewrite original .blend or .fbx assets. Commit reports to this existing PR only after inspecting, and request C01-02 exact SHA retest.

Native BVH overlap and exact coplanar triangle contacts are candidates requiring review, never silently welded and never automatically independent-QA-approved. PASS05 native and Unity currently **NOT RUN / BLOCKED**.
