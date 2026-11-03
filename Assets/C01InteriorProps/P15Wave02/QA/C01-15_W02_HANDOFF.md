# C01-15 — WAVE 02 / QA AND INTEGRATION HANDOFF

**Producer PR:** https://github.com/C8LyNn/Model-Test/pull/25  
**Wave 01 repair PR:** https://github.com/C8LyNn/Model-Test/pull/16  
**Issue:** https://github.com/C8LyNn/Model-Test/issues/3  
**Independent QA:** #8 / C01-02  
**Unity integrator:** #9 / C01-10

## Scope and ship safety
P15-04, 05, 06, 07 only; no modification of hull, floor, walls, doors, elevators, stairs, corridors, levels, or original ship scenes. New library and tools live under Assets/C01InteriorProps and Tools/C01Props15Wave02 only.

## Expected deliverables (verify files, not claims)
- Four actual Blender native source files P15-04..07.blend
- Four actual FBX models P15-04..07.fbx
- Twelve genuine Blender renders, front/iso/side
- Four machine-readable manifests with actual mesh bounds, triangle counts and declared mounting sockets
- QA/blender_roundtrip.json: source and FBX inspection, UV0, normals, scale, nondegenerate faces, input/output port, and elbow sweep clearance
- QA/file_integrity.json: signatures and SHA-256
- Unity Editor C# builder to create **four** prefab files from real imported FBX; not a replacement for actual Unity import

## Unity 6 URP runbook (C01-10)
1. Branch must be checked out with Git LFS content available. Verify actual binary FBX headers, not LFS text pointers.
2. Open Unity version 6000.3.14f1 with URP. Allow texture/material/FBX reimport.
3. In menu Tools > C01 Props15 > WAVE02 Build & Audit, run generator. It must output 4 actual Unity prefab assets plus QA/unity_editor_import.json. A failed bounds/UV/normals check throws and must be fixed by C01-15, not hidden by root scaling.
4. For P15-04 and P15-05 create a separate snap-test assembly using Reference/P15_Tray_Snap_Example.json. Outgoing connector must fit the straight segment rotated -90° around Y; inspect for gaps with camera and wireframe overlay.
5. Verify P15-06 cable mounts lie on a wall plane Z=0 without negative back penetration. Verify P15-07 root at mounting wall Z=0 and bottom Y=0; gauge rims must face player.
6. Check URP Lit materials, metal and warning tint, UV and normals. Test colliders vs real mesh surfaces.
7. Check placement at engineering zone and ceiling of separate showcase, not in the existing ship source. Door/elevator/3-meter corridor clearance must be verified with actual game geometry; if not possible mark NOT RUN.
8. Save screenshots and commit generated .prefab/.meta and material files on a reviewed integration branch; do not edit producer FBX meshes.

## Independent C01-02 decision matrix
| ID | Source Blender | FBX | UV/normals | Unity prefab | Ship clearance | QA signoff |
|---|---|---|---|---|---|---|
| P15-04 | Verify CI | Verify CI | Verify CI | NOT RUN | NOT RUN | PENDING |
| P15-05 | Verify CI | Verify CI | Verify CI + actual port mesh | NOT RUN | NOT RUN | PENDING |
| P15-06 | Verify CI | Verify CI | Verify CI | NOT RUN | NOT RUN | PENDING |
| P15-07 | Verify CI | Verify CI | Verify CI | NOT RUN | NOT RUN | PENDING |

**Review status:** producer does not grant QA_PASS or UNITY_PASS. No merge until independent C01-02 approval and C01-10 Unity scene integration.
