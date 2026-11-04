using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class WallRepairGeometryTests
{
    [Serializable] class Plan { public Move[] moves; public string[] singleSeamWalls,topBandFascias; }
    [Serializable] class Move { public string id;public float fromY,toY; }
    [Serializable] class RoofPlan { public Roof[] roofs; }
    [Serializable] class Roof { public string id;public float bottom,top;public Cap[] caps; }
    [Serializable] class Cap { public float[] outline; }
    ShipExplorerV5 explorer;Plan plan;Dictionary<string,ShipInstanceV5> instances;

    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v70",LoadSceneMode.Single);
        yield return null;
        explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();Assert.That(explorer,Is.Not.Null);
        plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV70/Data/wall_repair.json")));
        instances=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(x=>!string.IsNullOrEmpty(x.placementId)).ToDictionary(x=>x.placementId);
    }
    static Mesh WallMesh(ShipInstanceV5 wall)
    {
        var part=wall.GetComponentsInChildren<ShipSolidV5>(true).OrderBy(x=>x.partIndex).First();
        return part.GetComponent<MeshFilter>().sharedMesh;
    }
    static int TopBandTriangles(Mesh mesh,float height)
    {
        if(mesh==null||mesh.subMeshCount<2)return 0;
        var v=mesh.vertices;var t=mesh.GetTriangles(1);int count=0;
        for(int i=0;i<t.Length;i+=3)
            if(v[t[i]].y>height-.061f && v[t[i+1]].y>height-.061f && v[t[i+2]].y>height-.061f)count++;
        return count;
    }
    [UnityTest] public IEnumerator UpperModulesAlignWithTheRealSlabAndKeepTheirColliders()
    {
        Assert.That(plan.moves.Length,Is.GreaterThan(0));Physics.SyncTransforms();
        foreach(var move in plan.moves)
        {
            Assert.That(instances.TryGetValue(move.id,out var marker),Is.True,move.id);
            Assert.That(marker.transform.position.y,Is.EqualTo(move.toY).Within(.001f),move.id);
            var colliders=marker.GetComponentsInChildren<Collider>(true);Assert.That(colliders.Length,Is.GreaterThan(0),move.id);
            float h=marker.modelId.Contains("H3000")?3f:.4f;
            Assert.That(colliders.Min(c=>c.bounds.min.y),Is.EqualTo(move.toY).Within(.002f),move.id);
            Assert.That(colliders.Max(c=>c.bounds.max.y),Is.EqualTo(move.toY+h).Within(.002f),move.id);
        }
        yield return null;
    }
    [UnityTest] public IEnumerator WallSeamsDoNotOutlineASecondSmallPanel()
    {
        Assert.That(plan.singleSeamWalls.Length,Is.GreaterThan(0));
        foreach(var id in plan.singleSeamWalls)
        {
            Assert.That(instances.TryGetValue(id,out var marker),Is.True,id);
            var mesh=WallMesh(marker);Assert.That(mesh,Is.Not.Null,id);
            Assert.That(TopBandTriangles(mesh,3f),Is.Zero,id+" retains upper band below the slab");
        }
        foreach(var id in plan.topBandFascias)
        {
            var mesh=WallMesh(instances[id]);Assert.That(TopBandTriangles(mesh,.4f),Is.GreaterThan(0),id+" missing final edge");
        }
        yield return null;
    }
    [UnityTest] public IEnumerator SectorRoofsHaveFlushTopsAndKeepTheirCeilingHeight()
    {
        var roofs=JsonUtility.FromJson<RoofPlan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV70/Data/roof_repair.json"))).roofs;
        Assert.That(roofs.Length,Is.GreaterThan(0));Physics.SyncTransforms();
        foreach(var roof in roofs)
        {
            Assert.That(instances.TryGetValue(roof.id,out var marker),Is.True,roof.id);
            var colliders=marker.GetComponentsInChildren<Collider>(true);Assert.That(colliders.Length,Is.GreaterThan(0),roof.id);
            Assert.That(colliders.Min(c=>c.bounds.min.y),Is.EqualTo(roof.bottom).Within(.002f),roof.id+" underside");
            Assert.That(colliders.Max(c=>c.bounds.max.y),Is.EqualTo(roof.top).Within(.002f),roof.id+" exterior top");
            var renderers=marker.GetComponentsInChildren<MeshRenderer>(true);
            Assert.That(renderers.Max(r=>r.bounds.max.y),Is.EqualTo(roof.top).Within(.002f),roof.id+" visual top");
        }
        yield return null;
    }
    [UnityTest] public IEnumerator RoofCapsArePartOfTheirTilesAndDoNotPenetrateOtherGeometry()
    {
        var roofs=JsonUtility.FromJson<RoofPlan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV70/Data/roof_repair.json"))).roofs;
        int checkedCaps=0;Physics.SyncTransforms();
        foreach(var roof in roofs)
        {
            if(roof.caps==null||roof.caps.Length==0)continue;
            var marker=instances[roof.id];var part=marker.GetComponentsInChildren<ShipSolidV5>(true).OrderBy(x=>x.partIndex).First();
            var colliders=part.GetComponents<Collider>();
            Assert.That(colliders.Length,Is.EqualTo(roof.caps.Length+1),roof.id+" cap colliders");
            foreach(var cap in colliders.Skip(1))
            {
                checkedCaps++;var b=cap.bounds;
                Assert.That(b.min.y,Is.EqualTo(6.4f).Within(.002f),roof.id);
                Assert.That(b.max.y,Is.EqualTo(6.6f).Within(.002f),roof.id);
                foreach(var other in Physics.OverlapBox(b.center,b.extents,Quaternion.identity,Physics.DefaultRaycastLayers,QueryTriggerInteraction.Ignore))
                {
                    if(other==cap||other.transform.IsChildOf(explorer.player.transform))continue;
                    if(Physics.ComputePenetration(cap,cap.transform.position,cap.transform.rotation,other,other.transform.position,other.transform.rotation,out var dir,out var depth))
                        Assert.That(depth,Is.LessThan(.002f),roof.id+" roof cap intersects "+other.name+" depth="+depth);
                }
            }
        }
        Assert.That(checkedCaps,Is.GreaterThan(0));yield return null;
    }
}
