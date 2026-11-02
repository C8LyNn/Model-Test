using NUnit.Framework;
using UnityEditor;
using C01.Ship.V5.Editor;

public class ShipV6SettingsTests
{
    [Test]
    public void AddsV6AfterExistingScenesWithoutChangingTheirOrderOrEnabledState()
    {
        var first=new EditorBuildSettingsScene("Assets/UserFirst.unity",true);
        var disabled=new EditorBuildSettingsScene("Assets/UserDisabled.unity",false);
        var result=ShipV6Builder.WithV6Scene(new[]{first,disabled});
        Assert.That(result.Length,Is.EqualTo(3));
        Assert.That(result[0].path,Is.EqualTo(first.path));
        Assert.That(result[0].enabled,Is.True);
        Assert.That(result[1].path,Is.EqualTo(disabled.path));
        Assert.That(result[1].enabled,Is.False);
        Assert.That(result[2].path,Is.EqualTo(ShipV6Builder.ScenePath));
        Assert.That(result[2].enabled,Is.True);
    }

    [Test]
    public void DoesNotMoveOrEnableAnExistingV6Entry()
    {
        var current=new[]{new EditorBuildSettingsScene("Assets/Existing.unity",true),
            new EditorBuildSettingsScene(ShipV6Builder.ScenePath,false)};
        var result=ShipV6Builder.WithV6Scene(current);
        Assert.That(result.Length,Is.EqualTo(2));
        Assert.That(result[0].path,Is.EqualTo(current[0].path));
        Assert.That(result[1].path,Is.EqualTo(ShipV6Builder.ScenePath));
        Assert.That(result[1].enabled,Is.False);
    }
}
