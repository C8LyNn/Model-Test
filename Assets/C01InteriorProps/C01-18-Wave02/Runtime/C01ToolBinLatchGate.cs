using UnityEngine;

namespace C01.Cargo
{
    /// <summary>
    /// QA-scoped functional lock contract for the existing P18-07 tool-bin lid.
    /// The imported Front_Lock collider remains solid while the lid is locked.
    /// Open the lid only through TrySetOpeningDegrees, AFTER TryUnlock succeeds.
    /// Real Unity6 PlayMode / imported FBX pivot-axis validation is required.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class C01ToolBinLatchGate : MonoBehaviour
    {
        [SerializeField] private Transform lidHinge;
        [SerializeField] private Collider frontLockCollider;
        [SerializeField] private Vector3 localOpeningAxis = Vector3.left;
        // Proven signed Blender4 source AND binary FBX 23-pose BVH geometric
        // release clearance: Blender WORLD (0,-0.020,0) => original authoring
        // Unity XYZ (0,0,+0.020). Verify imported local axis in actual Unity.
        [SerializeField] private Vector3 lockReleaseLocalOffset = new Vector3(0f, 0f, 0.020f);
        [SerializeField, Range(0f, 180f)] private float maximumOpeningDegrees = 110f;

        private Quaternion closedLocalRotation;
        private Vector3 closedLockLocalPosition;
        private MeshRenderer visibleLockRenderer;
        private bool initialized;
        private bool unlocked;

        public bool IsUnlocked => initialized && unlocked;
        public float MaximumOpeningDegrees => maximumOpeningDegrees;
        public bool IsLockVisiblyReleased =>
            initialized && unlocked && visibleLockRenderer != null &&
            visibleLockRenderer.enabled &&
            (frontLockCollider.transform.localPosition - closedLockLocalPosition).sqrMagnitude > 0.000001f;

        /// <summary>Called by the W02 QA prefab builder on the imported REAL FBX nodes.</summary>
        public void Configure(Transform hinge, Collider lockCollider)
        {
            if (hinge == null || lockCollider == null)
                throw new System.ArgumentNullException("P18-07 requires both native lid hinge and Front_Lock collider");
            if (hinge == lockCollider.transform)
                throw new System.InvalidOperationException("P18-07 lid hinge cannot be its own fixed Front_Lock");
            lidHinge = hinge;
            frontLockCollider = lockCollider;
            closedLocalRotation = lidHinge.localRotation;
            closedLockLocalPosition = frontLockCollider.transform.localPosition;
            visibleLockRenderer = frontLockCollider.GetComponent<MeshRenderer>();
            if (visibleLockRenderer == null || !visibleLockRenderer.enabled)
                throw new System.InvalidOperationException("P18-07 Front_Lock must be visible in LOCKED state");
            initialized = true;
            unlocked = false;
            frontLockCollider.enabled = true;
        }

        private void Awake()
        {
            if (lidHinge == null || frontLockCollider == null)
            {
                Debug.LogError("C01-18 P18-07 latch not bound to real FBX hinge/Front_Lock", this);
                enabled = false;
                return;
            }
            closedLocalRotation = lidHinge.localRotation;
            closedLockLocalPosition = frontLockCollider.transform.localPosition;
            visibleLockRenderer = frontLockCollider.GetComponent<MeshRenderer>();
            if (visibleLockRenderer == null || !visibleLockRenderer.enabled ||
                lockReleaseLocalOffset.sqrMagnitude < 0.0001f)
            {
                Debug.LogError("P18-07 missing VISIBLE lock or release offset", this);
                enabled = false;
                return;
            }
            initialized = true;
            unlocked = false;
            frontLockCollider.enabled = true;
        }

        public bool TryUnlock()
        {
            if (!initialized || unlocked || !IsLidClosed())
                return false;
            // First retract the ACTUAL visible mesh itself (collider lives on it),
            // THEN release collision gate in the SAME synchronous action.
            frontLockCollider.transform.localPosition = closedLockLocalPosition + lockReleaseLocalOffset;
            frontLockCollider.enabled = false;
            unlocked = true;
            return IsLockVisiblyReleased;
        }

        /// <summary>Uses the imported hinge's LOCAL axis; verify sign in REAL Unity Editor.</summary>
        public bool TrySetOpeningDegrees(float degrees)
        {
            if (!initialized || !unlocked || !IsLockVisiblyReleased ||
                frontLockCollider.enabled || (float.IsNaN(degrees) || float.IsInfinity(degrees)) ||
                degrees < 0f || degrees > maximumOpeningDegrees ||
                localOpeningAxis.sqrMagnitude < 0.5f)
            {
                Debug.LogWarning("P18-07 opening refused: lid LOCKED, lock still engaged, or angle invalid", this);
                return false;
            }
            lidHinge.localRotation =
                closedLocalRotation * Quaternion.AngleAxis(degrees, localOpeningAxis.normalized);
            return true;
        }

        public bool TryRelock()
        {
            if (!initialized || !unlocked || !IsLidClosed())
                return false;
            unlocked = false;
            frontLockCollider.transform.localPosition = closedLockLocalPosition;
            frontLockCollider.enabled = true;
            return true;
        }

        private bool IsLidClosed()
        {
            return initialized && lidHinge != null &&
                Quaternion.Angle(lidHinge.localRotation, closedLocalRotation) <= 0.1f;
        }

        private void LateUpdate()
        {
            if (!initialized || lidHinge == null || frontLockCollider == null)
                return;
            if (!unlocked && !IsLidClosed())
                lidHinge.localRotation = closedLocalRotation;
            if (frontLockCollider.enabled == unlocked)
                frontLockCollider.enabled = !unlocked;
            Vector3 expectedLockPosition = closedLockLocalPosition +
                (unlocked ? lockReleaseLocalOffset : Vector3.zero);
            if ((frontLockCollider.transform.localPosition - expectedLockPosition).sqrMagnitude > 0.00000001f)
                frontLockCollider.transform.localPosition = expectedLockPosition;
        }
    }
}
