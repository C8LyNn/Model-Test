"""Rzut poziomu 1 z danych montażowych, nie zrzut ekranu Unity."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

root=Path(__file__).resolve().parent.parent
data=json.loads((root/'C01SourceV77/Data/ship_v77.json').read_text(encoding='utf8'))
zones={z['id']:z for z in data['zones']}
names={'L1_GYM':'TRENING','L1_LAB':'LABORATORIUM I SYSTEMY ŻYCIA','L1_MED':'MEDYCZNY',
       'L1_TECH':'TECHNICZNY','L1_ENGINE_CONTROL':'MASZYNOWNIA I STEROWANIE','L1_CARGO':'ŁADOWNIA I HANGAR'}
colors={'L1_GYM':'#355d4c','L1_LAB':'#305561','L1_MED':'#60474e','L1_TECH':'#405262','L1_ENGINE_CONTROL':'#594d3e','L1_CARGO':'#505b68'}
im=Image.new('RGB',(1800,800),'#101c2a');d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17);title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',34)
d.text((55,25),'POZIOM 1 — DWUPOKŁADOWY STATEK',font=title,fill='#edf4f7')
d.text((55,72),'Schemat na podstawie danych sceny • kratka 3 m • nowe funkcje na zachowanych pokładach',font=small,fill='#aec8d5')
scale=9.3;ox=190;oz=145
def xy(x,z):return ox+x*scale,oz+(75-z)*scale
for ident,label in names.items():
    z=zones[ident];x0,x1,z0,z1=z['bounds'];a=xy(x0,z1);b=xy(x1,z0)
    d.rectangle((*a,*b),fill=colors[ident],outline='#8299a7',width=2)
    box=d.textbbox((0,0),label,font=small);d.text(((a[0]+b[0]-(box[2]-box[0]))/2,(a[1]+b[1])/2-9),label,font=small,fill='#f1f6f6')
for side in ('N','S'):
    for z in data['zones']:
        if z['deck']!=1 or z['kind'] not in ('cabin','support') or f'L1_{side}_' not in z['id']:continue
        x0,x1,z0,z1=z['bounds'];a=xy(x0,z1);b=xy(x1,z0)
        d.rectangle((*a,*b),fill='#223848',outline='#5b7887',width=1)
        d.text((a[0]+5,a[1]+6),'KAJUTA' if z['kind']=='cabin' else 'ZAPLECZE',font=small,fill='#abc2ca')
a,b=xy(0,45),xy(126,42);d.rectangle((*a,*b),fill='#477389',outline='#91aab4',width=2)
d.text((xy(54,44)[0],xy(54,44)[1]-10),'KORYTARZ',font=small,fill='white')
legend={'P_Reactor':('#ffbb62','REAKTOR'),'P_Purifier_ROOM3':('#83dbef','OCZYSZCZANIE'),'P_Plant':('#8ce193','UPRAWY'),'P_Shuttle_ROOM3':('#ffe591','PROM')}
for p in data['placements']:
    if p['model'] not in legend or p['deck']!=1:continue
    x,z=xy(p['x']+.7,p['z']+.7);color,_=legend[p['model']];d.ellipse((x-4,z-4,x+4,z+4),fill=color)
d.line((xy(111,27),xy(111,6)),fill='#ffe591',width=5)
x,y=xy(111,6);d.polygon([(x,y+8),(x-7,y-7),(x+7,y-7)],fill='#ffe591')
for i,(model,(color,label)) in enumerate(legend.items()):
    x=55+i*300;d.ellipse((x,730,x+12,742),fill=color);d.text((x+20,725),label,font=small,fill='#d4e3eb')
d.text((55,765),'DZIÓB',font=small,fill='#b8cdd8');d.text((1450,765),'RUFA →',font=small,fill='#b8cdd8')
out=root/'C01ShipV77_QA/Screenshots/deck1_plan.png';out.parent.mkdir(parents=True,exist_ok=True);im.save(out);print(out)
