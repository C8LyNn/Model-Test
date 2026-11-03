// Unity PlayMode imported-source smoke only. Not full authored wheel/hinge/PhysX approval.
using System.Collections;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
namespace C01.InteriorProps.Pass29 {
 public sealed class W29Play {
  [UnityTest]public IEnumerator RealFBXMeshAndUrpMaterialSmoke() {
   foreach(string id in new[]{"W01","F01","C01","P16-01","P17-02","P18-01","P19-03","P15-03","P18-03"}) {
    var p=Resources.Load<GameObject>("W29QA/"+id);Assert.NotNull(p);
    var g=Object.Instantiate(p);
    try {
     yield return null;
     var ms=g.GetComponentsInChildren<MeshFilter>(true);
     Assert.Greater(ms.Length,0);Assert.IsTrue(ms.All(f=>f.sharedMesh!=null));
     var rs=g.GetComponentsInChildren<MeshRenderer>(true);
     Assert.Greater(rs.Length,0);
     foreach(var r in rs)foreach(var m in r.sharedMaterials){
      Assert.NotNull(m);Assert.IsTrue(m.shader.name.StartsWith("Universal Render Pipeline/"));
     }
    }finally{if(g!=null)Object.Destroy(g);}
   }
  }
 }
}
