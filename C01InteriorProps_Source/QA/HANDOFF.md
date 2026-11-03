# C01-17 handoff to C01-02 / C01-10
Parent: https://github.com/C8LyNn/Model-Test/issues/2
Task: https://github.com/C8LyNn/Model-Test/issues/5
C01-02 independent QA: https://github.com/C8LyNn/Model-Test/issues/8
C01-10 integration: https://github.com/C8LyNn/Model-Test/issues/9

Owner produced real glTF meshes for P17-01, P17-02, P17-03, with independent LeverPivot
and materials. No ship architecture edits.
Dimensions:
P17-01 W1.60 D0.65 H1.10, console floor;
P17-02 W0.18 D0.07 H0.28, wall (Z=0 mount plane);
P17-03 W0.40 D0.30 H0.55, lever floor; axis X pivot Y=0.35.
Measured geometry and normals are in QA/STATIC_GEOMETRY_RESULTS.json.

Do not claim Blender (.blend/.fbx), actual screenshot or Unity prefab PASS
unless GitHub Actions/Unity editor generated and checked those files.
Final QA: PENDING C01-02. Unity corridor, door clearance and materials: NOT RUN.
C01-01 must confirm pivot/mounting conventions.
No merge until C01-02 and C01-10 sign off.
