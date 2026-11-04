using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using C01.Ship.V5;
using C01.Ship.V5.Editor;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipSurfaceV70Builder
{
    const string Root="Assets/C01ShipV70";
    public const string ScenePath=Root+"/Scenes/C01_Ship_Multideck_v70.unity";
    public const string MasterPath=Root+"/Prefabs/C01_SHIP_MASTER_V70.prefab";
    const string PreviousScene="Assets/C01ShipV69/Scenes/C01_Ship_Multideck_v69.unity";
    [Serializable] class WallPlan { public Move[] moves;public string[] singleSeamWalls,topBandFascias; }
    [Serializable] class Move { public string id;public float fromY,toY; }
    [Serializable] class RoofPlan { public Roof[] roofs; }
    [Serializable] class Roof { public string id,model,variant;public float bottom,top;public Cap[] caps; }
    [Serializable] class Cap { public float[] outline; }
    static readonly Dictionary<string,Mesh> meshes=new Dictionary<string,Mesh>();

    static string Hash(string value)
    {
        using(var h=SHA1.Create())return BitConverter.ToString(h.ComputeHash(Encoding.UTF8.GetBytes(value))).Replace("-","").Substring(0,16);
    }
    static Mesh SaveMesh(string key,Mesh mesh)
    {
        if(meshes.TryGetValue(key,out var cached)){UnityEngine.Object.DestroyImmediate(mesh);return cached;}
        var path=Root+"/Meshes/"+key+".asset";
        var saved=AssetDatabase.LoadAssetAtPath<Mesh>(path);
        if(saved==null){mesh.name=key;AssetDatabase.CreateAsset(mesh,path);saved=mesh;}
        else {EditorUtility.CopySerialized(mesh,saved);UnityEngine.Object.DestroyImmediate(mesh);}
        meshes.Add(key,saved);return saved;
    }
    static string AssetKey(Mesh source)
    {
        var path=AssetDatabase.GetAssetPath(source);var guid=AssetDatabase.AssetPathToGUID(path);
        if(string.IsNullOrEmpty(guid))throw new Exception("Mesh must be a reusable asset: "+source.name);
        return guid;
    }
    static Mesh WithoutTopBand(Mesh source)
    {
        if(source==null||source.subMeshCount!=2)throw new Exception("Expected a two-material modular wall");
        var mesh=UnityEngine.Object.Instantiate(source);var vertices=source.vertices;
        var plain=new List<int>(source.GetTriangles(0));var band=new List<int>();var triangles=source.GetTriangles(1);int removed=0;
        for(int i=0;i<triangles.Length;i+=3)
        {
            bool top=vertices[triangles[i]].y>2.939f&&vertices[triangles[i+1]].y>2.939f&&vertices[triangles[i+2]].y>2.939f;
            var target=top?plain:band;target.Add(triangles[i]);target.Add(triangles[i+1]);target.Add(triangles[i+2]);if(top)removed++;
        }
        if(removed==0||band.Count==0)throw new Exception("Wall has no expected top/bottom bands: "+source.name);
        mesh.SetTriangles(plain,0);mesh.SetTriangles(band,1);mesh.RecalculateBounds();
        return SaveMesh("wall_one_seam_"+AssetKey(source),mesh);
    }
    static Mesh FasciaTopBand()
    {
        const float l=.15f,r=2.85f,z=.15f,h=.4f,cut=.34f;
        var v=new List<Vector3>();var plain=new List<int>();var band=new List<int>();
        void Quad(Vector3 a,Vector3 b,Vector3 c,Vector3 d,Vector3 n,bool stripe)
        {
            int k=v.Count;v.Add(a);v.Add(b);v.Add(c);v.Add(d);var t=stripe?band:plain;
            if(Vector3.Dot(Vector3.Cross(b-a,c-a),n)>=0)t.AddRange(new[]{k,k+1,k+2,k,k+2,k+3});
            else t.AddRange(new[]{k,k+2,k+1,k,k+3,k+2});
        }
        foreach(var section in new[]{(0f,cut,false),(cut,h,true)})
        {
            float a=section.Item1,b=section.Item2;bool stripe=section.Item3;
            Quad(new Vector3(l,a,z),new Vector3(r,a,z),new Vector3(r,b,z),new Vector3(l,b,z),Vector3.forward,stripe);
            Quad(new Vector3(l,a,-z),new Vector3(r,a,-z),new Vector3(r,b,-z),new Vector3(l,b,-z),Vector3.back,stripe);
        }
        Quad(new Vector3(l,0,-z),new Vector3(l,0,z),new Vector3(l,h,z),new Vector3(l,h,-z),Vector3.left,false);
        Quad(new Vector3(r,0,-z),new Vector3(r,0,z),new Vector3(r,h,z),new Vector3(r,h,-z),Vector3.right,false);
        Quad(new Vector3(l,0,-z),new Vector3(r,0,-z),new Vector3(r,0,z),new Vector3(l,0,z),Vector3.down,false);
        Quad(new Vector3(l,h,-z),new Vector3(r,h,-z),new Vector3(r,h,z),new Vector3(l,h,z),Vector3.up,false);
        var mesh=new Mesh();mesh.SetVertices(v);mesh.subMeshCount=2;mesh.SetTriangles(plain,0);mesh.SetTriangles(band,1);mesh.RecalculateNormals();mesh.RecalculateBounds();
        return SaveMesh("fascia_top_seam",mesh);
    }
    static Mesh ExtendedRoof(Mesh source,float amount)
    {
        var mesh=UnityEngine.Object.Instantiate(source);var vertices=mesh.vertices;
        for(int i=0;i<vertices.Length;i++)if(vertices[i].y>-.00001f)vertices[i].y+=amount;
        mesh.vertices=vertices;mesh.RecalculateBounds();
        return SaveMesh("roof_thick_"+AssetKey(source),mesh);
    }
    static PartDataV5 CapPart(Cap cap)
    {
        if(cap.outline==null||cap.outline.Length<6||cap.outline.Length%2!=0)throw new Exception("Invalid roof cap");
        return new PartDataV5 {outline=cap.outline,y0=.2f,y1=.4f};
    }
    static Mesh CapMesh(Cap cap)
    {
        var key=Hash(string.Join(",",cap.outline.Select(v=>v.ToString("R",System.Globalization.CultureInfo.InvariantCulture))));
        if(meshes.TryGetValue("roof_cap_"+key,out var existing))return existing;
        return SaveMesh("roof_cap_"+key,ShipV68Builder.Prism(CapPart(cap)));
    }
    static Mesh RoofWithCaps(Mesh extended,Cap[] caps)
    {
        if(caps==null||caps.Length==0)return extended;
        var key="roof_complete_"+Hash(extended.name+"|"+string.Join("|",caps.Select(c=>string.Join(",",c.outline.Select(v=>v.ToString("R",System.Globalization.CultureInfo.InvariantCulture))))));
        if(meshes.TryGetValue(key,out var cached))return cached;
        var list=new List<CombineInstance>{new CombineInstance{mesh=extended,transform=Matrix4x4.identity}};
        foreach(var cap in caps)list.Add(new CombineInstance{mesh=CapMesh(cap),transform=Matrix4x4.identity});
        var mesh=new Mesh();mesh.CombineMeshes(list.ToArray(),true,false,false);mesh.RecalculateBounds();
        return SaveMesh(key,mesh);
    }
    static ShipSolidV5[] Parts(ShipInstanceV5 marker)=>marker.GetComponentsInChildren<ShipSolidV5>(true).OrderBy(p=>p.partIndex).ToArray();
    static ShipSolidV5[] Parts(GameObject module)=>module.GetComponentsInChildren<ShipSolidV5>(true).OrderBy(p=>p.partIndex).ToArray();
    static GameObject EditableModuleCopy(ShipInstanceV5 marker,string name)
    {
        var copy=UnityEngine.Object.Instantiate(marker.gameObject);copy.name=name;
        if(PrefabUtility.IsPartOfPrefabInstance(copy))
        {
            if(PrefabUtility.GetNearestPrefabInstanceRoot(copy)!=copy)throw new Exception("Module copy is not a prefab root: "+name);
            PrefabUtility.UnpackPrefabInstance(copy,PrefabUnpackMode.Completely,InteractionMode.AutomatedAction);
        }
        var metadata=copy.GetComponent<ShipInstanceV5>();if(metadata!=null)UnityEngine.Object.DestroyImmediate(metadata);
        copy.transform.SetParent(null,false);copy.transform.SetPositionAndRotation(Vector3.zero,Quaternion.identity);copy.transform.localScale=Vector3.one;
        return copy;
    }
    static GameObject SaveModule(GameObject module,string modelId)
    {
        foreach(var part in Parts(module))part.modelId=modelId;
        var prefab=PrefabUtility.SaveAsPrefabAsset(module,Root+"/Prefabs/Modules/"+modelId+".prefab");
        UnityEngine.Object.DestroyImmediate(module);
        if(prefab==null)throw new Exception("Failed to save reusable module "+modelId);
        return prefab;
    }
    static GameObject WallModule(ShipInstanceV5 sample,bool fascia)
    {
        string id=fascia?"W3_H400_V70_TopSeam":"W3_H3000_V70_OneSeam";
        var copy=EditableModuleCopy(sample,id);var parts=Parts(copy);
        if(parts.Length==0)throw new Exception("Wall module has no parts");
        var filter=parts[0].GetComponent<MeshFilter>();if(filter==null)throw new Exception("Wall module has no mesh");
        filter.sharedMesh=fascia?FasciaTopBand():WithoutTopBand(filter.sharedMesh);
        return SaveModule(copy,id);
    }
    static GameObject RoofModule(ShipInstanceV5 sample,Roof item)
    {
        if(string.IsNullOrEmpty(item.variant))throw new Exception("Missing reusable roof ID: "+item.id);
        var copy=EditableModuleCopy(sample,item.variant);var parts=Parts(copy);
        if(parts.Length==0)throw new Exception("Roof geometry missing: "+item.id);
        for(int i=0;i<parts.Length;i++)
        {
            var part=parts[i];var filter=part.GetComponent<MeshFilter>();var collider=part.GetComponent<Collider>();
            if(filter==null||collider==null)throw new Exception("Roof part missing mesh/collider: "+item.id);
            var extended=ExtendedRoof(filter.sharedMesh,.4f);
            filter.sharedMesh=i==0?RoofWithCaps(extended,item.caps):extended;
            if(collider is BoxCollider box)
            {
                var size=box.size;size.y+=.4f;box.size=size;var center=box.center;center.y+=.2f;box.center=center;
            }
            else if(collider is MeshCollider meshCollider)meshCollider.sharedMesh=extended;
            else throw new Exception("Unsupported roof collider: "+item.id);
        }
        foreach(var cap in item.caps??Array.Empty<Cap>())
        {
            var data=CapPart(cap);var part=parts[0].gameObject;
            if(ShipV68Builder.Rectangle(data))
            {
                var bounds=ShipV68Builder.Bounds(data);var collider=part.AddComponent<BoxCollider>();collider.center=bounds.center;collider.size=bounds.size;
            }
            else {var collider=part.AddComponent<MeshCollider>();collider.sharedMesh=CapMesh(cap);collider.convex=true;}
        }
        return SaveModule(copy,item.variant);
    }
    static ShipInstanceV5 ReplaceModule(ShipInstanceV5 old,GameObject prefab,string modelId)
    {
        if(old.GetComponents<MonoBehaviour>().Any(c=>c!=old))throw new Exception("Module contains extra behaviour: "+old.placementId);
        var t=old.transform;var parent=t.parent;var position=t.localPosition;var rotation=t.localRotation;var scale=t.localScale;
        var id=old.placementId;var category=old.category;var zone=old.zoneId;var deck=old.deck;var sibling=t.GetSiblingIndex();var active=old.gameObject.activeSelf;
        var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,parent);go.name=id;go.transform.localPosition=position;go.transform.localRotation=rotation;go.transform.localScale=scale;
        go.transform.SetSiblingIndex(sibling);go.SetActive(active);
        var marker=go.AddComponent<ShipInstanceV5>();marker.placementId=id;marker.modelId=modelId;marker.category=category;marker.zoneId=zone;marker.deck=deck;
        UnityEngine.Object.DestroyImmediate(old.gameObject);return marker;
    }

    [MenuItem("Tools/C01 Ship v7.0/Unify walls and roof")]
    public static void Build()
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode)throw new InvalidOperationException("Stop Play mode first");
        var wall=JsonUtility.FromJson<WallPlan>(File.ReadAllText(Root+"/Data/wall_repair.json"));
        var roof=JsonUtility.FromJson<RoofPlan>(File.ReadAllText(Root+"/Data/roof_repair.json"));
        if(wall?.moves==null||wall.moves.Length==0||roof?.roofs==null||roof.roofs.Length==0)throw new Exception("Missing repair data");
        foreach(var folder in new[]{"Meshes","Prefabs/Modules","Scenes"})Directory.CreateDirectory(Root+"/"+folder);
        AssetDatabase.Refresh();meshes.Clear();
        var scene=EditorSceneManager.OpenScene(PreviousScene,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();if(explorer==null||explorer.master==null)throw new Exception("Master missing");
        var master=explorer.master;var signage=master.GetComponent<ButtonSignage>();if(signage!=null)signage.enabled=false;
        var markers=master.GetComponentsInChildren<ShipInstanceV5>(true).Where(p=>!string.IsNullOrEmpty(p.placementId)).ToDictionary(p=>p.placementId);
        foreach(var move in wall.moves)
        {
            if(!markers.TryGetValue(move.id,out var p)||Mathf.Abs(p.transform.position.y-move.fromY)>.001f)throw new Exception("Incorrect original position: "+move.id);
            var pos=p.transform.position;pos.y=move.toY;p.transform.position=pos;PrefabUtility.RecordPrefabInstancePropertyModifications(p.transform);
        }
        var wallPrefab=WallModule(markers[wall.singleSeamWalls[0]],false);
        foreach(var id in wall.singleSeamWalls)markers[id]=ReplaceModule(markers[id],wallPrefab,"W3_H3000_V70_OneSeam");
        var fasciaPrefab=WallModule(markers[wall.topBandFascias[0]],true);
        foreach(var id in wall.topBandFascias)markers[id]=ReplaceModule(markers[id],fasciaPrefab,"W3_H400_V70_TopSeam");
        int capCount=0;var roofPrefabs=new Dictionary<string,GameObject>();
        foreach(var item in roof.roofs)
        {
            if(!markers.TryGetValue(item.id,out var marker)||marker.modelId!=item.model)throw new Exception("Roof tile missing: "+item.id);
            if(!roofPrefabs.TryGetValue(item.variant,out var prefab))roofPrefabs[item.variant]=prefab=RoofModule(marker,item);
            markers[item.id]=ReplaceModule(marker,prefab,item.variant);capCount+=(item.caps??Array.Empty<Cap>()).Length;
        }
        if(signage!=null)signage.enabled=true;
        explorer.InvalidateSceneCache();explorer.SetWalking(true);Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)throw new Exception("Failed to save master variant");
        EditorSceneManager.MarkSceneDirty(scene);if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Failed to save scene variant");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();Debug.Log("C01 V7.0 surfaces: moved="+wall.moves.Length+" wallSeams="+wall.singleSeamWalls.Length+" roofTiles="+roof.roofs.Length+" roofCaps="+capCount+" sharedRoofPrefabs="+roofPrefabs.Count);
    }
}
