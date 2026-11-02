# v6.1 button signage

Add `ButtonSignage` to the ship root in the v6.1 scene. In the editor setup call
`signage.Configure(AssetDatabase.LoadAssetAtPath<Shader>("Assets/C01ShipV61/Signage/ButtonText.shader"))`
and save the scene. The shader is serialized on the component so that the player build includes it.
The component works with the existing v5 button and solid markers, without changing their interaction logic.
It replaces labels temporarily and restores the originals according to the associated screen visibility when disabled or destroyed.
Missing screens, labels, fonts or shaders leave existing labels alone.

Validation required in Unity: run `C01ShipV61.Signage.EditTests`; inspect a gate and lift button from
both sides, check the label remains inside the screen, and put an opaque wall between the camera and
label. Check both Play Mode and a player build; verify screen normals, font atlas alpha, text bounds and
shader availability on the project's target renderer. The new shader is URP-specific. The component
retries fitting if Unity has not yet supplied nonzero text bounds.
