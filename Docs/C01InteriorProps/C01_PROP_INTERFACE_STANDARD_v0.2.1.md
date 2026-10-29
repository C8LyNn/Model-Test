# C01-01 — INTERIOR PROP INTERFACE STANDARD v0.2.1 / WAVE 01

**Owner:** C01-01 — ASSET STANDARDS & PIPELINE. **Reference:** issue #2, producer issues #3–7, independent QA #8, integration #9. **Base:** `codex/c01-ship-integration` (ship draft PR #1).

**Normative contract:** [prop_contract.json](./prop_contract.json); 16 planned asset IDs. **Scope:** nonstructural props only. This addendum does **not** replace or modify C01-MAS-0.2-W02's architectural interfaces.

## 1. Protect the current ship

- Reference project: Unity **6000.3.14f1**, URP **17.3.0**; ship v4 scene `Assets/C01ShipV4/Scenes/C01_Ship_Multideck.unity`; master `Assets/C01ShipV4/Prefabs/C01_SHIP_MULTIDECK_MASTER.prefab`. These files are read-only during this wave.
- The current ship uses **3 m architectural cells**, nominal **3 m corridors**, **9×9 m cabins**, and **6 m cabin/corridor height**. This does not mean props must be 3 m wide. **1 Unity unit = 1 m**; dimensions from issue #3–7 are W×D×H in metres.
- Earlier first-nine-model 1 m modular room kit and its 3 m ceilings are **not** the ship v4 placement coordinate frame. Never transfer its older door opening/portal or room height into the current ship by assumption.
- Ship geometry, wall/floor/ceiling, hull, decks, doors/gates, airlocks, elevators, passage widths and existing ship scenes must remain untouched. Producers commit only independent assets under `Assets/C01InteriorProps` (and raw source under `C01PropSources`).

## 2. Dimensions, axes and pivot profiles

**Universal:** +X right, +Y up, +Z back relative to prop front (front = local −Z). W×D×H maps to **X×Z×Y**, *not* X×Y×Z. Every Unity root and child authored at meaningful pivot with identity local rotation/scale (1,1,1). Negative scale is prohibited.

| Profile | Local pivot/origin | Mesh local bounds, W×D×H | Socket normal |
|---|---|---|---|
| `floor` | Centre of floor contact at Y=0 | X=[−W/2,+W/2], Y=[0,H], Z=[−D/2,+D/2] | (0,1,0) |
| `wall` | Rear-face centre on *actual finished wall plane* | X=[−W/2,+W/2], Y=[−H/2,+H/2], Z=[−D,0] | (0,0,−1) |
| `ceiling` | Centre of upper mounting face | X=[−W/2,+W/2], Y=[−H,0], Z=[−D/2,+D/2] | (0,−1,0) |
| `rail` (P15-01) | Straight pipe run start centre | X=[0,W], Y=[−H/2,+H/2], Z=[−D/2,+D/2] | explicit bracket socket |

`wall` and `ceiling` sockets are positioned on finished surfaces, **not** the architectural grid plane. Do not bury solid body into the ship wall or ceiling.

**Pipe detail:** end ports must be coaxial at X=0/X=W and compatible upon a 90° roll around the **pipe's own longitudinal axis**, preserving the bore. A perpendicular route needs an elbow/adapter: rotating a straight tube cannot make a geometrically valid 90° bend.

**Numerical limits:** imported-vs-declared local dimensions ±0.002 m, local pivot offset ±0.001 m, root scale ±0.0001, unintended solid-solid penetration >0.0001 m is failure. Nominal dimensions in the catalogue are targets, not proof; deviations >0.01 m require explicit C01-01 approval reference in manifest.

## 3. All 16 ownership slots

| IDs | Owner | Models | Target W×D×H [m] |
|---|---|---|---|
| P15-01/02/03 | C01-15 | Straight pipe; vent grille; service cabinet | 1×.14×.14; .6×.08×.4; .8×.35×1.8 |
| P16-01/02/03 | C01-16 | Ceiling lightbar; emergency wall lamp; status beacon | 1.2×.15×.12; .35×.14×.22; .2×.2×.3 |
| P17-01/02/03 | C01-17 | Control console; access keypad; lever panel | 1.6×.65×1.1; .18×.07×.28; .4×.3×.55 |
| P18-01/02/03 | C01-18 | Cargo crate; storage rack; maintenance cart | .9×.9×.9; 2.1×.8×2.1; 1×.7×1.2 |
| P19-01/02/03/04 | C01-19 | Crew bunk; locker; desk; chair | .95×2.1×.65; .65×.55×1.8; 1.4×.65×.75; .6×.6×.95 |

