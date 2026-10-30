# C01-15 — DETAIL PASS 15 — P15-01 source handoff

**Current authoring spec:** `Assets/C01InteriorProps/P15/Sources/geometry_spec.json` v0.1.4; source edit commit `4de19533a134203d415f39f07fef449f0b41f4a8`; SHA-256 `7f3d602af1040431134aa4cca236fb36c9613d77160b383f175ec6c02d144703`. Existing producer Draft PR #16 only; PR #25 untouched. No merge, ship change or new model IDs.

**Actual source geometry edited:**
- Four pre-existing plate screws previously floated 0.5 mm: changed Z = 0.015 → 0.014 m, resulting in 0.5 mm positive plate seating.
- Four existing top/bottom clamps previously had 8.5 mm gap to pipe crown: moved Y = ±0.064 → ±0.0555 m and increased strap depth Z from 0.081 to 0.113 m; pipe tangency now 0 mm while preserving X and root/pivot.
- Added two mechanically seated retaining ties per existing mount, front/back, and two locking heads per mount: eight purposeful parts. Rear ties seat 2 mm into mount plates, front ties maintain 2.5 mm clearance from pipe; 1 mm screw seating and exposed head. 17→25 P15-01 separate components.
- No changes to P15-02, P15-03, their door or hinge. Other assets unchanged.

**Executed offline source geometry checks:** 48/48 targeted numerical interface checks PASS; static reconstructed indexed meshes 17→25, V306→394, triangles 544→688, 25/25 closed, positive-volume and consistent winding; zero zero-area triangles. Full bounds before X[0,1], Y[-.070,.070], Z[0,.141] m → after X[0,1], Y[-.066,.066], Z[0,.141] m. Separate axis-aligned, same-facing triangle planar overlap screen found 0→0 overlapping mesh triangle pairs. **These are offline reconstructed-source checks, not native Blender or Unity acceptance.** Oblique overlap, complete triangle surface contact, UV0 in Blender and runtime behavior still need checking.

**Physical local evidence package** (delivered in producer conversation, not committed as native assets): `C01-15_DETAIL_PASS15_P15-01_SOURCE_QA.zip`, SHA-256 `84cdabf3cddcc844afa96f112f996d1ab3f1242c0c10e7be00fd1e125983bdc2`; includes same-view before/after STATIC shaded/wireframe previews, real offline candidate GLB SHA-256 `a92e2df83c3a58621907f0a0420600823b2e5cf4020447ad416585e4a0ef68a7` and machine JSON. GLB is **NOT** a Blender-origin FBX.

**Gates:** source PASS; Blender 4.x native save, Blender-origin binary FBX export/reimport, real Blender screenshots, independent C01-02 and Unity6 import **NOT RUN / PENDING**. Existing old native files are stale relative to v0.1.4. Need owner runner/authorized Windows Blender4 + Git LFS, then actual `.blend` and FBX SHA, exact C01-02 QA, C01-10 staging. **KEEP DRAFT — NO MERGE.**
