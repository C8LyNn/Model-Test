"""C01-12 PASS17 viewer bundler.
Embeds exact GLB binary and actual Blender source-mesh shaded/wireframe PNGs
from this run. No placeholders, synthetic replacement geometry or old FBX.
Three.js code is fetched from CDN when online; PNG comparisons work offline.
"""
import base64
import hashlib
import json
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'C01StandaloneKits'/'FloorCeiling'/'DetailPass17'
REPORT=ROOT/'QA'/'DETAIL_PASS17_NATIVE_SHA256.json'
data=json.loads(REPORT.read_text())
assets={}
for key in ('F01','F02','C01'):
    rec=data['asset_ids'][key]
    p=REPO/rec['native']['glb']['path']
    blob=p.read_bytes()
    assert blob[:4]==b'glTF' and hashlib.sha256(blob).hexdigest()==rec['native']['glb']['sha256']
    previews={}
    for phase in ('before','after'):
        previews[phase]={}
        for title,row in zip(('SHADED','WIREFRAME'),rec['previews'][phase]):
            q=REPO/row['path'];image=q.read_bytes()
            assert image[:8]==b'\x89PNG\r\n\x1a\n'
            assert hashlib.sha256(image).hexdigest()==row['sha256']
            previews[phase][title]='data:image/png;base64,'+base64.b64encode(image).decode('ascii')
    assets[key]={
        'glb_base64':base64.b64encode(blob).decode('ascii'),
        'glb_sha256':rec['native']['glb']['sha256'],
        'previews':previews,
        'triangle_count':28
    }
