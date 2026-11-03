using System;
using UnityEngine;

namespace C01.Cargo
{
    /// <summary>
    /// P18-03: eight render-only hub parts overlap stationary fork cheeks by 2mm
    /// (C01-02 W22: 576/576 swept positions). THIS IS A VISUAL BEARING, NOT A
    /// collision/PhysX joint. Keep all hubs, forks and axles free of solid
    /// colliders. Physical cart collisions belong to the six shelf/upright
    /// colliders assigned by BuildWave01CargoPrefabs.
    /// Attach only to authentic signed P18-03 FBX. Real Unity PlayMode NOT_RUN.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class C01CartWheelVisualBearing : MonoBehaviour
    {
        [SerializeField] private Transform[] wheels = new Transform[4];
        [SerializeField, Min(0.01f)] private float radiusMeters = 0.105f;
        private Quaternion[] restingRotations;
        public bool IsConfigured => restingRotations != null && restingRotations.Length == 4;

        public void Configure(Transform[] nativeWheels)
        {
            if (nativeWheels == null || nativeWheels.Length != 4)
                throw new ArgumentException("P18-03 requires all 4 genuine signed FBX wheel pivots");
            wheels = (Transform[])nativeWheels.Clone();
            restingRotations = new Quaternion[4];
            string[] suffixes = {"Wheel_LB", "Wheel_LF", "Wheel_RB", "Wheel_RF"};
            for (int i = 0; i < 4; ++i)
            {
                if (wheels[i] == null || wheels[i].name != suffixes[i])
                    throw new InvalidOperationException("Incorrect P18-03 wheel pivot: " + suffixes[i]);
                if (wheels[i].GetComponent<MeshFilter>() == null)
                    throw new InvalidOperationException("P18-03 missing wheel mesh: " + suffixes[i]);
                foreach (var c in wheels[i].GetComponentsInChildren<Collider>(true))
                    throw new InvalidOperationException("P18-03 decorative wheel/hub collider forbidden: " + c.name);
                restingRotations[i] = wheels[i].localRotation;
            }
        }

        private void Awake()
        {
            // Nonserialized runtime caches do NOT survive prefab deserialization.
            // Reconstruct all original wheel pivots before gameplay uses the guard.
            try { Configure(wheels); }
            catch (Exception e)
            {
                Debug.LogError("P18-03 visual bearing is not safe to roll: " + e.Message, this);
                enabled = false;
            }
        }

        /// <summary>
        /// For visual rolling ONLY. Not a wheel PhysX drive; gameplay should call
        /// this after moving the kinematic cart. Four wheels use local X axle.
        /// Signed-travel distance in meters; no Time.deltaTime assumption.
        /// </summary>
        public bool AdvanceVisualRolling(float signedTravelMeters)
        {
            if (!IsConfigured || float.IsNaN(signedTravelMeters) || float.IsInfinity(signedTravelMeters))
                return false;
            float angle = signedTravelMeters * (180f / (Mathf.PI * radiusMeters));
            for (int i = 0; i < wheels.Length; ++i)
                wheels[i].localRotation *= Quaternion.AngleAxis(angle, Vector3.right);
            return true;
        }
    }
}
