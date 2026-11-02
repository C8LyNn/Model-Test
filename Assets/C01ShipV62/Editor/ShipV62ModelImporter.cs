using System;
using UnityEditor;

public sealed class ShipV62ModelImporter : AssetPostprocessor
{
    void OnPreprocessModel()
    {
        if(!assetPath.StartsWith("Assets/C01ShipV62/Models/",StringComparison.Ordinal)) return;
        var importer=(ModelImporter)assetImporter;
        importer.globalScale=1;importer.useFileScale=true;importer.isReadable=true;
        importer.importAnimation=false;importer.importLights=false;importer.importCameras=false;
    }
}
