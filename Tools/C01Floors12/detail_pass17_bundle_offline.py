"""C01-12 PASS17 offline HTML packer.
Extracts the REAL already-generated inline-GLB viewer module, then embeds
a locally esbuild-bundled Three.js implementation with its MIT license.
No vendor geometry, remote scripts, old FBX, or proxy models.
Usage:
  python detail_pass17_bundle_offline.py extract /tmp/build-dir
  esbuild /tmp/build-dir/viewer_client.mjs --bundle --format=iife ...
  python detail_pass17_bundle_offline.py embed /tmp/build-dir
"""
import pathlib, re, sys

ROOT=pathlib.Path(__file__).resolve().parents[2]
HTML=ROOT/'C01StandaloneKits/FloorCeiling/DetailPass17/C01_12_DETAIL_PASS17_REAL_GLB_INTERACTIVE.html'
assert len(sys.argv)==3 and sys.argv[1] in {'extract','embed'},sys.argv
mode=sys.argv[1]
tmp=pathlib.Path(sys.argv[2]).resolve()
tmp.mkdir(parents=True,exist_ok=True)
html=HTML.read_text(encoding='utf-8')
pattern=r'<script type="module">([\s\S]*?)</script>'
module=re.search(pattern,html)
assert module,'Expected unbundled Three module present in real viewer generator'
if mode=='extract':
    (tmp/'viewer_client.mjs').write_text(module.group(1),encoding='utf-8')
    print('Extracted REAL GLB viewer client, no proxy mesh')
else:
    bundle=(tmp/'viewer_bundle.js').read_text(encoding='utf-8')
    license=(tmp/'node_modules/three/LICENSE').read_text(encoding='utf-8')
    assert len(bundle)>100000
    assert 'MIT License' in license
    importmap=re.search(r'<script type="importmap">[\s\S]*?</script>',html)
    assert importmap
    html=html.replace(importmap.group(0),'')
    html=html.replace(module.group(0),
        '<script>/* C01_PASS17_BUNDLED_OFFLINE_THREE */\n'+bundle.replace('</script>','<\\/script>')+'\n</script>')
    html=html.replace('Wymaga internetu wyłącznie do pobrania biblioteki Three.js;','Biblioteka Three.js dołączona bezpośrednio — podgląd działa offline;')
    html=html.replace('Statyczne zdjęcia działają bez dostępu do internetu.','Podgląd działa offline, bez CDN.')
    html=html.replace('</body>', '<!-- THREE.JS MIT LICENSE\n'+license.replace('-->','-- >')+'\n--></body>')
    assert 'three@0.165.0/' not in html
    assert '<script type="module">' not in html
    assert 'C01_PASS17_BUNDLED_OFFLINE_THREE' in html
    assert all(s in html for s in ('glb_base64','F01','F02','C01'))
    HTML.write_text(html,encoding='utf-8')
    print('OFFLINE HTML READY:',str(HTML.relative_to(ROOT)),'bytes',HTML.stat().st_size)
