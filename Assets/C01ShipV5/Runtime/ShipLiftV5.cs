using System;
using UnityEngine;

namespace C01.Ship.V5
{
    [DefaultExecutionOrder(-100)]
    public class ShipLiftV5 : MonoBehaviour
    {
        public string id;
        public Transform car;
        public ShipGateV5[] landings = new ShipGateV5[3];
        public float[] elevations = { -12.4f, 0, 6.4f };
        public int currentFloor = 1, targetFloor = 1;
        public CharacterController player;
        public float speed = 4;
        // World-space manifest bounds: x0, x1, z0, z1. Ground contact remains mandatory.
        public Vector4 footprint;
        bool travelling;
        bool initialized;
        public bool IsMoving => travelling;

        void Start()
        {
            if (!initialized) ResetToFloor(currentFloor);
        }

        void Bind()
        {
            for (int i = 0; i < landings.Length; i++)
                if (landings[i] != null)
                {
                    landings[i].interlockLift = this;
                    landings[i].landingFloor = i;
                }
        }

        bool Valid(int floor) => floor >= 0 && floor < elevations.Length && floor < landings.Length && landings[floor] != null;

        public bool CanOpenLanding(ShipGateV5 gate)
        {
            if (car == null || travelling || !Valid(currentFloor)) return false;
            return landings[currentFloor] == gate && Mathf.Abs(car.position.y - elevations[currentFloor]) <= .005f;
        }

        public void RequestFloor(int floor)
        {
            if (!Valid(floor) || car == null) return;
            Bind();
            initialized = true;
            targetFloor = floor;
            if (!travelling && floor == currentFloor && Mathf.Abs(car.position.y - elevations[floor]) < .005f)
            {
                for (int i = 0; i < landings.Length; i++)
                    if (landings[i] != null) landings[i].SetTarget(i == floor);
                return;
            }
            travelling = true;
            CloseLandings();
        }

        public void ResetToFloor(int floor)
        {
            if (!Valid(floor) || car == null) return;
            Bind();
            initialized = true;
            travelling = false;
            currentFloor = targetFloor = floor;
            // QA setup only resets the car. It never teleports a player, nearby or aboard.
            var position = car.position;
            position.y = elevations[floor];
            car.position = position;
            for (int i = 0; i < landings.Length; i++)
                if (landings[i] != null) landings[i].SetImmediate(0);
            Physics.SyncTransforms();
        }

        void CloseLandings()
        {
            foreach (var gate in landings) if (gate != null) gate.SetTarget(false);
        }

        void FixedUpdate()
        {
            if (!travelling || car == null) return;
            CloseLandings();
            foreach (var gate in landings) if (gate != null && !gate.IsClosed) return;
            bool rider = HasRider();
            var before = car.position;
            var after = before;
            after.y = Mathf.MoveTowards(before.y, elevations[targetFloor], Mathf.Max(.01f, speed) * Time.fixedDeltaTime);
            // Lift the capsule before raising the platform into its feet; lower the platform
            // first when descending. This avoids a second upward depenetration impulse.
            if (rider && after.y > before.y) player.Move(after - before);
            car.position = after;
            Physics.SyncTransforms();
            if (rider && after.y <= before.y) player.Move(after - before);
            if (Mathf.Abs(after.y - elevations[targetFloor]) > .0001f) return;
            currentFloor = targetFloor;
            travelling = false;
            if (landings[currentFloor] != null) landings[currentFloor].SetTarget(true);
        }

        bool HasRider()
        {
            if (player == null || !player.enabled || !player.gameObject.activeInHierarchy) return false;
            var bottom = player.transform.TransformPoint(player.center) - Vector3.up * (player.height * .5f);
            if (footprint.y > footprint.x && footprint.w > footprint.z &&
                (bottom.x < footprint.x || bottom.x > footprint.y || bottom.z < footprint.z || bottom.z > footprint.w)) return false;
            var hits = Physics.RaycastAll(bottom + Vector3.up * .15f, Vector3.down,
                .4f, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
            Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
            foreach (var hit in hits)
            {
                if (hit.collider.transform.IsChildOf(player.transform)) continue;
                return hit.collider.transform == car || hit.collider.transform.IsChildOf(car);
            }
            return false;
        }
    }
}
