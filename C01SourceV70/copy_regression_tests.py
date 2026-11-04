"""Retarget existing end-to-end tests to the v7.0 scene without stale visual assertions."""
from pathlib import Path
root=Path(__file__).resolve().parent.parent
out=root/'Assets/C01ShipV70/Tests/PlayMode'
bridge=(root/'Assets/C01ShipV69/Tests/PlayMode/ShipBridgeV69Tests.cs').read_text(encoding='utf8')
bridge=bridge.replace('class ShipBridgeV69Tests','class ShipBridgeV70RegressionTests').replace('C01_Ship_Multideck_v69','C01_Ship_Multideck_v70')
(out/'ShipBridgeV70RegressionTests.cs').write_text(bridge,encoding='utf8',newline='\n')
systems=(root/'Assets/C01ShipV68/Tests/PlayMode/ShipV68SceneTests.cs').read_text(encoding='utf8')
systems=systems.replace('class ShipV68SceneTests','class ShipSystemsV70RegressionTests').replace('C01_Ship_Multideck_v68','C01_Ship_Multideck_v70')
for name in ('FrameAndAdjacentWallMatchTheSameFullThreeMetreModule','AllWallBandsFollowTheirOwnFullModuleEdges'):
    start=systems.index('[UnityTest] public IEnumerator '+name+'(')
    opening=systems.index('{',start);depth=0;end=None
    for i in range(opening,len(systems)):
        if systems[i]=='{':depth+=1
        elif systems[i]=='}':
            depth-=1
            if depth==0:end=i+1;break
    if end is None:raise RuntimeError('Unbalanced test '+name)
    systems=systems[:start]+systems[end:]
(out/'ShipSystemsV70RegressionTests.cs').write_text(systems,encoding='utf8',newline='\n')
print('Prepared bridge and systems regression tests for v7.0')
