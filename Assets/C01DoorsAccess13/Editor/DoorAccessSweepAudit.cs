// C01-13 / access-to-gate sweep preflight. Read-only Editor utility.
// Checks Unity world-space AABB swept by translation; a hit is POSSIBLE, not a physics collision.
// Does not modify existing doors, scenes, prefabs or runtime scripts.
#if UNITY_EDITOR
using System;
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;
using C01.Ship.V4;

namespace C01.Doors.Access
{
    public static class DoorAccessSweepAudit
    {
        const float ClearanceM = 0.02f;

        [Serializable]
        class Finding
        {
            public string status;
            public string gate;
            public string accessory;
            public string detail;
        }

        [Serializable]
        class Evidence
        {
            public string tool = "C01-13 DoorAccessSweepAudit";
            public string scope;
            public string utc;
            public string contract = "C01-SHIP-V4 SLIDING GATES (NOT LEGACY D01/D02)";
            public string method = "World-space Collider+Renderer AABB translational sweep; conservative broadphase plus P17-02 visual/collider envelope check";
            public float safetyMarginMetres = ClearanceM;
            public int gatesFound;
            public int accessoriesFound;
            public int movingLeavesChecked;
            public int possibleIntersections;
            public int visualColliderMismatches;
            public int readerAttachmentGapCandidates;
            public int incompleteChecks;
            public List<Finding> findings = new List<Finding>();
        }

