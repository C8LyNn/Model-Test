// Executes the ACTUAL Unity-targeted C01ToolBinLatchGate.cs against API doubles.
// This is *NOT* Unity6, PlayMode, PhysX, Blender or FBX importer acceptance.
using System;
using System.Reflection;
using C01.Cargo;
using UnityEngine;
class P1807OfflineRuntimeTests
{
    static int passed;
    static void Check(bool condition,string name)
    {
        if(!condition)throw new Exception("P18-07 W24 C# runtime FAIL: "+name);
        passed++;
        Console.WriteLine("C01_P1807_W24_PASS "+name);
    }
    static void Near(float actual,float expected,string name)
    {
        Check(Math.Abs(actual-expected)<0.0003f,name+" actual="+actual);
    }
    static void Late(C01ToolBinLatchGate gate)
    {
        typeof(C01ToolBinLatchGate).GetMethod("LateUpdate",
            BindingFlags.NonPublic|BindingFlags.Instance).Invoke(gate,null);
    }
    sealed class Fixture
    {
        public GameObject root, imported, lid, lockObj;
        public Transform hinge;
        public BoxCollider collider;
        public MeshRenderer renderer;
        public C01ToolBinLatchGate gate;
        public Fixture(bool rotateImported=false)
        {
            root=new GameObject("P18_07");
            imported=new GameObject("P18-07_FBX");
            imported.transform.parent=root.transform;
            if(rotateImported)
                imported.transform.localRotation=Quaternion.AngleAxis(90f,Vector3.up);
            lid=new GameObject("Bin_Lid");
            GameObject h=new GameObject("Toolbox_LidHinge");
            h.transform.parent=imported.transform;
            hinge=h.transform;
            lid.transform.parent=hinge;
            lockObj=new GameObject("Front_Lock");
            lockObj.transform.parent=imported.transform;
            lockObj.transform.localPosition=new Vector3(0,-0.165f,0.225f);
            collider=lockObj.AddComponent<BoxCollider>();
            renderer=lockObj.AddComponent<MeshRenderer>();
            gate=root.AddComponent<C01ToolBinLatchGate>();
            gate.Configure(hinge,collider);
        }
    }
    static void Main()
    {
        var f=new Fixture();
        Check(f.gate.IsLocked && !f.gate.IsUnlocked,"default locked after prefab builder Configure");
        Check(f.collider.enabled && f.renderer.enabled,"visible collider engaged by default");
        Check(!f.gate.TrySetOpeningDegrees(5f),"locked 5deg opening rejected");
        Check(!f.gate.TryRelock(),"cannot relock an already locked lid");
        Check(f.gate.TryUnlock(),"unlock request accepted only closed");
        Check(f.gate.IsTransitioning && !f.gate.IsUnlocked,"unlock starts ANIMATED retract, not teleport");
        Check(!f.gate.TryUnlock(),"duplicate unlock request blocked during retract");
        Check(!f.gate.TrySetOpeningDegrees(5),"lid cannot move while latch partly retracted");
        f.gate.Tick(float.NaN);
        Near(f.gate.ReleaseProgress,0f,"NaN delta not advanced");
        f.gate.Tick(0.10f);
        Check(f.gate.IsTransitioning && !f.gate.IsUnlocked,"after 100ms still retracting");
        Near(f.gate.ReleaseProgress,.4f,"100ms progress 40 percent at duration 250ms");
        Near(f.lockObj.transform.localPosition.z,.225f+.008f,"visible mesh physically moves 8mm during retract");
        Check(f.collider.enabled,"latch remains solid while retract not complete");
        Check(!f.gate.TrySetOpeningDegrees(10f),"0..110 hinge disabled until FULL retract");
        f.gate.Tick(.15f);
        Check(f.gate.IsUnlocked && !f.gate.IsTransitioning,"250ms transitions to unlocked");
        Check(!f.collider.enabled && f.gate.IsLockVisiblyReleased,"collider released only after visible retract");
        Near(f.lockObj.transform.localPosition.z,.245f,"visual Front_Lock fully travels 20mm root Z");
        Check(f.gate.TrySetOpeningDegrees(5f),"5deg permitted after full release");
        Check(!f.gate.TryRelock(),"cannot relock with lid at 5deg");
        Check(f.gate.TrySetOpeningDegrees(110f),"110deg upper endpoint permitted");
        Check(!f.gate.TrySetOpeningDegrees(111f),"111deg refused");
        Check(!f.gate.TrySetOpeningDegrees(-1f),"negative lid angle refused");
        Check(!f.gate.TrySetOpeningDegrees(float.PositiveInfinity),"infinite lid angle refused");
        Check(!f.gate.TrySetOpeningDegrees(float.NaN),"NaN lid angle refused");
        Check(!f.gate.TryRelock(),"cannot relock while 110deg open");
        Check(f.gate.TrySetOpeningDegrees(0f),"explicit close accepted");
        Check(f.gate.TryRelock(),"relock begins only when lid fully closed");
        Check(f.gate.IsTransitioning && !f.gate.IsLocked,"relock is animated, not immediate");
        Check(!f.gate.TrySetOpeningDegrees(1f),"cannot reopen mid relock");
        f.gate.Tick(.125f);
        Near(f.gate.ReleaseProgress,.5f,"relock midway progress");
        Check(!f.collider.enabled,"collider remains disabled until visual relock finished");
        f.gate.Tick(.125f);
        Check(f.gate.IsLocked && !f.gate.IsTransitioning,"relock completion");
        Check(f.collider.enabled,"collider returns ON only at end of relock");
        Near(f.lockObj.transform.localPosition.z,.225f,"visible lock returns exactly to rest");
        var g=new Fixture(true);
        Check(g.gate.TryUnlock(),"rotated FBX parent unlock request");
        g.gate.Tick(.25f);
        // Offset must be expressed in authored root +Z, converted through
        // imported 90deg Y parent: imported-local release follows -X.
        Near(g.lockObj.transform.localPosition.x,-.020f,"rotated FBX lock-parent translation converted, not local +Z");
        Near(g.lockObj.transform.localPosition.z,.225f,"rotated FBX lock retains original local Z");
        Check(g.gate.IsLockVisiblyReleased,"rotated parent reaches exact release pose");
        var h=new Fixture();
        Check(h.gate.TryUnlock(),"tamper fixture unlock accepted");
        h.gate.Tick(.25f);
        Check(h.gate.TrySetOpeningDegrees(20),"tamper fixture opens lid");
        h.renderer.enabled=false;
        Late(h.gate);
        Check(!h.gate.enabled && h.gate.IsLocked,"invisible lock fails closed and disables controller");
        Check(h.collider.enabled,"invisible lock fails to solid collider");
        Near(Quaternion.Angle(h.hinge.localRotation,Quaternion.identity),0f,"failsafe returns lid to closed");
        var p=new Fixture();
        Check(p.gate.TryUnlock(),"external angular tamper fixture begins retract");
        p.gate.Tick(.1f);
        p.hinge.localRotation=Quaternion.AngleAxis(30f,Vector3.right);
        Late(p.gate);
        Near(Quaternion.Angle(p.hinge.localRotation,Quaternion.identity),0f,"hinge kept closed during retract");
        Console.WriteLine("C01_W24_P1807_REAL_CSHARP_OFFLINE_LOGIC_PASS checks="+passed+
           " UNITY_EDITOR=NOT_RUN FBX_HASH_UNCHANGED");
    }
}
