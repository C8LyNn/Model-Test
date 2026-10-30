# C01-17 — DETAIL PASS12 — P17-02 source geometry handoff

**Owner:** C01-17. **Asset:** existing P17-02 access keypad. **Issue:** #36. **Producer Draft:** #17. **Blocker:** #33.

## Actual authoring geometry delivered (not merely a spec)
- Directly modified existing **P17-02.gltf**, **P17-02.obj.txt**, **P17-02.json**, and **catalog.json** in this PR. No new model ID, no ship model changes, no merge.
- Kept all **20 original parts / 240 triangles**, including 12 distinct keys, Housing/Gasket, wall backing, LED and existing side clamps. Added **18 functional parts / 296 triangles**: 12 key-retaining steel plates (each intersects backing Keybed ~1mm), 2 steel clamp flanges (mechanically intersect clamps ~0.5mm) and 4 eight-sided mounting screw heads (intersect wall backing ~0.5mm). Final **38 independent visual parts / 536 triangles**.
- New screw mesh is indexed and closed: **18 vertices, 48 edges, 32 triangular faces, zero nonmanifold edges**. All 4 bolts instance this same mesh, with separate model nodes.
- Original AABB preserved exactly **0.18 × 0.07 × 0.28 m**, wall-mount origin/pivot unchanged, key materials and UV0 preserved in the authoritative glTF. New geometries have STEEL material and valid UV0. No uncontrolled welding.
- **Actual source glTF and OBJ triangles compare 536/536 EXACT (triangle coordinates quantized to 1µm), 0 degenerate triangles.**
- Independent geometric comparison against the original real Blender PASS03 exported binary FBX: after details, all 18 have positive AABB attachment overlap; **0 before → 0 after** cross-part same-facing coplanar triangle-overlap candidates; 536 total triangles. This is analytic geometry QA, not Blender/Unity.

## New immutable SHA-256 after source edits
| File | SHA-256 |
|---|---|
| `Assets/C01InteriorProps/Models/P17-02.gltf` | `3fba39e0e5813e6abc486c8ca5685247b59b0614a4186a545dd57903ed51e077` |
| `C01InteriorProps_Source/MeshText/P17-02.obj.txt` | `1c54a13792661fa06ff7e56d7aef4dd9534227d5c2a54a22bbd5fa1eaba6bd53` |
| `C01InteriorProps_Source/Specs/P17-02.json` | `715c018b12134a9ce47fb6bf18d0036dee9288a194c2199be798ff28b7bcb472` |
| `C01InteriorProps_Source/Specs/catalog.json` | `f387049adcadfe28f84db0d3d0c11d4b8799935cdb4335601a9ef29137e466d2` |

## Blender / FBX gate: DO NOT ACCEPT HISTORICAL FILES
Old REAL native `C01InteriorProps_Source/Blender/P17-02.blend` LFS SHA-256 `183d4ebbcc9e13ad220aaa869db80949fb315d58666f79c2e1c7ae85f6e69649` (603,584 bytes) and actual Blender-produced binary `Assets/C01InteriorProps/Models/P17-02.fbx` LFS SHA-256 `af858385a0abae9c623ee4002bcf22bcbc401b5687024acd8df142eb1b848147` (63,004 bytes) remain **PRE-PASS12 STALE**. They are *real binary files*, but **do not contain the added 18 parts**. Native Blender 4.x AFTER save + fresh binary FBX + reimport **NOT RUN**. Independent C01-02 final acceptance **PENDING**; Unity 6 URP import **NOT RUN**.

Blender execution must start from the genuine **PASS03 repaired 20-part native .blend** and append only the 18 new P17-02 authored parts from the updated glTF, preserving original Blender mesh topology and materials; **do not blindly run legacy `build_blender.py` to overwrite PASS03 with un-repaired glTF reimport**. Keep static KeyGuide/Clamp/Bolt children attached to the original stationary root. For each new Blender mesh, weld by coordinate **within the new object only** at tolerance <= 1µm, revalidate UV0/material and 0 nonmanifold/degenerate faces. Preserve existing 20 meshes unmodified. Capture real same-camera shaded/wireframe BEFORE/AFTER, save true Blender `.blend`, export binary FBX through Blender 4.x, import into clean scene and recheck **38 / 536**, dimension bounds, UV0 and hashes. Commit real after files only if runtime PASS, then independent C01-02 and C01-10 Unity.

**Owner unblock:** private C01 GitHub Actions still fail before assigning runners and current container has no Blender/bpy/Git-LFS. `NEEDS_OWNER_ACTION` to restore private runner allocation or execute on authorized Blender 4.x workstation. DO NOT mark PASS merely from glTF/OBJ/analytic preview.

## Preview and downloadable geometry package
User-visible C01-17 PASS12 ChatGPT artifacts:
- `C01-17_PASS12_P17-02_BEFORE_AFTER_ANALYTIC.png` SHA-256 `cc36d511683389029b6334f9196cf5978f13211d9a26f24d0a21defd0a656682`. Uses ACTUAL previous native Blender-produced FBX triangles and new source-authored geometry, **NOT new Blender AFTER shaded render**.
- `C01-17_PASS12_P17-02_DETAIL_SOURCES_AND_QA.zip` SHA-256 `289f0063fcbdad89d2c8e936c4b9ace59e126e415c98f1cbead5e7d3a7df4b2a`; ZIP CRC PASS. Contains actual 536-triangle full OBJ from physical before FBX + new details, original native BLEND/FBX explicitly labeled BEFORE/HISTORIC, images and QA. No new claimed native export.
