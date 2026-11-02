using System;
using UnityEngine;
namespace C01.Ship.V5 {
    [Serializable] public class DeckDataV5 {public int id;public float y;}
    [Serializable] public class MaterialDataV5 {public string role;public float[] color;}
    [Serializable] public class PartDataV5 {public string role;public float[] outline;public float y0,y1;}
    [Serializable] public class SocketDataV5 {public string name,kind;public float[] position,normal;}
    [Serializable] public class ModelDataV5 {public string id,family;public float[] nominal;public SocketDataV5[] sockets;public PartDataV5[] parts;}
    [Serializable] public class PlacementDataV5 {
        public string id,model,category,zone,parent,gate,buttonGate,buttonLift;
        public int deck,buttonFloor;public float x,y,z,yaw;public float[] travel;
    }
    [Serializable] public class ZoneDataV5 {public string id,label,kind,parent;public int deck;public float floor,height;public float[] bounds,waypoint;}
    [Serializable] public class GateDataV5 {public string id,airlock,lift;public int deck,floor;public float x,y,z,yaw,width,height;public string[] zones,leaves,buttons;}
    [Serializable] public class AirlockDataV5 {public string id;public string[] gates;}
    [Serializable] public class LiftDataV5 {public string id,car;public float x,z;public float[] bounds,elevations;public int startFloor;public int[] floors;public string[] landings;public WaypointV5[] waypoints;}
    [Serializable] public class WaypointV5 {public float[] position;}
    [Serializable] public class LinkDataV5 {public string a,b,kind,gate;}
    [Serializable] public class CoverageDataV5 {public string id,normal;public int deck;public float plane;public float[] poly;}
    [Serializable] public class ShipDataV5 {
        public string version;public float unit;public float[] body;public DeckDataV5[] decks;public MaterialDataV5[] materials;public ModelDataV5[] models;public PlacementDataV5[] placements;public ZoneDataV5[] zones;public GateDataV5[] gates;public AirlockDataV5[] airlocks;public LiftDataV5[] lifts;public LinkDataV5[] links;public CoverageDataV5[] coverage;
    }
}
