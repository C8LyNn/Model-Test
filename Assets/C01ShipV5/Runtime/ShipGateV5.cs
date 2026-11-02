using System.Collections.Generic;
using UnityEngine;

namespace C01.Ship.V5
{
    public class ShipGateV5 : MonoBehaviour
    {
        public string id;
        public Transform[] leaves = new Transform[0];
        public Vector3[] travel = new Vector3[0];
        [Range(0, 1)] public float openness;
        [Range(0, 1)] public float target;
        public float speed = 1.8f;
        public ShipAirlockV5 interlockAirlock;
        public ShipLiftV5 interlockLift;
        public int landingFloor;
        public bool IsOpen => openness >= .999f;
        public bool IsClosed => openness <= .001f;

        [SerializeField, HideInInspector] List<Transform> cachedLeaves = new List<Transform>();
        [SerializeField, HideInInspector] List<Vector3> closedPositions = new List<Vector3>();

        readonly Dictionary<Transform, Vector3> closed = new Dictionary<Transform, Vector3>();
        readonly Dictionary<Transform, Rigidbody> bodies = new Dictionary<Transform, Rigidbody>();

        void Start()
        {
            CacheLeaves();
            SetImmediate(openness);
        }

        void CacheLeaves()
        {
            for (int i = 0; i < leaves.Length; i++)
            {
                var leaf = leaves[i];
                if (leaf == null || closed.ContainsKey(leaf)) continue;
                // Cache lazily: the Editor builder assigns references after AddComponent/Awake.
                int stored = cachedLeaves.IndexOf(leaf);
                Vector3 origin;
                if (stored >= 0 && stored < closedPositions.Count) origin = closedPositions[stored];
                else
                {
                    var displacement = i < travel.Length ? travel[i] : Vector3.zero;
                    var localTravel = leaf.parent != null ? leaf.parent.InverseTransformVector(displacement) : displacement;
                    origin = leaf.localPosition - localTravel * openness;
                    cachedLeaves.Add(leaf);
                    closedPositions.Add(origin);
                }
                closed.Add(leaf, origin);
                var body = leaf.GetComponent<Rigidbody>();
                if (body == null) body = leaf.gameObject.AddComponent<Rigidbody>();
                body.isKinematic = true;
                body.useGravity = false;
                body.interpolation = RigidbodyInterpolation.None;
                bodies.Add(leaf, body);
            }
        }

        public void SetOpen(bool open)
        {
            if (interlockAirlock != null)
            {
                interlockAirlock.Request(this, open);
                return;
            }
            SetTarget(open);
        }

        // Controller-only path; deliberately does not route back through an airlock.
        internal void SetTarget(bool open)
        {
            target = open && (interlockLift == null || interlockLift.CanOpenLanding(this)) ? 1 : 0;
        }

        public void SetImmediate(float value)
        {
            CacheLeaves();
            value = Mathf.Clamp01(value);
            if (value > 0 && interlockLift != null && !interlockLift.CanOpenLanding(this)) value = 0;
            if (value > 0 && interlockAirlock != null && !interlockAirlock.CanOpenImmediately(this)) value = 0;
            openness = target = value;
            Apply(true);
            Physics.SyncTransforms();
        }

        void FixedUpdate()
        {
            CacheLeaves();
            if (interlockLift != null && !interlockLift.CanOpenLanding(this)) target = 0;
            openness = Mathf.MoveTowards(openness, Mathf.Clamp01(target), Mathf.Max(0, speed) * Time.fixedDeltaTime);
            Apply(false);
        }

        void Apply(bool immediate)
        {
            for (int i = 0; i < leaves.Length; i++)
            {
                var leaf = leaves[i];
                if (leaf == null) continue;
                var displacement = i < travel.Length ? travel[i] : Vector3.zero;
                // Manifest travel is in world axes, even when a leaf has a rotated parent.
                var localTravel = leaf.parent != null ? leaf.parent.InverseTransformVector(displacement) : displacement;
                var local = closed[leaf] + localTravel * openness;
                var world = leaf.parent != null ? leaf.parent.TransformPoint(local) : local;
                if (immediate)
                {
                    leaf.localPosition = local;
                    bodies[leaf].position = world;
                }
                else bodies[leaf].MovePosition(world);
            }
        }
    }
}
