using System.Collections;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class VentilationPrototypeTests
{
    const string Scene="C01_Ship_Ventilation_PROTOTYPE_v79";
    [UnityTest] public IEnumerator UpperCabinsConvertedButLowerCabinsRemain()
    {
        yield return SceneManager.LoadSceneAsync(Scene,LoadSceneMode.Single);yield return null;
        var ex=Object.FindFirstObjectByType<ShipExplorerV5>();Assert.That(ex,Is.Not.Null);ex.SetWalking(true);
        var zones=ex.master.GetComponentsInChildren<ShipZoneV5>(true);
        Assert.That(zones.Count(z=>z.deck==2&&z.kind=="ventilation_service"),Is.EqualTo(12));
        Assert.That(zones.Count(z=>z.deck==2&&(z.kind=="cabin"||z.kind=="bathroom")),Is.Zero);
        Assert.That(zones.Count(z=>z.deck==1&&z.kind=="cabin"),Is.EqualTo(12));
        Assert.That(zones.Count(z=>z.deck==1&&z.kind=="bathroom"),Is.EqualTo(12));
        var ducts=ex.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(m=>m.placementId.StartsWith("V79_VENT_")).ToArray();
        Assert.That(ducts.Length,Is.EqualTo(24));Assert.That(ducts.All(m=>m.GetComponentsInChildren<Collider>().Length>0),Is.True);
        Assert.That(ex.master.transform.Find("VENTILATION_PROTOTYPE_NOT_CONNECTED"),Is.Not.Null);
    }
    [UnityTest] public IEnumerator CharacterCanTraverseEachLocalDuctPair()
    {
        yield return SceneManager.LoadSceneAsync(Scene,LoadSceneMode.Single);yield return null;
        var ex=Object.FindFirstObjectByType<ShipExplorerV5>();ex.SetWalking(true);ex.enabled=false;
        var starts=ex.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(m=>m.placementId.StartsWith("V79_VENT_")&&m.placementId.EndsWith("_0")).ToArray();
        Assert.That(starts.Length,Is.EqualTo(12));
        foreach(var start in starts)
        {
            var c=ex.player;c.enabled=false;c.transform.position=start.transform.position+new Vector3(.5f,.04f,.75f);c.enabled=true;Physics.SyncTransforms();
            for(int i=0;i<54;i++)c.Move(new Vector3(.08f,-.01f,0));
            Assert.That(c.transform.position.x,Is.GreaterThan(start.transform.position.x+4.2f),start.placementId+" blocked at "+c.transform.position);
        }
    }
}