Machine manifest contains each slot's owner, allowable mounting surfaces, default pivot profile and required separate child parts.

## 4. Meshes, children, materials and colliders

- Use clean simple low-poly, outward normals, no unintended floating or duplicate coplanar geometry; meaningful UV0 and no NaN or degenerate faces. Report triangle count from **real geometry**, not a planning number.
- Maximum **four URP/Lit material slots** per prefab. Reuse consistent steel/black panel/caution/emission families. Three status variants (green/amber/red) for P16-03 are separate materials, not three models.
- A moving cover (P15-03), mechanical lever (P17-03), cart wheels (P18-03) are separate children, with mechanical pivot coordinates in asset manifest. P16-01 emission surface, P17-01 screen and P19-01 mattress are separate mesh children. Optional locker door must have its own pivot if authored.
- Prefer precise compound primitive colliders: no invisible whole-bounds collider blocking doorways/negative space. Moving parts cannot be static-batched. Any MeshCollider needs documented reason and convex/static policy.
- Mesh/import roots must have identity transforms; parent prefab root uses 1,1,1. Keep front −Z consistent. No extra game logic required for this pilot.

## 5. Blender → FBX → Unity process

Each producer stores actual `.blend` (native source), `.fbx` (export), Unity `.prefab`, front/side/top screenshots and manifest. Create source collection `C01_PROP_P18_01` etc., Blender **Metric/Unit scale=1**. Use `Tools/c01_props/blender_export_prop.py` as a reference exporter (axis_forward='-Z', axis_up='Y', apply_unit_scale=True), then **measure imported geometry in Unity**. Export settings alone are not a PASS.

For each asset record: UUID/human ID/version/owner, measured W×D×H, local bounds, pivot/axis, socket/normal/mount plane, triangle count, mesh components, materials, collider child paths and shape, moving subparts, real file paths with SHA-256 and individual QA states. Output paths are repository-relative. Filenames `P18_01_CARGO_CRATE_v001.blend`, `.fbx`, `.prefab`. Reference `manifest_example_UNVERIFIED.json` intentionally contains no mesh or files; **do not** label as delivery.

## 6. Clearance in the unchanged ship

The ship corridors are nominal 3 m. Do **not** interpret this as automatic 3 m physical clearance or permission to narrow the navigable route. Producers send isolated test scenes and mounting/placement bounds. **C01-02** verifies actual finished surfaces, obstacles, swept arcs of gates/doors/lever covers, colliders, player capsule and walking access in Unity. Keep existing passage usable, preserve door opening, lift/airlock travel, stairs and egress. Report min clear width and tested capsule radius/height, actual positions and screenshots. No placement into ship source scene before QA.

**C01-10** creates a separate `Assets/C01InteriorProps/Scenes/C01_InteriorProps_Showcase.unity` and editable `C01_InteriorProps_Showcase_MASTER.prefab`; missing assets remain BLOCKED, never filled with fake placeholder models.

## 7. Quality gates and status semantics

- Static manifest lint is **not** a Blender/Unity import test. `static:PASS` only means the supplied metadata is self-consistent.
- `delivery:READY_FOR_REVIEW` requires real .blend, .fbx, .prefab, three previews and matching SHA-256 hashes, plus the listed verification fields PASS. Absent files or NOT_RUN QA keep delivery BLOCKED.
- C01-02 conducts truly independent QA (#8), with a PASS/FAIL/NOT RUN matrix over all 16 IDs; actual mesh review, import and clearance must be documented. C01-10 integrates only accepted models (#9). C01-00 approves closure of #2.
- **Current C01-01 status:** contract locked for pilot, Blender/Unity tests NOT RUN, no 3D models claimed. The per-specialist production packages, actual Unity prefabs and playtest require their owners.

The earlier C01-01 architectural contract remains unchanged.
