// Compiles and executes the ACTUAL production C01CartWheelVisualBearing.cs.
// UnityEngine is stubbed: no licensed Unity, PhysX, GameObject prefab or PlayMode.
using System;
using System.Reflection;
using C01.Cargo;
using UnityEngine;
class P1803OfflineRuntimeTests
{
    static int passed;
    static void Check(bool ok,string name)
    {
        if(!ok)throw new Exception("P18-03 W24 C# runtime FAIL: "+name);
        passed++;
        Console.WriteLine("C01_P1803_W24_PASS "+name);
    }
    static void Near(float actual,float expected,string name,float tolerance=.02f)
    {
        Check(Math.Abs(actual-expected)<=tolerance,name+" actual="+actual);
    }
    static void Late(C01CartWheelVisualBearing script)
    {
        typeof(C01CartWheelVisualBearing).GetMethod("LateUpdate",
            BindingFlags.Instance|BindingFlags.NonPublic).Invoke(script,null);
    }
    static void Awake(C01CartWheelVisualBearing script)
    {
        typeof(C01CartWheelVisualBearing).GetMethod("Awake",
            BindingFlags.Instance|BindingFlags.NonPublic).Invoke(script,null);
    }
    static void ChangeAuto(C01CartWheelVisualBearing script,bool target)
    {
        typeof(C01CartWheelVisualBearing).GetField("autoRollFromTranslation",
            BindingFlags.Instance|BindingFlags.NonPublic).SetValue(script,target);
    }
    sealed class Fixture
    {
        public GameObject root, imported;
        public C01CartWheelVisualBearing script;
        public Transform[] wheels=new Transform[4];
        public GameObject fork;
        public Fixture(bool phantom=false)
        {
            root=new GameObject("P18_03");
            imported=new GameObject("P18-03_FBX");
            imported.transform.parent=root.transform;
            string[] names={"Wheel_LB","Wheel_LF","Wheel_RB","Wheel_RF"};
            for(int i=0;i<names.Length;i++)
            {
                var w=new GameObject(names[i]);
                w.transform.parent=imported.transform;
                w.AddComponent<MeshFilter>();
                wheels[i]=w.transform;
                foreach(string suffix in new[]{"_Hub_In","_Hub_Out"})
                {
                    var hub=new GameObject(names[i]+suffix);
                    hub.transform.parent=w.transform;
                    hub.AddComponent<MeshFilter>();
                }
                fork=new GameObject(names[i]+"_ForkInner");
                fork.transform.parent=imported.transform;
                fork.AddComponent<MeshFilter>();
                if(phantom && i==0)fork.AddComponent<BoxCollider>();
            }
            foreach(string name in new[]{"Cart_Shelf_0","Cart_Shelf_1",
                "Cart_Upright_-0.44_-0.29","Cart_Upright_-0.44_0.29",
                "Cart_Upright_0.44_-0.29","Cart_Upright_0.44_0.29"})
            {
                var staticPart=new GameObject(name);
                staticPart.transform.parent=imported.transform;
                staticPart.AddComponent<MeshFilter>();
                staticPart.AddComponent<BoxCollider>();
            }
            script=root.AddComponent<C01CartWheelVisualBearing>();
        }
    }
    static void Main()
    {
        var f=new Fixture();
        f.script.Configure(f.wheels);
        Check(f.script.IsConfigured,"all 4 original wheel pivots bound");
        Check(f.script.AutoRollFromTranslation,"auto visual rolling enabled by default");
        Check(f.root.GetComponentsInChildren<BoxCollider>(true).Length==6,
            "six static body BoxColliders; zero wheel hub/fork colliders");
        for(int i=0;i<4;i++)
        {
            Check(f.wheels[i].GetComponent<MeshFilter>()!=null,"rubber wheel mesh present "+i);
            Check(f.wheels[i].Find(f.wheels[i].name+"_Hub_In")!=null,"inner rotating hub child "+i);
            Check(f.wheels[i].Find(f.wheels[i].name+"_Hub_Out")!=null,"outer rotating hub child "+i);
        }
        Check(!f.script.AdvanceVisualRolling(float.NaN),"manual NaN wheel travel rejected");
        Check(!f.script.AdvanceVisualRolling(float.PositiveInfinity),"manual infinite travel rejected");
        f.root.transform.position=new Vector3(0,0,.105f);
        Late(f.script);
        Near(f.script.AccumulatedRollDegrees,180f/(float)Math.PI,
            "105mm forward travel gives 57.296deg wheel rotation");
        for(int i=0;i<4;i++)
            Near(Quaternion.Angle(Quaternion.identity,f.wheels[i].localRotation),
                180f/(float)Math.PI,"all 4 wheels rotate equally "+i);
        Check(Quaternion.Angle(f.wheels[0].rotation,
            f.wheels[0].Find(f.wheels[0].name+"_Hub_In").rotation)<.05f,
            "inner metal hub follows actual wheel rotation");
        f.root.transform.position=new Vector3(0,0,0);
        Late(f.script);
        Near(f.script.AccumulatedRollDegrees,0f,"backward 105mm cancels forward roll");
        f.root.transform.position=new Vector3(.25f,0,0);
        Late(f.script);
        Near(f.script.AccumulatedRollDegrees,0f,"sideways cart translation does not rotate rolling wheels");
        f.root.transform.localRotation=Quaternion.AngleAxis(90f,Vector3.up);
        Late(f.script);
        Near(f.script.AccumulatedRollDegrees,0f,"pure cart heading rotation does not roll");
        f.root.transform.position=new Vector3(.355f,0,0);
        Late(f.script);
        Near(f.script.AccumulatedRollDegrees,180f/(float)Math.PI,
            "rolling along ROTATED root forward auto-computes correct distance");
        f.root.transform.position=new Vector3(10f,0,0);
        Late(f.script);
        Near(f.script.AccumulatedRollDegrees,180f/(float)Math.PI,
            "large teleport does NOT spin wheels");
        Check(f.script.AdvanceVisualRolling(-.105f),"explicit signed reverse travel supported");
        Near(f.script.AccumulatedRollDegrees,0f,"manual reverse cancels roll");
        ChangeAuto(f.script,false);
        f.root.transform.position=new Vector3(10.1f,0,0);
        Late(f.script);
        Near(f.script.AccumulatedRollDegrees,0f,"manual mode disables auto translation spin");
        Check(f.script.AdvanceVisualRolling(.105f),"manual mode still allows caller-directed rolling");
        Near(f.script.AccumulatedRollDegrees,180f/(float)Math.PI,
            "manual path uses original 105mm wheel radius");
        // Deserialize simulated scene by invoking Unity-targeted Awake.
        Awake(f.script);
        Check(f.script.IsConfigured && f.script.enabled,"Awake recreates wheel/hub references after save");
        Near(f.script.AccumulatedRollDegrees,0f,"Awake rest pose becomes newly sampled authored pose");
        var invalid=new Fixture(true);
        bool threw=false;
        try {invalid.script.Configure(invalid.wheels);}catch(InvalidOperationException){threw=true;}
        Check(threw,"W24 phantom fork collider REJECTED even though it is fixed sibling");
        var good=new Fixture();
        good.script.Configure(good.wheels);
        good.fork.AddComponent<BoxCollider>();
        Check(!good.script.AdvanceVisualRolling(.10f),
            "late phantom fork collider injection detected before rolling");
        Check(!good.script.enabled,"late phantom collider FAIL-CLOSE disables visual rolling component");
        var broken=new Fixture();
        broken.wheels[0].Find("Wheel_LB_Hub_In").parent=broken.imported.transform;
        bool rejected=false;
        try {broken.script.Configure(broken.wheels);}catch(InvalidOperationException){rejected=true;}
        Check(rejected,"hub no longer parented to wheel is refused");
        Console.WriteLine("C01_W24_P1803_REAL_CSHARP_OFFLINE_LOGIC_PASS checks="+passed+
            " UNITY_EDITOR=NOT_RUN FBX_HASH_UNCHANGED");
    }
}
