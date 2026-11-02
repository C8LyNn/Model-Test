using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;

public class ExplorerVisibilityTests
{
    GameObject root, actor, cameraObject;
    ShipExplorerV5 explorer;
    [SetUp] public void Setup()
    {
        root = new GameObject("ship");
        cameraObject = new GameObject("camera");
        actor = new GameObject("explorer");
        explorer = actor.AddComponent<ShipExplorerV5>();
        explorer.master = root;
        explorer.view = cameraObject.AddComponent<Camera>();
    }
    [TearDown] public void Cleanup()
    {
        Object.DestroyImmediate(root); Object.DestroyImmediate(actor); Object.DestroyImmediate(cameraObject);
    }
    Renderer Piece(string category, int deck)
    {
        var obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        obj.transform.SetParent(root.transform);
        var marker = obj.AddComponent<ShipInstanceV5>(); marker.category = category; marker.deck = deck;
        return obj.GetComponent<Renderer>();
    }
    [Test] public void CutawayAndWalkingKeepDifferentCategoriesCorrect()
    {
        var wall = Piece("Walls", 1); var roof = Piece("ROOF", 1); var shell = Piece("Hull", 1); var upper = Piece("Walls", 2);
        explorer.SetWalking(false); explorer.SetDeck(1);
        Assert.That(wall.enabled, Is.True); Assert.That(roof.enabled, Is.False);
        Assert.That(shell.enabled, Is.False); Assert.That(upper.enabled, Is.False);
        explorer.SetWalking(true);
        Assert.That(wall.enabled && roof.enabled && shell.enabled && upper.enabled, Is.True);
    }
    [Test] public void InvalidatingCachePicksUpNewModulesAndRemovedOnes()
    {
        var old = Piece("Wall", 1); explorer.SetWalking(false);
        Object.DestroyImmediate(old.gameObject);
        var added = Piece("Roof", 1);
        explorer.InvalidateSceneCache(); explorer.SetDeck(1);
        Assert.That(added.enabled, Is.False);
        explorer.SetWalking(true); Assert.That(added.enabled, Is.True);
    }
    [Test] public void ReplacingMasterAutomaticallyRefreshesCache()
    {
        var old = Piece("Wall", 1); explorer.SetWalking(false);
        var replacement = new GameObject("new ship");
        var roof = GameObject.CreatePrimitive(PrimitiveType.Cube); roof.transform.SetParent(replacement.transform);
        roof.AddComponent<ShipInstanceV5>().category = "roof";
        explorer.master = replacement; explorer.SetDeck(1);
        Assert.That(roof.GetComponent<Renderer>().enabled, Is.False);
        Assert.That(old.enabled, Is.True);
        Object.DestroyImmediate(replacement);
    }
}
