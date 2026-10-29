# C01 v4.0 — specification and confirmed units

User requests a larger editable three-deck ship in Model Test, followed by uploading the complete deliverable to Google Drive. The existing v3.1 scene and previous versions must remain intact. User clarified ALL stated design dimensions are counts of 3 m floor squares: cabins 3×3 squares = 9×9 m; bathrooms 1×2 squares = 3×6 m; cabin/corridor clear height 2 squares = 6 m; sectors height 4 squares = 12 m; stern width 4 squares = 12 m. Corridor width remains 3 m; six residential side corridors remain 9 m long.

## Layout

Body x=0..63, z=0..45. Three 21 m blocks (9 m cabin + 3 m branch + 9 m cabin). On deck 1: south sectors z=0..12; south cabins/branches z=12..21; main corridor z=21..24; north cabins/branches z=24..33; north sectors z=33..45. Deck 2 repeats both cabin rows and exactly the main/side corridor plan, without duplicating the large sector rooms. It is reached via vertical cores at both ends. All 24 cabins have four separate beds, eight lockers and their own 6×3 m bathroom; bathroom partitions are part of the floor ownership graph.

Deck elevations: deck 0 = -12.4 m, deck 1 = 0, deck 2 = 6.4 m. Floors are 0.4 m structural slabs. Sectors on deck 1 have 12 m clear height, cabin/corridor ceilings 6 m. Lower deck main corridor also has 6 m clear height and its sectors 12 m.

Deck 1 sectors: north GYM (exercise equipment, zero beds), LAB, MED (research equipment and exactly two exam beds); south CARGO, ENGINE_CONTROL (consoles, not main reactors), TECH. Each sector 21×12 m. Deck 0 north: ENGINE_ROOM 21×21, PURIFICATION 21×21, EVAC_HANGAR 21×21. Deck 0 south: EXTRA_CARGO 21×21, HYDROPONICS 42×21 with real planted model instances.

Bridge is a larger bow polygon [[0,3],[0,42],[-12,42],[-24,22.5],[-12,3]]. Lower/main floors occupy that footprint; upper bridge has a rear gallery x=-3..0. Bridge is a vertical atrium with an actual three-stop elevator. Stern is x=63..75, full width 12 m; lower/main floors with upper perimeter galleries. A second actual three-stop elevator serves its vertical core. Both shafts have physical floor holes and landing gates; the player rides a moving platform, not a teleport. Exactly 5 exterior engines remain. A small editable escape craft is parked on deck 0 and faces a wide gated route via the stern dock to an exterior pad.

## Gates and controls

All former hinged passages become button-operated telescopic sliding gates. Standard gate modules 3 m wide; stern gates 6 m, evacuation gates 9 m. Frame height follows room clearance (6/12 m). Eight staggered leaf panels retract into non-solid side pockets. Root scale remains 1. Physical buttons on both sides are clicked with left mouse through the first-person ray; pressing a gate directly is not interaction. Airlocks close the other gate before opening. Elevator call buttons summon the car before opening the landing; inside buttons choose decks 0/1/2. Landing gates never open away from their car.

## Geometry rules

Keep the 3 m assembly grid, shared junctions, zero duplicate walls, and module scale 1. Build wall intervals in 3D: merge overlapping wall ranges across decks, subtract full gate envelopes, and give shared nodes separate ownership. Floor and ceiling polygons must be clipped against vertical wall/node volumes that cross their slab elevation and against elevator shafts. A ceiling may be the underside of the next shared structural floor; never duplicate that slab. This prevents tall-sector walls overlapping upper-deck slabs. Missing geometry tests must verify coverage independently of collision counts.

## Delivery and QA

Create Assets/C01ShipV4 beside v3.1, separate runtime/editor/test assemblies and scene C01_Ship_Multideck.unity, master C01_SHIP_MULTIDECK_MASTER.prefab. Preserve Model Test packages and user settings. Actual Unity compilation/import, physical button/gate and elevator/player tests, geometry/coverage/clearance checks and screenshots. Actual Blender .blend and FBX/OBJ/GLB export if available (installed Blender exists). Save unavailable checks as NOT RUN. Add to existing PR #1. Package complete project (exclude Library/Temp/.git), models, sources, scripts and QA; upload ZIP plus Unity package/readme to a new folder beside existing C01 Drive deliveries, then verify metadata and return observed download links.
