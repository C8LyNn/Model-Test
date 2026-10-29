# Expected supplier outputs

All paths are **proposed staging**, not claims that these files exist.

| Thread / issue | Asset IDs | Required deliverable |
| --- | --- | --- |
| C01-15 / #3 | P15-01 P15-02 P15-03 | pipe, vent, cabinet |
| C01-16 / #4 | P16-01 P16-02 P16-03 | lightbar, emergency wall lamp, beacon |
| C01-17 / #5 | P17-01 P17-02 P17-03 | console, access keypad, lever |
| C01-18 / #6 | P18-01 P18-02 P18-03 | crate, rack, maintenance cart |
| C01-19 / #7 | P19-01 P19-02 P19-03 P19-04 | bunk, locker, desk, chair |

Preferred relative file names inside each supplier staging folder:
- `Pxx-yy_source.blend`
- `Pxx-yy_export.fbx`
- `Pxx-yy_front.png`
- `Pxx-yy_side.png`
- `Pxx-yy_iso.png`
- `Pxx-yy_manifest.json`

Do not conflate GitHub issue #3–7 assignments with explicit GitHub assignee state. All five are open. C01-10 is an integrator and does not edit their meshes.

Unity-generated contents only after valid sources are imported: `Assets/C01InteriorProps/Generated/{Prefabs,Scenes}`. Preserve their `.meta` files and attach screenshot evidence to #8. Do not place files in `Assets/C01ShipV4` or overwrite the ship scene.
