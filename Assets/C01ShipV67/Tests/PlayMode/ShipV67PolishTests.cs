using System.Reflection;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;

public class ShipV67PolishTests
{
    const float X = 10000f;
    static MethodInfo Method(string name)
    {
        var method=typeof(ShipExplorerV5).GetMethod(name,BindingFlags.Public|BindingFlags.Instance);
        Assert.That(method,Is.Not.Null,"Missing public behavior: "+name);
        return method;
    }
    [Test] public void WalkingLabelsRespectWallsDistanceAndView()
    {
        var owner=new GameObject("ExplorerTest");var cameraObject=new GameObject("CameraTest");var room=new GameObject("ZoneTest");var wall=GameObject.CreatePrimitive(PrimitiveType.Cube);
        try {
            var explorer=owner.AddComponent<ShipExplorerV5>();explorer.walking=true;explorer.view=cameraObject.AddComponent<Camera>();
            cameraObject.transform.position=new Vector3(X,11.5f,X);cameraObject.transform.rotation=Quaternion.identity;
            var zone=room.AddComponent<ShipZoneV5>();zone.floor=10;zone.height=3;room.transform.position=new Vector3(X,10,X+6);
            wall.transform.position=new Vector3(X,11.5f,X+3);wall.transform.localScale=new Vector3(3,3,.3f);Physics.SyncTransforms();
            var method=Method("ShouldShowZoneLabel");
            bool Visible()=> (bool)method.Invoke(explorer,new object[]{zone});
            Assert.That(Visible(),Is.False,"A wall hides the room name");
            wall.SetActive(false);Physics.SyncTransforms();Assert.That(Visible(),Is.True,"A nearby room in view is labelled");
            room.transform.position=new Vector3(X,10,X-6);Assert.That(Visible(),Is.False,"A room behind the camera is hidden");
            room.transform.position=new Vector3(X,10,X+30);Assert.That(Visible(),Is.False,"A distant room is hidden");
        } finally {Object.DestroyImmediate(owner);Object.DestroyImmediate(cameraObject);Object.DestroyImmediate(room);Object.DestroyImmediate(wall);}
    }
    [Test] public void ButtonTargetRespectsWallsAndDoesNotPressUntilInteraction()
    {
        var owner=new GameObject("ExplorerTest");var cameraObject=new GameObject("CameraTest");var control=GameObject.CreatePrimitive(PrimitiveType.Cube);var wall=GameObject.CreatePrimitive(PrimitiveType.Cube);var gateObject=new GameObject("GateTest");
        try {
            var explorer=owner.AddComponent<ShipExplorerV5>();explorer.walking=true;explorer.view=cameraObject.AddComponent<Camera>();cameraObject.transform.position=new Vector3(X,10,X);cameraObject.transform.rotation=Quaternion.identity;
            var gate=gateObject.AddComponent<ShipGateV5>();var button=control.AddComponent<ShipButtonV5>();button.gate=gate;
            control.transform.position=new Vector3(X,10,X+2);control.transform.localScale=Vector3.one*.3f;
            wall.transform.position=new Vector3(X,10,X+1);wall.transform.localScale=new Vector3(1,1,.2f);Physics.SyncTransforms();
            var method=Method("FindButtonOnRay");var ray=new Ray(new Vector3(X,10,X),Vector3.forward);
            ShipButtonV5 Find(float distance)=>(ShipButtonV5)method.Invoke(explorer,new object[]{ray,distance});
            Assert.That(Find(3.5f),Is.Null,"Blocked button is not advertised");
            wall.SetActive(false);Physics.SyncTransforms();Assert.That(Find(1),Is.Null,"Out-of-range button is not advertised");
            Assert.That(Find(3.5f),Is.EqualTo(button));Assert.That(gate.target,Is.Zero,"Looking at a button must not press it");
            Assert.That(explorer.TryPressScreen(Vector2.zero),Is.True);Assert.That(gate.target,Is.EqualTo(1));
        } finally {Object.DestroyImmediate(owner);Object.DestroyImmediate(cameraObject);Object.DestroyImmediate(control);Object.DestroyImmediate(wall);Object.DestroyImmediate(gateObject);}
    }
}
