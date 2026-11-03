#if UNITY_EDITOR
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

namespace C01.Cargo
{
    /// <summary>
    /// W25 isolated P18-05 ONLY. Does not iterate P18-04/06/07, repack or
    /// export any BLEND/FBX. Full SHA256 of ORIGINAL 41388-byte binary FBX
    /// verified before any prefab/material writes. Licensed Unity Editor NOT_RUN.
    /// </summary>
    public static class BuildPass25P1805Only
    {
        private const string Root = "Assets/C01InteriorProps/C01-18-Wave02";
        private const string OriginalFBX = Root + "/Models/P18-05.fbx";
        private const string ImmutableSha256 = "58e33516ead13e35e8a48228045c67bd53d6caf8de01883a11625fa2961957e5";
        private const string MaterialSubdir = Root + "/Materials/W25P1805";

        [MenuItem("Tools/C01/Cargo/W25 Build ONLY P18-05 Released-Lid Prefab")]
        public static void Build()
        {
            VerifyOriginalPhysicalFBXBeforeAnyWrites();
            GameObject source = AssetDatabase.LoadAssetAtPath<GameObject>(OriginalFBX);
            if (source == null)
                throw new InvalidOperationException("P18-05 original signed FBX was not imported as an actual Unity model");

            GameObject root = new GameObject("P18_05");
            try
            {
                GameObject imported = (GameObject)PrefabUtility.InstantiatePrefab(source);
                if (imported == null)
                    throw new InvalidOperationException("P18-05 signed model prefab could not be instantiated");
                // Only on the isolated P18-05 copied instance: imported FBX asset
                // itself NEVER changes. Unpack permits three original handle nodes
                // to be reparented to the actual lid hinge while preserving rest.
                if (PrefabUtility.IsAnyPrefabInstanceRoot(imported))
                    PrefabUtility.UnpackPrefabInstance(imported,
                        PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                imported.name = "P18-05_SignedFBX";
                imported.transform.SetParent(root.transform, false);
                imported.transform.localPosition = Vector3.zero;
                imported.transform.localRotation = Quaternion.identity;
                imported.transform.localScale = Vector3.one;

                var meshes = root.GetComponentsInChildren<MeshFilter>(true);
                int triangles = 0;
                if (meshes.Length != 10)
                    throw new InvalidOperationException("P18-05 requires exactly TEN original signed native mesh parts");
                EnsureFolder(Root, "Materials");
                EnsureFolder(Root + "/Materials", "W25P1805");

                foreach (MeshFilter mf in meshes)
                {
                    if (mf.sharedMesh == null)
                        throw new InvalidOperationException("Missing native P18-05 real FBX mesh: " + mf.name);
                    Mesh mesh = mf.sharedMesh;
                    triangles += mesh.triangles.Length / 3;
                    if (mesh.normals.Length != mesh.vertexCount ||
                        mesh.uv.Length != mesh.vertexCount)
                        throw new InvalidOperationException("P18-05 original imported normals or UV mismatch: " + mf.name);
                    MeshRenderer renderer = mf.GetComponent<MeshRenderer>();
                    if (renderer == null)
                        throw new InvalidOperationException("P18-05 original visible renderer missing: " + mf.name);
                    renderer.sharedMaterial = GetP1805Material(mf.name);

                    if (mf.name == "Case_Bottom" || mf.name == "Case_Lid")
                    {
                        var bc = mf.GetComponent<BoxCollider>() ?? mf.gameObject.AddComponent<BoxCollider>();
                        bc.center = mesh.bounds.center;
                        bc.size = mesh.bounds.size;
                        bc.isTrigger = false;
                    }
                    else if (mf.GetComponent<Collider>() != null)
                        throw new InvalidOperationException("P18-05 only Case_Bottom/Case_Lid can have solid colliders");
                }
                if (triangles != 120 ||
                    root.GetComponentsInChildren<Collider>(true).Length != 2)
                    throw new InvalidOperationException("P18-05 mesh/triangle/collider authenticity gate failed");

                Transform hinge = Find(root.transform, "Lid_HingePivot");
                Transform lid = Find(root.transform, "Case_Lid");
                Transform accent = Find(root.transform, "Lid_Accent");
                Transform latchL = Find(root.transform, "Front_Latch_L");
                Transform latchR = Find(root.transform, "Front_Latch_R");
                if (hinge == null || lid == null || accent == null ||
                    latchL == null || latchR == null ||
                    lid.parent != hinge || accent.parent != hinge)
                    throw new InvalidOperationException("P18-05 original signed hinge/lid/lock part hierarchy invalid");

                string[] handles = { "Carry_Handle_Rail", "Carry_Handle_Stem_L", "Carry_Handle_Stem_R" };
                var movingHandles = new Transform[3];
                for (int i = 0; i < handles.Length; i++)
                {
                    Transform obj = Find(root.transform, handles[i]);
                    if (obj == null || obj.GetComponent<MeshRenderer>() == null)
                        throw new InvalidOperationException("P18-05 expected signed original handle mesh " + handles[i]);
                    Vector3 restWorldPos = obj.position;
                    Quaternion restWorldRotation = obj.rotation;
                    obj.SetParent(hinge, true); // original mesh/UV/material unchanged.
                    if (Vector3.Distance(restWorldPos, obj.position) > 0.0001f ||
                        Quaternion.Angle(restWorldRotation, obj.rotation) > 0.1f)
                        throw new InvalidOperationException("P18-05 lid-handle reparent changed signed CLOSED rest pose");
                    movingHandles[i] = obj;
                }
                var gate = root.AddComponent<C01EquipmentCaseLatchGate>();
                gate.Configure(hinge, latchL, latchR, lid.GetComponent<BoxCollider>(), movingHandles);
                if (!gate.IsLocked || gate.IsUnlocked || gate.IsVisibleLatchReleased)
                    throw new InvalidOperationException("P18-05 original prefab MUST initialize lid LOCKED with visible engaged latches");
                var rigid = root.AddComponent<Rigidbody>();
                rigid.isKinematic = true;
                rigid.useGravity = false;
                rigid.interpolation = RigidbodyInterpolation.Interpolate;

                EnsureFolder(Root, "Prefabs");
                const string prefabPath = Root + "/Prefabs/P18-05.prefab";
                if (PrefabUtility.SaveAsPrefabAsset(root, prefabPath) == null)
                    throw new InvalidOperationException("P18-05 W25 isolated real FBX prefab failed to persist");
                AssetDatabase.SaveAssets();
                AssetDatabase.Refresh();
                Debug.Log("C01_18_W25_P1805_SIGNED_UNIQUE_PREFAB_SOURCE_READY: original FBX SHA " +
                          ImmutableSha256 + "; 10 meshes/120T/2 colliders; 8mm visible latch + 2mm hinge lift; UNITY EDITOR TEST PENDING");
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        private static void VerifyOriginalPhysicalFBXBeforeAnyWrites()
        {
            if (!File.Exists(OriginalFBX))
                throw new FileNotFoundException("P18-05 ORIGINAL hydrated physical FBX missing", OriginalFBX);
            using (var f = File.OpenRead(OriginalFBX))
            using (var sha = SHA256.Create())
            {
                if (f.Length != 41388)
                    throw new InvalidOperationException("P18-05 expected 41388 original binary FBX bytes, Git LFS pointer forbidden");
                string digest = BitConverter.ToString(sha.ComputeHash(f)).Replace("-", "").ToLowerInvariant();
                if (!string.Equals(digest, ImmutableSha256, StringComparison.Ordinal))
                    throw new InvalidOperationException("P18-05 FULL FBX SHA256 incorrect, refusing ANY prefab writes");
            }
        }

        private static Transform Find(Transform root, string name)
        {
            if (root.name == name) return root;
            foreach (Transform c in root)
            {
                Transform hit = Find(c, name);
                if (hit != null) return hit;
            }
            return null;
        }

        private static void EnsureFolder(string parent, string child)
        {
            string path = parent + "/" + child;
            if (!AssetDatabase.IsValidFolder(path))
                AssetDatabase.CreateFolder(parent, child);
        }

        private static Material GetP1805Material(string name)
        {
            string role = name.Contains("Lid_Accent") || name.StartsWith("Front_Latch_")
                ? "CAUTION"
                : name == "Case_Bottom" ? "STEEL"
                : name.StartsWith("Rubber_") || name == "Carry_Handle_Rail"
                ? "GASKET" : "DARK";
            string path = MaterialSubdir + "/P18-05_" + role + ".mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m != null) return m;
            Shader urp = Shader.Find("Universal Render Pipeline/Lit");
            if (urp == null) throw new InvalidOperationException("Real Unity6 URP Lit shader is missing");
            m = new Material(urp);
            Color color = role == "CAUTION" ? new Color(.94f,.52f,.13f) :
                role == "STEEL" ? new Color(.31f,.39f,.46f) :
                role == "GASKET" ? new Color(.11f,.15f,.19f) :
                new Color(.07f,.11f,.16f);
            m.SetColor("_BaseColor", color);
            m.SetFloat("_Metallic", role == "GASKET" ? .12f : .55f);
            m.SetFloat("_Smoothness", .34f);
            AssetDatabase.CreateAsset(m, path);
            return m;
        }
    }
}
#endif
