using System;
using UnityEngine;

namespace C01.Cargo
{
    /// <summary>
    /// P18-05 W25 scoped motion on ORIGINAL signed P18-05 binary FBX:
    /// 8mm visible outward Front_Latch_L/R slide, followed by 2mm upward lid
    /// hinge lift, then 0..110deg rotation around the original local -X axis.
    /// Three ORIGINAL handle meshes stay rigidly attached to the lid.
    /// Genuine signed BLEND and reimported FBX BVH each showed zero opened-pose
    /// mesh contacts at all 23 sampled -X positions (Actions #41634630338).
    /// Licensed Unity Editor/FBX-imported PlayMode has NOT run.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class C01EquipmentCaseLatchGate : MonoBehaviour
    {
        private enum MotionPhase
        {
            Locked,
            ReleasingLatches,
            LiftingLid,
            Unlocked,
            LoweringLid,
            RelockingLatches
        }

        [SerializeField] private Transform lidHinge;
        [SerializeField] private Transform leftLatch;
        [SerializeField] private Transform rightLatch;
        [SerializeField] private Transform[] handleParts = new Transform[3];
        [SerializeField] private Collider caseLidCollider;

        // These values are authored in the enclosing P18_05 prefab-root
        // Unity axes, NOT the actual imported P18-05_Root's local FBX axes.
        [SerializeField] private Vector3 rootSpaceLatchRelease = new Vector3(0f, 0f, 0.008f);
        [SerializeField] private Vector3 rootSpaceHingeLift = new Vector3(0f, 0.002f, 0f);
        [SerializeField, Range(0.05f, 1f)] private float unlatchDurationSeconds = 0.20f;
        [SerializeField, Range(0.05f, 1f)] private float hingeLiftDurationSeconds = 0.15f;
        [SerializeField, Range(0f, 180f)] private float maximumOpeningDegrees = 110f;

        private readonly Transform[] latchOriginalParents = new Transform[2];
        private readonly Vector3[] latchRestLocalPositions = new Vector3[2];
        private readonly Vector3[] latchParentLocalRelease = new Vector3[2];
        private Transform hingeOriginalParent;
        private Vector3 hingeRestLocalPosition;
        private Vector3 hingeParentLocalLift;
        private Quaternion hingeRestLocalRotation;
        private MotionPhase phase = MotionPhase.Locked;
        private float progress;
        private bool initialized;

        public bool IsLocked => initialized && phase == MotionPhase.Locked;
        public bool IsUnlocked => initialized && phase == MotionPhase.Unlocked;
        public bool IsTransitioning => initialized && phase != MotionPhase.Unlocked &&
                                        phase != MotionPhase.Locked;
        public float TransitionProgress => progress;
        public float MaximumOpeningDegrees => maximumOpeningDegrees;
        public bool IsVisibleLatchReleased =>
            initialized && (phase == MotionPhase.LiftingLid ||
                            phase == MotionPhase.Unlocked ||
                            phase == MotionPhase.LoweringLid) &&
            LatchesAtExpected(1f) && VisibleLatchesAreValid();

        public void Configure(
            Transform hinge,
            Transform latchL,
            Transform latchR,
            Collider lidCollider,
            Transform[] importedHandleParts)
        {
            if (hinge == null || latchL == null || latchR == null ||
                lidCollider == null || importedHandleParts == null ||
                importedHandleParts.Length != 3)
                throw new ArgumentException("P18-05 requires one original lid hinge, 2 visible latches, 3 handle meshes, actual Case_Lid collider");
            if (hinge.name != "Lid_HingePivot" ||
                latchL.name != "Front_Latch_L" || latchR.name != "Front_Latch_R" ||
                lidCollider.transform.name != "Case_Lid" || lidCollider.isTrigger)
                throw new InvalidOperationException("P18-05 invalid original signed FBX part identity");

            lidHinge = hinge;
            leftLatch = latchL;
            rightLatch = latchR;
            caseLidCollider = lidCollider;
            handleParts = (Transform[])importedHandleParts.Clone();

            if (caseLidCollider.transform.parent != lidHinge)
                throw new InvalidOperationException("P18-05 signed Case_Lid must follow Lid_HingePivot");
            string[] expectedHandleNames = {
                "Carry_Handle_Rail", "Carry_Handle_Stem_L", "Carry_Handle_Stem_R"
            };
            for (int i = 0; i < handleParts.Length; i++)
            {
                Transform h = handleParts[i];
                if (h == null || h.name != expectedHandleNames[i] ||
                    h.parent != lidHinge || h.GetComponent<MeshRenderer>() == null)
                    throw new InvalidOperationException("P18-05 original handle part must be a child of the moving lid: " + expectedHandleNames[i]);
            }
            if (leftLatch == rightLatch ||
                leftLatch.IsChildOf(lidHinge) || rightLatch.IsChildOf(lidHinge))
                throw new InvalidOperationException("P18-05 two fixed-parented release latches must not rotate with lid");
            if (!VisibleLatchesAreValid())
                throw new InvalidOperationException("P18-05 physical visible latch meshes are missing or disabled");

            hingeOriginalParent = hinge.parent;
            hingeRestLocalPosition = hinge.localPosition;
            hingeRestLocalRotation = hinge.localRotation;

            Transform[] latches = { leftLatch, rightLatch };
            Vector3 worldSlide = transform.TransformVector(rootSpaceLatchRelease);
            for (int i = 0; i < latches.Length; i++)
            {
                latchOriginalParents[i] = latches[i].parent;
                if (latchOriginalParents[i] == null ||
                    latchOriginalParents[i].IsChildOf(hinge) ||
                    latchOriginalParents[i] == hinge)
                    throw new InvalidOperationException("P18-05 latch must be a fixed original body child");
                latchRestLocalPositions[i] = latches[i].localPosition;
                latchParentLocalRelease[i] =
                    latchOriginalParents[i].InverseTransformVector(worldSlide);
                if (latchParentLocalRelease[i].magnitude < 0.0075f)
                    throw new InvalidOperationException("P18-05 latch missing required 8mm genuine clearance movement");
            }

            Vector3 worldLift = transform.TransformVector(rootSpaceHingeLift);
            hingeParentLocalLift = hingeOriginalParent != null
                ? hingeOriginalParent.InverseTransformVector(worldLift) : worldLift;
            if (hingeParentLocalLift.magnitude < 0.0019f)
                throw new InvalidOperationException("P18-05 lid cannot raise 2mm before rotation");

            initialized = true;
            phase = MotionPhase.Locked;
            progress = 0f;
            RestoreOriginalLockedState();
        }

        private void Awake()
        {
            try { Configure(lidHinge, leftLatch, rightLatch, caseLidCollider, handleParts); }
            catch (Exception e)
            {
                initialized = false;
                enabled = false;
                Debug.LogError("P18-05 original FBX prefab invalid, fail-closed: " + e.Message, this);
            }
        }

        public bool TryUnlock()
        {
            if (!IsLocked || !IsHingeAtRest() || !VisibleLatchesAreValid())
                return false;
            phase = MotionPhase.ReleasingLatches;
            progress = 0f;
            return true;
        }

        public bool TrySetOpeningDegrees(float openingDegrees)
        {
            if (!IsUnlocked || !IsVisibleLatchReleased ||
                float.IsNaN(openingDegrees) || float.IsInfinity(openingDegrees) ||
                openingDegrees < 0f || openingDegrees > maximumOpeningDegrees ||
                !CheckImportedHierarchy())
                return false;
            // Source independent C01-02 W24 selected -X; +X was a proven bad path.
            lidHinge.localRotation =
                hingeRestLocalRotation * Quaternion.AngleAxis(-openingDegrees, Vector3.right);
            return true;
        }

        public bool TryRelock()
        {
            if (!IsUnlocked || !IsLidClosed() || !LatchesAtExpected(1f))
                return false;
            phase = MotionPhase.LoweringLid;
            progress = 1f;
            return true;
        }

        private bool VisibleLatchesAreValid()
        {
            return leftLatch != null && rightLatch != null &&
                   leftLatch.GetComponent<MeshRenderer>() != null &&
                   rightLatch.GetComponent<MeshRenderer>() != null &&
                   leftLatch.GetComponent<MeshRenderer>().enabled &&
                   rightLatch.GetComponent<MeshRenderer>().enabled;
        }

        private bool CheckImportedHierarchy()
        {
            if (lidHinge == null || lidHinge.parent != hingeOriginalParent ||
                caseLidCollider == null || caseLidCollider.transform.parent != lidHinge ||
                leftLatch == null || rightLatch == null ||
                leftLatch.parent != latchOriginalParents[0] ||
                rightLatch.parent != latchOriginalParents[1] ||
                !VisibleLatchesAreValid())
                return false;
            for (int i = 0; i < 3; i++)
                if (handleParts[i] == null || handleParts[i].parent != lidHinge)
                    return false;
            return true;
        }

        private bool IsHingeAtRest()
        {
            return initialized &&
                   Quaternion.Angle(lidHinge.localRotation, hingeRestLocalRotation) <= 0.1f &&
                   (lidHinge.localPosition - hingeRestLocalPosition).sqrMagnitude < 0.00000001f;
        }

        private bool IsLidClosed()
        {
            return initialized &&
                   Quaternion.Angle(lidHinge.localRotation, hingeRestLocalRotation) <= 0.1f;
        }

        private bool LatchesAtExpected(float alpha)
        {
            Transform[] latches = { leftLatch, rightLatch };
            for (int i = 0; i < 2; i++)
            {
                Vector3 expected = latchRestLocalPositions[i] + latchParentLocalRelease[i] * alpha;
                if ((latches[i].localPosition - expected).sqrMagnitude > 0.0000000625f)
                    return false;
            }
            return true;
        }

        private void SetLatchRelease(float alpha)
        {
            leftLatch.localPosition = latchRestLocalPositions[0] + latchParentLocalRelease[0] * alpha;
            rightLatch.localPosition = latchRestLocalPositions[1] + latchParentLocalRelease[1] * alpha;
        }

        private void SetHingeLift(float alpha)
        {
            lidHinge.localPosition = hingeRestLocalPosition + hingeParentLocalLift * alpha;
        }

        private void Update() { Tick(Time.deltaTime); }

        /// <summary>
        /// Advance current real C# state machine deterministically for tests;
        /// actual licensed Unity6 import/editor/PlayMode remains NOT_RUN.
        /// </summary>
        internal void Tick(float dt)
        {
            if (!initialized || !enabled || float.IsNaN(dt) ||
                float.IsInfinity(dt) || dt <= 0f)
                return;
            if (!CheckImportedHierarchy())
            {
                FailClosed("FBX parent, moving handle, or visible latch tampered");
                return;
            }
            if (!IsTransitioning) return;
            if (!IsLidClosed())
            {
                FailClosed("Hinge rotated while a latch was engaged/transiting");
                return;
            }
            switch (phase)
            {
                case MotionPhase.ReleasingLatches:
                    progress = Mathf.MoveTowards(progress, 1f,
                        dt / Mathf.Max(0.05f, unlatchDurationSeconds));
                    SetLatchRelease(progress);
                    if (progress >= 1f)
                    {
                        phase = MotionPhase.LiftingLid;
                        progress = 0f;
                    }
                    break;
                case MotionPhase.LiftingLid:
                    progress = Mathf.MoveTowards(progress, 1f,
                        dt / Mathf.Max(0.05f, hingeLiftDurationSeconds));
                    SetHingeLift(progress);
                    if (progress >= 1f)
                    {
                        phase = MotionPhase.Unlocked;
                        progress = 1f;
                    }
                    break;
                case MotionPhase.LoweringLid:
                    progress = Mathf.MoveTowards(progress, 0f,
                        dt / Mathf.Max(0.05f, hingeLiftDurationSeconds));
                    SetHingeLift(progress);
                    if (progress <= 0f)
                    {
                        phase = MotionPhase.RelockingLatches;
                        progress = 1f;
                    }
                    break;
                case MotionPhase.RelockingLatches:
                    progress = Mathf.MoveTowards(progress, 0f,
                        dt / Mathf.Max(0.05f, unlatchDurationSeconds));
                    SetLatchRelease(progress);
                    if (progress <= 0f)
                    {
                        phase = MotionPhase.Locked;
                        progress = 0f;
                    }
                    break;
            }
        }

        private void LateUpdate()
        {
            if (!initialized || !enabled) return;
            if (!CheckImportedHierarchy())
            {
                FailClosed("Original signed FBX geometry hierarchy changed");
                return;
            }
            if (!IsUnlocked && !IsLidClosed())
                lidHinge.localRotation = hingeRestLocalRotation;
        }

        private void RestoreOriginalLockedState()
        {
            lidHinge.localRotation = hingeRestLocalRotation;
            SetHingeLift(0f);
            SetLatchRelease(0f);
            caseLidCollider.enabled = true;
        }

        private void FailClosed(string reason)
        {
            Debug.LogError("P18-05 unlock FAIL-CLOSED: " + reason, this);
            if (lidHinge != null && leftLatch != null && rightLatch != null &&
                caseLidCollider != null)
                RestoreOriginalLockedState();
            phase = MotionPhase.Locked;
            progress = 0f;
            enabled = false;
        }
    }
}
