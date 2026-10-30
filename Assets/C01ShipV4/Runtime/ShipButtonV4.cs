using UnityEngine;

namespace C01.Ship.V4
{
    public class ShipButtonV4 : MonoBehaviour
    {
        public string gateId, liftId;
        public int floor;
        public ShipGateV4 gate;
        public ShipLiftV4 lift;
        public ShipAirlockV4 airlock;

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
