// W25: Compile/execute ACTUAL production C01EquipmentCaseLatchGate.cs using
// offline UnityEngine doubles. This NEVER constitutes Unity PlayMode or PhysX.
using System;
using System.Reflection;
using C01.Cargo;
using UnityEngine;

class P1805W25OfflineProductionTests
{
    static int passed;
    static void OK(bool value, string name)
    {
        if (!value) throw new Exception("C01_18_P1805_W25_TEST_FAIL " + name);
        passed++;
        Console.WriteLine("C01_P1805_W25_OFFLINE_PASS " + name);
    }
    static void Close(float actual, float expected, string name, float eps=.00003f)
    {
        OK(Math.Abs(actual - expected) <= eps,
            name + " actual=" + actual + " expected=" + expected);
    }
    static void Late(C01EquipmentCaseLatchGate gate)
    {
        typeof(C01EquipmentCaseLatchGate)
            .GetMethod("LateUpdate", BindingFlags.NonPublic | BindingFlags.Instance)
            .Invoke(gate, null);
    }

    sealed class Case
    {
        public GameObject root, fbx, lid, bottom;
        public Transform hinge, latchL, latchR;
        public Transform[] handle = new Transform[3];
        public BoxCollider lidCollider;
        public C01EquipmentCaseLatchGate gate;
        public Case(bool negativeXImported=true)
        {
            root = new GameObject("P18_05");
            fbx = new GameObject("P18-05_SignedFBX");
            fbx.transform.parent = root.transform;
            if (negativeXImported)
                fbx.transform.localRotation = Quaternion.AngleAxis(-90f, Vector3.right);
            var e = new GameObject("Lid_HingePivot");
            e.transform.parent = fbx.transform;
            hinge = e.transform;
            hinge.localPosition = new Vector3(0,-.2f,.2f);

            lid = new GameObject("Case_Lid");
            lid.transform.parent = hinge;
            lid.AddComponent<MeshFilter>();
            lid.AddComponent<MeshRenderer>();
            lidCollider = lid.AddComponent<BoxCollider>();
            var accent = new GameObject("Lid_Accent");
            accent.transform.parent = hinge;
            accent.AddComponent<MeshFilter>();
            accent.AddComponent<MeshRenderer>();

            bottom = new GameObject("Case_Bottom");
            bottom.transform.parent = fbx.transform;
            bottom.AddComponent<MeshFilter>();
            bottom.AddComponent<MeshRenderer>();
            bottom.AddComponent<BoxCollider>();
            var left = new GameObject("Front_Latch_L");
            left.transform.parent = fbx.transform;
            left.transform.localPosition = new Vector3(-.23f,-.208f,.19f);
            left.AddComponent<MeshFilter>();
            left.AddComponent<MeshRenderer>();
            var right = new GameObject("Front_Latch_R");
            right.transform.parent = fbx.transform;
            right.transform.localPosition = new Vector3(.23f,-.208f,.19f);
            right.AddComponent<MeshFilter>();
            right.AddComponent<MeshRenderer>();
            latchL = left.transform;
            latchR = right.transform;

            string[] names = { "Carry_Handle_Rail", "Carry_Handle_Stem_L", "Carry_Handle_Stem_R" };
            for (int i = 0; i < 3; i++)
            {
                GameObject p = new GameObject(names[i]);
                p.transform.parent = hinge;
                p.AddComponent<MeshFilter>();
                p.AddComponent<MeshRenderer>();
                handle[i] = p.transform;
            }
            gate = root.AddComponent<C01EquipmentCaseLatchGate>();
            gate.Configure(hinge, latchL, latchR, lidCollider, handle);
        }
    }
    static void Main()
    {
        var f = new Case();
        OK(f.gate.IsLocked && !f.gate.IsUnlocked, "original prefab starts engaged LOCKED");
        OK(f.root.GetComponentsInChildren<BoxCollider>(true).Length == 2,
            "two original bottom/lid solid colliders only");
        OK(f.handle[0].parent == f.hinge && f.handle[1].parent == f.hinge &&
            f.handle[2].parent == f.hinge, "three original handle meshes follow true lid pivot");
        OK(!f.gate.TrySetOpeningDegrees(5), "locked lid cannot open even 5deg");
        OK(!f.gate.TryRelock(), "cannot relock closed original latch");
        OK(f.gate.TryUnlock(), "unlock begins real visual release phase");
        OK(f.gate.IsTransitioning && !f.gate.IsUnlocked, "unlock is staged, not instant 8mm teleport");
        OK(!f.gate.TryUnlock(), "cannot double-unlock");
        OK(!f.gate.TrySetOpeningDegrees(5), "hinge cannot move while visible latches retract");
        f.gate.Tick(float.NaN);
        Close(f.gate.TransitionProgress,0,"NaN timespan does not advance latch");
        f.gate.Tick(.10f);
        Close(f.gate.TransitionProgress,.5f,"0.1s of 0.2s latch release is 50 percent");
        Close(f.latchL.localPosition.y,-.208f-.004f,
            "original real FBX -90X translates root +Z to latch-parent LOCAL -Y half 4mm");
        Close(f.latchR.localPosition.y,-.208f-.004f,"both original latches slide identically");
        Close(f.latchL.localPosition.z,.19f,"latch does not incorrectly travel local +Z");
        OK(f.gate.IsTransitioning && !f.gate.IsVisibleLatchReleased,
            "half-retracted latch still mechanically engaged");
        OK(!f.gate.TrySetOpeningDegrees(1),"lid remains closed at half latch release");
        f.gate.Tick(.1f);
        Close(f.latchL.localPosition.y,-.216f,"8mm FRONT latch fully disengaged");
        Close(f.latchR.localPosition.y,-.216f,"both 8mm FRONT latches fully disengaged");
        OK(f.gate.IsVisibleLatchReleased && !f.gate.IsUnlocked,
            "visible release complete but lid still must lift 2mm");
        OK(!f.gate.TrySetOpeningDegrees(5),"lid cannot rotate before hinge pre-lift");
        f.gate.Tick(.075f);
        Close(f.hinge.localPosition.z,.2f+.001f,
            "source-root Unity +Y lifts through actual -90deg X import parent LOCAL +Z");
        OK(f.gate.IsTransitioning,"1mm lift midway remains gated");
        f.gate.Tick(.075f);
        Close(f.hinge.localPosition.z,.202f,
            "2mm true root UP lid clearance fully attained");
        OK(f.gate.IsUnlocked && !f.gate.IsTransitioning,
            "ready to open only AFTER both physical transformations");
        OK(f.gate.IsVisibleLatchReleased,"visible original latch renderer still visible and retracted");
        OK(f.gate.TrySetOpeningDegrees(5),"true signed local -X angle 5deg allowed");
        Close(Quaternion.Angle(f.hinge.localRotation, Quaternion.identity),5f,
            "local -X hinge signed 5deg not positive opposite path",.1f);
        OK(!f.gate.TryRelock(),"cannot relock while 5deg open");
        OK(f.gate.TrySetOpeningDegrees(110),"original 110deg limit allowed");
        OK(!f.gate.TrySetOpeningDegrees(110.01f),"beyond 110deg refused");
        OK(!f.gate.TrySetOpeningDegrees(-5f),"wrong-signed opening refused");
        OK(!f.gate.TrySetOpeningDegrees(float.NaN),"NaN lid angle refused");
        OK(!f.gate.TrySetOpeningDegrees(float.PositiveInfinity),"Infinity angle refused");
        OK(!f.gate.TryRelock(),"cannot reengage while lid 110deg open");
        OK(f.gate.TrySetOpeningDegrees(0),"only after real zero-angle can we relock");
        OK(f.gate.TryRelock(),"closed lid begins staged lowering/relock");
        OK(f.gate.IsTransitioning && !f.gate.IsLocked,"relock cannot teleport");
        OK(!f.gate.TrySetOpeningDegrees(1),"lid cannot reopen during lowering");
        f.gate.Tick(.075f);
        Close(f.hinge.localPosition.z,.201f,"lower lid halfway 1mm");
        OK(f.gate.IsTransitioning,"lower stage continues");
        f.gate.Tick(.075f);
        Close(f.hinge.localPosition.z,.2f,"hinge returns original signed FBX pivot height");
        OK(f.gate.IsTransitioning,"latches must re-engage before LOCKED");
        f.gate.Tick(.1f);
        Close(f.latchL.localPosition.y,-.212f,"half relock 4mm re-engagement");
        OK(!f.gate.IsLocked && !f.gate.IsUnlocked,"still engaged in relock transition");
        f.gate.Tick(.1f);
        OK(f.gate.IsLocked && !f.gate.IsTransitioning,"final locked state only after full latch return");
        Close(f.latchL.localPosition.y,-.208f,"original left latch CLOSED rest pose restored");
        Close(f.latchR.localPosition.y,-.208f,"original right latch CLOSED rest pose restored");
        Close(f.hinge.localPosition.z,.2f,"original hinge full rest position restored");
        OK(f.lidCollider.enabled,"original lid collider remains physically present");
        var alt = new Case(false);
        OK(alt.gate.TryUnlock(),"identity importer root supported");
        alt.gate.Tick(.2f);
        Close(alt.latchL.localPosition.z,.19f+.008f,
            "identity importer release goes local +Z, no hard-coded FBX -Y");
        alt.gate.Tick(.15f);
        Close(alt.hinge.localPosition.y,-.198f,
            "identity importer hinge root +Y matches parent local +Y");
        OK(alt.gate.IsUnlocked,"identity imported case ready to open");
        var bad = new Case();
        OK(bad.gate.TryUnlock(),"external hierarchy tamper fixture begins");
        bad.handle[0].parent = bad.fbx.transform;
        Late(bad.gate);
        OK(!bad.gate.enabled && bad.gate.IsLocked,
            "original handle parent external tamper disables gate FAIL-CLOSED");
        Close(bad.latchL.localPosition.y,-.208f,
            "tamper fails to physical closed latch pose");
        var hidden = new Case();
        OK(hidden.gate.TryUnlock(),"hidden latch fixture begins");
        hidden.latchL.GetComponent<MeshRenderer>().enabled = false;
        Late(hidden.gate);
        OK(!hidden.gate.enabled && hidden.gate.IsLocked,
            "latch renderer hidden externally forces safe closed state");
        var invalid = new Case();
        invalid.handle[1].parent = invalid.fbx.transform;
        bool refused = false;
        try { invalid.gate.Configure(invalid.hinge,invalid.latchL,invalid.latchR,
            invalid.lidCollider,invalid.handle); }
        catch (InvalidOperationException) { refused=true; }
        OK(refused,"builder would reject signed FBX handle that fails to follow lid");
        Console.WriteLine("C01_W25_P1805_ACTUAL_PRODUCTION_CSHARP_OFFLINE_PASS checks="+passed+
            " REAL_UNITY_NOT_RUN ORIGINAL_SIGNED_FBX_IMMUTABLE");
    }
}
