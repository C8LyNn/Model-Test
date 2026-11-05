using System;
using System.IO;
using UnityEditor;

public static class ShipTallSectorsV78Delivery
{
    public static void Export()
    {
        Directory.CreateDirectory("C01SourceV78/Delivery");
        string path=Path.GetFullPath("C01SourceV78/Delivery/C01_Ship_Multideck_v7.8.unitypackage");
        AssetDatabase.ExportPackage(new[]{"Assets/C01ShipV78","Assets/C01ShipV77","Assets/C01ShipV76","Assets/C01ShipV75","Assets/C01ShipV74","Assets/C01ShipV73","Assets/C01ShipV72","Assets/C01ShipV71","Assets/C01ShipV70","Assets/C01ShipV69","Assets/C01ShipV68","Assets/C01ShipV5/Runtime","Assets/C01ShipV6/Cargo/Runtime","Assets/C01ShipV61/Signage"},path,ExportPackageOptions.Recurse|ExportPackageOptions.IncludeDependencies);
        if(!File.Exists(path)||new FileInfo(path).Length<1024)throw new IOException("Unity package export failed");
    }
}
