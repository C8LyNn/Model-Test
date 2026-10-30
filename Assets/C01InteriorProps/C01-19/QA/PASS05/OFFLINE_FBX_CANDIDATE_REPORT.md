# C01-19 / PASS05 — actual binary FBX triangulation fallback
Existing DRAFT producer PR #15, no merge and no architecture edits.
Context: GitHub Actions fails before runner allocation, no job steps or Blender logs; direct Blender unavailable to this assistant.
**Real actions executed:** Offline constrained triangulation of ORIGINAL hydrated PASS03 FBX 7.4 polygon payloads; preserved object transforms, original mesh vertex arrays, material and connection nodes, UV-index and normal-per-corner data. Regenerated authentic FBX binary candidates and re-read with independent parser. Candidate archive is delivered to the user in the companion chat attachment; source files in this PR are deliberately NOT replaced by unverified outputs.
**Not executed:** Blender .blend source modification, Blender FBX importer roundtrip, Unity 6 URP, independent C01-02 review. Old QA FAIL P1 remains until new native source binaries are verified.
## Static binary candidate measurements (NOT final source repairs)
| ID | V(before→candidate) | Edges before→candidate | Faces before→candidate | Triangles unchanged | Naive fan degenerates before→candidate | Candidate FBX SHA256 |
|---|---:|---:|---:|---:|---:|---|
| P19-02 | 118→118 | 194→15 | 86→10 | 10 | 216→0 | `8371d9bacedb1dec4ed9edb038e14b76f62dc1fe4eadba801d318ccbbce11837` |
## Actual export trust boundary
Writer serializes parsed FBX 7400 binary node tree without changes to geometry vertex coordinate buffers or model hierarchies; raw parse→write roundtrip is byte-for-byte identical before triangulation. UV0, normals and materials retained by per-polygon-loop remapping. Independent binary reparse confirms 0 zero-area triangles, 0 non-manifold edges, 0 boundary edges and correct triangle count in each candidate. This is static evidence only.
P19-01 additional blocker: original native PASS03 FBX has one 6-corner projected self-intersecting polygon (Geometry Cube.001, polygon 59). Offline fallback intentionally refuses unsafe triangulation of that model. Requires native Blender source repair by visual inspection.
## Native Blender execution fallback
When GitHub Actions runner allocation remains broken, use `Tools/run_pass05_native_windows.ps1` in THIS existing branch on a Windows machine with Blender 4.x, e.g. `pwsh -File Tools/run_pass05_native_windows.ps1 -Wave W01 -BlenderPath 'C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe' -Push`.
This fail-closed runner pulls LFS assets, executes the already committed native source script, verifies 4 `.blend` and binary FBX files, and pushes only to its existing branch after successful real Blender roundtrips. Script itself has NOT RUN on Windows in this environment.
GitHub Actions status: cross-repository official GitHub dashboard currently reports Actions operational, so a broad confirmed global outage cannot be asserted. Local repo jobs have steps=[] and zero runtime; GitHub Actions account/billing/runner access should be examined in repository settings by an administrator. Do not mark PASS from source scripts.
## QA
C01-02 must review the final new Blender-produced source/FBX SHA (not these candidate hashes), and P19-07/08 T-junction candidates before changing topology. Unity NOT RUN.
