using System;
using UnityEngine;

namespace C01.Cargo
{
    /// <summary>
    /// P18-03 signed FBX: 8 hub render meshes interpenetrate the 8 stationary
    /// fork seats in all 576 sampled configurations (C01-02 independent W22).
    /// Those metal surfaces and all wheels are VISUAL ONLY. They must never
    /// receive mutually solid physics colliders or WheelCollider components.
    /// Exactly 6 shelf/upright BoxColliders describe the cart body.
    ///
    /// W24 visual rolling follows actual kinematic root translation; no hidden
    /// Rigidbody, invented wheel-ground collisions or unsupported PhysX claims.
    /// Real licensed Unity 6 Editor/PlayMode remains NOT_RUN.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class C01CartWheelVisualBearing : MonoBehaviour
    {
        [SerializeField] private Transform[] wheels = new Transform[4];
        [SerializeField, Min(0.01f)] private float radiusMeters = 0.105f;
        [SerializeField] private bool autoRollFromTranslation = true;
        // Treat large single-frame relocations as teleports, not wheel travel.
        [SerializeField, Min(0.1f)] private float maximumMeasuredStepMeters = 2f;

        private Quaternion[] restLocalRotations;
        private float accumulatedRollDegrees;
        private Vector3 lastWorldPosition;
        private bool worldPositionInitialized;

        public bool IsConfigured => restLocalRotations != null && restLocalRotations.Length == 4;
        public bool AutoRollFromTranslation => autoRollFromTranslation;
        public float AccumulatedRollDegrees => accumulatedRollDegrees;

        public void Configure(Transform[] nativeWheels)
        {
            if (nativeWheels == null || nativeWheels.Length != 4)
                throw new ArgumentException("P18-03 needs exactly 4 native FBX wheels");
            wheels = (Transform[])nativeWheels.Clone();
            restLocalRotations = new Quaternion[4];
            string[] names = { "Wheel_LB", "Wheel_LF", "Wheel_RB", "Wheel_RF" };
            for (int i = 0; i < wheels.Length; i++)
            {
                Transform wheel = wheels[i];
                if (wheel == null || wheel.name != names[i] ||
                    wheel.GetComponent<MeshFilter>() == null)
                    throw new InvalidOperationException("P18-03 wheel hierarchy missing " + names[i]);
                // The original genuine BLEND/FBX has both moving metal hubs
                // parented to each rubber wheel. Never spin the fixed forks.
                foreach (string suffix in new[] { "_Hub_In", "_Hub_Out" })
                {
                    Transform hub = wheel.Find(names[i] + suffix);
                    if (hub == null || hub.parent != wheel ||
                        hub.GetComponent<MeshFilter>() == null)
                        throw new InvalidOperationException("P18-03 lost moving hub " + names[i] + suffix);
                }
                restLocalRotations[i] = wheel.localRotation;
            }
            VerifyNoWheelPhysics();
            accumulatedRollDegrees = 0f;
            lastWorldPosition = transform.position;
            worldPositionInitialized = true;
        }

        private void Awake()
        {
            try { Configure(wheels); } // Restore caches after prefab deserialization.
            catch (Exception e)
            {
                Debug.LogError("P18-03 visual bearing FAIL-CLOSED: " + e.Message, this);
                enabled = false;
            }
        }

        private void OnEnable()
        {
            lastWorldPosition = transform.position;
            worldPositionInitialized = true;
        }

        private void VerifyNoWheelPhysics()
        {
            foreach (Collider c in GetComponentsInChildren<Collider>(true))
                if (c.gameObject.name.StartsWith("Wheel_", StringComparison.Ordinal))
                    throw new InvalidOperationException("P18-03 wheel/fork/hub/axle PhysX collider forbidden: " + c.name);
        }

        /// <summary>
        /// Manual signed travel for integrations that DISABLE autoRollFromTranslation
        /// in the prefab Inspector; do not call this in addition to automatic roll.
        /// Radius: 0.105m. Each wheel rotates around its authentic local X axis.
        /// </summary>
        public bool AdvanceVisualRolling(float signedTravelMeters)
        {
            if (!IsConfigured || radiusMeters <= 0f ||
                float.IsNaN(signedTravelMeters) || float.IsInfinity(signedTravelMeters))
                return false;
            try { VerifyNoWheelPhysics(); }
            catch (Exception e)
            {
                Debug.LogError("P18-03 refusing wheel roll: " + e.Message, this);
                enabled = false;
                return false;
            }
            if (Mathf.Abs(signedTravelMeters) < 0.000001f) return true;
            accumulatedRollDegrees = (accumulatedRollDegrees +
                signedTravelMeters * (180f / (Mathf.PI * radiusMeters))) % 360f;
            Quaternion roll = Quaternion.AngleAxis(accumulatedRollDegrees, Vector3.right);
            for (int i = 0; i < wheels.Length; i++)
                wheels[i].localRotation = restLocalRotations[i] * roll;
            return true;
        }

        private void LateUpdate()
        {
            if (!IsConfigured) return;
            Vector3 currentPosition = transform.position;
            if (!worldPositionInitialized)
            {
                lastWorldPosition = currentPosition;
                worldPositionInitialized = true;
                return;
            }
            Vector3 delta = currentPosition - lastWorldPosition;
            lastWorldPosition = currentPosition;
            if (!autoRollFromTranslation || !enabled) return;
            float distance = delta.magnitude;
            if (float.IsNaN(distance) || float.IsInfinity(distance) ||
                distance > maximumMeasuredStepMeters)
                return; // Ignore scene teleports and invalid motion deltas.
            // Movement along prefab root forward is the actual cart rolling axis.
            // Sideways sliding and pure heading rotation do not rotate wheels.
            AdvanceVisualRolling(Vector3.Dot(delta, transform.forward));
        }
    }
}
