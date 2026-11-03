"""Derive versioned Unity builders and repair manifest without altering v6/v6.2."""
from pathlib import Path

root=Path(__file__).resolve().parent.parent
edit=root/'Assets/C01ShipV64/Editor';edit.mkdir(parents=True,exist_ok=True)
def replace(text,old,new):
    if old not in text:raise RuntimeError('Missing expected builder text: '+old)
    return text.replace(old,new)

src=(root/'Assets/C01ShipV6/Editor/ShipV6Builder.cs').read_text(encoding='utf8')
src=replace(src,'public static class ShipV6Builder','public static class ShipV64Builder')
src=replace(src,'Root="Assets/C01ShipV6"','Root="Assets/C01ShipV64"')
src=replace(src,'C01_Ship_Multideck_v6.unity','C01_Ship_Multideck_v64_base.unity')
src=replace(src,'C01_SHIP_MULTIDECK_MASTER_V6','C01_SHIP_MULTIDECK_MASTER_V64_BASE')
src=replace(src,'C01ShipV6_QA','C01ShipV64_QA')
src=replace(src,'ship_v6.json','ship_v64.json')
src=replace(src,'WithV6Scene','WithV64Scene')
src=replace(src,'lift=cargo.Lift;}else', 'lift=cargo.Lift;lift.elevations=l.elevations;lift.ResetToFloor(1);}else')
src=replace(src,'explorer.view=camera;explorer.player=player;', 'explorer.climbHeight=3f;explorer.view=camera;explorer.player=player;')
src=replace(src,'Tools/C01 Ship v6/Rebuild','Tools/C01 Ship v6.4/Rebuild base')
src=src[:src.index('    public class ShipV6ModelImporter:AssetPostprocessor')]+'}\n'
(edit/'ShipV64Builder.cs').write_text(src,encoding='utf8')

src=(root/'Assets/C01ShipV62/Editor/ShipV62Builder.cs').read_text(encoding='utf8')
src=replace(src,'public static class ShipV62Builder','public static class ShipV64PolishBuilder')
src=replace(src,'const string Root = "Assets/C01ShipV62"','const string Root = "Assets/C01ShipV64"')
src=replace(src,'C01_Ship_Multideck_v62.unity','C01_Ship_Multideck_v64.unity')
src=replace(src,'C01_SHIP_MASTER_V62.prefab','C01_SHIP_MASTER_V64.prefab')
src=replace(src,'polish_v62.json','polish_v64.json')
src=replace(src,'Assets/C01ShipV61/Scenes/C01_Ship_Multideck_v61.unity','Assets/C01ShipV64/Scenes/C01_Ship_Multideck_v64_base.unity')
src=replace(src,'Tools/C01 Ship v6.2/Build repaired ship','Tools/C01 Ship v6.4/Build final')
src=replace(src,'var signage=master.GetComponent<ButtonSignage>(); if(signage!=null) signage.enabled=false;',
            'var signage=master.GetComponent<ButtonSignage>(); if(signage==null) { signage=master.AddComponent<ButtonSignage>(); signage.Configure(AssetDatabase.LoadAssetAtPath<Shader>("Assets/C01ShipV61/Signage/ButtonText.shader")); } signage.enabled=false;')
src=replace(src,'C01 V6.2 BUILD COMPLETE','C01 V6.4 BUILD COMPLETE')
# The original 3.18 m viewscreen intersects a 3 m room ceiling.
src=replace(src,'new Vector3(0,1.72f,0),new Vector3(.18f,2.72f,2.78f)', 'new Vector3(0,1.62f,0),new Vector3(.18f,2.52f,2.78f)')
src=replace(src,'new Vector3(0,1.72f,-1.445f),new Vector3(.3f,2.72f,.11f)', 'new Vector3(0,1.62f,-1.445f),new Vector3(.3f,2.52f,.11f)')
src=replace(src,'new Vector3(0,1.72f,1.445f),new Vector3(.3f,2.72f,.11f)', 'new Vector3(0,1.62f,1.445f),new Vector3(.3f,2.52f,.11f)')
src=replace(src,'new Vector3(0,3.13f,0),new Vector3(.3f,.1f,3)', 'new Vector3(0,2.93f,0),new Vector3(.3f,.1f,3)')
(edit/'ShipV64PolishBuilder.cs').write_text(src,encoding='utf8')

src=(root/'C01SourceV62/design_v62.py').read_text(encoding='utf8')
src=replace(src,'Assets/C01ShipV6/Data/ship_v6.json','Assets/C01ShipV64/Data/ship_v64.json')
src=replace(src,'Assets/C01ShipV62/Data/polish_v62.json','Assets/C01ShipV64/Data/polish_v64.json')
src=replace(src,'C01.SHIP.6.2','C01.SHIP.6.4')
(root/'C01SourceV64/design_v64.py').write_text(src,encoding='utf8')
print('v6.4 builders prepared')
