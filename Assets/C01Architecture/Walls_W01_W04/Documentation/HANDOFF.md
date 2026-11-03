# C01-11 / W01–W04 architecture handoff / WAVE 02

Scope: **W01 full wall, W02 interchangeable wall finish, W03 90-degree L corner, W04 door opening**. These are **architecture candidates, not part of the 16 P15–P19 interior props**. Reference: parent issue #2. No source ship scenes, corridors, doors, cabin layout, hull or levels were edited.

The independent Blender generator in Sources creates a **new greybox candidate** matching nominal W01/W02/W03/W04 envelopes. **IMPORTANT:** W02 is a material-family variant of W01 in this revision; the older October 28 r2 W02 had geometric recessed details and is still the reference for preserving production art. Do NOT silently replace the previous detailed W02 with this candidate.

Provisional wall geometry (Unity world axes, Y up, meters):
- W01/W02: 1 × 3 × 0.2; local pivot (0,0,0); geometry positive XYZ.
- W03: 1 × 3 × 1 L-corner within X/Z ±0.5; pivot (0,0,0), at floor.
- W04: 2 × 3 × 0.2; opening X 0.20..1.80, Y 0..2.40, Z 0..0.20.

Gates:
- CI uses **real Blender** to generate .blend / Blender FBX / three PNG views per model. Inspect the workflow run and generated files before claiming Blender PASS.
- Blender-side checks: envelope, pivot, mesh manifoldness, degenerate triangles and UV presence. They DO NOT validate Unity/URP import or actual clearance.
- Unity Editor prefab builder: Tools > C01 > C01-11 > Build W01-W04 Prefabs. Requires Unity 6 URP and generated FBX; NOT RUN here.
- **BLOCKED** until C01-01 approves the interface and C01-13 confirms actual D01 frame aperture. The ship v5 uses 3m horizontal wall bays, with some sectors 6m high. These W modules must not be substituted without explicit integration QA.
- C01-02 performs independent QA on exact produced SHA; C01-10 decides placement after sign-off. PR remains draft. No formal QA acceptance claimed.

This PR is additive and does not change ship geometry or C01-15–19 families.
