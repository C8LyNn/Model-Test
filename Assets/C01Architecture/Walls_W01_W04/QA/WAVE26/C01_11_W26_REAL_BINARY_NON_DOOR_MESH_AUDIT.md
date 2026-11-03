# C01-11 — WAVE 26 / GLOBAL MESH REPAIR — W01/W02/W03 physical-source audit

**Owner:** C01-11 WALLS & ARCHITECTURE. **Scope:** only three existing non-door assets W01 FULL WALL, W02 PANEL WALL, W03 CORNER 90°. They are **legacy architecture outside the canonical 36 P15–P19 props**. Existing [Draft PR #22](https://github.com/C8LyNn/Model-Test/pull/22), baseline head `7e6b159d0742f082e836bc7a4c6b12aee75b312e`. No new models or ship geometry changes.

**ABSOLUTE EXCLUSION:** ALL Claude-delegated doors/gates and door-adjacent W04 model are frozen. No D01, D02, W04 mesh, native files, materials, transforms, prefabs, door scripts or PR #19/#32 were modified or analyzed as models. This W26 report does not request door testing.

## REAL physically executed W26 audit (not LFS-only)

Retrieved original successful [Blender 4.0.2 Actions run #41346578552](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552), original artifact [#13098949702](https://github.com/C8LyNn/Model-Test/actions/runs/41346578552/artifacts/13098949702), original ZIP 4,771,746 bytes, recomputed **full ZIP SHA-256 `52bcbcb53d08b587a21bcd582c1e216f640c4346518448537ebbc46cdc8e5e6c` EXACT PASS**. Read and full SHA-hashed only the three explicitly authorized native Blender-v400 and FBX-7400 assets below; all six match original signed producer receipts. No need to re-export immutable geometry.

Unlike W23–25's Git-LFS-pointer checks, this time W26 read **actual full binary FBX geometry**. A new independent Python FBX7400 property/array decoder parsed real indexed polygon vertices, per-corner split normals and UV, model transform and mesh layers; independently reconstructed tris using fan triangulation for valid quad faces. NumPy checked topology and vertex-on-nonincident-edge 1µm witnesses, trimesh checked watertightness, winding and connected components; nonshared triangle-pair AABB broadphase plus strict segment–triangle and projected coplanar-polygon positive-area narrowphase checked self-intersections. UV area / face geometric-normal direction were independently evaluated. **This was executed offline locally, NOT a new Blender or Unity Editor session.**

| Asset | Exact native BLEND SHA-256 | Exact signed native FBX SHA-256 | Vertices / triangles |
|---|---|---|---|
| W01 | `7918bea022a05b0676e97f1995a66cccc28745590941240f5c3efe6b4a5006dd` | `c644e95d548cafbac61cebe000d7b0fb4b584a1fe4527565ba55d4c8e0415a79` | 8 / 12 |
| W02 detailed | `28c71407f49d84d653a4844b82933599bf1a4083783bcd619804cdc75e9ed360` | `a23f602d8dd61a6dc61ee52af347e472f2e6f6ce546988f50409911d1b11a317` | 288 / **572** |
| W03 | `609c862ea8ee85c0b48a87547a37c442ab8840e3c26a8a0f7494dd7e2c7aac07` | `9dcc8feca9475626e393910b4176d8c2eadf9c645d34e32718a417a10214807a` | 12 / 20 |

## Actual numerical mesh checks

| Metric | W01 | W02 detailed | W03 |
|---|---:|---:|---:|
| Watertight / winding consistent | PASS / PASS | PASS / PASS | PASS / PASS |
| Connected mesh components | 1 | 1 | 1 |
| Boundary / non-manifold edges | 0 / 0 | 0 / 0 | 0 / 0 |
| Repeated indexed triangles | 0 | 0 | 0 |
| Degenerate triangles (<1e-10 m²) | 0 | 0 | 0 |
| Nonincident vertex–edge T-junctions (<1µm) | 0 | 0 | 0 |
| Nonshared triangle broadphase candidates | 8 | 1398 | 18 |
| Strict triangle interior crossings / coplanar positive-area overlaps | 0 / 0 | 0 / 0 | 0 / 0 |
| Degenerate UV triangle faces | 0 | 0 | 0 |
| Min signed dot between FBX corner normal and geometric triangle normal | 1.0 | 0.9999999060 | 1.0 |
| UV area / 3D face area min | 1.0 | 0.8115941 | 1.0 |

Actual imported model root has `Lcl Rotation = approx (-90°,0°,0°)` for all three. Applying this transform yields original authoring coordinate bounds: W01 [0,0,0]..[1,3,0.2] m; W02 same; W03 [-0.5,0,-0.5]..[0.5,3,0.5] m. Thus 1-m modular length and original root pivot grid relationship are preserved; **this is not an in-engine 4×4m assembly-gap test**.

Face formats: W01 6 quads → 12 triangles, W02 572 native triangles, W03 8 tris + 6 quads → 20 triangles. Ordinary quads are valid and are not silently treated as bad n-gons. W02 thin edge/recess detailing is preserved; do NOT replace 572T physical W02 with original tracked 12T prototype LFS FBX `7dfcf0fe84952e607a74845ad193acfbb9f4fc029e7f168a94a7bac2edacb78b`. Historical W02 source→FBX normal max Δ 2.654e-6 and strict 1e-6 vs 1e-5 tolerance decision still needs C01-02.

**Limits / honesty:** UV area ratio is geometry vs UV-area density, not proof of artistic texture stretch; minimum W02 0.8116 is a possible discretionary visual QA item, not a confirmed defect absent materials/textures/target texel criteria. AABB + strict triangle testing may not capture all tolerance-level near-touching surfaces. Visual shading and lighting under URP, prefabs and physics require actual Unity 6000.3.14f1. There are no moving parts in these wall meshes; movement sweep N/A.

## NEW W26 evidence pack

A new isolated **non-door-only** archive `C01-11_W26_NON_DOOR_REAL_FBX_QA.zip`, 755,668 bytes, SHA256 `31d4c68c96678fdff8163c4c411619f5e9cbf5f3ecc816718e40bcee2dbb1558`, contains: only these 3 genuine native BLEND+FBX files, executed offline audit/triangle-intersection/wireframe Python source scripts, measurement JSON+CSV, source SHA manifest, and **6 current native-FBX triangle renders** (solid + wireframe for each; labeled OFFLINE, not Blender or Unity). Its content is available as a conversation attachment; **it is NOT uploaded as a GitHub Actions artifact**, so the original GitHub production artifact #13098949702 remains the durable GitHub physical-source reference. The exact result rows and digest appear in this committed GitHub report and in the accompanying machine JSON.

## Per-model disposition and next gate

| ID | AUDITED | DEFECT | REPAIRED | Independent C01-02 | Real Unity6 URP |
|---|---|---|---|---|---|
| W01 | PHYSICAL_FBX_PASS | No confirmed defect in tested categories | NOT_NEEDED | PENDING | NOT_RUN |
| W02 | PHYSICAL_FBX_PASS | No confirmed defect; UV visual/tolerance review | NOT_NEEDED | PENDING | NOT_RUN |
| W03 | PHYSICAL_FBX_PASS | No confirmed defect in tested categories | NOT_NEEDED | PENDING | NOT_RUN |

No automatic weld/remesh/decimate or speculative optimization. No mesh, UV, shader, FBX, Blender, collider, pivot, ship geometry or model ID changed. PR #22 remains Draft; no merge/release. Owner of independent gate **C01-02** should reproduce against exact full binary SHA and decide W02 normal/UV visual standard; licensed Unity remains **C01-10 / OWNER_ACTION_REQUIRED**, after the 3-prop P0 pilot, and must use non-door-only test paths.

**Overall W26 C01-11:** `ACTUAL_BINARY_AUDIT_3/3 / NO_CONFIRMED_ACTIONABLE_MESH_DEFECT / INDEPENDENT_QA_PENDING / UNITY_NOT_RUN / CLAUDE_DOORS_FROZEN`.
