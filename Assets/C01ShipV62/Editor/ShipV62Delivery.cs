using System.IO;
using UnityEditor;
using UnityEngine;

public static class ShipV62Delivery
{
    public static void CaptureAndExport()
    {
        ShipV62Diagnostics.CaptureAndVerify();
        var directory=Path.GetFullPath("C01ShipV62_QA");
        Directory.CreateDirectory(directory);
        AssetDatabase.ExportPackage(new[]{"Assets/C01ShipV62","Assets/C01ShipV61","Assets/C01ShipV6","Assets/C01ShipV5/Runtime"},
            Path.Combine(directory,"C01_Ship_Multideck_v6.2.unitypackage"),
            ExportPackageOptions.Recurse|ExportPackageOptions.IncludeDependencies);
        Debug.Log("C01 V6.2 UNITY PACKAGE EXPORTED");
    }
}
