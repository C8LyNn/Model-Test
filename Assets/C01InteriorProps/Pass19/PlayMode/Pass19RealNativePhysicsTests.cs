// WAVE19 — actual Unity Test Framework PlayMode, after EditMode has generated QA prefabs.
// No fabricated test geometry; instantiate ONLY imported real FBX-backed QA prefabs.
using System.Collections;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace C01.InteriorProps.Pass19
{
    public sealed class RealNativePhysicsTests
    {
        static readonly string[] Ids={"P16-01","P17-02","P18-01"};

        [UnityTest]
        public IEnumerator RealThreeNativePrefabsHaveVisibleMeshesAndRaycastableColliders()
        {
            var created=new System.Collections.Generic.List<GameObject>();
            try
            {
                for(int i=0;i<Ids.Length;i++)
                {
                    string id=Ids[i];
                    var prefab=Resources.Load<GameObject>("Pass19QA/"+id);
                    Assert.NotNull(prefab,"EditMode must generate genuine prefab before PlayMode: "+id);
                    var go=Object.Instantiate(prefab);
                    created.Add(go);
                    go.transform.position=new Vector3((i-1)*4f,0f,0f);
                    var filters=go.GetComponentsInChildren<MeshFilter>(true);
                    Assert.Greater(filters.Length,0,"No real FBX MeshFilter: "+id);
                    Assert.IsTrue(filters.All(f=>f.sharedMesh!=null),"Missing native mesh on "+id);
                    Assert.Greater(go.GetComponentsInChildren<MeshRenderer>(true).Length,0);
                    var collider=go.GetComponent<BoxCollider>();
                    Assert.NotNull(collider,"Missing QA-only native-bounds collider on "+id);
                    Assert.Greater(collider.bounds.size.sqrMagnitude,0);
                    yield return new WaitForFixedUpdate();
                    Physics.SyncTransforms();
                    var center=collider.bounds.center;
                    float above=collider.bounds.extents.y+2f;
                    var ray=new Ray(center+Vector3.up*above,Vector3.down);
                    var hits=Physics.RaycastAll(ray,above*2f+1f,~0,QueryTriggerInteraction.Collide);
                    Assert.IsTrue(hits.Any(h=>h.collider==collider),
                        "PhysX ray failed to hit the real native-bounds QA collider "+id);
                }
            }
            finally
            {
                foreach(var go in created)if(go!=null)Object.Destroy(go);
            }
        }

        [UnityTest]
        public IEnumerator NativeLightingComponentExistsAndImportedRendererMaterialsAreNonNull()
        {
            var prefab=Resources.Load<GameObject>("Pass19QA/P16-01");
            Assert.NotNull(prefab);
            var root=Object.Instantiate(prefab);
            try
            {
                yield return null;
                Assert.Greater(root.GetComponentsInChildren<Light>(true).Length,0);
                var renderers=root.GetComponentsInChildren<MeshRenderer>(true);
                Assert.Greater(renderers.Length,0);
                foreach(var renderer in renderers)
                    foreach(var material in renderer.sharedMaterials)
                    {
                        Assert.NotNull(material);
                        Assert.IsTrue(material.shader.name.StartsWith("Universal Render Pipeline/"),
                            "Material is not URP: "+material.name);
                    }
            }
            finally { if(root!=null)Object.Destroy(root); }
        }
    }
}
