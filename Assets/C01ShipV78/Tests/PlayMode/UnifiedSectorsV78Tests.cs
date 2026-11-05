using System.Collections;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class UnifiedSectorsV78Tests
{
    [System.Serializable] class Plan { public GateDataV5[] gates; }
    [System.Serializable] class Expected { public PlacementDataV5[] placements; }
    [System.Serializable] class RoofPlan { public string[] roof; }
    ShipExplorerV5 explorer;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v78",LoadSceneMode.Single);yield return null;
        explorer=Object.FindFirstObjectByType<ShipExplorerV5>();Assert.That(explorer,Is.Not.Null);explorer.SetWalking(true);explorer.enabled=false;
    }
    void Place(Vector3 p){var c=explorer.player;c.enabled=false;c.transform.position=p;c.enabled=true;Physics.SyncTransforms();}
    [UnityTest] public IEnumerator SixSectorOwnersContainBothDecksAndRespectCutaway()
    {
        var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true);
        var owners=zones.Where(z=>z.spansDecks).ToArray();Assert.That(owners.Length,Is.EqualTo(6));
        foreach(var z in owners)
        {
            Assert.That(z.deck,Is.EqualTo(1));Assert.That(z.height,Is.EqualTo(9));
            var markers=z.GetComponentsInChildren<ShipInstanceV5>(true);Assert.That(markers.Count(m=>m.deck==1),Is.GreaterThan(0),z.zoneId);
            Assert.That(markers.Count(m=>m.deck==2),Is.GreaterThan(0),z.zoneId);
            Assert.That(markers.All(m=>m.zoneId==z.zoneId),Is.True,z.zoneId);
        }
        foreach(string id in new[]{"L2_GYM","L2_CARGO","L2_LAB","L2_ENGINE_CONTROL","L2_MED","L2_TECH"})Assert.That(zones.Any(z=>z.zoneId==id),Is.False,id);
        explorer.SetWalking(false);explorer.SetDeck(1);
        var sector=owners.Single(z=>z.zoneId=="L1_GYM");
        var lower=sector.GetComponentsInChildren<ShipInstanceV5>(true).First(m=>m.deck==1&&m.GetComponentInChildren<Renderer>()!=null);
        var upper=sector.GetComponentsInChildren<ShipInstanceV5>(true).First(m=>m.placementId=="L2_ROUTE_GYM_FLOOR_0");
        Assert.That(lower.GetComponentInChildren<Renderer>().enabled,Is.True,"lower sector visible");
        Assert.That(upper.GetComponentInChildren<Renderer>().enabled,Is.False,"upper floor hidden in lower cutaway");
        explorer.SetDeck(2);Assert.That(upper.GetComponentInChildren<Renderer>().enabled,Is.True,"upper floor visible");
        Assert.That(explorer.ShouldShowZoneLabel(sector),Is.True,"shared sector visible on upper plan");
        explorer.SetWalking(true);Assert.That(upper.GetComponentInChildren<Renderer>().enabled,Is.True,"sector modules visible walking");
        yield return null;
    }
    [UnityTest] public IEnumerator BothFloorsHaveUsableEntrancesIntoEverySector()
    {
        foreach(float x in new[]{9f,51f,93f})foreach(bool north in new[]{false,true})foreach(int deck in new[]{1,2})
        {
            float z=north?54:33,sign=north?1:-1,y=deck==1?0:3.4f;
            var gate=explorer.gates.FirstOrDefault(g=>g!=null&&Mathf.Abs(g.transform.position.x-x)<.01f&&Mathf.Abs(g.transform.position.z-z)<.01f&&Mathf.Abs(g.transform.position.y-y)<.01f);
            Assert.That(gate,Is.Not.Null,$"gate {x} {z} deck {deck}");gate.SetImmediate(1);Physics.SyncTransforms();
            Place(new Vector3(x+1.5f,y+.04f,z-sign*1.3f));
            for(int i=0;i<40;i++)explorer.player.Move(new Vector3(0,-.015f,sign*.08f));
            Assert.That(sign*(explorer.player.transform.position.z-z),Is.GreaterThan(.6f),$"blocked sector {x} {z} deck {deck}, at {explorer.player.transform.position}");
            Assert.That(explorer.player.transform.position.y,Is.GreaterThan(y-.12f),"missing platform");
        }
        yield return null;
    }
    [UnityTest] public IEnumerator NewPlatformGatesWorkFromBothSides()
    {
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV75/Data/platforms.json")));
        Assert.That(plan.gates.Length,Is.EqualTo(6));
        foreach(var g in plan.gates)
        {
            var gate=explorer.gates.Single(x=>x!=null&&x.id==g.id);Assert.That(gate.IsOpen,Is.True,g.id);
            foreach(int side in new[]{0,1})
            {
                var button=explorer.buttons.Single(x=>x!=null&&x.gate==gate&&x.GetComponent<ShipInstanceV5>().placementId==g.buttons[side]);
                var target=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
                var point=target.bounds.center;var facing=button.transform.forward;Physics.SyncTransforms();
                Assert.That(explorer.TryPressRay(new Ray(point+facing*.9f,-facing),1.5f),Is.True,g.id+" button "+side);
                float deadline=Time.time+6;while((side==0?!gate.IsClosed:!gate.IsOpen)&&Time.time<deadline)yield return new WaitForFixedUpdate();
                Assert.That(side==0?gate.IsClosed:gate.IsOpen,Is.True,g.id+" state "+side);
            }
        }
    }
    [UnityTest] public IEnumerator ReparentedModulesRetainTheirWorldTransforms()
    {
        var expected=JsonUtility.FromJson<Expected>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV75/Data/sector_placements.json")));
        var roof=JsonUtility.FromJson<RoofPlan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV78/Data/tall_sectors.json"))).roof.ToHashSet();
        var all=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(m=>!string.IsNullOrEmpty(m.placementId)).ToDictionary(m=>m.placementId);
        Assert.That(expected.placements.Length,Is.GreaterThan(1000));
        foreach(var p in expected.placements)
        {
            Assert.That(all.TryGetValue(p.id,out var m),Is.True,p.id);
            Assert.That(m.zoneId,Is.EqualTo(p.zone),p.id+" owner");
            Assert.That(Vector3.Distance(m.transform.position,new Vector3(p.x,p.y+(roof.Contains(p.id)?3:0),p.z)),Is.LessThan(.003f),p.id+" position");
            Assert.That(Quaternion.Angle(m.transform.rotation,Quaternion.Euler(0,p.yaw,0)),Is.LessThan(.05f),p.id+" rotation");
        }
        yield return null;
    }
}