template=r"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C01-12 PASS17 — authentic GLB & native Blender evidence</title>
<style>
:root{color-scheme:dark;background:#0d1219;color:#e3e8ed;font-family:system-ui,sans-serif}
*{box-sizing:border-box}body{margin:0;max-width:1480px;padding:24px;margin:auto}
h1{font-size:1.35rem;margin:0 0 8px}.intro{color:#9eabb9;line-height:1.6;margin:0 0 14px}
.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:12px 0}
button,select{background:#273343;color:white;border:1px solid #55677d;padding:9px 13px;border-radius:7px;cursor:pointer}
button:focus-visible,select:focus-visible{outline:3px solid #f5b458}
#view{width:100%;height:min(58vh,580px);min-height:280px;background:#131b25;border:1px solid #324053;border-radius:10px;display:block}
#status{font-size:.83rem;color:#91a6b8;margin:12px 0;overflow-wrap:anywhere}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:12px}
figure{margin:0}figure img{width:100%;aspect-ratio:900/660;object-fit:contain;background:#101620;border-radius:8px;border:1px solid #344356}
figcaption{margin:8px 0;color:#b7c8d7;font-size:.85rem}
small{color:#94a8ba}@media(max-width:750px){.compare{grid-template-columns:1fr}body{padding:12px}}
</style>
<script type="importmap">{"imports":{
"three":"https://cdn.jsdelivr.net/npm/three@0.165.0/build/three.module.js",
"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.165.0/examples/jsm/"
}}</script>
</head><body>
<h1>C01-12 — DETAIL PASS17 | F01 · F02 · C01</h1>
<p class="intro">3D: aktualne prawdziwe GLB v004 zapisane z modeli Blender v003; obrazy porównawcze wygenerowano na prawdziwej siatce w Blender Workbench. Siatka geometrycznie niezmieniona — różnice dotyczą materiałów. Bez modeli zastępczych i bez historycznego FBX jako źródła podglądu.</p>
<div class="controls">
<label>Model <select id="model"><option value="F01">F01 — Basic Floor</option><option value="F02">F02 — Marked Floor</option><option value="C01">C01 — Ceiling</option></select></label>
<label><input id="wire" type="checkbox"> Wireframe 3D</label>
<label><input id="spin" type="checkbox" checked> Automatyczny obrót</label>
<button id="reset">Wycentruj</button>
<label>Zdjęcia <select id="shot"><option value="SHADED">Shaded Workbench</option><option value="WIREFRAME">True mesh wireframe</option></select></label>
</div>
<canvas id="view"></canvas>
<div id="status" role="status">Wczytywanie modułu 3D… Statyczne zdjęcia działają bez dostępu do internetu.</div>
<section class="compare">
<figure><figcaption>BEFORE — autentyczny materiał v003</figcaption><img id="before" alt="Autentyczny oryginalny Blender model przed zmianami materiałowymi"></figure>
<figure><figcaption>AFTER — materiał v004, dokładnie ta sama siatka</figcaption><img id="after" alt="Autentyczny model Blender po zmianach materiałowych"></figure>
</section>
<p><small>Wymaga internetu wyłącznie do pobrania biblioteki Three.js; zawarte obrazy i 3 pliki GLB są osadzone w tym HTML. Unity 6 URP: NOT RUN; niezależny finalny C01-02: PENDING. Wcześniejsze UV0 v003 zachowane, brak merge.</small></p>
<script>
const SOURCES=__EMBEDDED_SOURCE_DATA__;
const model=document.getElementById('model');
const shot=document.getElementById('shot');
const status=document.getElementById('status');
function showEvidence(){
  const a=SOURCES[model.value];
  document.getElementById('before').src=a.previews.before[shot.value];
  document.getElementById('after').src=a.previews.after[shot.value];
  status.dataset.sha=a.glb_sha256;
}
model.addEventListener('change',showEvidence);shot.addEventListener('change',showEvidence);
showEvidence();
</script>
<script type="module">
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const sources=JSON.parse(JSON.stringify(SOURCES));
const canvas=document.getElementById('view');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setClearColor(0x131b25);
renderer.outputColorSpace=THREE.SRGBColorSpace;
const scene=new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xffffff,0x2a394b,2.2));
const light=new THREE.DirectionalLight(0xffffff,3.1);
light.position.set(2,4,3);scene.add(light);
const camera=new THREE.PerspectiveCamera(42,1,.01,100);
const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;
const loader=new GLTFLoader();
let active=null,meshes=[];
async function load(id){
  if(active){scene.remove(active);active.traverse(o=>{if(o.isMesh){o.geometry.dispose();if(Array.isArray(o.material))o.material.forEach(m=>m.dispose());else o.material.dispose()}})}
  let data=sources[id].glb_base64;
  let bytes=Uint8Array.from(atob(data),c=>c.charCodeAt(0));
  const gltf=await new Promise((resolve,reject)=>loader.parse(bytes.buffer,'',resolve,reject));
  active=gltf.scene;scene.add(active);
  const box=new THREE.Box3().setFromObject(active);
  const center=box.getCenter(new THREE.Vector3());
  const radius=Math.max(box.getSize(new THREE.Vector3()).length()*.5,.25);
  active.position.sub(center);
  meshes=[];let tris=0;
  active.traverse(o=>{if(o.isMesh){
      o.material=Array.isArray(o.material)?o.material.map(m=>m.clone()):o.material.clone();
      meshes.push(o);tris+=o.geometry.index?o.geometry.index.count/3:o.geometry.attributes.position.count/3;
  }});
  const distance=Math.max(2.2,radius*3.7);
  camera.position.set(distance*.75,distance*.7,distance);
  camera.near=.01;camera.far=100;camera.updateProjectionMatrix();
  controls.target.set(0,0,0);controls.update();
  document.getElementById('wire').dispatchEvent(new Event('change'));
  status.textContent=id+' | real v004 GLB | '+tris+' triangulated GLB faces | SHA256: '+sources[id].glb_sha256;
}
model.addEventListener('change',()=>load(model.value).catch(e=>{status.textContent='Błąd prawdziwego GLB: '+e.message}));
document.getElementById('wire').addEventListener('change',()=>{
  const wire=document.getElementById('wire').checked;
  meshes.forEach(o=>{for(const m of (Array.isArray(o.material)?o.material:[o.material]))m.wireframe=wire})
});
document.getElementById('reset').addEventListener('click',()=>{if(active)load(model.value)});
function loop(){
 requestAnimationFrame(loop);
 const w=canvas.clientWidth,h=canvas.clientHeight;
 if(w&&h&&(canvas.width!==Math.round(w*renderer.getPixelRatio())||canvas.height!==Math.round(h*renderer.getPixelRatio()))){
  renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();
 }
 if(active&&document.getElementById('spin').checked)active.rotation.y+=.003;
 controls.update();renderer.render(scene,camera);
}
loop();load(model.value).catch(e=>{status.textContent='WebGL/GLB niedostępne: '+e.message});
</script></body></html>"""
# script module resolves global lexical const SOURCES from classic <script>
html=template.replace('__EMBEDDED_SOURCE_DATA__',json.dumps(assets,separators=(',',':')))
target=ROOT/'C01_12_DETAIL_PASS17_REAL_GLB_INTERACTIVE.html'
target.write_text(html,encoding='utf-8')
print(json.dumps({'viewer_file':str(target.relative_to(REPO)),
                  'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                  'bytes':target.stat().st_size,
                  'glbs':{k:v['glb_sha256'] for k,v in assets.items()}},indent=2))
