# C01-01 — Interior Props / WAVE 01 — delivery and handoff

**Issue:** #2; producer tickets #3–7; QA #8; integration #9.
**Branch:** `c01/standards-interior-props-wave01` (isolated from `codex/c01-ship-integration`).
**Scope:** standards, source-export pipeline, evidence-aware QA tooling. **No ownership of producer geometry.**

## Supplied (real files in this PR)

- `Docs/C01InteriorProps/C01_PROP_INTERFACE_STANDARD_v0.2.1.md`: 1 m units, current ship 3 m structural grid, all 16 W×D×H sizes, mount/socket pivot profiles, collision and URP rules, 90° pipe ambiguity, clearance/QA.
- `Docs/C01InteriorProps/prop_contract.json`: machine-readable list of exactly 16 planned IDs and associated issue ownership.
- `Docs/C01InteriorProps/manifest_example_UNVERIFIED.json`: deliberately incomplete reference; **NOT a model**.
- `Tools/c01_props/validate_props.py`: standard-library manifest verifier; checks file existence and SHA-256; `static:PASS` never implies Blender/Unity PASS.
- `Tools/c01_props/blender_export_prop.py`: helper to export existing authored Blender collections, **requires Blender and actual meshes**; does not generate placeholder geometry.
- `Tests/c01_props/test_validator.py`: 14 unit tests, including expected rejection of incorrect or falsely complete data.

## Executed tests in C01-01 local runtime

- `python -m unittest discover -s Tests/c01_props -v` → **14 PASS**, 0 FAIL; all 16 planned asset IDs checked structurally.
- `python -m py_compile Tools/c01_props/validate_props.py Tools/c01_props/blender_export_prop.py Tests/c01_props/test_validator.py` → PASS syntax check.
- Example manifest with triangle_count=0 and no real files → intentional `static:FAIL`, `delivery:BLOCKED`. This is expected negative evidence.
- ZIP package archive CRC integrity → PASS.

**NOT RUN:** Blender import, actual .blend generation/FBX roundtrip, Unity prefab and URP import, collision clearance in ship, scene PlayMode, independent C01-02 QA. No screenshot, real prop mesh or Unity prefab is claimed created by C01-01.

## Contract decisions and incompatible assumptions

- The real current ship v4 uses 3 m architectural cells and 6 m typical rooms. Older C01 first-wave 1 m room kit with 3 m ceiling **must not be misapplied**. No ship source or geometry is modified.
- Props may use real-world sub-metre dimensions; no scaling to 3 m.
- A pipe rotated around its X-axis by 90° retains coaxial ports; a perpendicular run needs an elbow; do not claim perpendicular join with a single straight segment.
- Wall/ceiling sockets are relative to the actual finished surface and placement requires C01-02 measured clearance, not just a screenshot.

## Next owners / blockers

- **C01-15–19 (#3–7):** produce the 16 actual Blender sources, FBX exports, Unity prefabs, three previews per asset and filled evidence manifests. No fake PASS for absent components.
- **C01-02 (#8):** independent geometry/import/collider/traversal QA; 16-row PASS/FAIL/NOT RUN matrix. Do not edit source producer branches.
- **C01-10 (#9):** stage ONLY accepted models in distinct showcase scene and master prefab, avoid modifying ship scene.
- **C01-00:** review this interface lock, then merge after independent review, not ahead of delivery.
- **Remaining blocker for overall #2:** supplier assets and Unity QA missing; C01-01 cannot claim completion of production package.

**Overall status:** `C01-01 STATIC CONTRACT PASS / ASSET DELIVERY BLOCKED / UNITY NOT RUN`.
