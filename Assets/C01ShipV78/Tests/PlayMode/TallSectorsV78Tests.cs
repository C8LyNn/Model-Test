using System.Collections;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class TallSectorsV78Tests
{
    [UnityTest] public IEnumerator SixSectorsHaveContinuousNineMetreCeilings()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v78",LoadSceneMode.Single);yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();Assert.That(explorer,Is.Not.Null);explorer.SetWalking(true);Physics.SyncTransforms();
        var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true).Where(z=>z.spansDecks).ToArray();Assert.That(zones.Length,Is.EqualTo(6));
        foreach(var zone in zones)Assert.That(zone.height,Is.EqualTo(9).Within(.001f),zone.zoneId);
        foreach(float x in new[]{4.5f,46.5f,88.5f})foreach(float z in new[]{19.5f,58.5f})
        {
            var hits=Physics.RaycastAll(new Vector3(x,8,z),Vector3.up,2f).OrderBy(h=>h.distance).ToArray();
            Assert.That(hits.Length,Is.GreaterThan(0),$"missing ceiling {x} {z}");
            Assert.That(hits[0].point.y,Is.EqualTo(9).Within(.02f),$"wrong ceiling {x} {z}");
        }
        Assert.That(explorer.minDeck,Is.EqualTo(1));Assert.That(explorer.lifts.All(l=>l.landings[0]==null),Is.True);
    }

    [UnityTest] public IEnumerator RaisedPerimeterUsesSeparateModules()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v78",LoadSceneMode.Single);yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();var markers=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true);
        var walls=markers.Where(m=>m.placementId.StartsWith("V78_W_")).ToArray();var nodes=markers.Where(m=>m.placementId.StartsWith("V78_N_")).ToArray();
        Assert.That(walls.Length,Is.EqualTo(216));Assert.That(nodes.Length,Is.EqualTo(212));
        Assert.That(walls.All(m=>m.modelId=="W78_H2600"&&Mathf.Abs(m.transform.position.y-6.4f)<.001f),Is.True);
        Assert.That(markers.Count(m=>m.category=="Ceilings"&&Mathf.Abs(m.transform.position.y-9.2f)<.001f),Is.EqualTo(504));
    }
}
