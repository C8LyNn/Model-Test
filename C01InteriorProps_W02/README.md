# C01-17 Wave02 — Real controls and puzzle assets

Issue #5; parent #2. Standalone branch c01/props-17-wave02 targets codex/c01-ship-integration, separate from Wave01 PR #17.

Actual glTF geometry committed in Assets/C01InteriorProps/W02/Models; source recipes and mount/pivot contracts in C01InteriorProps_W02/Specs.

| ID | Function | W x D x H m | Movement |
|---|---|---|---|
| P17-04 | dual screen bridge station | 2.4 x 1.0 x 1.35 | two distinct screen meshes |
| P17-05 | medical diagnostic terminal | 0.85 x 0.6085 x 1.5 | none |
| P17-06 | emergency cutoff | 0.52 x 0.2265 x 0.72 | CoverPivot local X 0..95, SwitchPivot X -25..25 |
| P17-07 | fuse unit | 0.70 x 0.24 x 0.82 | CartridgePivot +Z translation 0..0.25 m |

All material slots: METAL, DARK, CAUTION, GLOW (emission). All geometry contains UV0 and normals; local Y-up and meters. Floor pivots at Y=0, wall pivots at Z=0. Architectural layout is untouched.

## Blender
Command: xvfb-run -a blender -b --factory-startup --python-exit-code 1 --python C01InteriorProps_W02/Tools/blender_build.py -- .
Blender exports 4 native .blend, 4 actual FBX, 12 actual PNG previews. An isolated GitHub workflow runs this on push.

## Unity 6 URP
After actual FBX import, use Unity menu C01 / Controls / Wave02 / Build FBX Prefabs (code in Assets/C01InteriorProps/W02/Editor). This actually produces prefab/material files inside Unity, not when run from Python. Static root box collider, separate articulated cover and cartridge colliders. No gameplay logic. Verify 3m corridor and door clearance, assign approved positions in C01-10 showcase only after C01-02 approval.

## Tests / acceptance
Static test: python3 C01InteriorProps_W02/Tools/qa_gltf.py. Blender runs when CI completes. Unity, final colliders, import, physical clearance and independent QA: NOT RUN until actual engine review. PR remains draft and unmerged.
