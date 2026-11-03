"""Derive versioned Unity builders and repair manifest without altering v6/v6.2."""
from pathlib import Path

root=Path(__file__).resolve().parent.parent
edit=root/'Assets/C01ShipV65/Editor';edit.mkdir(parents=True,exist_ok=True)
def replace(text,old,new):
    if old not in text:raise RuntimeError('Missing expected builder text: '+old)
    return text.replace(old,new)

src=(root/'Assets/C01ShipV6/Editor/ShipV6Builder.cs').read_text(encoding='utf8')
src=replace(src,'public static class ShipV6Builder','public static class ShipV65Builder')
src=replace(src,'Root="Assets/C01ShipV6"','Root="Assets/C01ShipV65"')
src=replace(src,'C01_Ship_Multideck_v6.unity','C01_Ship_Multideck_v65_base.unity')
src=replace(src,'C01_SHIP_MULTIDECK_MASTER_V6','C01_SHIP_MULTIDECK_MASTER_V65_BASE')
src=replace(src,'C01ShipV6_QA','C01ShipV65_QA')
src=replace(src,'ship_v6.json','ship_v65.json')
src=replace(src,'WithV6Scene','WithV65Scene')
src=replace(src,'lift=cargo.Lift;}else', 'lift=cargo.Lift;lift.elevations=l.elevations;lift.ResetToFloor(1);}else')
src=replace(src,'explorer.view=camera;explorer.player=player;', 'explorer.climbHeight=3f;explorer.view=camera;explorer.player=player;')
src=replace(src,'Tools/C01 Ship v6/Rebuild','Tools/C01 Ship v6.5/Rebuild base')
src=src[:src.index('    public class ShipV6ModelImporter:AssetPostprocessor')]+'}\n'
(edit/'ShipV65Builder.cs').write_text(src,encoding='utf8')

src=(root/'Assets/C01ShipV62/Editor/ShipV62Builder.cs').read_text(encoding='utf8')
src=replace(src,'public static class ShipV62Builder','public static class ShipV65PolishBuilder')
src=replace(src,'const string Root = "Assets/C01ShipV62"','const string Root = "Assets/C01ShipV65"')
src=replace(src,'C01_Ship_Multideck_v62.unity','C01_Ship_Multideck_v65.unity')
src=replace(src,'C01_SHIP_MASTER_V62.prefab','C01_SHIP_MASTER_V65.prefab')
src=replace(src,'polish_v62.json','polish_v65.json')
src=replace(src,'Assets/C01ShipV61/Scenes/C01_Ship_Multideck_v61.unity','Assets/C01ShipV65/Scenes/C01_Ship_Multideck_v65_base.unity')
src=replace(src,'Tools/C01 Ship v6.2/Build repaired ship','Tools/C01 Ship v6.5/Build final')
src=replace(src,'var signage=master.GetComponent<ButtonSignage>(); if(signage!=null) signage.enabled=false;',
            'var signage=master.GetComponent<ButtonSignage>(); if(signage==null) { signage=master.AddComponent<ButtonSignage>(); signage.Configure(AssetDatabase.LoadAssetAtPath<Shader>("Assets/C01ShipV61/Signage/ButtonText.shader")); } signage.enabled=false;')
src=replace(src,'C01 V6.2 BUILD COMPLETE','C01 V6.5 BUILD COMPLETE')
src=replace(src,'data.lifts.Length!=4','data.lifts.Length!=6')
# The original 3.18 m viewscreen intersects a 3 m room ceiling.
src=replace(src,'new Vector3(0,1.72f,0),new Vector3(.18f,2.72f,2.78f)', 'new Vector3(0,1.62f,0),new Vector3(.18f,2.52f,2.78f)')
src=replace(src,'new Vector3(0,1.72f,-1.445f),new Vector3(.3f,2.72f,.11f)', 'new Vector3(0,1.62f,-1.445f),new Vector3(.3f,2.52f,.11f)')
src=replace(src,'new Vector3(0,1.72f,1.445f),new Vector3(.3f,2.72f,.11f)', 'new Vector3(0,1.62f,1.445f),new Vector3(.3f,2.52f,.11f)')
src=replace(src,'new Vector3(0,3.13f,0),new Vector3(.3f,.1f,3)', 'new Vector3(0,2.93f,0),new Vector3(.3f,.1f,3)')
(edit/'ShipV65PolishBuilder.cs').write_text(src,encoding='utf8')

src=(root/'C01SourceV62/design_v62.py').read_text(encoding='utf8')
src=replace(src,'Assets/C01ShipV6/Data/ship_v6.json','Assets/C01ShipV65/Data/ship_v65.json')
src=replace(src,'Assets/C01ShipV62/Data/polish_v62.json','Assets/C01ShipV65/Data/polish_v65.json')
src=replace(src,'C01.SHIP.6.2','C01.SHIP.6.5')
src=replace(src,"door_center = -1.5 if cargo else 0","door_center = (1.5 if source['id']=='STERN_CARGO_N' else -1.5) if cargo else 0")
src=replace(src,"    return dict(version='C01.SHIP.6.5'","    for p in bridge: p['position'][2] -= 1.5\n    return dict(version='C01.SHIP.6.5'")
(root/'C01SourceV65/design_v65.py').write_text(src,encoding='utf8')
print('v6.5 builders prepared')
