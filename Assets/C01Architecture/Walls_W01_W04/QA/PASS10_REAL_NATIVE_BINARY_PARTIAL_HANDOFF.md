# C01-11 / PASS 10 — Real Blender-native partial artifact handoff

## Scope and provenance
C01-11 owns historic **architecture W01–W04**, OUTSIDE the 36 P15–P19 interior prop models in #33. No new designs, mesh edits, ship modifications or merges. Existing Draft PR [#22](https://github.com/C8LyNn/Model-Test/pull/22), prior HEAD `df20535c367a930ae7cc0b4cd998a6f846acc479` (no authoring source edited in this pass).

**Actually delivered physical binary archive** to ChatGPT personal Project Library path:
`/C01 — 3D Asset Factory/C01-11/PASS10/C01-11_PASS10_REAL_NATIVE_PARTIAL_W01_W03_W04.zip`.
Archive **2,608,901 bytes**, SHA-256 **`5ca644980e5b7754d839e8f99742f07ad713a0a8fab5ee712f189cc0e50b632e`**. ZIP CRC PASS, 23 files and internal SHA256 manifest match all contents. Archive has **actual Blender v400 native .blend + binary Blender FBX** for W01/W03/W04, **actual immutable original r2 binary FBX for W01/W02/W03/W04**, real Blender previews and historical exact-file Blender export/reimport QA JSON.

### Verified REAL Blender v400 candidate pairs (not newly generated this pass)

| ID | Actual v400 .blend SHA256 | Actual Blender-export FBX SHA256 | Historic real Blender 4.0.2 source→FBX→import QA | PASS10 original-r2 surface equivalence |
|---|---|---|---|---|
| W01 | `ca2f2f631dfa6f847f06df3120c3e226f915b2067926e7cecf38be322bf760aa` | `bbceb73143ee4e4956aff596d841feafe45b237b4493eaecffdf16d14f354d47` | PASS, 12 tris, UV0 + 1 material slot | PASS at 1e-6 m |
| W03 | `7e156a29a1ad4d45e0ad4bfb6c3f24f4e313656ee7368f8d90cf71e480c82ede` | `5a69769c3e23137b9842c8a92dba26283a73e952f549b340cd9f42d960fccf8d` | PASS, 20 tris, UV0 + 1 material slot | PASS at 1e-6 m |
| W04 | `3d72bac74e2eadf086942c7786c57fb53ad438405ecf7b611c6b1ed753eb770c` | `95fac1a2c466bc7f60e71363dc05b625ce637f9dd698d09dc9980f7c1282d008` | PASS, 28 tris, UV0 + 1 material slot | PASS at 1e-6 m |

True native files have literal `BLENDER-v400` header and FBX files have the `Kaydara FBX Binary` signature. Historical real Blender 4.0.2 QA data (source and imported triangle world positions, source/import UV0 presence and material slot count) from [run 41088902223](https://github.com/C8LyNn/Model-Test/actions/runs/41088902223): Blender audit steps **PASS**, but overall workflow **FAIL** at later Git push; archive contents were preserved and downloaded. A separate [run 41072466328](https://github.com/C8LyNn/Model-Test/actions/runs/41072466328) was successful but produced DIFFERENT file hashes from these later QA-version binaries.

### PASS10 new actual binary geometry comparison (not Blender execution)

Parsed exact FBX polygons directly, including compressed Blender array records. Normalized candidate export coordinates `(x,y,z)→(x,z,-y)`, rounded to 1e-6 meters, and compared **unions of coplanar actual polygon surfaces** against original immutable October 28 r2 FBX. Original/candidate W01/W03/W04 had **0 m² symmetric surface difference**, identical bounds, signed volumes, and triangulated triangle counts. Genuine binary file inputs, portable executable `QA/geometry_comparison_reproducible.py`, parser and machine-readable report included; re-execution on unpacked archive PASS 3/3.

**This exterior equivalence does NOT prove UV coordinate equality, normals/smoothing/material identity, Unity prefab acceptability, or preservation of historical authored topology.**

### Critical W02 rejection

Original detailed W02 r2 FBX has 288V / 858E / 572 triangles, SHA-256 `3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037`. Previous real Blender .blend candidate W02 has 8V / 12 triangles, **3.8552 m² true surface mismatch** against detailed original r2. Its .blend is **NOT present in the PASS10 delivery** to prevent accidental swap; only original detailed FBX is included. A genuine authored detailed r2 W02 .blend is still missing; recreating source must be explicitly labelled *RECOVERED FROM ORIGINAL FBX* and must pass Blender open→export→reimport and UV0/material/pivot validation on actual source.

### Current Draft PR LFS receipts do NOT match these historical Blender QA-version hashes

Current [PR22](https://github.com/C8LyNn/Model-Test/pull/22) Git LFS version for native W01/W03/W04 .blend/FBX comes from earlier successful run 41072466328, not the later exact-files QA archive; e.g. W01 PR22 LFS blend `80a8999cc0a039eb4f5f907c38c492ec4c4ed49c22a66d44f36fbe14cb1356b2`, FBX `4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f`; W03 LFS blend `77e1a52db293d4fc6b27b27e151c89865eb4473465bfeafefcc85935b810f9cc`, FBX `4c268d554d4e5948ea1927e29b0d32fc581a6f9f14f41fd070bf116a8eb7864c`; W04 LFS blend `4e533365634ffc5207734bbd258c7f7d267348813dacc8bdf6943354d8367f53`, FBX `b8751c3816ac6745b99ca17cf0489187dda6f1fd3e5fe4f209030aaccef0ddc8`. **Do not transfer the exact QA PASS from one set of file SHAs to a different PR version.** This is physical archive handoff, NOT silent in-PR binary replacement or a merge.

### PASS10 gates

- Newly repaired source meshes: **0** (original indexed topology had no confirmed defect to fix).
- Existing real native Blender+binary-FBX candidate pairs physically included: **3**, historical source→FBX→reimport QA PASS at exact archived hashes.
- New PASS10 Blender runtime / newly exported files: **NOT RUN**; this execution environment lacks Blender/bpy, package installs fail DNS, GitHub C01 private-repo runners still terminate with `steps=[]`.
- Original detailed W02 native .blend: **MISSING**.
- Independent C01-02 acceptance and Unity 6 URP: **PENDING / NOT RUN**.
- None of W01–W04 belongs to the 36 P15–P19 acceptance denominator; global 36 count unaffected.

**NEEDS_OWNER_ACTION** to run authentic detailed W02 FBX→recovered .blend→binary FBX→Blender import on a real Blender4.x Windows machine or unblock native C01 runner. Keep all PRs Draft, no merge.
