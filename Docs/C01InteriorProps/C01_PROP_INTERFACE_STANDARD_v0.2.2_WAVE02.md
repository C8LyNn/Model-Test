# C01-01 — INTERIOR PROP INTERFACE STANDARD v0.2.2 / WAVE 02

**Owner:** C01-01 — ASSET STANDARDS & PIPELINE. **Scope:** P15-04…P19-08 (20 nonstructural assets), independent of architectural alterations.
**Normative file:** [prop_contract_wave02.json](./prop_contract_wave02.json). **Parent immutable contract:** [prop_contract.json](./prop_contract.json), `C01-PROP-INTERFACE-0.2.1` for P15-01…P19-04. The 16 existing IDs, pivots and dimensions are unchanged.
**Status:** TECHNICAL STANDARD LOCKED FOR PILOT; independent QA C01-02 and Unity integration C01-10 NOT APPROVED by this specification.

## Scope isolation and current ship protection
The ship integration is PR #1 (`codex/c01-ship-integration`), now evolving beyond the old v4 name. **Do not assume historic 3-metre room-kit doors, 3-metre ceilings or 4x4 room layout represent this ship**. Structural authoring grid in ship PR #1 is 3 m, itself an integer multiple of the underlying 1 m metre grid. Nonstructural furniture/props use their actual metric dimensions, **never scaled up to 3m**. The following are read-only: hull, doors/airlocks, elevators, stairs, decks, walls, ship layout, engine structures and ship scenes.

## Axes, dimensions and pivot/socket invariants
- Unity = +X right, +Y up, +Z forward; **visual front of prop is -Z**. All dimensions **W×D×H = X×Z×Y**. 1 Unity unit = 1 metre, root rotation (0,0,0), scale (1,1,1). Blender: METRIC, unit scale 1; FBX export only from real authored objects. Verify actual imported axes, root and child transform in Unity, do not rely on export settings alone.
- Floor = pivot at ground centre, bounds x=[−W/2,+W/2], y=[0,H], z=[−D/2,+D/2]. Wall = rear mounting face centre, bounds x=[−W/2,+W/2], y=[−H/2,+H/2], z=[−D,0]. Ceiling = upper mounting face centre, bounds x=[−W/2,+W/2], y=[−H,0], z=[−D/2,+D/2]. Rail = run-start centre; bounds x=[0,W], y=[−H/2,+H/2], z=[−D/2,+D/2].
- Socket **SOCKET_MOUNT** mandatory (part owner supplies exact local position, outward normal and mounting plane). Model-to-ship placement is relative to **actual visible surface**, not an inferred grid centre. Asset-specific extra sockets are enumerated in JSON. Moving parts use named mesh children, with separate pivot objects, local axes and consistent hierarchy; never fake rotation with an offset mesh root.
- Elbow is a distinct P15-05 pivot profile. Its pivot is bend apex `(0,0,0)`, reference AABB [(-0.50,−0.09,−0.12), (0.12,0.09,0.50)] m, corresponding nominal W×D×H 0.62×0.62×0.18 m. See port geometry below.
- Bounds: dimension tolerance ±2 mm, pivot ±1 mm, rail port position ±1 mm; unit-scale tolerance 1e-4. Deliberate dimensional deviation >1 cm requires explicit C01-01 approval ref. Unintended solid-solid penetration >0.1 mm is a defect. Variants must retain identical mount socket and footprint classes.

## P15-04 / P15-05 physically defined channel mating
Straight **P15-04**, run in local +X, nominal 3.00×0.24×0.18 m: port A `(0,0,0)` normal `(−1,0,0)`, B `(3,0,0)` normal `(+1,0,0)`. The cross section is 0.18 m (height Y) × 0.24 m (width transverse Z).
Elbow **P15-05**, nominal 0.62×0.62×0.18 m: port A `(−0.50,0,0)` normal `(−1,0,0)`, port B `(0,0,+0.50)` normal `(0,0,+1)`; same cross section. Place elbow root `(3.50,0,0)` to connect its port A exactly at straight's B `(3,0,0)`, with opposing normals. A following straight at **−90° Y** has its A normal `(0,0,−1)`, opposing elbow B `(0,0,+1)`; translate its root to `(3.50,0,0.50)`. Rotating a straight channel in place cannot substitute a corner. Both runs have continuous mount brackets/sockets authored by C01-15.

