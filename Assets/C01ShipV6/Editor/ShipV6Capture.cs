using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using C01.Ship.V5;

public static class ShipV6Capture
{
    static void Save(Camera camera,string path)
    {
        var rt=new RenderTexture(1600,900,24,RenderTextureFormat.ARGB32);
        camera.targetTexture=rt;
        var old=RenderTexture.active;
        camera.Render();
        RenderTexture.active=rt;
        var texture=new Texture2D(1600,900,TextureFormat.RGB24,false);
        texture.ReadPixels(new Rect(0,0,1600,900),0,0);
        texture.Apply();
        File.WriteAllBytes(path,texture.EncodeToPNG());
        camera.targetTexture=null;
        RenderTexture.active=old;
        Object.DestroyImmediate(texture);
        Object.DestroyImmediate(rt);
    }
    public static void Capture()
    {
        EditorSceneManager.OpenScene("Assets/C01ShipV6/Scenes/C01_Ship_Multideck_v6.unity");
        var dir=Path.GetFullPath(Path.Combine(Application.dataPath,"../C01ShipV6_QA/Screenshots"));
        Directory.CreateDirectory(dir);
        var go=new GameObject("QA_Camera");
        var cam=go.AddComponent<Camera>();
        cam.backgroundColor=new Color(.025f,.04f,.06f);
        cam.clearFlags=CameraClearFlags.SolidColor;
        cam.nearClipPlane=.05f;cam.farClipPlane=1000;
        cam.transform.position=new Vector3(24,8,69);
        cam.transform.rotation=Quaternion.LookRotation(new Vector3(24,10,88)-cam.transform.position,Vector3.up);
        cam.fieldOfView=70;
        Save(cam,Path.Combine(dir,"sector_top_fascia.png"));
        cam.transform.position=new Vector3(-15,9,45);
        cam.transform.rotation=Quaternion.LookRotation(new Vector3(-47,11,45)-cam.transform.position,Vector3.up);
        Save(cam,Path.Combine(dir,"bridge_top_fascia.png"));
        cam.transform.position=new Vector3(127.5f,1.65f,10.5f);
        cam.transform.rotation=Quaternion.LookRotation(new Vector3(129,1.4f,10.5f)-cam.transform.position,Vector3.up);
        Save(cam,Path.Combine(dir,"stern_cargo_lift.png"));
        foreach(var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
        {
            var marker=r.GetComponentInParent<ShipInstanceV5>();
            if(marker==null) continue;
            if(marker.category=="Ceilings" || (marker.category=="Floors" && marker.deck>1) ||
               ((marker.category=="Walls" || marker.category=="Nodes") && r.bounds.min.y>6.01f))
                r.enabled=false;
        }
        cam.orthographic=true;cam.orthographicSize=67;
        cam.transform.position=new Vector3(63,250,45);
        cam.transform.rotation=Quaternion.Euler(90,0,0);
        Save(cam,Path.Combine(dir,"deck1_overview.png"));
        Object.DestroyImmediate(go);
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null) throw new System.Exception("Explorer missing");
        explorer.SetWalking(false);
        explorer.SetDeck(1);
        explorer.ResetView();
        Save(explorer.view,Path.Combine(dir,"overview_actual_camera.png"));
    }
}
