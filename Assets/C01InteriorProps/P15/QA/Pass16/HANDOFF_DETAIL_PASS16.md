# C01-15 — DETAIL PASS16 / P15-02 production handoff

**Existing producer Draft:** [PR #16](https://github.com/C8LyNn/Model-Test/pull/16); [HQ #36](https://github.com/C8LyNn/Model-Test/issues/36). No merge. No new asset IDs, no ship source changes. W02 PR #25, P15-01 and P15-03 geometry untouched.

## Actual edited source
- `Assets/C01InteriorProps/P15/Sources/geometry_spec.json` v0.1.4 → **v0.1.5**, producer commit [a737a4998fe5](https://github.com/C8LyNn/Model-Test/commit/a737a4998fe5deb3598c2f301c28b1126914aed4); Git blob SHA1 `e34122a51507ca5374498c0be734460ac47f37f5`.
- Four old corner mount screws `center.Z .078→.079` m: old caps exactly coplanar with frame outward face `Z=.080` m. Now 1 mm proud, 3 mm embedded, no new support detachment.
- Two rear louver support rails (L/R) now intersect top/bottom frame and all six louvers.
- Twelve small seated fixing studs (one per end of each original louver) meet louvers.
- 16 → 30 P15-02 parts, source-wide 75 → 89 parts. Original six louver blades untouched, no pivot/material/hierarchy change. Width/height unchanged (0.6×0.4 m); depth 0.080→0.081 m (+1 mm).

## Construction references / source rights
See [verified four reference pages](https://github.com/C8LyNn/Model-Test/blob/c01/props-15-installations/Assets/C01InteriorProps/P15/References/DETAIL_PASS16_CONSTRUCTION_REFERENCES.md). We did not copy third-party images/CAD/proprietary dimensions.

## Measured QA on actual reconstructed authoring mesh (NOT native Blender)
- **32/32 TRUE triangle-edge/surface-intersection support pairs** found by bidirectional Möller–Trumbore segment/triangle tests on generated indexed source geometry; 2 rear rails↔16 support junctions, 12 rivets↔blades, 4 raised screws↔frame.
- **104/104 coarse analytical interface checks** PASS; independent triangulated scene source geometry: **V184→416; T304→712; 16→30 closed, positive-volume and consistent-winding independent objects**; 0 degenerate triangles.
- Same-facing AXIS-ALIGNED coplanar triangle polygon intersection: **4 bad mesh pairs / 40 triangle pairs / 1692.8215 mm² BEFORE → 0 pairs / 0 mm² AFTER**. Does not prove arbitrary oblique or total collision-free assembly.
- OFFLINE physical evidence: `C01-15_DETAIL_PASS16_P15-02_SOURCE_QA.zip` **230581 bytes**, **12 files**, CRC PASS, ZIP SHA256 `ee0786d03f34746501ff547957f3c3647a0a0c470dc79c0353b12b29781f4f8a`; offline GLB SHA256 `c8b81d26c52f9d7416cc137988836108deb6b9173fe0327ac6f25c4e2b240034`. Includes BEFORE/AFTER shaded/wireframe with same camera and fastener closeup, full strict contact QA JSON, offline GLB, JSON part specs and SHA manifest. **Not genuine Blender screenshots or exporter bytes.**
- [Machine-readable QA summary](https://github.com/C8LyNn/Model-Test/blob/c01/props-15-installations/Assets/C01InteriorProps/P15/QA/Pass16/P15-02_ACTUAL_AUTHORING_SOURCE_AND_OFFLINE_MESH_QA.json).

## RELEASE GATES — honest status
`SOURCE_AUTHORING=PASS`, `OFFLINE_TARGETED_CONTACT=PASS`, `OFFLINE_AXIS_COPLANAR=PASS`; `NEW_NATIVE_BLEND=NOT_RUN`, `NEW_BLENDER_FBX=NOT_RUN`, `BLENDER_REIMPORT=NOT_RUN`, `ACTUAL_BLENDER_WIREFRAME=NOT_RUN`, `INDEPENDENT_C01-02=PENDING`, `UNITY6_URP=NOT_RUN`. The historical native LFS files are **STALE** relative to source v0.1.5. Source evidence cannot be promoted as a native final mesh.

**NEEDS_OWNER_ACTION:** On a working Blender 4.x host with Git LFS hydrated, check out exact PR16 HEAD, run existing `Tools/C01Props15/blender_build.py` against v0.1.5; real save `P15-02.blend`, binary Blender-origin `P15-02.fbx`, re-import, visually inspect proper bracket and blade contacts, hard normals, UV0, material slots, pivot, actual total topology, complete z-fighting (incl. non-axis) and Unity clearance. Capture genuine Blender same-camera shaded/wireframe and actual new SHA256. Independent C01-02 signs exact new FBX; C01-10 tests real Unity 6000.3.14f1 URP. **Remain Draft, no merge.**
