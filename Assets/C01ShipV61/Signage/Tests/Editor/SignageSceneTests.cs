using System.Collections;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.TestTools;

public class SignageSceneTests
{
    [UnityTest] public IEnumerator ButtonsRemainFittedAndFollowDeckVisibility()
    {
        EditorSceneManager.OpenScene("Assets/C01ShipV61/Scenes/C01_Ship_Multideck_v61.unity");
        yield return null;
        var explorer = Object.FindFirstObjectByType<ShipExplorerV5>();
        var signs = explorer.master.GetComponent<ButtonSignage>();
        Assert.That(signs, Is.Not.Null);
        explorer.SetWalking(true); signs.Synchronize();
        var buttons = explorer.buttons.Where(b => b != null && b.transform.Find("Button_Label") != null).ToArray();
        Assert.That(buttons.Length, Is.GreaterThan(0));
        foreach (var button in buttons)
        {
            var original = button.transform.Find("Button_Label").GetComponent<Renderer>();
            var screen = button.GetComponentsInChildren<ShipSolidV5>(true).First(p => p.role == "SCREEN");
            var fitted = screen.transform.Find("Button_Label_V61");
            Assert.That(fitted, Is.Not.Null, button.name);
            Assert.That(original.enabled, Is.False, button.name);
            var text = fitted.GetComponent<Renderer>();
            Assert.That(text.enabled, Is.True, button.name);
            Assert.That(text.sharedMaterial.shader.name, Is.EqualTo("C01/V61/ButtonText"));
            var textSize = text.localBounds.size * fitted.localScale.x;
            var screenSize = screen.GetComponent<MeshFilter>().sharedMesh.bounds.size;
            Assert.That(textSize.x, Is.LessThanOrEqualTo(screenSize.x + .001f), button.name);
            Assert.That(textSize.y, Is.LessThanOrEqualTo(screenSize.y + .001f), button.name);
        }
        explorer.SetWalking(false); explorer.SetDeck(0); signs.Synchronize();
        foreach (var button in buttons)
        {
            var screen = button.GetComponentsInChildren<ShipSolidV5>(true).First(p => p.role == "SCREEN");
            var text = screen.transform.Find("Button_Label_V61").GetComponent<Renderer>();
            Assert.That(text.enabled, Is.EqualTo(screen.GetComponent<Renderer>().enabled), button.name);
            Assert.That(button.transform.Find("Button_Label").GetComponent<Renderer>().enabled, Is.False);
        }
    }
}
