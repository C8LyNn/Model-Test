using UnityEditor;
namespace C01.Editor {
    public class C01ModelImporter : AssetPostprocessor {
        void OnPreprocessModel(){
            if(!assetPath.StartsWith(C01Builder.Root+"/Models/"))return;
            var importer=(ModelImporter)assetImporter;importer.globalScale=1;importer.useFileScale=true;importer.isReadable=true;importer.importAnimation=false;importer.importCameras=false;importer.importLights=false;
        }
    }
}
