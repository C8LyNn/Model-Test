// C01-13 W21: QA-only physical native FBX staging, fail-closed and transactional. Never modifies the live ship
// nor adds D01/D02 to the P15-P19 set of 36 production props.
#if UNITY_EDITOR
using System;
using System.IO;
using System.Security.Cryptography;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace C01.Doors.Access
{
    public static class LegacyDoorNativeImportGate
    {
        const string Source = "C01-13_PASS18_Transport/Native/";
        const string Staging = "Assets/C01DoorsAccess13/QA_Candidates/PASS19_Native/";
        const string Output = "Library/C01Doors13/legacy_pass19_native_import.json";
        // SHA-256 of ACTUAL Blender 4.0.2 exported FBX, NOT git blob hash.
        static readonly string[] Names = { "D01_DETAIL_PASS18.fbx", "D02_DETAIL_PASS18.fbx" };
        static readonly string[] ExpectedSha = {
            "b1300e771ad8178c36997d7333fc669c835ee814a3ef6035c00247567e5e7e68",
            "290943f58904e8cb4097dd8c2237d8694b7c5b7b86fdcdd070d1fb1fa35de591"
        };
        static readonly int[] ExpectedMeshes = { 33, 34 };
        static readonly int[] ExpectedTriangles = { 1468, 1248 };

        [Serializable] class Entry
        {
            public string name, sha256, assetPath, status, error;
            public int meshes, triangles, missingUv0, missingNormals;
        }
        [Serializable] class Evidence
        {
            public string scope = "QA-ONLY LEGACY D01/D02, NOT 36 P15-P19 ASSETS";
            public string utc, unityVersion, status;
            public List<Entry> entries = new List<Entry>();
        }
        [MenuItem("Tools/C01/Doors & Access/QA Only/Stage PASS18 Native D01-D02")]
        public static void StageNativeForQAOnly()
        {
            var evidence = new Evidence {
                utc = DateTime.UtcNow.ToString("o"),
                unityVersion = Application.unityVersion,
                status = "HOLD"
            };
            // Track files created by THIS invocation only. Existing QA imports are
            // never overwritten or deleted; this is a candidate staging tool.
            var newlyStaged = new List<string>();
            string activeFile = "preflight";
            try
            {
                // Fail closed BEFORE writing anything to Assets.
                for (int i = 0; i < Names.Length; i++)
                {
                    string name = Names[i];
                    string file = Path.Combine(Source, name);
                    if (!File.Exists(file)) throw new IOException("Missing hydrated FBX: " + file);
                    byte[] bytes = File.ReadAllBytes(file);
                    byte[] magic = System.Text.Encoding.ASCII.GetBytes("Kaydara FBX Binary");
                    if (bytes.Length < 27) throw new IOException("Too short: " + file);
                    for (int k = 0; k < magic.Length; k++)
                        if (bytes[k] != magic[k])
                            throw new IOException("Not binary FBX; possible Git-LFS pointer: " + file);
                    string digest;
                    using (var sha = SHA256.Create())
                        digest = BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
                    if (digest != ExpectedSha[i])
                        throw new IOException("STALE OR INVALID FBX " + name + " SHA256=" + digest);
                    evidence.entries.Add(new Entry { name=name, sha256=digest, status="SHA_OK" });
                }

                // ALSO reject stale files already occupying the isolated QA folder.
                // This validation covers BOTH assets before any copy/import writes.
                for (int i = 0; i < Names.Length; i++)
                {
                    string staged = Staging + Names[i];
                    if (!File.Exists(staged)) continue;
                    string existingSha;
                    using (var stream = File.OpenRead(staged))
                    using (var sha = SHA256.Create())
                        existingSha = BitConverter.ToString(sha.ComputeHash(stream))
                            .Replace("-", "").ToLowerInvariant();
                    if (existingSha != ExpectedSha[i])
                        throw new IOException("STALE_EXISTING_QA_FILE: " + staged +
                            " SHA256=" + existingSha + "; quarantine must be reconciled manually.");
                }

                Directory.CreateDirectory(Staging);
                for (int i = 0; i < Names.Length; i++)
                {
                    Entry e = evidence.entries[i];
                    activeFile = Names[i];
                    string staged = Staging + Names[i];
                    if (!File.Exists(staged))
                    {
                        // Enlist before writing so even a partial copy is rolled back.
                        newlyStaged.Add(staged);
                        File.Copy(Path.Combine(Source, Names[i]), staged, false);
                    }
                    AssetDatabase.ImportAsset(staged, ImportAssetOptions.ForceSynchronousImport);
                    e.assetPath = staged;
                    if (!(AssetImporter.GetAtPath(staged) is ModelImporter))
                        throw new InvalidOperationException("Expected ModelImporter for " + staged);
                    GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(staged);
                    if (model == null) throw new InvalidOperationException("Null imported FBX: " + staged);
                    MeshFilter[] filters = model.GetComponentsInChildren<MeshFilter>(true);
                    e.meshes = filters.Length;
                    foreach (MeshFilter mf in filters)
                    {
                        Mesh mesh = mf.sharedMesh;
                        if (mesh == null) throw new InvalidOperationException("Null FBX mesh " + mf.name);
                        if (!mesh.HasVertexAttribute(VertexAttribute.TexCoord0)) e.missingUv0++;
                        if (!mesh.HasVertexAttribute(VertexAttribute.Normal)) e.missingNormals++;
                        for (int j = 0; j < mesh.subMeshCount; j++)
                        {
                            if (mesh.GetTopology(j) != MeshTopology.Triangles)
                                throw new InvalidOperationException("Non-triangle FBX submesh: " + mf.name);
                            long indexCount = (long)mesh.GetIndexCount(j);
                            if (indexCount % 3 != 0)
                                throw new InvalidOperationException("Non-triangle index count: " + mf.name);
                            e.triangles += checked((int)(indexCount / 3));
                        }
                    }
                    if (e.meshes != ExpectedMeshes[i] || e.triangles != ExpectedTriangles[i] ||
                        e.missingUv0 != 0 || e.missingNormals != 0)
                        throw new InvalidOperationException("Mesh count / triangle count / UV0 / normals mismatch: " +
                            e.name + " meshes=" + e.meshes + " triangles=" + e.triangles +
                            " missing UV0=" + e.missingUv0 + " missing normals=" + e.missingNormals);
                    e.status = "QA_STAGED_EXACT_NATIVE_IMPORT_GEOMETRY_PASS";
                }
                evidence.status = "QA_ONLY_PREFLIGHT_PASS_NO_PLAYMODE_NO_RELEASE_APPROVAL";
            }
            catch (Exception ex)
            {
                evidence.status = "HOLD";
                evidence.entries.Add(new Entry { name=activeFile, status="HOLD",
                    error=ex.ToString() });
                // Roll back ONLY newly copied candidate assets; never touch an asset
                // that was present before this QA invocation, nor any ship prefab.
                for (int i = newlyStaged.Count - 1; i >= 0; i--)
                {
                    string staged = newlyStaged[i];
                    try
                    {
                        if (!AssetDatabase.DeleteAsset(staged))
                        {
                            if (File.Exists(staged)) File.Delete(staged);
                            if (File.Exists(staged + ".meta")) File.Delete(staged + ".meta");
                        }
                    }
                    catch (Exception rollbackError)
                    {
                        evidence.entries.Add(new Entry { name=staged,
                            status="ROLLBACK_FAILED_MANUAL_CLEANUP_REQUIRED",
                            error=rollbackError.ToString() });
                        Debug.LogError("[C01-13 W21] QA-only rollback failed: " + rollbackError);
                    }
                }
                AssetDatabase.Refresh();
                Debug.LogError("[C01-13 W21] Import gate HOLD; new candidates rolled back: " + ex);
            }
            finally
            {
                Directory.CreateDirectory(Path.GetDirectoryName(Output));
                File.WriteAllText(Output, JsonUtility.ToJson(evidence, true));
                Debug.Log("[C01-13 W19] " + evidence.status + " " + Output +
                    " — NOT a Unity PlayMode or independent C01-02 acceptance");
            }
        }
    }
}
#endif
