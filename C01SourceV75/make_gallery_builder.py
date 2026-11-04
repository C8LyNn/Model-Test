"""Derive the v7.5 platform builder from the already tested v7.4 module logic."""
from pathlib import Path
r=Path(__file__).resolve().parent.parent
s=(r/'C01SourceV74/build_route.py').read_text(encoding='utf8')
s=s.replace("C01SourceV73/Data/ship_v73.json","C01SourceV74/Data/ship_v74.json")
start=s.index('routes=[');end=s.index('\nmodels=',start)
s=s[:start]+'''routes=[dict(name='TECH',zone='L2_CARGO',x0=9,x1=33,z0=30,z1=33,side='S',branches=(1,2)),
        dict(name='LAB',zone='L2_LAB',x0=51,x1=75,z0=54,z1=57,side='N',branches=(3,4)),
        dict(name='CARGO',zone='L2_TECH',x0=93,x1=117,z0=30,z1=33,side='S',branches=(5,6))]'''+s[end:]
start=s.index("models['G_V74_Frame']=");end=s.index("ids={p['id']",start)
s=s[:start]+s[end:]
s=s.replace("zone='L2_'+name", "zone=route['zone']")
s=s.replace('L2_ROUTE_', 'L2_PLATFORM_')
start=s.index('    for i,x in enumerate((x0+6,x0+12,x0+18)):');end=s.index('    for label,x,branch in',start)
s=s[:start]+s[end:]
start=s.index('for x in (18,60,102):');end=s.index("data['version']=",start)
s=s[:start]+s[end:]
s=s.replace('C01.SHIP.7.4','C01.SHIP.7.5')
s=s.replace("models=[models['G_V74_Frame'],models['G_V74_Leaf']]", "models=[]")
s=s.replace("('L2_GYM','L2_ENGINE_CONTROL','L2_MED')", "('L2_CARGO','L2_LAB','L2_TECH')")
s=s.replace('Assets/C01ShipV74/Data/pursuit.json','Assets/C01ShipV75/Data/platforms.json')
s=s.replace('C01SourceV74/Data/ship_v74.json\').write_text','C01SourceV75/Data/ship_platforms.json\').write_text')
assert "C01SourceV75/Data/ship_platforms.json').write_text" in s
(r/'C01SourceV75/build_galleries.py').write_text(s,encoding='utf8')
