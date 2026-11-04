"""Diagram of the route from the same placement manifest used by Unity."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parent.parent
plan=json.loads((root/'Assets/C01ShipV74/Data/pursuit.json').read_text(encoding='utf8'))
im=Image.new('RGB',(1600,740),'#101c2a'); d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',29)
def pt(x,z):return (150+x*9,580-z*7)
def rect(x0,z0,x1,z1,fill,outline=None):
    a=pt(x0,z1);b=pt(x1,z0);d.rectangle([a,b],fill=fill,outline=outline,width=2)
d.text((42,28),'POZIOM 2  /  TRASA POŚCIGU',font=bold,fill='#edf6ff')
d.text((42,72),'Schemat danych montażowych • kratka 3 m • widok z góry',font=font,fill='#a7bac9')
rect(0,42,126,45,'#55768a','#93b0bb')
for r in plan['routes']:
    x0,x1,z0=r['x0'],r['x1'],r['z0']
    rect(x0,z0,x1,z0+3,'#218d88','#b1f3dc')
    if z0>42:
        rect(x0,45,x0+3,z0,'#218d88');rect(x1-3,45,x1,z0,'#218d88')
    else:
        rect(x0,z0+3,x0+3,42,'#218d88');rect(x1-3,z0+3,x1,42,'#218d88')
    for x in range(x0,x1+1,3):
        a=pt(x,z0);b=pt(x,z0+3);d.line([a,b],fill='#80c9bb',width=1)
for x in (18,60,102):
    a=pt(x,42);b=pt(x,45);d.line([a,b],fill='#f4b056',width=7)
for x,z,label in [(9,61,'SEKTOR TRENINGOWY'),(51,25,'STEROWNIA MASZYNOWNI'),(93,61,'SEKTOR MEDYCZNY')]:
    p=pt(x,z);d.text((p[0],p[1]-10),label,font=small,fill='#dbf7ed')
points=[(0,43.5),(10.5,43.5),(10.5,55.5),(31.5,55.5),(31.5,43.5),(52.5,43.5),(52.5,31.5),(73.5,31.5),(73.5,43.5),(94.5,43.5),(94.5,55.5),(115.5,55.5),(115.5,43.5),(126,43.5)]
d.line([pt(*p) for p in points],fill='#fff2a2',width=4,joint='curve')
for x,z in [(20,55.5),(62,31.5),(104,55.5),(123,43.5)]:
    px,py=pt(x,z);d.polygon([(px+6,py),(px-5,py-5),(px-5,py+5)],fill='#fff2a2')
d.text((42,650),'MOSTEK →',font=font,fill='#d8e9f3');d.text((1325,650),'→ WYJŚCIE',font=font,fill='#d8e9f3')
d.text((42,690),'Turkus: pomosty i przejścia   •   Pomarańcz: przegrody   •   Żółty: przebieg trasy',font=small,fill='#aac5d1')
out=root/'C01ShipV74_QA/Screenshots/plan_trasy.png';out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
