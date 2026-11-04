"""Render a schematic of the two cargo-aligned decks from the assembly data."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent.parent
data=json.loads((ROOT/'C01SourceV73/Data/ship_v73.json').read_text(encoding='utf8'))
zones={z['id']:z for z in data['zones']}
image=Image.new('RGB',(1800,1000),'#101d2b');draw=ImageDraw.Draw(image)
title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',36)
heading=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',28)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
support_font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
draw.text((65,30),'SPÓJNA LOGISTYKA — POZIOMY 1 I 0',font=title,fill='#edf5fa')
draw.text((65,82),'Rzut schematyczny wzdłuż statku; pomieszczenia zachowują pozycje z danych sceny.',font=small,fill='#a9c4d3')
origin,scale=220,11.3
def centertext(box,text,font,color='#f0f6fa'):
    bounds=draw.multiline_textbbox((0,0),text,font=font,align='center');x=(box[0]+box[2]-bounds[2]+bounds[0])/2;y=(box[1]+box[3]-bounds[3]+bounds[1])/2
    draw.multiline_text((x,y),text,font=font,fill=color,align='center')
def zonebox(ident,y0,y1,label,color):
    x0,x1,_,_=zones[ident]['bounds'];box=(origin+x0*scale,y0,origin+x1*scale,y1)
    draw.rectangle(box,fill=color,outline='#8eabbc',width=2);centertext(box,label,heading)
draw.text((65,165),'POZIOM 1',font=heading,fill='#dceaf3')
for ident,label,color in [('L1_TECH','SEKTOR TECHNICZNY','#385c69'),('L1_ENGINE_CONTROL','STEROWNIA MASZYNOWNI','#62513d'),('L1_CARGO','MAGAZYN ŁADUNKOWY','#536875')]:
    zonebox(ident,155,345,label,color)
draw.text((65,389),'ZAPLECZE',font=heading,fill='#dceaf3')
for ident,label in [('L1_S_SUPPORT_03','WARSZTAT'),('L1_S_SUPPORT_04','CZĘŚCI\nZAMIENNE'),
                    ('L1_S_SUPPORT_11','EWIDENCJA\nŁADUNKU'),('L1_S_SUPPORT_12','NARZĘDZIA\nŁADUNKOWE')]:
    x0,x1,_,_=zones[ident]['bounds'];box=(origin+x0*scale,385,origin+x1*scale,470)
    draw.rectangle(box,fill='#273f50',outline='#7995a5',width=2);centertext(box,label,support_font)
draw.text((65,585),'POZIOM 0',font=heading,fill='#dceaf3')
for ident,label,color in [('L0_FOOD_RESERVE','ZAPASY ŻYWNOŚCI','#6e5d39'),('L0_ENGINE_ROOM','MASZYNOWNIA','#62513d'),('L0_CARGO','ŁADOWNIA','#536875')]:
    zonebox(ident,570,760,label,color)
draw.line((origin+42*scale,493,origin+42*scale,550),fill='#819cac',width=2)
draw.line((origin+84*scale,493,origin+84*scale,550),fill='#819cac',width=2)
draw.text((65,861),'DZIÓB',font=small,fill='#bdd0da');draw.text((1450,861),'RUFA I ŚLUZA TOWAROWA →',font=small,fill='#bdd0da')
draw.text((65,918),'Sektory mają rzeczywiste szerokości z danych montażowych; linie nie przedstawiają bram.',font=small,fill='#9bb6c5')
out=ROOT/'C01ShipV73_QA/Screenshots/zoning_plan.png';out.parent.mkdir(parents=True,exist_ok=True);image.save(out)
print('Wrote',out)
