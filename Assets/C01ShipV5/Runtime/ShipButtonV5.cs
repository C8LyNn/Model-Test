using UnityEngine;

namespace C01.Ship.V5
{
    public class ShipButtonV5 : MonoBehaviour
    {
        public string gateId, liftId;
        public int floor;
        public ShipGateV5 gate;
        public ShipLiftV5 lift;
        public ShipAirlockV5 airlock;

        public void Press()
        {
            if (lift != null) { lift.RequestFloor(floor); return; }
            if (gate == null) return;
            var lockController = airlock != null ? airlock : gate.interlockAirlock;
            if (lockController != null)
                lockController.Request(gate, !lockController.IsRequestedOpen(gate));
            else gate.SetOpen(gate.target < .5f);
        }
    }
}
