using System;
using UnityEngine;
namespace C01.Ship.V4 {
    [Serializable] public class DeckDataV4 {public int id;public float y;}
    [Serializable] public class MaterialDataV4 {public string role;public float[] color;}
    [Serializable] public class PartDataV4 {public string role;public float[] outline;public float y0,y1;}
    [Serializable] public class SocketDataV4 {public string name,kind;public float[] position,normal;}
    [Serializable] public class ModelDataV4 {public string id,family;public float[] nominal;public SocketDataV4[] sockets;public PartDataV4[] parts;}
    [Serializable] public class PlacementDataV4 {
        public string id,model,category,zone,parent,gate,buttonGate,buttonLift;
        public int deck,buttonFloor;public float x,y,z,yaw;public float[] travel;
    }
    [Serializable] public class ZoneDataV4 {public string id,label,kind,parent;public int deck;public float floor,height;public float[] bounds,waypoint;}
    [Serializable] public class GateDataV4 {public string id,airlock,lift;public int deck,floor;public float x,y,z,yaw,width,height;public string[] zones,leaves,buttons;}
    [Serializable] public class AirlockDataV4 {public string id;public string[] gates;}
    [Serializable] public class LiftDataV4 {public string id,car;public float x,z;public float[] bounds,elevations;public int startFloor;public int[] floors;public string[] landings;public WaypointV4[] waypoints;}
    [Serializable] public class WaypointV4 {public float[] position;}
    [Serializable] public class LinkDataV4 {public string a,b,kind,gate;}
    [Serializable] public class CoverageDataV4 {public string id,normal;public int deck;public float plane;public float[] poly;}
    [Serializable] public class ShipDataV4 {
        public string version;public float unit;public float[] body;public DeckDataV4[] decks;public MaterialDataV4[] materials;public ModelDataV4[] models;public PlacementDataV4[] placements;public ZoneDataV4[] zones;public GateDataV4[] gates;public AirlockDataV4[] airlocks;public LiftDataV4[] lifts;public LinkDataV4[] links;public CoverageDataV4[] coverage;
    }
}
