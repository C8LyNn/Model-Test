using C01.Ship.V5.Editor;
using UnityEditor;
public static class ShipV68BuildAll
{
    [MenuItem("Tools/C01 Ship v6.8/Build complete")]
    public static void Build()
    {
        ShipV68Builder.Build();
        ShipV68PolishBuilder.Build();
    }
}
