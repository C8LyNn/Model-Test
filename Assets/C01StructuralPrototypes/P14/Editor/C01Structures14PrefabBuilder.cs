#if UNITY_EDITOR
// C01-14 W19 compatibility entry. Legacy v001 FBX inputs are obsolete.
// Historical menu calls can never load stale v001 or overwrite production prefabs.
using UnityEditor;

public static class C01Structures14PrefabBuilder
{
    [MenuItem("Tools/C01/Structures 14/Build reference prefabs")]
    public static void Build()
    {
        // This ONLY stages signed latest RAI v003 + repaired RMP v003 under
        // Pass19/UnityQA; it enforces true binary SHA256, mesh and URP checks.
        // No actual Unity prefab PASS is claimed unless Unity executes it.
        C01Structures14Pass19SignedUnityQa.RunSignedQaOnly();
    }
}
#endif
