using System;
using UnityEngine;
namespace C01.Ship {
    [Serializable] public class ShipZoneData {public string id,label,kind;public float[] bounds,waypoint,color;}
    [Serializable] public class ShipDoorData {public string id,axis,airlock;public string[] zones;public float x,z,yaw;}
    [Serializable] public class ShipPartData {public string role;public float[] outline;public float y0,y1;}
    [Serializable] public class ShipModuleData {public string id;public ShipPartData[] parts;}
    [Serializable] public class ShipPlacementData {public string id,module,category,zone;public float x,y,z,yaw;}
    [Serializable] public class ShipMaterialData {public string role;public float[] color;}
    [Serializable] public class ShipAirlockData {public string id;public string[] doors;}
    [Serializable] public class ShipData {public string version,reference;public float corridor_width,branch_length;public float[] body,bridge_outline;public ShipZoneData[] zones;public ShipDoorData[] doors;public ShipModuleData[] modules;public ShipPlacementData[] placements;public ShipMaterialData[] materials;public ShipAirlockData[] airlocks;}
}
