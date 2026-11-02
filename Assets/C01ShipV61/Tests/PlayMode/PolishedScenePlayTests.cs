using System.Collections;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class PolishedScenePlayTests
{
    [UnityTest] public IEnumerator PlayerCanOpenCabinGateWithFittedLabel()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v61", LoadSceneMode.Single);
        yield return null;
        var explorer = Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer, Is.Not.Null);
        explorer.SetWalking(true); explorer.enabled = false;
        var signs = explorer.master.GetComponent<ButtonSignage>(); signs.Synchronize();
        var button = explorer.buttons.First(b => b.gate != null && b.airlock == null && b.lift == null && b.gate.id.Contains("CABIN"));
        var screen = button.GetComponentsInChildren<ShipSolidV5>().First(p => p.role == "SCREEN");
        Assert.That(screen.transform.Find("Button_Label_V61").GetComponent<Renderer>().enabled, Is.True);
        button.gate.SetImmediate(0);
        var target = button.GetComponentsInChildren<Collider>().First().bounds.center;
        var forward = button.transform.forward; var player = explorer.player;
        player.enabled = false;
        player.transform.position = new Vector3(target.x + forward.x, button.transform.position.y - 1.05f, target.z + forward.z);
        player.transform.rotation = Quaternion.LookRotation(-forward, Vector3.up); player.enabled = true;
        explorer.view.transform.rotation = Quaternion.LookRotation(target - explorer.view.transform.position, Vector3.up);
        Physics.SyncTransforms();
        Assert.That(explorer.TryPressScreen(new Vector2(5, Screen.height - 5)), Is.True);
        float deadline = Time.time + 5;
        while (!button.gate.IsOpen && Time.time < deadline) yield return null;
        Assert.That(button.gate.IsOpen, Is.True);
    }
}
