# C01-14 / DETAIL PASS17 — real OBJ + GLB + interactive QA handoff

## Scope and physical evidence

**Only existing RAI-01**, optional prototype outside the canonical 36 P15–P19. RMP-01 unchanged. No model ID or ship structure modified, no merge.

Real source **PASS16 RAI-01 OBJ** (current latest C01-14 authored source): SHA-256 `634716a4ee5c7f8ffb5e53d80d862833670e28c90f07fec133c88d7632efb798`; 20 named separately watertight parts, 424 tris, UV0 + normal all 1272 face corners. All 10 specific mechanical joints have true triangle-edge crossings; zero full all-part same-facing coplanar area. Source-only QA **re-executed in PASS17**, not repeated from prior prose.

Produced **REAL latest source-derived glTF binary** (not historical FBX, no proxy): `RAI-01_DETAIL17_REAL_SOURCE.glb` = SHA-256 `6a79c33d4a1da1ae042ed9964376fc9416a0d34cc38b301e33da87426b377358`; independent GLB reimport **20/20 meshes, 424 triangles, UV0 20/20, exact WORLD triangles within 1µm vs latest source OBJ**. This GLB was generated offline by trimesh; NOT native Blender, so not a release native file.

Produced a real interactive standalone HTML view with **before PASS15 14/248 vs after PASS16 20/424**, two orbit/zoom scenes, exact source meshes, toggle SHADED/WIREFRAME/COMBINED. No old FBX, substitute placeholder geometry or internet asset needed. Physical HTML SHA-256 `1dbd0314b6f1197da9eed53fe6ec1e156a2e97ae9549322c20d89162e1bff633`. Delivered in conversation ZIP `C01_14_DETAIL_PASS17_INTERACTIVE_SOURCE_QA.zip` (18 files, size 1,746,038 bytes, SHA256 `93637638ae3e7737c9a06f07558eb77a01a250c0042025f3e515a9a20919b19a`, ZIP CRC PASS); not committed under canonical Git LFS. Old PASS15 vs PASS16 source-drawn shaded/wireframe PNGs included.

## Real Blender CI launch

**Key improvement:** verified an actual live GitHub Actions Blender 4.0.2 success in C01-15 on 2026-11-01 [run 41344475164](https://github.com/C8LyNn/Model-Test/actions/runs/41344475164). Created new isolated C01-14 [Blender4 real native CI workflow](https://github.com/C8LyNn/Model-Test/blob/c01/structures-14-prototypes-w02/.github/workflows/c01-14-detail17-real-native.yml) with SHA-verified losslessly encoded **real current source-derived GLB**, not old v002 FBX, and [native Blender script](https://github.com/C8LyNn/Model-Test/blob/c01/structures-14-prototypes-w02/Tools/C01Structural14/blender_detail17_native.py).

Actual isolated Blender job [41345517610](https://github.com/C8LyNn/Model-Test/actions/runs/41345517610) **FAILED** due to tool root-path mistake before opening model (zero native output); corrected code path in commit `7fe58029398ce5cd89f4132d0f49c82c821dcd3b`, new run [41345868244](https://github.com/C8LyNn/Model-Test/actions/runs/41345868244) **PENDING at this report snapshot**. Do NOT claim native PASS until logs, exact binaries and SHA report exist. Workflow uses genuine old Blender v002 original four mesh objects for unchanged original UV0, plus the **sixteen exact existing PASS16 support meshes** supplied by real latest OBJ-derived GLB; no new objects invented. It saves a NEW `.blend`, exports binary FBX and reimports with 20/424, 20 UV layers/materials. Outputs MUST stay on Draft PR24; NO merge. Unity6 remains NOT RUN; independent C01-02 full signoff PENDING.

## Source-level gates

- Re-executed 20/20 watertight, consistent winding, positive volume (QA-only same-position UV seam merge).
- Re-executed 1272/1272 OBJ face corners valid v/vt/vn, no zero-area triangles.
- Re-executed 10/10 genuine metal socket/post/bolt triangle support pair crossings.
- Re-executed 0 all-part same-facing coplanar overlapping triangle pairs.
- Independent GLB reimport: 20/20 meshes, 424/424 real triangles, 20/20 UV0, OBJ world-space triangle parity at 1µm.
- Unity6 URP C01-10 prefabs/physics = **NOT RUN** (not available). Release approval of 36 models unchanged by this optional RAI.

**Release caveat:** source preview and offline GLB parity are NOT native Blender/FBX release PASS. Native release requires successful actual run, SHA-pinned .blend and FBX, independent C01-02 mesh QA and Unity6.
