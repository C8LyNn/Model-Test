"""Audit the reconstructed assembly, including roof caps and gate motion."""
from pathlib import Path
import json,sys,time
import assembly_v70
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'C01SourceV68/Tools'))
sys.path.insert(0,str(ROOT/'C01SourceV68/Tools/v5_dependencies'))
from audit_floor_v6 import audit as floor_audit
from audit_ceiling_v6 import audit as ceiling_audit
from validate_ship_v5 import collision_audit

data=assembly_v70.build();qa=ROOT/'C01ShipV70_QA';qa.mkdir(exist_ok=True)
failed=False
for name,fn in [('floor_coverage',floor_audit),('ceiling_coverage',ceiling_audit)]:
    result=fn(data);(qa/(name+'.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
    print(name,result,flush=True);failed|=result['status']!='PASS'
for pose in (0,.5,1):
    start=time.time();result=collision_audit(data,pose);result['seconds']=round(time.time()-start,3)
    (qa/('geometry_'+str(pose)+'.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
    print('gate_pose',pose,'penetrations',result['penetrations'],'seconds',result['seconds'],flush=True)
    failed|=result['status']!='PASS'
sys.exit(1 if failed else 0)
