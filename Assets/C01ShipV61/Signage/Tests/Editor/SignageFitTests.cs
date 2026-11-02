using NUnit.Framework;
using UnityEngine;
using C01.Ship.V61.Signage;

public class SignageFitTests
{
    [Test]
    public void FitScalesLongTextToScreenWidth()
    {
        float scale = ButtonSignage.FitScale(new Vector2(2f, 0.5f), new Vector2(0.18f, 0.24f), 0.85f);
        Assert.That(scale, Is.EqualTo(0.0765f).Within(0.00001f));
    }

    [Test]
    public void FitRespectsHeightForTallText()
    {
        float scale = ButtonSignage.FitScale(new Vector2(0.1f, 2f), new Vector2(0.18f, 0.24f), 0.85f);
        Assert.That(scale, Is.EqualTo(0.102f).Within(0.00001f));
    }

    [Test]
    public void FitRejectsMissingTextBounds()
    {
        Assert.That(ButtonSignage.FitScale(Vector2.zero, Vector2.one, 0.85f), Is.EqualTo(0));
    }
}
