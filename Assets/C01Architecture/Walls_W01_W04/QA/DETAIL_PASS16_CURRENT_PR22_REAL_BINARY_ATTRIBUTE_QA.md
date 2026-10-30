# C01-11 — DETAIL PASS16 / exact current PR22 FBX geometry + UV0 + normal QA

**Scope:** C01-11 historical W01–W04 modular walls. They are **outside** the 36 P15–P19 models and Detail HQ #36 expressly prohibits ship architecture changes. No new designs, no additional geometric detail, no new source mesh or merge. Current PR [#22](https://github.com/C8LyNn/Model-Test/pull/22) remains Draft.

## Newly executed REAL binary QA (not stale digest-only comparison)
Source files: four immutable detailed r2 FBX 7400; current PR22 **exact Git LFS OID-matched physical Blender-origin binary FBX** W01/W03/W04 from [previous successful real Blender CI #41072466328](https://github.com/C8LyNn/Model-Test/actions/runs/41072466328). Directly decoded compressed FBX properties, indexed world positions, normals and UV channels. Rotated candidate axes `(x,y,z) -> (x,z,-y)` before comparing actual source surfaces; normalized to 1µm, grouped coplanar 3D planes as Shapely polygon unions and computed symmetric differences. Compared per-corner `(world position, UV0, world normal)` sets after import-axis correction. **No new Blender run in PASS16**.

| Model | Original r2 FBX SHA256 | Current PR22 candidate FBX SHA256 | Original / candidate triangles | Coplanar surface difference | Per-corner UV0 + normals | Result |
|---|---|---|---:|---:|---|---|
| W01 | `7cc73ea116aa82cab5aa4833db2e6d3ce58888b47907402169d13ac2d7a7ff10` | `4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f` | 12 / 12 | **0 m²** | exact set equality | **PASS** |
| W03 | `3f6d37472239fe2ab61be27eaafb928ee9cf0253c9783d465d81ec649a9b2ee2` | `4c268d554d4e5948ea1927e29b0d32fc581a6f9f14f41fd070bf116a8eb7864c` | 20 / 20 | **0 m²** | exact set equality | **PASS** |
| W04 | `c492539f3d33f65c90e0a0ac5279a6feded45d7cb14c3fefc147358dc9d7ecfe` | `b8751c3816ac6745b99ca17cf0489187dda6f1fd3e5fe4f209030aaccef0ddc8` | 28 / 28 | **0 m²** | exact set equality | **PASS** |

**Important nuance:** original r2 uses 12/20/28 triangle polygons; Blender FBX candidate stores 6/14/20 polygons respectively, some quads, whose triangulated counts remain unchanged. UV0 and split normals match when keyed by genuine world-space position after correct axis conversion, and each pair has one material-assignment entry. This **does NOT verify** full Unity materials/shaders, hidden T-junctions between other ship assets, native Blender reopening in PASS16, or engine import. No reason to retopologize these three sound meshes.

### Critical blocked W02
Authoritative **detailed original r2** W02 FBX SHA256 `3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037`, **572 triangles**, currently remains intact. Actual historical PR22 W02 candidate has **12 triangles** and **3.8552 m²** source/candidate coplanar surface difference after correct FBX axis normalization. Candidate quarantined at `QA_ONLY/REJECTED_W02_PROTOTYPE`; **never** replace the detailed panel. Authored historical detailed native `.blend` is still missing. Safe recovery must be explicitly labeled RECOVERED_FROM_ORIGINAL_FBX and run through genuine Blender4 open/save/export/reimport.

## Physical deliverables / shaded-wireframe QA views
`C01-11_PASS16_PR22_ACTUAL_FBX_UV_NORMALS_QA.zip`, **37 files / 1,322,733 bytes / SHA256 `0ffeb00e3099983904fadeca4bf759b438d0c1229a085ac881808011072fcda5`**. ZIP CRC and each internal file SHA256SUMS verified. Includes four unchanged source binary FBXs, three historic exact PR22 Blender-v400 `.blend` sources, three matching Blender-origin FBXs, rejected W02 candidate isolated as QA-only, **16 newly generated real-FBX mesh shaded/wireframe PNGs**, a new reproducible real FBX geometry+UV+normal script, and per-model JSON evidence.

**Image provenance:** new shaded/wireframe views are **offline Matplotlib renderings of real indexed FBX triangles**. NOT Blender renders; original r2 vs already-existing PR22 binary candidate, **not** newly changed BEFORE/AFTER meshes. W02 rejected historical prototype separately labeled. Source files unchanged in this pass. No new details/FBX/BLEND SHA since inputs are preserved.

## PASS16 gates
- New geometry repairs/details: **0** — no confirmed defects on W01/W03/W04, ship changes forbidden in #36.
- Current PR22 real binary candidate versus authoritative original full surface + UV0/normal per-corner QA: **3/3 PASS**.
- W02 detailed source FBX: static source preserved; correct authored `.blend` missing; unsuitable 12-triangle candidate **REJECTED**.
- New Blender4 native save→binary FBX export→reimport: **NOT RUN**; no `blender`/`bpy` installed locally. Historic successful CI outputs provided solely as historical evidence.
- Actual Unity6 URP importer/prefabs/shader/collider PlayMode: **NOT RUN**; independent C01-02 exact final model release **PENDING**.
- 36 P15–P19 props: **0 C01-11 changes**, no effect on their acceptance denominator.
- C01 private-runner [#41137690882](https://github.com/C8LyNn/Model-Test/actions/runs/41137690882) **FAILED before runner assignment** (runner_id=null, steps=0), reason unknown. **NEEDS_OWNER_ACTION** for authorized Windows Blender4/Unity6 or repo Actions runner settings. No pointless reruns, no settings/budget changes.
- No merge; PR22 remains Draft.