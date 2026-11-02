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
        [SerializeField, Range(0f, 180f)] private float maximumOpeningDegrees = 110f;

        private Quaternion closedLocalRotation;
        private bool initialized;
        private bool unlocked;

        public bool IsUnlocked => initialized && unlocked;
        public float MaximumOpeningDegrees => maximumOpeningDegrees;

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
            initialized = true;
            unlocked = false;
            frontLockCollider.enabled = true;
        }

        public bool TryUnlock()
        {
            if (!initialized || unlocked || !IsLidClosed())
                return false;
            frontLockCollider.enabled = false;
            unlocked = true;
            return true;
        }

        /// <summary>Uses the imported hinge's LOCAL axis; verify sign in REAL Unity Editor.</summary>
        public bool TrySetOpeningDegrees(float degrees)
        {
            if (!initialized || !unlocked || !Mathf.IsFinite(degrees) ||
                degrees < 0f || degrees > maximumOpeningDegrees ||
                localOpeningAxis.sqrMagnitude < 0.5f)
                return false;
            lidHinge.localRotation =
                closedLocalRotation * Quaternion.AngleAxis(degrees, localOpeningAxis.normalized);
            return true;
        }

        public bool TryRelock()
        {
            if (!initialized || !unlocked || !IsLidClosed())
                return false;
            unlocked = false;
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
        }
    }
}
