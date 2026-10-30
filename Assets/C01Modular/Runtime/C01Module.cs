using System;
using UnityEngine;

namespace C01 {
    [Serializable] public class SocketData { public string name, kind; public float[] position, normal, contact; }
    [Serializable] public class PartData { public string role; public float[] lo, hi; }
    [Serializable] public class ChildData { public string module, socket; public float[] position; public float yaw; }
    [Serializable] public class ModuleData { public string id, family, topology; public float[] nominal; public PartData[] parts; public SocketData[] sockets; public ChildData[] children; }
    [Serializable] public class PlacementData { public string id, group, tag; public float x,y,z,yaw; }
    [Serializable] public class MaterialData { public string role; public float[] color; }
    [Serializable] public class KitData { public string schema; public float tile_m, wall_height_m, wall_thickness_m; public ModuleData[] modules; public PlacementData[] placements; public MaterialData[] materials; }

    public class C01Module : MonoBehaviour {
        public string moduleId, family, placementTag;
        public SocketData[] sockets;
    }
}
