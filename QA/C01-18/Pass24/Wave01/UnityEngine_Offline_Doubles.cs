// Offline compilation-only UnityEngine API doubles for C01-18 W24 QA.
// These are NOT Unity, do not ship under Assets, and cannot prove PhysX/URP.
using System;
using System.Collections.Generic;

namespace UnityEngine
{
    [AttributeUsage(AttributeTargets.Class)] public sealed class DisallowMultipleComponent : Attribute { }
    [AttributeUsage(AttributeTargets.Field)] public sealed class SerializeField : Attribute { }
    [AttributeUsage(AttributeTargets.Field)] public sealed class RangeAttribute : Attribute
    { public RangeAttribute(float min, float max) { } }
    [AttributeUsage(AttributeTargets.Field)] public sealed class MinAttribute : Attribute
    { public MinAttribute(float min) { } }

    public struct Vector3
    {
        public float x,y,z;
        public Vector3(float ax,float ay,float az) { x=ax;y=ay;z=az; }
        public static Vector3 zero { get {return new Vector3();} }
        public static Vector3 left {get{return new Vector3(-1,0,0);}}
        public static Vector3 right {get{return new Vector3(1,0,0);}}
        public static Vector3 up {get{return new Vector3(0,1,0);}}
        public static Vector3 forward {get{return new Vector3(0,0,1);}}
        public float sqrMagnitude {get{return x*x+y*y+z*z;}}
        public float magnitude {get{return (float)Math.Sqrt(sqrMagnitude);}}
        public Vector3 normalized {get{return magnitude>1e-8f?this*(1/magnitude):zero;}}
        public static Vector3 operator+(Vector3 a,Vector3 b){return new Vector3(a.x+b.x,a.y+b.y,a.z+b.z);}
        public static Vector3 operator-(Vector3 a,Vector3 b){return new Vector3(a.x-b.x,a.y-b.y,a.z-b.z);}
        public static Vector3 operator*(Vector3 a,float v){return new Vector3(a.x*v,a.y*v,a.z*v);}
        public static Vector3 operator*(float v,Vector3 a){return a*v;}
        public static float Dot(Vector3 a,Vector3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
    }
    public struct Quaternion
    {
        public float x,y,z,w;
        public Quaternion(float a,float b,float c,float d){x=a;y=b;z=c;w=d;}
        public static Quaternion identity {get{return new Quaternion(0,0,0,1);}}
        public static Quaternion AngleAxis(float degrees,Vector3 axis)
        {
            axis=axis.normalized;double half=degrees*Math.PI/360.0;
            float sin=(float)Math.Sin(half);
            return new Quaternion(axis.x*sin,axis.y*sin,axis.z*sin,(float)Math.Cos(half));
        }
        public static Quaternion operator*(Quaternion a,Quaternion b)
        {
            return new Quaternion(a.w*b.x+a.x*b.w+a.y*b.z-a.z*b.y,
                a.w*b.y-a.x*b.z+a.y*b.w+a.z*b.x,
                a.w*b.z+a.x*b.y-a.y*b.x+a.z*b.w,
                a.w*b.w-a.x*b.x-a.y*b.y-a.z*b.z);
        }
        public Quaternion Inverse(){return new Quaternion(-x,-y,-z,w);}
        public Vector3 Rotate(Vector3 v)
        {
            Quaternion p=new Quaternion(v.x,v.y,v.z,0);
            Quaternion r=this*p*Inverse();
            return new Vector3(r.x,r.y,r.z);
        }
        public static float Angle(Quaternion a,Quaternion b)
        {
            float d=Math.Abs(a.x*b.x+a.y*b.y+a.z*b.z+a.w*b.w);
            if(d>1) d=1;
            return 2f*(float)(Math.Acos(d)*180.0/Math.PI);
        }
    }
    public class Component
    {
        public GameObject gameObject;
        public string name {get {return gameObject.name;}}
        public Transform transform {get{return gameObject.transform;}}
        public T GetComponent<T>() where T:Component {return gameObject.GetComponent<T>();}
        public T[] GetComponentsInChildren<T>(bool includeInactive) where T:Component
        {return gameObject.GetComponentsInChildren<T>(includeInactive);}
    }
    public class MonoBehaviour:Component {public bool enabled=true;}
    public class Collider:Component {public bool enabled=true;public bool isTrigger=false;}
    public sealed class BoxCollider:Collider { }
    public sealed class MeshRenderer:Component {public bool enabled=true;}
    public sealed class MeshFilter:Component { }
    public class Transform:Component
    {
        private Transform _parent;
        internal readonly List<Transform> children=new List<Transform>();
        public Transform parent
        {
            get{return _parent;}
            set{if(_parent!=null)_parent.children.Remove(this);_parent=value;if(value!=null)value.children.Add(this);}
        }
        public Quaternion localRotation=Quaternion.identity;
        public Vector3 localPosition;
        public Quaternion rotation{get{return parent==null?localRotation:parent.rotation*localRotation;}}
        public Vector3 position
        {
            get {return parent==null?localPosition:parent.position+parent.TransformVector(localPosition);}
            set {localPosition=parent==null?value:parent.InverseTransformVector(value-parent.position);}
        }
        public Vector3 forward {get{return rotation.Rotate(Vector3.forward);}}
        public Vector3 TransformVector(Vector3 v){return rotation.Rotate(v);}
        public Vector3 InverseTransformVector(Vector3 v){return rotation.Inverse().Rotate(v);}
        public bool IsChildOf(Transform ancestor)
        {
            for(Transform t=parent;t!=null;t=t.parent) if(t==ancestor)return true;
            return false;
        }
        public Transform Find(string childName)
        {
            foreach(Transform t in children)if(t.name==childName)return t;
            return null;
        }
    }
    public sealed class GameObject
    {
        public string name;
        public Transform transform;
        private readonly List<Component> components = new List<Component>();
        public GameObject(string n)
        {
            name=n;transform=new Transform {gameObject=this};components.Add(transform);
        }
        public T AddComponent<T>() where T:Component,new()
        {
            var o=new T{gameObject=this};components.Add(o);return o;
        }
        public T GetComponent<T>() where T:Component
        {
            foreach(Component c in components)if(c is T)return (T)c;
            return null;
        }
        public T[] GetComponentsInChildren<T>(bool includeInactive) where T:Component
        {
            var list=new List<T>();Walk(transform,list);return list.ToArray();
        }
        private static void Walk<T>(Transform t,List<T> a) where T:Component
        {
            foreach(Component c in t.gameObject.components)if(c is T)a.Add((T)c);
            foreach(Transform kid in t.children)Walk(kid,a);
        }
    }
    public static class Debug
    {
        public static readonly List<string> Errors=new List<string>();
        public static readonly List<string> Warnings=new List<string>();
        public static void LogError(object msg,Component obj){Errors.Add(msg.ToString());}
        public static void LogWarning(object msg,Component obj){Warnings.Add(msg.ToString());}
    }
    public static class Mathf
    {
        public const float PI=(float)Math.PI;
        public static float Abs(float v){return Math.Abs(v);}
        public static float Max(float a,float b){return Math.Max(a,b);}
        public static float MoveTowards(float current,float target,float step)
        {
            if(Math.Abs(target-current)<=step)return target;
            return current+Math.Sign(target-current)*step;
        }
    }
    public static class Time {public static float deltaTime=0.02f;}
}
