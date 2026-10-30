# C01-19 / PASS05 — actual binary FBX triangulation fallback
Existing DRAFT producer PR #29, no merge and no architecture edits.
Context: GitHub Actions fails before runner allocation, no job steps or Blender logs; direct Blender unavailable to this assistant.
**Real actions executed:** Offline constrained triangulation of ORIGINAL hydrated PASS03 FBX 7.4 polygon payloads; preserved object transforms, original mesh vertex arrays, material and connection nodes, UV-index and normal-per-corner data. Regenerated authentic FBX binary candidates and re-read with independent parser. Candidate archive is delivered to the user in the companion chat attachment; source files in this PR are deliberately NOT replaced by unverified outputs.
**Not executed:** Blender .blend source modification, Blender FBX importer roundtrip, Unity 6 URP, independent C01-02 review. Old QA FAIL P1 remains until new native source binaries are verified.
## Static binary candidate measurements (NOT final source repairs)
| ID | V(before→candidate) | Edges before→candidate | Faces before→candidate | Triangles unchanged | Naive fan degenerates before→candidate | Candidate FBX SHA256 |
|---|---:|---:|---:|---:|---:|---|
| P19-05 | 88→88 | 140→222 | 66→148 | 148 | 1→0 | `7b04a8b2f9fb7306b1e169f18bba25a322dd4ba726decbe1ecb69d5994f6f1b1` |
| P19-07 | 136→136 | 204→378 | 78→252 | 252 | 19→0 | `d9e832d4df2623b70842209944c1615d7aba7af6f042e16bf7720b4a95e9a3e1` |
| P19-08 | 149→149 | 241→423 | 100→282 | 282 | 7→0 | `c740c5de71443f2b01f20cb48f76f37e61fda53ddfd5c5a9d7d263d511772e11` |
## Actual export trust boundary
Writer serializes parsed FBX 7400 binary node tree without changes to geometry vertex coordinate buffers or model hierarchies; raw parse→write roundtrip is byte-for-byte identical before triangulation. UV0, normals and materials retained by per-polygon-loop remapping. Independent binary reparse confirms 0 zero-area triangles, 0 non-manifold edges, 0 boundary edges and correct triangle count in each candidate. This is static evidence only.
P19-01 additional blocker: original native PASS03 FBX has one 6-corner projected self-intersecting polygon (Geometry Cube.001, polygon 59). Offline fallback intentionally refuses unsafe triangulation of that model. Requires native Blender source repair by visual inspection.
## Native Blender execution fallback
When GitHub Actions runner allocation remains broken, use `Tools/run_pass05_native_windows.ps1` in THIS existing branch on a Windows machine with Blender 4.x, e.g. `pwsh -File Tools/run_pass05_native_windows.ps1 -Wave W02 -BlenderPath 'C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe' -Push`.
This fail-closed runner pulls LFS assets, executes the already committed native source script, verifies 4 `.blend` and binary FBX files, and pushes only to its existing branch after successful real Blender roundtrips. Script itself has NOT RUN on Windows in this environment.
GitHub Actions status: cross-repository official GitHub dashboard currently reports Actions operational, so a broad confirmed global outage cannot be asserted. Local repo jobs have steps=[] and zero runtime; GitHub Actions account/billing/runner access should be examined in repository settings by an administrator. Do not mark PASS from source scripts.
## QA
C01-02 must review the final new Blender-produced source/FBX SHA (not these candidate hashes), and P19-07/08 T-junction candidates before changing topology. Unity NOT RUN.
