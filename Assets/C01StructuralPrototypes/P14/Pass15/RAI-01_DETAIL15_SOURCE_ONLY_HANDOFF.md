# C01-14 / DETAIL PASS 15 — RAI-01 controlled enhancement (source only)

**Existing optional model RAI-01, outside 36 P15–P19. No merge or native overwrite.**

Physical OBJ+MTL candidate produced and delivered in the user's ChatGPT artifact `C01_14_DETAIL_PASS15_SOURCE_QA.zip` (26 entries, CRC PASS, SHA-256 `18d1c90f55b4b7c3b91ecd67656d0eb8500b0ff77121b75230f559648770493f`). The actual changed OBJ bytes are **in the user ZIP, not committed into GitHub**, so do not mistake this receipt for a ready-for-Unity model.

**Actual geometry:** Original four source meshes and 48 triangles preserved at 1µm; 2 functional base footplates, 4 eight-sided anchor fastener heads, 4 middle-rail post mounting collars; **4→14 watertight mesh objects, 48→248 triangles**. Original X 0–2m, Z 0–1.1m unchanged; local footplate Y extends ±0.07m from original ±0.05m. No forced weld, no altered pivot or rail/post. Two original FBX material names preserved in OBJ MTL: `M_C01_STEEL`, `M_C01_DARK`.

**ACTUAL source data SHA-256:** `C01_14_RAI-01_DETAIL15_SOURCE_ONLY.obj` = `bacd6d1266963b747f27ed978de99252794820fa3e3ce1e97d85591fe3d751f9`. Original genuine Blender-exported v002 RAI FBX SHA-256 = `b51c3c012f5680de2d02c2deaf5c67c4ae9a12bb7e8347f179ed08d181a7e103`; original native BLEND = `8a2f16205874f8485adb87c5251f6adbba3f51816936c0bf1964ad40a47850a5`.

**Executed independent SOURCE QA:** 14/14 individually watertight and consistent winding; 0 area degenerates, 744 valid UV0 + normal corner references, OBJ reread 14 parts/248 tris; 10/10 planned mechanical mount interfaces have actual triangle surface crossings (not merely touching AABBs): `[20,16,16,12,12,20,16,16,12,12]`; **0 same-facing coplanar overlapping cross-part triangle pairs over entire candidate**. Actual offline BEFORE/AFTER shaded/wireframe images are in ZIP (NOT Blender images). Original 48 triangles exactly preserved.

**STRICT GATES:** new native BLEND `NOT RUN`, Blender-origin binary FBX `NOT RUN`, Blender reimport `NOT RUN`, C01-02 independent QA `PENDING`, real Unity6 URP `NOT RUN`. Historic real Blender roundtrip at [run 41089475908](https://github.com/C8LyNn/Model-Test/actions/runs/41089475908) is only for unchanged v002. RMP-01 unchanged.

**NEEDS_OWNER_ACTION:** restore C01 Actions runners or use authorized Blender4 + Git LFS workstation to convert exact source candidate to a genuine NEW .blend and Blender-exported FBX, with actual render, pivots, material mapping, reimport, SHA and C01-02/Unity approval. Do not ship the candidate alone. No new asset IDs, ship changes, cross-project file mixing, or merge.