### Complete Wave 02 asset slots
| ID | Owner | Nominal W×D×H [m] | Pivot | Required behaviour / children |
|---|---|---|---|---|
| P15-04 | C01-15 | 3.00×0.24×0.18 | rail | Straight ceiling cable tray, two certified ports |
| P15-05 | C01-15 | 0.62×0.62×0.18 | elbow | 90° tray elbow, two certified ports |
| P15-06 | C01-15 | 2.00×0.20×0.18 | rail | Technical cable bundle, two bracket sockets |
| P15-07 | C01-15 | 1.20×0.35×1.40 | wall | Coolant distributor, paired service sockets, gauges |
| P16-04 | C01-16 | 1.50×0.60×0.12 | ceiling | Large light panel, separate luminous diffuser |
| P16-05 | C01-16 | 0.90×0.12×0.35 | wall | Corridor direction sign, separate icon/emissive face |
| P16-06 | C01-16 | 0.36×0.36×0.45 | ceiling | Alarm rotor, separate non-static rotating child |
| P16-07 | C01-16 | 0.30×0.12×0.35 | wall | Status indicator, available/locked/fault material variants |
| P17-04 | C01-17 | 2.40×1.00×1.35 | floor | Bridge desk, separate left/right screens |
| P17-05 | C01-17 | 0.90×0.55×1.30 | floor | Medical/lab terminal, distinct screen |
| P17-06 | C01-17 | 0.55×0.24×0.75 | wall | Emergency cutoff, distinct cover + switch pivots |
| P17-07 | C01-17 | 0.65×0.16×0.85 | wall | Fuse module, separate removable insert and fuse socket |
| P18-04 | C01-18 | 0.75×0.75×1.20 | floor | Transport cylinder, grip socket, dynamic-ready collider |
| P18-05 | C01-18 | 0.55×0.24×0.40 | floor | Locking equipment case, lid hinge + grip |
| P18-06 | C01-18 | 0.70×0.62×0.90 | floor | Secured sample container, grip socket |
| P18-07 | C01-18 | 0.48×0.30×0.32 | floor | Portable toolbox, lid hinge + grip |
| P19-05 | C01-19 | 1.40×0.55×0.82 | floor | Two-person crew bench |
| P19-06 | C01-19 | 0.80×0.55×0.15 | wall | Foldable wall table, **deployed** W×D×H, moving hinge/swept envelope separately |
| P19-07 | C01-19 | 1.05×2.20×0.85 | floor | Diagnostic bed, separate mattress |
| P19-08 | C01-19 | 0.75×0.55×1.30 | floor | Sanitary sink, water-in and drain sockets |

These dimensions are **C01-01 pilot targets** in absence of measured producer models, not claims that actual geometry already exists. Reviewable deviations retain an approval reference. The folded profile of P19-06 may extend outside the deployed bounds and must be represented separately in the hinge sweep/clearance manifest.

## Materials, normal/UV streams and collision contract
- Reuse at most four real URP/Lit materials per prefab, from `M_C01_STEEL`, `M_C01_PANEL_DARK`, `M_C01_CAUTION` and `M_C01_EMISSION`. Emission changes use material variants, not duplicated geometry. Status green/amber/red is semantic state, not three different UV layouts.
- UV0 must be present on every authored render surface, including glTF primitive TEXCOORD_0 or OBJ per-face-corner vt reference. Normals must be explicitly valid; generated FBX normals and winding must be checked after import. Degenerate triangles/NaNs/zero-scale prohibited. A source stream PASS **does not** prove actual FBX layers survive exporter conversion.
- Colliders are primitive/compound matching physical volume. No full bounding box collider that blocks a lever clearance, open frame or fold. Static supports keep static colliders. Dynamic/pick-up props use convex primitive compound and avoid nonconvex dynamic MeshColliders. Render and collision hierarchies are separately declared in manifest.
- Every movable child (rotor, cover, switch, fuse insert, case lid, folding tabletop) is a separate transform under correct hinge/rail pivot. Record permitted axis, min/max, closed pose, swept volume and collider policy; test entire movement in Unity and clear the unchanged routes. No full puzzle logic required.

## Deliverables, proof and ownership
Each of the 20 producer assets needs a **real** native `.blend`, valid Blender-exported `.fbx`, imported/editable Unity 6 prefab, three actual geometry views, manifest with local bounds/triangle/materials/pivots/sockets/colliders, SHA-256 of real bytes, and per-stage results. Producer branches isolated and wave-specific; no placeholder in ship scene. Repo-relative file paths must refer to actual files; unhydrated Git LFS pointers are not binary geometry.

The `Tools/c01_props/validate_wave02.py` script audits JSON catalog/manifest, 20 IDs, socket/port and hash requirements; its success is **STATIC ONLY**. Status `READY_FOR_INDEPENDENT_QA` only for manifest with complete evidence and declared positive producer QA; formal `APPROVED` must be documented by **C01-02** with exact revision SHA. C01-10 integrates only accepted assets into an isolated showcase; C01-00 handles final release.

### Handoff
- **C01-15–19:** take owned row + machine contract, construct actual meshes, export native files, manifest, importer/playmode evidence and repair previous W01 issues before accepting Wave02 release.
- **C01-02 (#8):** retest failed Wave01 per current file SHA; independently evaluate each Wave02 delivery against the contract including axis/pivot/UV/normal/real collider/sweep/clearance; mark PASS/FAIL/BLOCKED/NOT_RUN.
- **C01-03:** register exact W02 IDs/sha, maintain `PROTOTYPE` versus `APPROVED`.
- **C01-10 (#9):** assemble only accepted meshes; protect PR #1 ship scene and 3m traversal corridors.
- **C01-00:** no merge until C01-02 independently approves; leave Wave01 0/16 accepted until actual evidence changes.

**C01-01 state:** Technical contract authored; Blender/Unity runtime and supplier geometry tests NOT RUN by C01-01; 20 producer assets remain NOT_BUILT in this contract.
