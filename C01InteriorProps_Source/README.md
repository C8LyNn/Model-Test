# C01-17 — Controls & Puzzle Objects / #5
Origin branch: codex/c01-ship-integration. Implementation: c01/props-17-controls.
No ship structural meshes, scenes, corridors, doors, floors or engine placement changed.

## Three real meshes: glTF 2.0
- Assets/C01InteriorProps/Models/P17-01.gltf: W1.60 D0.65 H1.10 m, floor pivot; console screen separate emission mesh.
- Assets/C01InteriorProps/Models/P17-02.gltf: W0.18 D0.07 H0.28 m, wall mounting plane Z=0; install adjacent to door frame, not on leaf.
- Assets/C01InteriorProps/Models/P17-03.gltf: W0.40 D0.30 H0.55 m; floor pivot, separate LeverPivot at (0,0.35,-0.015); nominal rotation X 0-45 degrees.

These are full glTF indexed triangle data buffers with material slots and node hierarchy, not placeholders.
Spec JSON plus valid OBJ geometry stored in MeshText/*.obj.txt (rename to .obj).
Previews are procedural SVG geometry previews; they are NOT Unity screenshots.

## Blender native source and FBX
Run: blender -b --factory-startup --python-exit-code 1 --python C01InteriorProps_Source/Tools/build_blender.py -- .
Generates .blend under C01InteriorProps_Source/Blender; real .fbx under Assets/C01InteriorProps/Models; front/side/iso Blender-rendered PNG under Previews.
A branch-specific GitHub Actions workflow can build and commit generated binaries through Git LFS.
If this action fails or does not run, status remains MISSING — do not fake file existence.

## Unity 6 URP
After FBX export, open Unity project, call menu C01 / Controls / Build Prefabs.
The editor script creates three native .prefab outputs under Assets/C01InteriorProps/Prefabs and
four URP Lit material files, assigns BoxColliders and a separate lever SphereCollider.
Build the prefabs with the project Unity editor, commit their .prefab/.mat/.meta files,
then run C01 / Controls / Validate Prefabs. No gameplay logic is included.
Place props only after C01-02 independent QA and C01-10 clearance assessment.

## QA
Static mesh checks: python3 C01InteriorProps_Source/Tools/qa_gltf.py.
Authoring-only Blender and Unity tests must be reported as NOT RUN until actually executed.
The final 16-object showcase belongs exclusively to C01-10 (#9), not C01-17.
