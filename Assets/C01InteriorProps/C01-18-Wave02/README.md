# C01-18 WAVE02 — actual cargo geometry

Four new models P18-04–07; generated through real Blender 4.0.2 runner. Authoritative Blender generator: `Sources/build_wave02.py`. Download built `.blend`, binary `.fbx` and rendered PNG preview via GitHub Actions artifact; extract them into this directory's corresponding Sources / Models / Previews. No ship scene touched.

## Unity 6 URP import
1. Import 4 FBXs from CI artifact to `Assets/C01InteriorProps/C01-18-Wave02/Models/` in a Unity 6000.3.14f1 project with URP installed.
2. Wait for the real FBX importer. Verify materials (URP Lit) and child pivots.
3. Execute **Tools > C01 > Cargo > Build Wave 02 FBX Prefabs**. This editor utility builds individual prefabs from the imported FBX meshes (not built-in Unity primitive stand-ins), checks UV0 and normals, adds per-part BoxColliders and pickup-ready kinematic Rigidbody.
4. Capture Unity screenshots and test clearance in separate C01-10 showcase. Source ship unchanged.

**Do not claim Unity prefab PASS until executed in Unity.** Native files are generated and recorded by CI; QA ownership remains independent C01-02. No PR merge without approval.
