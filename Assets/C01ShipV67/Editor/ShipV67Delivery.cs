using System.IO;
using C01.Ship.V5;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipV67Delivery
{
    public static void CaptureAndExport()
    {
        Directory.CreateDirectory("C01ShipV67_QA/Screenshots");
        EditorSceneManager.OpenScene("Assets/C01ShipV67/Scenes/C01_Ship_Multideck_v67.unity",OpenSceneMode.Single);
        var e=Object.FindFirstObjectByType<ShipExplorerV5>();
        e.SetWalking(false);e.SetDeck(2);Capture(e.view,"C01ShipV67_QA/Screenshots/deck2.png");
        e.SetDeck(0);Capture(e.view,"C01ShipV67_QA/Screenshots/deck0.png");
        e.SetWalking(true);var cc=e.player;cc.enabled=false;
        cc.transform.SetPositionAndRotation(new Vector3(54,3.42f,43.5f),Quaternion.Euler(0,90,0));cc.enabled=true;
        e.SetWalking(true);Capture(e.view,"C01ShipV67_QA/Screenshots/chase.png");
        AssetDatabase.ExportPackage(new[]{"Assets/C01ShipV67","Assets/C01ShipV5/Runtime","Assets/C01ShipV6/Cargo/Runtime","Assets/C01ShipV61/Signage"},
            Path.GetFullPath("C01ShipV67_QA/C01_Ship_Multideck_v6.7.unitypackage"),ExportPackageOptions.Recurse|ExportPackageOptions.IncludeDependencies);
    }
    static void Capture(Camera camera,string path)
    {
        var previous=camera.targetTexture;var active=RenderTexture.active;var texture=new RenderTexture(1280,720,24);
        try{
            camera.targetTexture=texture;camera.Render();RenderTexture.active=texture;
            var image=new Texture2D(1280,720,TextureFormat.RGB24,false);image.ReadPixels(new Rect(0,0,1280,720),0,0);image.Apply();File.WriteAllBytes(path,image.EncodeToPNG());Object.DestroyImmediate(image);
        }finally{camera.targetTexture=previous;RenderTexture.active=active;texture.Release();Object.DestroyImmediate(texture);}
    }
}
