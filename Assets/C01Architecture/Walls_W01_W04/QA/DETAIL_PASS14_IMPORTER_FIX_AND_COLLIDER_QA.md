# C01-11 — DETAIL PASS 14: actual prefab importer fix + exact original-FBX collider QA

## Ownership and status
- C01-11: historical W01–W04 architecture, **not part of the 36 existing P15–P19 prop models** under #36.
- #36 explicitly disallows changing the ship's architecture. No new mesh ID, no architectural geometry or source FBX mutation, no merge.
- Existing [DRAFT PR #22](https://github.com/C8LyNn/Model-Test/pull/22) maintained; physical Unity import and native Blender execution remain **NOT RUN**.

## Actual program defect discovered and FIXED (not report-only)
File: `Assets/C01Architecture/Walls_W01_W04/Editor/C01WallPrefabBuilder.cs`.
- Prior PASS12 code removed the variable named `mesh` during preview-scene isolation but still referenced `mesh.GetComponentsInChildren<MeshRenderer>(true)`, causing a **C# compilation error (undefined name)**. Replaced with `temp.GetComponentsInChildren<MeshRenderer>(true)` on the actual imported prefab instance.
- Full original-r2 path previously created a new synthetic steel material and assigned `renderer.sharedMaterial = mat`, silently replacing the imported material array on all renderers; this violates source material preservation, especially for meshes with multiple submeshes. **Removed source material overrides and unnecessary steel-material asset generation.**
- Added a fail-closed importer sanity check that renderer material slot count is nonzero and at least the number of mesh submeshes. Original imported material associations are left untouched. URP shader availability is checked without modifying the models.
- Preserved separate QA-only W01/W03/W04 prefab paths and original W02 **572-triangle** gate, and existing `NewPreviewScene` / `ClosePreviewScene` isolation. The 12-triangle W02 prototype cannot be substituted.
- **Changed actual source commit:** [`88c2058354f169bd119b66c04784a41c6a50cdc0`](https://github.com/C8LyNn/Model-Test/commit/88c2058354f169bd119b66c04784a41c6a50cdc0). Read back exact new GitHub source: **14/14 static regression assertions PASS**. **No Unity compiler/runtime executed**, so no engine PASS claimed.

## Executed source geometry vs box collider QA
Actual original FBX bytes were reopened from the immutable PASS13 physical archive (not synthetic substitutes); their SHA and Kaydara binary header were checked. Exact original authored indexed triangle mesh vertices and faces were loaded from the same archive. `trimesh` volume, watertightness, signed orientation and all-position collision-union coverage were executed locally; ZIP CRC and complete SHA256SUMS verified.

| ID | Authored mesh V/F/T | Original FBX SHA-256 | Actual signed source volume (m³) | Unity box-collider union (m³) | Outside collider vertices | Source preflight |
|---|---:|---|---:|---:|---:|---|
| W01 | 8 / 12 / 12 | `7cc73ea116aa82cab5aa4833db2e6d3ce58888b47907402169d13ac2d7a7ff10` | 0.6000000 | 0.6000000 | 0 | PASS |
| W02 detailed | 288 / 572 / 572 | `3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037` | 0.5463396 | 0.6000000 | 0 | PASS WITH INTENTIONAL COARSE COLLIDER |
| W03 | 12 / 20 / 20 | `3f6d37472239fe2ab61be27eaafb928ee9cf0253c9783d465d81ec649a9b2ee2` | 1.0800000 | 1.0800000 | 0 | PASS |
| W04 | 16 / 28 / 28 | `c492539f3d33f65c90e0a0ac5279a6feded45d7cb14c3fefc147358dc9d7ecfe` | 0.4320000 | 0.4320000 | 0 | PASS |

All original indexed surfaces are watertight, consistent winding, and positive enclosed volume, with **zero original vertices outside assigned editor box-collider volume**. W02 occupies 0.0536604 m³ less than its 0.6m³ whole-wall box because the surface has detailed recesses; this is a **collision simplification**, not automatically a model defect or a Unity interaction PASS. The test verifies local-authoring geometry; it does not physically execute the Unity FBX importer.

## Exact off-GitHub physical evidence
Physical ZIP `C01-11_PASS14_BINARY_AND_IMPORTER_QA.zip`: **518754 bytes / 15 entries**, **SHA256 `4784c288ce457d1d407c29cb9be69aad1a5ad798c5d28e4cad63b7d600677d21`**, ZIP CRC and all internal SHA256SUMS PASS. Includes 4 original detailed-r2 binary FBX under exact Unity `OriginalR2/FBX` destination paths, 3 **historical** genuine Blender-v400 `.blend`+binary FBX candidate pairs W01/W03/W04 (provenance-only, not newly exported), a genuine original W02 wireframe, and this PASS14 executed collider check Python/JSON evidence. No fake AFTER rendering; no geometry changed. Current GitHub PR22 still lacks the physical OriginalR2 folder and requires operator to unzip original files into an isolated Unity staging project; no Git LFS upload or merge is claimed.

## Gates
- **New repaired geometry sources (.blend/.fbx): 0**; 4 previously correct originals remain unchanged.
- **Actual C# compiler blocker and importer material-loss bug: FIXED in PR #22**, 14/14 static code assertions PASS, physical Unity compilation **NOT RUN**.
- Real original collider/geometry preflight **PASS 4/4** (W02 coarse-collider caveat).
- New Blender4 native source save/export/reimport: **NOT RUN**. Three authentic archived previous Blender source pairs are evidence-only.
- Independent C01-02 acceptance: **PENDING**. Unity 6 URP scene/prefab execution: **NOT RUN**.
- GitHub Actions C01 latest examined [run #41124421941](https://github.com/C8LyNn/Model-Test/actions/runs/41124421941) fails before allocation (`steps=[]`, no runner ID). Available container has no Blender, `bpy`, `dotnet`, Unity or Git LFS; root cause of hosted runner failure is **unknown**.
- **NEEDS_OWNER_ACTION**: either obtain authorized working GitHub Actions runner/Windows Blender+Unity host, or stage the authentic ZIP in an isolated Unity6 project and run the preflight/build and inspect FBX materials, collider fits, prefab and actual Editor logs.

**P18-01/02/03 and P17-02 corrections stay in producer PR #18/#17; no source files belonging to those owners were edited by C01-11.**