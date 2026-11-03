# C01-01 — Interior Props / WAVE 01 — mesh stream QA addendum A2

**Reference:** #2, #3–7; independent QA #8, integrator #9. **PR:** #14.
**Contract:** `C01-PROP-INTERFACE-0.2.1` (unchanged). **Scope:** non-structural source-stream preflight; no ship geometry or layout changes.

## Artifact delivered
- `Tools/c01_props/mesh_stream_audit.py`: dependency-free static OBJ/glTF JSON stream scanner. It checks face indices, per-corner UV/normal presence, finite OBJ vertex streams, degenerate OBJ triangle fans, glTF primitive attribute semantics, accessor shapes and counts, triangle mode.
- `Tests/c01_props/test_mesh_stream_audit.py`: 12 positive/negative fixtures. Locally run using Python 3: **12/12 PASS**; `py_compile`: PASS.
- This inspector intentionally does NOT pretend to validate `.blend`, binary `.fbx`, `.prefab`, external glTF binary buffers or Unity. Unsupported files return FAIL rather than PASS.

## Source inspection of REAL supplier files in existing PR branches
Inspected on GitHub source branches on 2026-10-29 (not main and not a merged import). This audit counted source-level UV and normal declarations/attributes. **No Blender or Unity execution.**

| Asset | Source | Triangles / primitives | UV | Normal | Source attribute result |
|---|---|---:|---|---|---|
| P16-01 | `c01/props-16-lighting` OBJ | 60 triangles | 120 VT / 60 faces | 120 VN | STREAM PASS |
| P16-02 | same | 60 triangles | 120 VT / 60 faces | 120 VN | STREAM PASS |
| P16-03 | same | 60 triangles | 120 VT / 60 faces | 120 VN | STREAM PASS |
| P17-01 | `c01/props-17-controls` glTF | 17 primitives | 0/17 | 17/17 | **FAIL: missing TEXCOORD_0** |
| P17-02 | same | 20 primitives | 0/20 | 20/20 | **FAIL: missing TEXCOORD_0** |
| P17-03 | same | 12 primitives | 0/12 | 12/12 | **FAIL: missing TEXCOORD_0** |
| P18-01 | `c01/props-18-cargo` OBJ | 180 triangles | 0 VT | 0 VN | **FAIL: UV and normal streams missing** |
| P18-02 | same | 204 triangles | 0 VT | 0 VN | **FAIL: UV and normal streams missing** |
| P18-03 | same | 348 triangles | 0 VT | 0 VN | **FAIL: UV and normal streams missing** |

Additional sampled source `Assets/C01InteriorProps/C01-19/Models/P19-04/P19-04__Seat.obj` has 8 vertices, 12 faces, **0 VT and 0 VN**. This is one source part only, **not** a QA verdict for entire P19-04 or all furniture. C01-15 contains generator inputs rather than a verified complete export in PR #16; no synthetic producer PASS.

## Reproduction
```bash
python -m unittest discover -s Tests/c01_props -v
python Tools/c01_props/mesh_stream_audit.py C01Source/Lighting/OBJ/P16-01.obj --json-out local_P16.json
python Tools/c01_props/mesh_stream_audit.py Assets/C01InteriorProps/Models/P17-01.gltf --json-out local_P17.json
python Tools/c01_props/mesh_stream_audit.py Assets/C01InteriorProps/C01-18/Models/P18-01.obj --json-out local_P18.json
```
These commands apply to their respective PR checkouts. Files do **not** all coexist in PR #14 or on the ship base branch; use the corresponding producer branch when testing. Exit code 1 on FAIL, JSON status contains **static** result only.

## Handoff / acceptance
- **C01-17 (#5):** supply valid UV0 streams on all 49 glTF primitives (17+20+12) and ensure native Blender-generated FBX carries these streams. Test after export, not only before.
- **C01-18 (#6):** include UV and per-face-corner normal references in the actual OBJ or export corresponding complete streams into FBX. Unity prefabs must reference imported meshes; use C01-02 to verify.
- **C01-19 (#7):** sampled Seat OBJ requires UV/normal streams in delivered import geometry; producer owns all repairs.
- **C01-16 (#4):** static stream check passes for sampled OBJ files but native Blender/Unity source and prefab behavior still require verification.
- **C01-15 (#3):** run Blender exporter with actual source, deliver binaries and Unity prefabs; no PASS until evidence.
- **C01-02 (#8):** independently audit each delivered revision/SHA, dimensions, materials, full mesh and Unity import; do not infer real FBX quality from OBJ/glTF alone.
- **C01-10 (#9):** integrate only assets independently accepted; keep ship v4 layout and corridors unchanged.

**C01-01 result:** STATIC PIPELINE PASS / SOURCE SUPPLIER FAILS PRESENT / BLENDER NOT RUN / UNITY NOT RUN / FULL INTEGRATION BLOCKED. **No auto-merge.**
