"""Generate readable per-deck schematics from the same assembly data as Unity."""
from pathlib import Path
import json,textwrap
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2]
data=json.loads((root/'Assets/C01ShipV65/Data/ship_v65.json').read_text(encoding='utf8'))
out=root/'Assets/C01ShipV65/Documentation';out.mkdir(parents=True,exist_ok=True)
scale=40;left=110;top=170;w=74*scale+220;h=31*scale+300
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
fb=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
colors={'core':'#304b60','corridor':'#c2dfdf','airlock':'#83c0b7','sector':'#b4c8aa','cabin':'#eadfc5','bathroom':'#92bfc9','support':'#d6c3a0','exterior':'#9fb6be'}
sector_names={'L0_ENGINE_ROOM':'MASZYNOWNIA','L0_PURIFICATION':'OCZYSZCZANIE','L0_EVAC_HANGAR':'HANGAR EWAKUACYJNY','L0_CARGO':'MAGAZYN','L0_HYDROPONICS':'UPRAWA ROSLIN','L0_FOOD_RESERVE':'ZAPASY ZYWNOSCI','L1_GYM':'TRENING','L1_LAB':'LABORATORIUM','L1_MED':'MEDYCZNY','L1_CARGO':'MAGAZYN','L1_ENGINE_CONTROL':'STEROWANIE MASZYN','L1_TECH':'TECHNICZNY'}
def xy(x,z):return left+(x/3+16)*scale,top+(30-z/3)*scale
def rect(b):
 x0,y1=xy(b[0],b[2]);x1,y0=xy(b[1],b[3]);return (int(x0),int(y0),int(x1),int(y1))
def center_text(draw,box,text,size=18,color='#203743'):
 x0,y0,x1,y1=box
 words=text.split();lines=[];line=''
 for word in words:
  candidate=(line+' '+word).strip()
  if draw.textlength(candidate,font=fb(size))>x1-x0-12 and line:lines.append(line);line=word
  else:line=candidate
 if line:lines.append(line)
 if len(lines)>4:lines=lines[:4]
 y=(y0+y1-len(lines)*(size+4))/2
 for line in lines:
  width=draw.textlength(line,font=fb(size));draw.text(((x0+x1-width)/2,y),line,font=fb(size),fill=color);y+=size+4
for deck in (0,1,2):
 im=Image.new('RGB',(w,h),'#101c27');d=ImageDraw.Draw(im)
 d.text((left,40),f'C01  /  POKLAD {deck}',font=fb(48),fill='#f1f6f5')
 d.text((left,103),'SCHEMAT UKLADU  |  1 KRATKA = 3 M  |  OŚ KORYTARZA',font=font(24),fill='#9cbdc5')
 # Tapered bow from the actual cell rule; aft spans full beam.
 for x in range(-16,0):
  inset=max(0,int((-x-1)*.85));b=[x*3,(x+1)*3,(-1+inset)*3,(30-inset)*3]
  if b[2]<b[3]:d.rectangle(rect(b),fill=colors['core'])
 d.rectangle(rect([126,150,-3,90]),fill=colors['core'])
 for z in data['zones']:
  if z['deck']!=deck or z['kind'] in ('core','bathroom'):continue
  b=rect(z['bounds']);kind=z['kind'];d.rectangle(b,fill=('#20343f' if kind=='void' else colors.get(kind,'#d7ded7')),outline='#374f5c',width=3)
 for z in data['zones']:
  if z['deck']==deck and z['kind']=='bathroom':d.rectangle(rect(z['bounds']),fill=colors['bathroom'],outline='#486a77',width=2)
 for z in data['zones']:
  if z['deck']!=deck:continue
  kind=z['kind'];b=rect(z['bounds'])
  if z['id']=='L0_DOCK':center_text(d,b,'SLUZA EWAKUACYJNA',17)
  elif z['id']=='L0_FREIGHT_DOCK':center_text(d,b,'SLUZA LADUNKOWA',17)
  elif kind=='void':center_text(d,b,'OTWARCIE NAD SEKTOREM',18,'#77939c')
  elif kind=='sector':center_text(d,b,sector_names.get(z['id'],z['label']),22)
  elif kind=='support':center_text(d,b,z['label'],14)
  elif kind=='cabin':
   n=int(z['id'].split('_')[-1]);number=((n-1)//4)*2+(n-1)%2+1+(6 if '_S_' in z['id'] else 0)
   center_text(d,b,'KAJ '+str(number).zfill(2),16)
 if deck==1:
  for p in data['placements']:
   if p['category']=='Engines':
    b=rect([p['x'],p['x']+8.85,p['z']-1.2,p['z']+1.2]);d.rectangle(b,fill='#68838a',outline='#b0ced1',width=2)
 for lift in data['lifts']:
  x0,x1,z0,z1=lift['bounds'];b=rect([x0,x1,z0,z1]);d.rectangle(b,fill='#598594',outline='#daf7f8',width=3)
 for g in data['gates']:
  if g['deck']!=deck:continue
  x,z=g['x'],g['z'];x2,z2=(x+g['width'],z) if g['yaw']==0 else (x,z+g['width'])
  d.line([xy(x,z),xy(x2,z2)],fill='#e49b4e',width=5)
 d.line([xy(-48,43.5),xy(174,43.5)],fill='#dbf4ff',width=2)
 d.text((left+80,top+580),'MOSTEK',font=fb(24),fill='#f2faf9')
 d.text((left+(16+43)*scale,top+580),'RUFA',font=fb(24),fill='#f2faf9')
 legend=[('KORYTARZE',colors['corridor']),('KAJUTY',colors['cabin']),('LAZIENKI',colors['bathroom']),('POMIESZCZENIA ZALOGI',colors['support']),('SEKTORY',colors['sector']),('BRAMY','#e49b4e'),('WINDY','#598594')]
 lx=left
 for label,color in legend:
  d.rectangle((lx,h-72,lx+22,h-50),fill=color,outline='#d7e4e3',width=1)
  d.text((lx+30,h-75),label,font=font(21),fill='#c7d7dc')
  lx+=int(d.textlength(label,font=font(21)))+75
 im.save(out/f'Plan_Poklad_{deck}_v65.png',optimize=True)
 print('Plan pokladu',deck,'zapisany')
