using UnityEngine;

namespace C01.Ship.V4
{
    public class ShipAirlockV4 : MonoBehaviour
    {
        public ShipGateV4 gateA, gateB;
        ShipGateV4 wanted;

        void Start() { Bind(); }

        void Bind()
        {
            if (gateA != null) gateA.interlockAirlock = this;
            if (gateB != null) gateB.interlockAirlock = this;
        }

        public bool IsRequestedOpen(ShipGateV4 gate) => wanted == gate || (gate != null && gate.target > .5f);

        public bool CanOpenImmediately(ShipGateV4 gate)
        {
            var other = Other(gate);
            return other != null && other.IsClosed && other.target <= .001f;
        }

        public void Request(ShipGateV4 gate, bool open)
        {
            Bind();
            var other = Other(gate);
            if (gate == null || other == null) return;
            if (!open)
            {
                if (wanted == gate) wanted = null;
                gate.SetTarget(false);
                return;
            }
            wanted = gate;
            other.SetTarget(false);
            gate.SetTarget(other.IsClosed);
        }

        ShipGateV4 Other(ShipGateV4 gate) => gate == gateA ? gateB : gate == gateB ? gateA : null;

        void FixedUpdate()
        {
            Bind();
            if (wanted == null) return;
            var other = Other(wanted);
            if (other == null) { wanted = null; return; }
            other.SetTarget(false);
            wanted.SetTarget(other.IsClosed);
        }
    }
}
