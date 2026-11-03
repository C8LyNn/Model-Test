# C01-02 / WAVE01 — supplier-source independent QA (2026-10-29)

Issue #8, parent #2. Source review is strictly **static GitHub file inspection**, not a Blender/Unity test. Each candidate remains not accepted pending full gate.

## Immutable audited versions / evidence

- C01-15: `c01/props-15-installations` at `2ed37ba58c25f5b03223668c1f3502869f2d13a8` — geometry spec, Blender generator and Unity prefab builder. CI promises Blender artifacts, but no produced binary artifact was independently opened or imported.
- C01-16: `c01/props-16-lighting` at `e9cd92831c41ebd5fa2da026326831e524d08458` — direct independent parsing of three OBJ meshes and textual FBX headers; checked 3 prefab YAMLs and referenced .meta GUIDs.
- C01-17: `c01/props-17-controls` at `5b6bf2971bc8864e7c5f20ba936c9a0700fbbbbe` — direct independent JSON inspection of three embedded-buffer glTF meshes.
- C01-18: `c01/props-18-cargo` at `5f4e47c77e794290a6679e231af68b5f92348569` — direct independent OBJ and textual FBX inspection, prefab YAML analysis.
- C01-19: `c01/props-19-furniture` at `f3bccbf2fef5265e7cd37d094968d76bdc7b5192` — inspected 4 representative piece OBJs, source delivery/README, reported 37 OBJ pieces; not full independent mesh verification.

## Per asset

| ID | Static mesh/format finding | Unity/Blender acceptance | Overall |
|---|---|---|---|
| P15-01 | Generator/spec present; native output not audited | NOT RUN | BLOCKED |
| P15-02 | Generator/spec present; native output not audited | NOT RUN | BLOCKED |
| P15-03 | Generator/spec present; native output not audited | NOT RUN | BLOCKED |
| P16-01 | OBJ: 120 vertices, 60 triangles, 0 degenerates; XYZ 1.20×0.12×0.15; 3 material GUIDs resolve | NOT RUN | BLOCKED |
| P16-02 | OBJ: 120 vertices, 60 triangles, 0 degenerates; XYZ 0.35×0.22×0.14; 3 material GUIDs resolve | NOT RUN | BLOCKED |
| P16-03 | OBJ: 120 vertices, 60 triangles, 0 degenerates; XYZ 0.20×0.30×0.20; 3 material GUIDs resolve | NOT RUN | BLOCKED |
| P17-01 | glTF: 17/17 primitives missing TEXCOORD_0 | NOT RUN | FAIL (P1) |
| P17-02 | glTF: 20/20 primitives missing TEXCOORD_0 | NOT RUN | FAIL (P1) |
| P17-03 | glTF: 12/12 primitives missing TEXCOORD_0 | NOT RUN | FAIL (P1) |
| P18-01 | OBJ: 180 triangles, 0 degenerates; FBX lacks LayerElementUV/Normal | NOT RUN | FAIL (P1) |
| P18-02 | OBJ: 204 triangles, 0 degenerates; FBX lacks LayerElementUV/Normal | NOT RUN | FAIL (P1) |
| P18-03 | OBJ: 348 triangles, 0 degenerates; FBX lacks LayerElementUV/Normal | NOT RUN | FAIL (P1) |
| P19-01 | Actual OBJ assembly pieces present; native source/export/prefab not validated | NOT RUN | BLOCKED |
| P19-02 | Actual OBJ assembly pieces present; native source/export/prefab not validated | NOT RUN | BLOCKED |
| P19-03 | Actual OBJ assembly pieces present; native source/export/prefab not validated | NOT RUN | BLOCKED |
| P19-04 | Actual OBJ assembly pieces present; native source/export/prefab not validated | NOT RUN | BLOCKED |

## Concrete defects and reproduction

**C01QA-P1-17-UV0** / C01-17 / issue #5:
1. Fetch each `Assets/C01InteriorProps/Models/P17-0{1,2,3}.gltf` on audited commit.
2. Parse JSON `meshes[*].primitives[*].attributes`.
3. Found no `TEXCOORD_0` for **49/49** mesh primitives; position and normal accessors are present. Source glTF is not UV0-complete. Fix by authoring UV0 or documenting a C01-01-approved procedural UV exception, then re-export.

**C01QA-P1-18-UV-NORMAL** / C01-18 / issue #6:
1. Fetch `Assets/C01InteriorProps/C01-18/Models/P18-01.fbx` through `P18-03.fbx` on audited commit.
2. Confirm textual FBX 7.4 geometry exists, but `LayerElementUV` and `LayerElementNormal` blocks are absent in all 3.
3. OBJ sources likewise contain no `vt` or `vn` records. Blender/Unity may synthesize normals, but explicit UV0 requirement is not demonstrated. Re-export with actual normals and UV0 or provide approved exception plus Unity validation.

**C01QA-P1-18-FBX-LINK** / C01-18 / issue #6:
The three serialized prefabs refer to Unity builtin primitive meshes `guid: 0000000000000000e000000000000000`, rather than imported project FBX mesh GUIDs. This is not proof of broken rendering; it is a traceability/reproduction blocker for the Blender→FBX→Unity pipeline. Link prefab geometry to reviewed exports or provide verified equivalence evidence.

**C01QA-P1-19-EXPORT** / C01-19 / issue #7:
OBJ pieces examined have vertex and face data but no UV/normal records; native .blend/.fbx and Unity prefab outputs were not present in reviewed source deliverable. Required explicit import/UV/render proof before acceptance.

## Static positives (not full PASS)

- P16 OBJ files: exactly 3×(120 vertices, 60 triangles), UV and normals indexed, finite XYZ, no invalid indices or degenerate triangles. Matching FBX ASCII 7.4 headers present. All 3 prefabs: identity scale, colliders aligned to bounds, material count 3, all 9 sampled mesh/material GUID references resolve to committed meta files.
- P17 glTF: normal streams exist; 204/240/208 declared triangles, 4 materials per model, embedded buffers, no dangling accessor references.
- P18 OBJ: 0 invalid faces and 0 degenerate triangles across 180+204+348 triangles; prefab roots scale 1, contain serialized collider components. **No Unity engine proof.**

## Blocking steps

- Native `.blend`, reliable FBX importer round-trip, and actual Unity 6 URP playtest/screenshot evidence: NOT RUN.
- C01-10 showcase #9: not yet assembled with sixteen verified supplier models; corridor/door/stair/lift clearance NOT RUN.
- C01-02 never edits producer branches and does not authorize release while any required check remains unperformed.

**QA decision: FAIL on 6 source deliverables (P17 and P18), BLOCKED for remaining 10; 0/16 accepted.** This is the state of **audited SHAs**, not a claim about later revisions.