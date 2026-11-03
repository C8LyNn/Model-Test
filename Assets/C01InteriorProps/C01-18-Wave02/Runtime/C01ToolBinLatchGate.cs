using System;
using UnityEngine;

namespace C01.Cargo
{
    /// <summary>
    /// P18-07 signed native 10-mesh/120-triangle lid: a visible Front_Lock mesh
    /// must retract 20mm in authored ROOT +Z before the lid can move.
    /// World-geometry proof: genuine Blender4+binary FBX / 23 angles 0..110deg.
    /// Only licensed Unity6 Editor/PlayMode can validate runtime FBX import.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class C01ToolBinLatchGate : MonoBehaviour
    {
        private enum LatchPhase { Locked, Retracting, Unlocked, Relocking }

        [SerializeField] private Transform lidHinge;
        [SerializeField] private Collider frontLockCollider;
        [SerializeField] private Vector3 localOpeningAxis = Vector3.left;
        // Authoring Unity XYZ root basis (+Z). Do NOT apply blindly in the
        // imported Front_Lock's local axes: the FBX parent may be rotated.
        [SerializeField] private Vector3 rootSpaceReleaseOffset = new Vector3(0f, 0f, 0.020f);
        [SerializeField, Range(0.05f, 1f)] private float retractDurationSeconds = 0.25f;
        [SerializeField, Range(0f, 180f)] private float maximumOpeningDegrees = 110f;

        private Quaternion closedLocalRotation;
        private Vector3 engagedLockLocalPosition;
        private Vector3 retractedDeltaInLockParent;
        private MeshRenderer visibleLockRenderer;
        private Transform originalLockParent;
        private LatchPhase phase = LatchPhase.Locked;
        private float releaseProgress;
        private bool initialized;

        public bool IsUnlocked => initialized && phase == LatchPhase.Unlocked;
        public bool IsTransitioning => initialized &&
            (phase == LatchPhase.Retracting || phase == LatchPhase.Relocking);
        public bool IsLocked => initialized && phase == LatchPhase.Locked;
        public float ReleaseProgress => releaseProgress;
        public float MaximumOpeningDegrees => maximumOpeningDegrees;
        public bool IsLockVisiblyReleased =>
            IsUnlocked && visibleLockRenderer != null && visibleLockRenderer.enabled &&
            frontLockCollider != null && !frontLockCollider.enabled &&
            (frontLockCollider.transform.localPosition -
             (engagedLockLocalPosition + retractedDeltaInLockParent)).sqrMagnitude <= 0.0000000625f;

        /// <summary>Called on imported, SHA-pinned FBX parts by W02 prefab builder.</summary>
        public void Configure(Transform hinge, Collider lockCollider)
        {
            if (hinge == null || lockCollider == null)
                throw new ArgumentNullException("P18-07 requires imported hinge and physical Front_Lock");
            if (hinge == lockCollider.transform)
                throw new InvalidOperationException("P18-07 lock cannot be lid hinge");
            lidHinge = hinge;
            frontLockCollider = lockCollider;
            originalLockParent = lockCollider.transform.parent;
            if (originalLockParent == hinge ||
                (originalLockParent != null && originalLockParent.IsChildOf(hinge)))
                throw new InvalidOperationException("P18-07 Front_Lock must NOT ride with opening lid");
            visibleLockRenderer = lockCollider.GetComponent<MeshRenderer>();
            if (visibleLockRenderer == null || !visibleLockRenderer.enabled || lockCollider.isTrigger)
                throw new InvalidOperationException("P18-07 needs VISIBLE, solid, non-trigger Front_Lock");

            // Map original AUTHORING ROOT motion through any FBX importer parent
            // transforms instead of assuming Blender / Unity local bases agree.
            Vector3 worldRelease = transform.TransformVector(rootSpaceReleaseOffset);
            retractedDeltaInLockParent = originalLockParent != null
                ? originalLockParent.InverseTransformVector(worldRelease) : worldRelease;
            if (retractedDeltaInLockParent.sqrMagnitude < 0.000225f)
                throw new InvalidOperationException("P18-07 latch needs >=15mm real visual release");

            closedLocalRotation = hinge.localRotation;
            engagedLockLocalPosition = lockCollider.transform.localPosition;
            releaseProgress = 0f;
            phase = LatchPhase.Locked;
            initialized = true;
            lidHinge.localRotation = closedLocalRotation;
            frontLockCollider.transform.localPosition = engagedLockLocalPosition;
            frontLockCollider.enabled = true;
        }

        private void Awake()
        {
            try { Configure(lidHinge, frontLockCollider); }
            catch (Exception ex)
            {
                Debug.LogError("P18-07 invalid imported lock/hinge; release blocked: " + ex.Message, this);
                initialized = false;
                enabled = false;
            }
        }

        /// <summary>Starts a visible release. Opening is REJECTED during animation.</summary>
        public bool TryUnlock()
        {
            if (!initialized || phase != LatchPhase.Locked || !IsLidClosed() ||
                visibleLockRenderer == null || !visibleLockRenderer.enabled ||
                !frontLockCollider.enabled)
                return false;
            phase = LatchPhase.Retracting;
            releaseProgress = 0f;
            return true;
        }

        /// <summary>Starts a visible reengagement, only from fully closed lid.</summary>
        public bool TryRelock()
        {
            if (!initialized || phase != LatchPhase.Unlocked || !IsLidClosed() ||
                !IsLockVisiblyReleased)
                return false;
            phase = LatchPhase.Relocking;
            releaseProgress = 1f;
            return true;
        }

        public bool TrySetOpeningDegrees(float degrees)
        {
            if (!IsLockVisiblyReleased || IsTransitioning ||
                float.IsNaN(degrees) || float.IsInfinity(degrees) ||
                degrees < 0f || degrees > maximumOpeningDegrees ||
                localOpeningAxis.sqrMagnitude < 0.5f)
            {
                Debug.LogWarning("P18-07 refused lid motion before complete visual release", this);
                return false;
            }
            lidHinge.localRotation =
                closedLocalRotation * Quaternion.AngleAxis(degrees, localOpeningAxis.normalized);
            return true;
        }

        private bool IsLidClosed() =>
            initialized && lidHinge != null &&
            Quaternion.Angle(lidHinge.localRotation, closedLocalRotation) <= 0.1f;

        private void Update() { Tick(Time.deltaTime); }

        /// <summary>
        /// Internal deterministic frame advance, also exercised using compiled
        /// C# test doubles. That is NOT a Unity Editor or PlayMode test.
        /// </summary>
        internal void Tick(float dt)
        {
            if (!initialized || float.IsNaN(dt) || float.IsInfinity(dt) || dt <= 0f)
                return;
            if (phase != LatchPhase.Retracting && phase != LatchPhase.Relocking)
                return;
            if (frontLockCollider.transform.parent != originalLockParent ||
                visibleLockRenderer == null || !visibleLockRenderer.enabled)
            {
                FailClosed("Front_Lock parent/visible renderer changed during motion");
                return;
            }

            float step = dt / Mathf.Max(0.05f, retractDurationSeconds);
            if (phase == LatchPhase.Retracting)
            {
                releaseProgress = Mathf.MoveTowards(releaseProgress, 1f, step);
                frontLockCollider.transform.localPosition =
                    engagedLockLocalPosition + retractedDeltaInLockParent * releaseProgress;
                // Remains solid until visually FULLY retracted; hinge always locked.
                frontLockCollider.enabled = true;
                if (releaseProgress >= 1f)
                {
                    frontLockCollider.enabled = false;
                    phase = LatchPhase.Unlocked;
                }
            }
            else
            {
                releaseProgress = Mathf.MoveTowards(releaseProgress, 0f, step);
                frontLockCollider.enabled = false; // Never relock while sliding.
                frontLockCollider.transform.localPosition =
                    engagedLockLocalPosition + retractedDeltaInLockParent * releaseProgress;
                if (releaseProgress <= 0f)
                {
                    frontLockCollider.transform.localPosition = engagedLockLocalPosition;
                    frontLockCollider.enabled = true;
                    phase = LatchPhase.Locked;
                }
            }
        }

        private void LateUpdate()
        {
            if (!initialized) return;
            if (frontLockCollider.transform.parent != originalLockParent ||
                visibleLockRenderer == null || !visibleLockRenderer.enabled)
            {
                FailClosed("Front_Lock visible mesh or parent unexpectedly changed");
                return;
            }
            if (phase != LatchPhase.Unlocked && !IsLidClosed())
                lidHinge.localRotation = closedLocalRotation;

            Vector3 expected = engagedLockLocalPosition +
                retractedDeltaInLockParent * releaseProgress;
            if ((frontLockCollider.transform.localPosition - expected).sqrMagnitude > 0.00000001f)
                frontLockCollider.transform.localPosition = expected;
            bool shouldBeSolid = phase == LatchPhase.Locked ||
                                  phase == LatchPhase.Retracting;
            if (frontLockCollider.enabled != shouldBeSolid)
                frontLockCollider.enabled = shouldBeSolid;
        }

        private void FailClosed(string reason)
        {
            Debug.LogError("P18-07 lock FAIL-CLOSED: " + reason, this);
            if (lidHinge != null) lidHinge.localRotation = closedLocalRotation;
            if (frontLockCollider != null)
            {
                frontLockCollider.transform.localPosition = engagedLockLocalPosition;
                frontLockCollider.enabled = true;
            }
            releaseProgress = 0f;
            phase = LatchPhase.Locked;
            enabled = false;
        }
    }
}
