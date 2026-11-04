"""Draw a labelled plan directly from the same layout manifest used by tests."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / 'C01SourceV72/Data/ship_v72.json').read_text(encoding='utf8'))
zones = {z['id']: z for z in data['zones']}
names = {'L0_PURIFICATION': 'OCZYSZCZALNIA', 'L0_ENGINE_ROOM': 'MASZYNOWNIA',
         'L0_EVAC_HANGAR': 'HANGAR EWAKUACYJNY', 'L0_FOOD_RESERVE': 'ZAPASY ŻYWNOŚCI',
         'L0_HYDROPONICS': 'HYDROPONIKA', 'L0_CARGO': 'ŁADOWNIA',
         'L0_MAIN': 'KORYTARZ GŁÓWNY', 'L0_DOCK': 'ŚLUZA EWAK.',
         'L0_FREIGHT_DOCK': 'ŚLUZA TOWAROWA'}
colors = {'L0_PURIFICATION':'#305561','L0_ENGINE_ROOM':'#55493a','L0_EVAC_HANGAR':'#524b66',
          'L0_FOOD_RESERVE':'#6a5c38','L0_HYDROPONICS':'#365e4a','L0_CARGO':'#525e69',
          'L0_MAIN':'#273f52','L0_DOCK':'#635a75','L0_FREIGHT_DOCK':'#576978'}
image = Image.new('RGB',(1800,850),'#101c2a')
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
small = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',35)
draw.text((56,26),'POZIOM 0 — LOGISTYKA I SYSTEMY STATKU',font=title,fill='#e7f1f8')
draw.text((56,75),'Jedna kratka = 3 m  •  widok z góry  •  bramy oznaczono kolorem pomarańczowym',font=small,fill='#a8c4d6')
scale=10.3;ox=170;oz=136
def xy(x,z): return (ox+x*scale,oz+(75-z)*scale)
for zone_id in names:
    zone=zones[zone_id];x0,x1,z0,z1=zone['bounds']
    ax,ay=xy(x0,z1);bx,by=xy(x1,z0)
    draw.rectangle((ax,ay,bx,by),fill=colors[zone_id],outline='#8aabbc',width=2)
    label=names[zone_id];box=draw.textbbox((0,0),label,font=font)
    draw.text(((ax+bx-(box[2]-box[0]))/2,(ay+by-28)/2),label,font=font,fill='#f1f6f6')
for side in ('N','S'):
    for i in range(3):
        z=zones[f'L0_{side}_ACCESS_{i}'];x0,x1,z0,z1=z['bounds'];a,b=xy(x0,z1),xy(x1,z0)
        draw.rectangle((*a,*b),fill='#243949',outline='#607989',width=1)
        draw.text((a[0]+6,a[1]+6),'SERWIS',font=small,fill='#9fb6c5')
for gate in data['gates']:
    if gate['deck']!=0 or not any(name in names for name in gate['zones']):continue
    x,z=gate['x'],gate['z'];width=gate['width']
    start=xy(x,z)
    end=xy(x,z+width) if abs(gate['yaw'])==90 else xy(x+width,z)
    draw.line((start,end),fill='#f4a75c',width=7)
draw.text((56,815),'DZIÓB',font=small,fill='#b4cddb')
draw.text((1550,815),'RUFA  →',font=small,fill='#b4cddb')
out=ROOT/'C01ShipV72_QA/Screenshots/level0_plan.png'
out.parent.mkdir(parents=True,exist_ok=True)
image.save(out)
print('Wrote',out)
