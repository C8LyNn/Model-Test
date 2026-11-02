# C01-13 / PASS03 — Legacy door topology repair

**Role:** C01-13 / DOORS & ACCESS. **Scope:** archival D01 + D02 (first architecture pass), *not* the 36 interior props in #30. No ship layout or gate changed. The ship's live V4/V5 uses sliding ShipGateV4, not this hinged D02.

## Real, source-derived changes

The OBJ files in this folder contain **actual geometry traced from earlier C01-13 v002 GLB triangles**, rather than any model recreated for a screenshot. Provenance:
- D01 v002 GLB SHA256: `661fce22f352640f4a9dd2153dc48be019d2064b89afbf367a8ebfe326ca4bc5`
- D02 v002 GLB SHA256: `8604ac2e53be8fce93e015ad916e9a65baff31cb87938ac83b831003c1303e2c`

**D01:** original 3 individually manifold closed cuboids had two touching internal coplanar face patches (~0.02 m² on each junction). Result unites **only stationary jambs + header** into a single continuous manifold part, preserving outer silhouette, volume, world dimensions, orientation and portal opening. Before V/E/F/T = **24/54/36/36** (3 parts). After = **20/54/36/36** (1 part). No boundary edges, nonmanifold edges, or degenerate triangles in either indexed topology.

**D02:** indexed geometry remains **8/18/12/12** (one part) before and after, unchanged hinge-relative vertex positions and pivot; no geometric defect detected. Both old exported FBX/GLB lacked UV0. New OBJs include per-corner `vt`, explicit face `vn`, preserving welded geometric vertices and hard-edge shading.

## Concrete binaries + proof outside GitHub

A downloadable **D01/D02 PASS03 local package** accompanies the ChatGPT C01-13 report and contains original GLB+FBX bytes, repaired actual GLB/FBX (provisional Python FBX7400), before/after true-triangle wireframes, zooms, static test evidence (35 PASS, 0 FAIL), full reproducible source code, input and output SHA256, and steps for Unity. This PR stores the repaired source geometry in human-readable OBJ for code review; binary FBX/GLB are **not included in this PR** and should not be inferred to be present here.

## Blender real verification — not yet run

Run in Blender 4.x, from repository root:
`blender --background --python Assets/C01DoorsAccess13/LegacyPass03/blender_validate_export.py`

This Blender source reads the v003 actual-geometry OBJ, creates native `.blend` and Blender-exported binary `.fbx`, reimports FBX and asserts bounding differences <1 mm and the presence of UV0. The script has **not** been run, so no `.blend`, Blender roundtrip or Unity result is claimed.

## Unity prefab / no inadvertent collisions

- Do not replace V4/V5 slide gates with these old hinged models.
- W04 (owner C01-11) must be 2×3 m wall with 1.80×2.50 m structural opening. Imported D01 frame occupies X [0.10,1.90], Y [0,2.50], Z [0,0.20] and has 1.60×2.40 m light.
- D02 original leaf bounds relative to hinge: X [0,1.54], Y [.04,2.36], Z [-.025,.025], pivot root at W04 local (.23,0,.145), 0→90° around +Y.
- Use three frame BoxColliders around separate physical jamb/header volumes despite welded **render mesh**; one moved leaf collider. Never put full door-blocking collider over opening.
- C01-10 may test this only as a separate architecture prototype, not inside the existing ship; C01-02 independent QA required.

## Gate status
STATIC SOURCE GEOMETRY: **LOCAL PASS**; BLENDER REIMPORT: **NOT RUN**; UNITY: **NOT RUN**; INDEPENDENT C01-02: **PENDING**. No merge before QA acceptance. See #30.
