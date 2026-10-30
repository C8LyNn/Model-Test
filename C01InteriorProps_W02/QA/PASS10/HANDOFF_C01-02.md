# C01-17 — PASS10 / P17-05 actual binary evidence

Verified actual source `.blend` and Kaydara FBX candidate bytes on 2026-10-30, not merely generator code.

**Physical ZIP** `C01-17_PASS10_P17-05_REAL_BINARY_EVIDENCE.zip` (211195 bytes, SHA-256 `d5ea004504f1793e37fea78476005653da3f1ca5ec7b0dcfba58dafeab3d0b56`, ZIP CRC PASS) is in the user-visible ChatGPT PASS10 turn; it contains original and corrected copies of both `.blend` and FBX plus raw audit. It is NOT uploaded as production LFS blobs to GitHub.

**Confirmed actual changes:** 3 source Blender-v400 bytes within existing LowerDisplayRail object location; six FBX-7400 bytes for the corresponding Lcl Translation property. 1664 Blender BHead records before/after identical in header/size/order; FBX parser structural diff has EXACTLY ONE modified property, every other FBX property byte-identical. Actual indexed FBX triangle geometry: **20 mesh parts, 240 tris**, correct before/after; same-facing coplanar `DisplayBezel / LowerDisplayRail` triangle intersections **6 to 0**, overlap area **0.059199983764 m² → 0**.

**Truthful gate:** these are offline-patched **QUARANTINED** binary candidates, NOT Blender 4.x loaded/saved/exported runtime outputs. They were not submitted as current Git LFS producer FBX because actual Blender roundtrip is NOT RUN. Previous real PASS03 Blender outcomes still refer to OLD SHA. Independent C01-02 signoff PENDING, Unity 6 NOT RUN. No merge and no new models.

**P0 unblock:** GitHub Actions private C01 repository jobs fail before runner allocation (runner_id=0, steps=[]), while B01 public repository previously executed real runners. Root cause unknown; do not change billing or repo privacy without owner decision. Local execution environment lacks Blender/bpy and network DNS prevents installing. **NEEDS_OWNER_ACTION**: run bundled Blender reopen/save/export/reimport on authorized Windows Blender 4.x or restore C01 runner eligibility. Review generated real wireframe, load tests and exact new SHA before promoting to PR #23, then request C01-02 and C01-10 Unity.

Cross-project QA knowledge shared in B01 #407 during PASS09, no source assets crossed repositories.
