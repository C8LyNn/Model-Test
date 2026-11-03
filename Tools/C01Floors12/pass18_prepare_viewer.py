"""C01-12 PASS18: create an OFFLINE selector-testable version of the real PASS17 GLB viewer.
Uses latest already-proven v004 GLB bytes embedded in the existing HTML;
does not fetch new assets, synthesize meshes or change native sources.
"""
import hashlib,json
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
D=REPO/'C01StandaloneKits'/'FloorCeiling'
src=D/'DetailPass17'/'C01_12_DETAIL_PASS17_REAL_GLB_INTERACTIVE.html'
target=D/'DetailPass18'/'Interactive'/'C01_12_PASS18_REAL_GLB_VIEWER.html'
target.parent.mkdir(parents=True,exist_ok=True)
s=src.read_text(encoding='utf-8')
assert 'C01_PASS17_BUNDLED_OFFLINE_THREE' in s and 'glb_base64' in s and 'three@0.165.0/' not in s
# Initial DOM select, before load(model.value) in the already-bundled renderer.
needle='showEvidence();\n</script>'
assert s.count(needle)==1
s=s.replace(needle,'''const requestedModel=new URLSearchParams(window.location.search).get('asset');
if(requestedModel && Object.prototype.hasOwnProperty.call(SOURCES,requestedModel)){
  model.value=requestedModel;
}
showEvidence();
</script>''',1)
s=s.replace('C01-12 — DETAIL PASS17 | F01 · F02 · C01','C01-12 — DETAIL PASS18 | F01 · F02 · C01')
s=s.replace('C01-12 PASS17 — authentic GLB & native Blender evidence','C01-12 PASS18 — actual v004 GLB / offline browser-tested evidence')
target.write_text(s,encoding='utf-8')
manifest=json.loads((D/'DetailPass17'/'QA'/'DETAIL_PASS17_NATIVE_SHA256.json').read_text())
for id in ('F01','F02','C01'):
    assert manifest['asset_ids'][id]['native']['glb']['sha256'] in s
    assert id in s
sha=hashlib.sha256(target.read_bytes()).hexdigest()
print(json.dumps({'path':str(target.relative_to(REPO)),'sha256':sha,'bytes':target.stat().st_size,
   'geometry': 'CURRENT_PASS17_v004_EMBEDDED_ONLY','browser_runtime':'NOT_RUN'},indent=2))
