using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using C01.Ship.V5.Editor;

public static class ShipV6FinalQA
{
    public static void Run()
    {
        var data=ShipV6Builder.Read();
        var errors=new System.Collections.Generic.List<string>();
        int imported=0;
        foreach(var model in data.models)
        {
            string path=ShipV6Builder.Root+"/Models/"+model.id+".fbx";
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if(prefab==null) { errors.Add(model.id+": missing FBX import");continue; }
            int actual=prefab.GetComponentsInChildren<MeshFilter>(true).Length;
            if(actual!=model.parts.Length) errors.Add(model.id+": mesh parts "+actual+" != "+model.parts.Length);
            else imported++;
        }
        var dir=ShipV6Builder.QA;
        Directory.CreateDirectory(dir);
        var report=new Report { status=errors.Count==0?"PASS":"FAIL",expected=data.models.Length,imported=imported,errors=errors.ToArray() };
        File.WriteAllText(Path.Combine(dir,"fbx_import_v6.json"),JsonUtility.ToJson(report,true));
        if(errors.Count>0) throw new Exception("FBX import verification failed: "+string.Join("; ",errors.Take(10)));
        ShipV6Capture.Capture();
        ShipV6Builder.Export();
    }
    [Serializable] class Report
    {
        public string status;
        public int expected,imported;
        public string[] errors;
    }
}
