using System;
using System.Collections.Generic;
using C01.Ship.V5;
using UnityEngine;

namespace C01.Ship.V6.Cargo
{
    // Must run immediately before ShipLiftV5 (-100): move supported bodies by the
    // exact step the V5 lift is about to take, before it moves the platform.
    [DefaultExecutionOrder(-101)]
    public sealed class CargoLiftController : MonoBehaviour
    {
        readonly HashSet<Rigidbody> movedBodies = new HashSet<Rigidbody>();
        [SerializeField, HideInInspector] ShipLiftV5 lift;
        [SerializeField, HideInInspector] Collider[] surfaces;
        [SerializeField, HideInInspector] bool configured;
        public bool allowMissingDeckZero;

        public ShipLiftV5 Lift => lift;
        public bool IsMoving => configured && lift != null && lift.IsMoving;
        public int CurrentFloor => configured && lift != null ? lift.currentFloor : -1;

        /// <summary>Call once during scene setup, before starting a trip. The
        /// platform root pivot Y is aligned with each world-space landing elevation.</summary>
        public void Configure(Transform platformRoot, Collider platformSurface,
            CharacterController player, ShipGateV5[] landingGates, int initialFloor, float speed)
        {
            Configure(platformRoot, new[] { platformSurface }, player, landingGates, initialFloor, speed);
        }

        /// <summary>Configure a platform made of multiple surface colliders.</summary>
        public void Configure(Transform platformRoot, Collider[] platformSurfaces,
            CharacterController player, ShipGateV5[] landingGates, int initialFloor, float speed)
        {
            if (configured) throw new InvalidOperationException("Cargo lift is already configured.");
            if (!isActiveAndEnabled) throw new InvalidOperationException("Enable the cargo lift before configuring it.");
            if (platformRoot == null || platformSurfaces == null || platformSurfaces.Length == 0 || player == null)
                throw new ArgumentNullException("Platform, surface, and player are required.");
            foreach (var platformSurface in platformSurfaces)
                if (platformSurface == null || (platformSurface.transform != platformRoot && !platformSurface.transform.IsChildOf(platformRoot)))
                    throw new ArgumentException("Each platform surface must be on the platform root or a child.");
            if (landingGates == null || landingGates.Length != 3 || initialFloor < 0 || initialFloor > 2 ||
                float.IsNaN(speed) || float.IsInfinity(speed) || speed <= 0)
                throw new ArgumentException("Provide exactly three gates, a floor from 0 to 2, and a positive finite speed.");
            for (int i = 0; i < 3; i++)
            {
                if (landingGates[i] == null || landingGates[i].interlockAirlock != null || landingGates[i].interlockLift != null)
                    throw new ArgumentException("Every landing needs an unbound, non-airlock V5 gate.");
                for (int j = 0; j < i; j++)
                    if (landingGates[i] == landingGates[j]) throw new ArgumentException("Landing gates must be distinct.");
            }
            if (GetComponent<ShipLiftV5>() != null)
                throw new InvalidOperationException("A V5 lift is already attached; this controller owns its lift.");

            surfaces = (Collider[])platformSurfaces.Clone();
            lift = gameObject.AddComponent<ShipLiftV5>();
            lift.car = platformRoot;
            lift.player = player;
            lift.landings = (ShipGateV5[])landingGates.Clone();
            lift.elevations = new[] { -12.4f, 0f, 6.4f };
            lift.speed = speed;
            lift.ResetToFloor(initialFloor);
            configured = true;
        }

        /// <summary>Call with floor 0, 1, or 2; returns false when unavailable or invalid.</summary>
        public bool RequestFloor(int floor)
        {
            if (!configured || !isActiveAndEnabled || lift == null || !lift.enabled || floor < 0 || floor > 2 ||
                floor >= lift.landings.Length || lift.landings[floor] == null)
                return false;
            lift.RequestFloor(floor);
            return true;
        }

        void FixedUpdate()
        {
            if (!configured || lift == null || !lift.enabled || !lift.IsMoving || lift.car == null || surfaces == null) return;
            // ShipLiftV5 will not move until every gate has fully closed.
            for (int i = 0; i < lift.landings.Length; i++)
            {
                var gate=lift.landings[i];
                if (gate == null) { if (i == 0 && allowMissingDeckZero) continue; lift.enabled = false; return; }
                if (!gate.IsClosed) return;
            }
            var y = lift.car.position.y;
            var next = Mathf.MoveTowards(y, lift.elevations[lift.targetFloor], Mathf.Max(.01f, lift.speed) * Time.fixedDeltaTime);
            float delta = next - y;
            if (Mathf.Abs(delta) < .000001f) return;
            CarrySupportedBodies(delta);
        }

        void CarrySupportedBodies(float delta)
        {
            movedBodies.Clear();
            foreach (var surface in surfaces)
            {
                if (surface == null || !surface.enabled || !surface.gameObject.activeInHierarchy) continue;
                var bounds = surface.bounds;
                // Sample a thin slab above each module, so nearby bodies are not carried.
                var center = new Vector3(bounds.center.x, bounds.max.y + .1f, bounds.center.z);
                var half = new Vector3(bounds.extents.x, .2f, bounds.extents.z);
                var contacts = Physics.OverlapBox(center, half, Quaternion.identity,
                    Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
                foreach (var contact in contacts)
                {
                    var body = contact.attachedRigidbody;
                    if (body == null || body.transform == lift.car || body.transform.IsChildOf(lift.car) ||
                        movedBodies.Contains(body) || !IsSupported(contact, body)) continue;
                    movedBodies.Add(body);
                    // Position preserves linear/angular velocity without parenting gameplay objects.
                    body.position += Vector3.up * delta;
                }
            }
        }
        bool IsSupported(Collider contact, Rigidbody body)
        {
            var b = contact.bounds;
            var origin = new Vector3(b.center.x, b.min.y + .08f, b.center.z);
            var hits = Physics.RaycastAll(origin, Vector3.down, .35f,
                Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
            Array.Sort(hits, (a, b2) => a.distance.CompareTo(b2.distance));
            foreach (var hit in hits)
            {
                if (hit.collider.attachedRigidbody == body) continue;
                foreach (var surface in surfaces) if (hit.collider == surface) return true;
                return false;
            }
            return false;
        }

        void OnDisable()
        {
            // An inactive cargo carrier must never leave its owned lift running alone.
            if (lift != null) lift.enabled = false;
        }

        void OnEnable()
        {
            if (configured && lift != null) lift.enabled = true;
        }
    }
}



