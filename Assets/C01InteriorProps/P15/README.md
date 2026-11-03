# C01-15 / P15-01..P15-03 — actual geometry pilot
Issue: https://github.com/C8LyNn/Model-Test/issues/3

Only interior props. This PR does not change the ship scene, hull, corridors, deck topology or door geometry.

- P15-01 wall/ceiling pipe, 1 m nominal, +X run, wall plane local Z=0
- P15-02 ventilation grille, 0.60 x 0.08 x 0.40 m, wall plane local Z=0
- P15-03 electrical service cabinet, 0.80 x 0.35 x 1.80 m, floor origin (0,0,0). Cabinet leaf is a separate FBX and prefab child with hinge at (-0.352,0,0.138), rotation around +Y.

Three low-poly material families: STEEL, DARK, WARN. Canonical geometry specification: Sources/geometry_spec.json.

In CI, Blender produces three real .blend files, five .fbx files, and 9 rendered previews. Validate signature/hashes with `python Tools/C01Props15/validate_generated.py`. For locally installed Blender: `blender -b --python Tools/C01Props15/blender_build.py`.

With Unity 6 URP open, run `Tools > C01 Props15 > Build FBX prefab set`; this creates 3 real prefab assets and colliders. The generated prefabs and Unity import have not been tested unless the QA folder contains actual Unity editor execution evidence. Do not mark Unity PASS on a purely static check. C01-02 independently reviews #8 and C01-10 integrates in #9.

Never merge without independent QA or publish a screenshot as proof of Unity import.