        [MenuItem("Tools/C01/Doors & Access/Audit Gate-Accessory Clearance")]
        static void Audit()
        {
            var report = new Evidence { utc = DateTime.UtcNow.ToString("o") };
            var roots = new List<GameObject>();
            if (Selection.activeTransform != null)
            {
                roots.Add(Selection.activeTransform.gameObject);
                report.scope = "Selected root: " + Selection.activeTransform.name;
            }
            else
            {
                Scene scene = SceneManager.GetActiveScene();
                if (scene.IsValid()) roots.AddRange(scene.GetRootGameObjects());
                report.scope = "Active scene: " + scene.name;
            }

            var gates = new HashSet<ShipGateV4>();
            var accessories = new HashSet<Transform>();
            foreach (var root in roots)
            {
                if (root == null) continue;
                foreach (var gate in root.GetComponentsInChildren<ShipGateV4>(true))
                    if (gate.gameObject.activeInHierarchy) gates.Add(gate);
                foreach (var t in root.GetComponentsInChildren<Transform>(true))
                    if (t.gameObject.activeInHierarchy && IsAccessory(t.name))
                        accessories.Add(t);
            }

            report.gatesFound = gates.Count;
            report.accessoriesFound = accessories.Count;
            if (gates.Count == 0) Incomplete(report, "NO_GATE", "", "No active ShipGateV4 in selected scope");
            if (accessories.Count == 0) Incomplete(report, "NO_ACCESSORY", "",
                "No active P17-02 / P16-07 / P_Button in scope; supplier showcase cannot be assessed");

            foreach (var accessory in accessories)
            {
                Bounds accessoryBounds;
                bool accessoryCollider;
                if (!TryBounds(accessory.gameObject, out accessoryBounds, out accessoryCollider))
                {
                    Incomplete(report, "NO_ACCESSORY_GEOMETRY", accessory.name,
                        "No enabled collider or renderer; mount dimensions cannot be checked");
                    continue;
                }
                if (!accessoryCollider)
                    Incomplete(report, "ACCESSORY_RENDERER_ONLY", accessory.name,
                        "Geometry bounds used; accessory has no enabled collision volume");

                // P17-02 access-reader has a strict fixed-wall visual/collider contract.
                // Do not let its historical root box collider hide oversized new mesh details.
                if (accessory.name.IndexOf("P17-02", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    Bounds visual, physical;
                    bool visualFound = TryRendererBounds(accessory.gameObject, out visual);
                    bool colliderFound = TryColliderBounds(accessory.gameObject, out physical);
                    if (!visualFound || !colliderFound)
                        Incomplete(report, "READER_VISUAL_OR_COLLIDER_MISSING", accessory.name,
                            "P17-02 requires both actual enabled renderers and a fixed-envelope collider");
                    else if (ExtendsOutside(visual, physical, 0.03f))
                    {
                        report.visualColliderMismatches++;
                        Add(report, "ERROR_READER_VISUAL_COLLIDER_MISMATCH", "", accessory.name,
                            "P17-02 render geometry protrudes >30 mm beyond collider AABB; " +
                            "verify imported FBX actual mesh (oversized fasteners, misbound guide mesh, pivot), " +
                            "do NOT accept based only on root box collider.");
                    }

                    // A positive AABB gap is proof of separation. AABB overlap is
                    // only broadphase and never claims full triangle-surface contact.
                    // Missing new components = STALE native FBX or incomplete importer;
                    // never award a clean gate result to an old 20-part P17-02 export.
                    CheckReaderAttachment(report, accessory, "Keybed", "Housing");
                    for (int guide = 1; guide <= 12; guide++)
                        CheckReaderAttachment(report, accessory, "KeyGuide_" + guide.ToString("D2"), "Keybed");
                    CheckReaderAttachment(report, accessory, "LeftClampReinforcement", "LeftClamp");
                    CheckReaderAttachment(report, accessory, "RightClampReinforcement", "RightClamp");
                    CheckReaderAttachment(report, accessory, "LeftBottomMountScrew", "MountBacking");
                    CheckReaderAttachment(report, accessory, "LeftTopMountScrew", "MountBacking");
                    CheckReaderAttachment(report, accessory, "RightBottomMountScrew", "MountBacking");
                    CheckReaderAttachment(report, accessory, "RightTopMountScrew", "MountBacking");
                }

                bool boundToController = accessory.GetComponent<ShipButtonV4>() != null ||
                    accessory.GetComponentInParent<ShipButtonV4>() != null ||
                    accessory.GetComponentInChildren<ShipButtonV4>(true) != null;
                if (!boundToController)
                    Add(report, "INFO_UNVERIFIED_BINDING", "", accessory.name,
                        "No ShipButtonV4 in hierarchy; external wiring may be intentional and needs integration review");

                foreach (var gate in gates)
                {
                    if (gate.leaves == null || gate.leaves.Length == 0)
                    {
                        Incomplete(report, "EMPTY_GATE", gate.name, "Gate has no configured moving leaves");
                        continue;
                    }
                    for (int i = 0; i < gate.leaves.Length; i++)
                    {
                        var leaf = gate.leaves[i];
                        if (leaf == null)
                        {
                            Incomplete(report, "NULL_LEAF", gate.name, "Missing leaf index " + i);
                            continue;
                        }
                        if (accessory.IsChildOf(leaf) || accessory == leaf)
                        {
                            Add(report, "ERROR_MOVING_MOUNT", gate.name, accessory.name,
                                "Accessory belongs to a moving gate leaf; mount to non-moving structure");
                            report.possibleIntersections++;
                            continue;
                        }
                        if (gate.travel == null || i >= gate.travel.Length)
                        {
                            Incomplete(report, "MISSING_TRAVEL", gate.name, "Missing world-space travel for leaf " + i);
                            continue;
                        }
                        Bounds leafBounds;
                        bool leafCollider;
                        if (!TryBounds(leaf.gameObject, out leafBounds, out leafCollider))
                        {
                            Incomplete(report, "NO_LEAF_GEOMETRY", gate.name,
                                "No enabled collider or renderer for leaf " + i);
                            continue;
                        }
                        if (!leafCollider)
                            Incomplete(report, "LEAF_RENDERER_ONLY", gate.name,
                                "Leaf " + i + " has no enabled collision volume");

                        report.movingLeavesChecked++;
                        Vector3 delta = gate.travel[i];
                        Bounds swept = Translate(leafBounds, -Mathf.Clamp01(gate.openness) * delta);
                        swept.Encapsulate(Translate(leafBounds, (1f - Mathf.Clamp01(gate.openness)) * delta));
                        swept.Expand(2f * ClearanceM);
                        if (swept.Intersects(accessoryBounds))
                        {
                            report.possibleIntersections++;
                            Add(report, "POSSIBLE_SWEEP_INTERSECTION", gate.name, accessory.name,
                                "Leaf " + i + " broadphase sweep overlaps accessory AABB (includes 20 mm safety margin). " +
                                "Check actual mesh/colliders and PlayMode; this is NOT definitive collision");
                        }
                    }
                }
            }

            if (report.possibleIntersections == 0 && report.visualColliderMismatches == 0 &&
                report.readerAttachmentGapCandidates == 0 && report.incompleteChecks == 0)
                Add(report, "STATIC_BROADPHASE_CLEAR", "", "",
                    "No potential AABB conflicts in inspected scope; NOT Unity PlayMode or independent QA");
            else
                Add(report, "REVIEW_REQUIRED", "", "",
                    "Any positive/incomplete result needs C01-10 integration review and C01-02 independent QA");

            string directory = Path.Combine("Library", "C01Doors13");
            Directory.CreateDirectory(directory);
            string path = Path.Combine(directory, "access_sweep_audit.json");
            File.WriteAllText(path, JsonUtility.ToJson(report, true));
            Debug.Log("[C01-13] gates=" + report.gatesFound + " props=" + report.accessoriesFound +
                " leavesChecked=" + report.movingLeavesChecked + " possible=" +
                report.possibleIntersections + " visualMismatch=" + report.visualColliderMismatches +
                " readerAttachmentGaps=" + report.readerAttachmentGapCandidates +
                " incomplete=" + report.incompleteChecks +
                "; report=" + path);
            EditorUtility.DisplayDialog("C01-13 Gate Access Audit",
                "Possible AABB conflicts: " + report.possibleIntersections +
                "\nVisual/Collider mismatches: " + report.visualColliderMismatches +
                "\nReader attachment gaps: " + report.readerAttachmentGapCandidates +
                "\nIncomplete checks: " + report.incompleteChecks +
                "\nReport: " + path + "\nNo formal QA or PlayMode verdict.", "OK");
        }

        static bool IsAccessory(string name)
        {
            return name.IndexOf("P17-02", StringComparison.OrdinalIgnoreCase) >= 0 ||
                   name.IndexOf("P16-07", StringComparison.OrdinalIgnoreCase) >= 0 ||
                   name.IndexOf("P_Button", StringComparison.OrdinalIgnoreCase) >= 0;
        }

        static Bounds Translate(Bounds source, Vector3 offset)
        {
            return new Bounds(source.center + offset, source.size);
        }

        static bool TryBounds(GameObject go, out Bounds result, out bool usedCollider)
        {
            result = new Bounds();
            bool found = false;
            usedCollider = false;
            foreach (var c in go.GetComponentsInChildren<Collider>(true))
            {
                if (!c.enabled || !c.gameObject.activeInHierarchy) continue;
                if (!found) { result = c.bounds; found = true; }
                else result.Encapsulate(c.bounds);
                usedCollider = true;
            }
            // Conservative broadphase must union BOTH colliders and visible meshes.
            // Otherwise an oversized imported screw hidden by a small root collider is missed.
            foreach (var renderer in go.GetComponentsInChildren<Renderer>(true))
            {
                if (!renderer.enabled || !renderer.gameObject.activeInHierarchy) continue;
                if (!found) { result = renderer.bounds; found = true; }
                else result.Encapsulate(renderer.bounds);
            }
            return found;
        }

        static bool TryRendererBounds(GameObject go, out Bounds bounds)
        {
            bounds = new Bounds();
            bool found = false;
            foreach (var renderer in go.GetComponentsInChildren<Renderer>(true))
            {
                if (!renderer.enabled || !renderer.gameObject.activeInHierarchy) continue;
                if (!found) { bounds = renderer.bounds; found = true; }
                else bounds.Encapsulate(renderer.bounds);
            }
            return found;
        }

        static bool TryColliderBounds(GameObject go, out Bounds bounds)
        {
            bounds = new Bounds();
            bool found = false;
            foreach (var collider in go.GetComponentsInChildren<Collider>(true))
            {
                if (!collider.enabled || !collider.gameObject.activeInHierarchy) continue;
                if (!found) { bounds = collider.bounds; found = true; }
                else bounds.Encapsulate(collider.bounds);
            }
            return found;
        }

        static void CheckReaderAttachment(Evidence report, Transform reader,
            string partName, string supportName)
        {
            Bounds part, support;
            if (!TryNamedRendererBounds(reader, partName, out part) ||
                !TryNamedRendererBounds(reader, supportName, out support))
            {
                Incomplete(report, "READER_ATTACHMENT_MESH_MISSING", reader.name,
                    partName + " / " + supportName +
                    " mesh renderer missing from current import. The native FBX may be stale.");
                return;
            }

            float gap = AabbSeparation(part, support);
            if (gap > 0.00025f)
            {
                report.readerAttachmentGapCandidates++;
                Add(report, "POSSIBLE_READER_ATTACHMENT_GAP", "", reader.name,
                    partName + " / " + supportName +
                    " world-space AABB separation " + (gap * 1000f).ToString("F3") +
                    " mm (>0.250 mm). Verify actual source/FBX triangles; no auto-welding.");
            }
        }

        static bool TryNamedRendererBounds(Transform root, string exactName, out Bounds bounds)
        {
            bounds = new Bounds();
            foreach (var child in root.GetComponentsInChildren<Transform>(true))
            {
                if (!child.gameObject.activeInHierarchy ||
                    !string.Equals(child.name, exactName, StringComparison.OrdinalIgnoreCase))
                    continue;
                return TryRendererBounds(child.gameObject, out bounds);
            }
            return false;
        }

        // For disjoint AABBs the magnitude is a lower bound on true mesh separation.
        // Rotated meshes can yield 0 even when actual triangles are disconnected.
        static float AabbSeparation(Bounds a, Bounds b)
        {
            float dx = Mathf.Max(0f, Mathf.Max(a.min.x - b.max.x, b.min.x - a.max.x));
            float dy = Mathf.Max(0f, Mathf.Max(a.min.y - b.max.y, b.min.y - a.max.y));
            float dz = Mathf.Max(0f, Mathf.Max(a.min.z - b.max.z, b.min.z - a.max.z));
            return new Vector3(dx, dy, dz).magnitude;
        }

        static bool ExtendsOutside(Bounds visual, Bounds collider, float tolerance)
        {
            return visual.min.x < collider.min.x - tolerance ||
                   visual.min.y < collider.min.y - tolerance ||
                   visual.min.z < collider.min.z - tolerance ||
                   visual.max.x > collider.max.x + tolerance ||
                   visual.max.y > collider.max.y + tolerance ||
                   visual.max.z > collider.max.z + tolerance;
        }

        static void Incomplete(Evidence report, string code, string name, string reason)
        {
            report.incompleteChecks++;
            Add(report, "INCOMPLETE_" + code, name, "", reason);
        }

        static void Add(Evidence report, string status, string gate, string accessory, string detail)
        {
            report.findings.Add(new Finding { status = status, gate = gate,
                accessory = accessory, detail = detail });
        }
    }
}
#endif
