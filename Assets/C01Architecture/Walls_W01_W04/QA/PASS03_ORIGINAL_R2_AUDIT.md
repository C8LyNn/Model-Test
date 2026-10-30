# C01-11 / PASS03 — authentic r2 FBX mesh integrity

**Audit date:** 2026-10-30. **Source:** original W01–W04 binary FBX delivered with October 28 WAVE02 r2; geometry exactly compared against original `Sources/mesh_data.json`. This is **not** a reconstructed viewer proxy.

| ID | V / E / F / T | Source SHA-256 | Detected unintended topology defects | Change |
|---|---|---|---:|---|
| W01 | 8 / 18 / 12 / 12 | `7cc73ea116aa82cab5aa4833db2e6d3ce58888b47907402169d13ac2d7a7ff10` | 0 | 0 |
| W02 **detailed r2** | 288 / 858 / 572 / 572 | `3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037` | 0 | 0 |
| W03 | 12 / 30 / 20 / 20 | `3f6d37472239fe2ab61be27eaafb928ee9cf0253c9783d465d81ec649a9b2ee2` | 0 | 0 |
| W04 | 16 / 42 / 28 / 28 | `c492539f3d33f65c90e0a0ac5279a6feded45d7cb14c3fefc147358dc9d7ecfe` | 0 | 0 |

Measurements are derived from actual FBX binary Geometry.Vertices / PolygonVertexIndex and UV and normal layer nodes, with independent topological checks (not Blender runtime): zero unused/coincident vertices, zero zero-length edges, zero unexpected boundary/nonmanifold edges, zero incorrect winding, zero degenerates/duplicate triangles, zero vertex-on-edge T-junctions, zero coplanar overlaps, zero detected strict interior noncoplanar triangle intersections. All four closed manifold meshes contain one connected component, preserve UV0 + FBX normals, and have positive volumes.

**No arbitrary weld performed.** No verified defect warrants destructive edits. BEFORE/AFTER both refer to identical source SHA. These are measurements with numeric tolerances (1e-8 m for T-junction tests; 1e-9 m² coplanar overlap threshold), not a proof that Unity rendering is correct.

**Critical W02 mismatch:** This PR's `W02_PANEL_WALL_1M.blend` from CI has 12 triangles and is merely a simplified prototype; archived detailed r2 W02 is 572 triangles. DO NOT replace archived W02 with this prototype or treat its Blender roundtrip as proof of archived W02's topology.

**Native Blender scope:** PR's 4 .blend+FBX generated in workflow run [41072466328](https://github.com/C8LyNn/Model-Test/actions/runs/41072466328) (SUCCESS). Separate PASS03 Blender read, true FBX export/import, source+roundtrip audit and source-wireframe renders are added under `Sources/pass03_native_topology_audit.py` and workflow. This validates **the PR's native candidates**, not the different archived r2 source. Inspect new CI output before claiming PASS.

**BLOCKED:** Archived original r2 .blend source MISSING; original r2 Blender reimport NOT RUN. Unity 6 URP import/clearance NOT RUN. C01-01/C01-13 door interface approval and C01-02 independent gate PENDING. No changes to ship layouts or user-approved model silhouettes.

**Disposition:** Original r2 mesh topology locally STATIC PASS UNCHANGED; current PR22 candidate W02 must not supersede it. PR remains DRAFT.
