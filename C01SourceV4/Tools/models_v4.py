"""Editable prism models, retaining original C01 prop geometry where suitable."""
import json
from pathlib import Path
from ship_geometry import ccw
ROOT=Path(__file__).resolve().parents[1]
def part(role,poly,a,b):return dict(role=role,outline=[v for p in ccw(poly) for v in p],y0=a,y1=b)
def box(role,lo,hi):return part(role,[[lo[0],lo[2]],[hi[0],lo[2]],[hi[0],hi[2]],[lo[0],hi[2]]],lo[1],hi[1])
def make_models():
    old=json.loads((ROOT/'Reference/ship_v3.json').read_text(encoding='utf-8'))
    models={m['id']:m for m in old['modules'] if m['id'].startswith('P_')}
    def add(mid,parts):models[mid]=dict(id=mid,parts=parts)
    add('P_Button',[box('DARK',[0,0,0],[.22,.28,.09]),box('SCREEN',[.02,.02,.09],[.20,.26,.105])])
    add('P_Toilet',[box('WHITE',[.08,0,.08],[.52,.40,.65]),box('WHITE',[0,.40,0],[.60,.48,.80]),box('METAL',[.05,.48,.67],[.55,.80,.80])])
    add('P_Sink',[box('METAL',[.08,0,.08],[.22,.88,.47]),box('WHITE',[0,.88,0],[1.2,1.0,.55]),box('METAL',[.88,1,.40],[.96,1.23,.48])])
    add('P_Shower',[box('WHITE',[0,0,0],[1.2,.10,1.2]),box('GLASS',[0,.10,0],[.04,2.2,1.2]),box('GLASS',[.04,.10,1.16],[1.2,2.2,1.2]),box('METAL',[.55,1.9,1.10],[.75,2.0,1.16])])
    add('P_Treadmill',[box('METAL',[0,0,0],[2.4,.18,1.2]),box('DARK',[.1,.18,.1],[2.2,.25,1.1]),box('METAL',[1.95,.25,.1],[2.1,1.5,.23]),box('METAL',[1.95,.25,.97],[2.1,1.5,1.1]),box('SCREEN',[1.8,1.5,.15],[2.2,1.65,1.05])])
    add('P_Rowing',[box('METAL',[0,0,0],[3,.18,1]),box('DARK',[0,.18,0],[.7,1.1,1]),box('BED',[1.2,.18,.15],[1.8,.50,.85]),box('METAL',[.7,.55,.45],[1.4,.60,.55])])
    add('P_Pullup',[box('METAL',[0,0,0],[3,.12,1.4]),box('METAL',[0,.12,0],[.15,3.2,.15]),box('METAL',[2.85,.12,0],[3,3.2,.15]),box('ACCENT',[.15,3.05,0],[2.85,3.2,.15])])
    add('P_Weights',[box('METAL',[0,0,0],[2.4,.12,.8]),box('DARK',[0,.12,.15],[.15,1.4,.65]),box('DARK',[2.25,.12,.15],[2.4,1.4,.65]),box('METAL',[.15,.60,.1],[2.25,.72,.7]),box('ACCENT',[.25,.72,.2],[2.15,.95,.6])])
    add('P_ExamScanner',[box('METAL',[0,0,0],[3,.2,2.4]),box('WHITE',[0,.2,.1],[.25,3.2,2.3]),box('WHITE',[2.75,.2,.1],[3,3.2,2.3]),box('SCREEN',[.25,2.9,.1],[2.75,3.2,2.3]),box('BED',[.4,.2,.4],[2.6,.9,2.0])])
    add('P_Analyser',[box('WHITE',[0,0,0],[2.2,1.4,1]),box('SCREEN',[.15,1.4,.1],[1.4,1.9,.9]),box('METAL',[1.5,1.4,.1],[2.05,1.7,.8])])
    add('P_ExamChair',[box('METAL',[.2,0,.2],[.8,.65,.8]),box('BED',[0,.65,0],[1,.80,1]),box('BED',[0,.8,.85],[1,1.75,1])])
    add('P_Purifier',[box('METAL',[0,0,0],[4,.2,3]),box('WATER',[.2,.2,.2],[2.2,4.8,2.8]),box('WHITE',[2.4,.2,.2],[3.8,3.5,2.8]),box('SCREEN',[2.5,3.5,.4],[3.7,3.7,2.4])])
    add('P_ReactorLarge',[box('METAL',[0,0,0],[5,.3,5]),box('DARK',[.4,.3,.4],[4.6,8,4.6]),box('SCREEN',[1.4,8,1.4],[3.6,8.4,3.6]),box('ACCENT',[1.5,1.0,.25],[3.5,6,.4])])
    add('P_Plant',[box('METAL',[0,0,0],[1.4,.45,1.4]),box('SOIL',[.1,.45,.1],[1.3,.55,1.3]),box('PLANT',[.6,.55,.6],[.8,1.8,.8]),box('PLANT',[.15,1.0,.35],[.6,1.2,1.05]),box('PLANT',[.8,1.3,.35],[1.25,1.5,1.05])])
    shuttle=[box('METAL',[0,.4,0],[9,2.2,4]),part('HULL',[[9,0],[11,1.4],[11,2.6],[9,4]],.4,2.2),box('GLASS',[6,2.2,.7],[8.7,3.1,3.3]),box('DARK',[.4,0,.4],[1.1,.4,1.1]),box('DARK',[.4,0,2.9],[1.1,.4,3.6]),box('DARK',[7.7,0,.4],[8.4,.4,1.1]),box('DARK',[7.7,0,2.9],[8.4,.4,3.6]),box('THRUST',[-.2,.8,.7],[0,1.9,1.5]),box('THRUST',[-.2,.8,2.5],[0,1.9,3.3])]
    add('P_Shuttle',shuttle)
    return models

PALETTE={'FLOOR':[.22,.34,.42,1],'TRIM':[.4,.51,.56,1],'WALL':[.13,.21,.28,1],'PANEL':[.23,.34,.43,1],
 'HULL':[.075,.11,.15,1],'METAL':[.32,.4,.47,1],'DARK':[.07,.12,.17,1],'BED':[.22,.34,.4,1],
 'LIGHT':[.69,.77,.77,1],'WHITE':[.7,.8,.82,1],'ACCENT':[.84,.48,.13,1],'SCREEN':[.08,.7,.84,1],
 'GLASS':[.2,.59,.72,.38],'CRATE':[.38,.31,.2,1],'ENGINE':[.21,.28,.34,1],'THRUST':[.9,.44,.12,1],
 'PLANT':[.15,.48,.2,1],'SOIL':[.14,.10,.06,1],'WATER':[.12,.43,.58,1],
 'F_CABIN':[.47,.43,.31,1],'F_BATH':[.42,.55,.57,1],'F_GYM':[.3,.42,.3,1],'F_LAB':[.4,.32,.48,1],
 'F_MED':[.5,.35,.38,1],'F_CARGO':[.48,.4,.24,1],'F_CONTROL':[.42,.31,.22,1],'F_TECH':[.25,.4,.46,1],
 'F_ENGINE':[.22,.28,.31,1],'F_PURIFY':[.2,.42,.45,1],'F_HANGAR':[.30,.35,.4,1],'F_HYDRO':[.21,.36,.22,1]}

