using UnityEditor;
namespace C01.Ship.Editor {
    public class ShipModelImporter : AssetPostprocessor {
        void OnPreprocessModel(){if(!assetPath.StartsWith(ShipBuilder.Root+"/Models/"))return;var importer=(ModelImporter)assetImporter;importer.globalScale=1;importer.useFileScale=true;importer.isReadable=true;importer.importAnimation=false;importer.importLights=false;importer.importCameras=false;}
    }
}
