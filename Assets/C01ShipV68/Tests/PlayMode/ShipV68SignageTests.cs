using System.Collections;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipV68SignageTests
{
    [UnityTest] public IEnumerator LegacyButtonTextNeverFlashesThroughWallsOnModeChange()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v67",LoadSceneMode.Single);
        yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();
        var signage=explorer.master.GetComponent<ButtonSignage>();
        Assert.That(signage,Is.Not.Null);Assert.That(signage.isActiveAndEnabled,Is.True);
        signage.Synchronize();
        var labels=explorer.buttons.Where(b=>b!=null).Select(b=>b.transform.Find("Button_Label"))
            .Where(t=>t!=null).Select(t=>t.GetComponent<Renderer>()).Where(r=>r!=null).ToArray();
        Assert.That(labels.Length,Is.GreaterThan(20));
        explorer.SetWalking(true);
        Assert.That(labels.Count(r=>r.enabled),Is.Zero,"Walking view re-enabled the old overlay labels");
        explorer.SetWalking(false);
        Assert.That(labels.Count(r=>r.enabled),Is.Zero,"Overview re-enabled the old overlay labels");
    }
}
