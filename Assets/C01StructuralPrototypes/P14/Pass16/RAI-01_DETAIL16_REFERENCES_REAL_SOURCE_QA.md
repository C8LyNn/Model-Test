# C01-14 / DETAIL PASS 16 — actually authored RAI-01 source OBJ, engineering references, QA

**Deliverable quarantine:** Actual `RAI-01` modified source OBJ+MTL, native/FBX provenance, 12 offline actual-mesh shaded/wireframe preview PNGs, five reference sources and executed independent QA are physically in user-downloadable `C01_14_DETAIL_PASS16_SOURCE_REFERENCES_QA.zip`, **35 verified entries / 1,577,776 bytes / CRC PASS / SHA256 `c9d3beb401a0d27ded0c87af1462a2111e59546f3aa11a1246eb4855134a9842`**. The actual **new source OBJ is in the ZIP, NOT committed to canonical production Git LFS**. This GitHub Markdown is a receipt, not a staged source build or new native deliverable.

**Existing optional RAI-01 only**, NOT part of canonical 36 P15–P19. RMP-01 unchanged. The full PASS15 14 meshes/248 triangles are unchanged, including all original geometry. PASS16 adds only **2 physical hollow 100×100×120 mm square steel socket sleeves** around original 80×80 mm posts (1mm side clearance; bottom 2mm seated into each existing anchor plate), and **4 8-sided transverse screw cylinders** through socket wall and clearance to engage the original upright at two heights each; +6 individual closed meshes, +176 purposeful triangles. **RAI-01 total 20 parts, 424 triangles**. Original silhouette X=2m, Z=1.1m, Y=±0.07m unchanged; original material roles `M_C01_STEEL`/`M_C01_DARK`, original meshes and pivots unchanged. No random surface noise, auto-weld, ship edits or new asset ID.

**NEW real source SHA256:** `C01_14_RAI-01_DETAIL16_SOURCE_ONLY.obj` = **`634716a4ee5c7f8ffb5e53d80d862833670e28c90f07fec133c88d7632efb798`**. Prior PASS15 source SHA256 = `bacd6d1266963b747f27ed978de99252794820fa3e3ce1e97d85591fe3d751f9`. Historic genuine v002 native Blender .blend SHA256 = `8a2f16205874f8485adb87c5251f6adbba3f51816936c0bf1964ad40a47850a5`; genuine original binary FBX = `b51c3c012f5680de2d02c2deaf5c67c4ae9a12bb7e8347f179ed08d181a7e103`. RMP original binary BLEND/FBX SHA unchanged: `7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa` / `97f0b125313057f4ecf601dd60a02b4d3f0d55b87c1713d71a0adbedcc6d1443`.

## Executed independent REAL geometry source QA (not Blender)

- Reopened final physical Wavefront OBJ and individually parsed all 20 named meshes and actual triangles; original 14 mesh triangle sets preserved to 1µm.
- **20/20** individual solids watertight and consistently wound with positive oriented volume after UV/hard-normal split vertices merged **in an audit-only copy** (not welded in production OBJ), **0 degenerate triangle areas**.
- All **1272/1272** indexed OBJ face-corner UV0 and normal references valid.
- Actual strict non-coplanar segment–triangle interior intersections across **10/10 newly authored support pairs**: 2 socket↔footplate intersections (20 tri pairs each), 4 screw↔original post (16 each), 4 screw↔socket (32 each). No floating sockets/screws, and intentional metal intersections are not auto-declared z-fighting.
- Complete 20-object **same-facing coplanar overlap** polygon-clip scan: **0 triangle-pair overlaps, 0 m²**. This is a scoped static source check, not a full visual/animated Unity collision/physics approval.
- Offline **shaded/wireframe BEFORE/AFTER previews are real OBJ renders in Python**, explicitly NOT Blender or Unity screenshots. Individual SRC v002 previous source retained.
- All 35 ZIP entries and SHA manifest validated; no source model/FBX overwritten in Git LFS.

## Five primary engineering references (conceptual cues ONLY, no 1:1 copying)

1. Kee Safety / Kee Systems, **62 Standard Railing Flange**, real 2 set-screws in vertical socket on anchored flange: https://keesystems.com/shop/fittings/kee-klamp/62-standard-railing-flange/ → 2 hollow socket sleeves + 2 side screws per upright.
2. Kee Safety, **Type 26 Two Socket Cross**, actual rail/post junction instead of floating mid rail: https://www.keesafety.com/media/yzrnpaas/safety_components_catalogue_v10_0623_s2.pdf → preserved previous 4 purposeful middle-rail mounting collars.
3. Hilti, **HSA expansion anchor installation**, nut/washer and plate support mechanics: https://files-ask.hilti.com/original/uu/uucwxlanek.pdf → preserved 4 purposeful PASS15 foot bolts / support plate, no fake invisible bolts.
4. OSHA **29 CFR 1910.29**, industrial top rail/mid rail system and height/strength context: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.29 → original 1.10m rail silhouette retained; **NOT a claim of structural/legal safety compliance**.
5. McNICHOLS **GRIP STRUT Safety Grating**, purposeful slip-resistant walking surfaces and supporting members: https://www.mcnichols.com/plank-grating/grip-strut → keep RMP-01 original functional grip details and existing optimized geometry; unnecessary extra holes would degrade source triangle economy.

## Release hold

Actual *NEW* Blender4 `.blend` save **NOT RUN**; Blender-origin binary FBX export/reimport **NOT RUN**; new native Blender shaded/wireframe **NOT RUN**; independent C01-02 FBX QA **PENDING**; real Unity 6 URP **NOT RUN**. All four genuine v002 historical binary native sources remain unchanged and **STALE relative to PASS16**. The real Blender4 run 41089475908 applies only to original v002. Current private C01 Actions run 41137690882: 1 failed job, `runner_id=null`, `steps=0`. Accessible executor has no Blender, bpy, Unity or git-lfs.

**NEEDS_OWNER_ACTION:** restore eligible private GitHub Actions runners or run approved Windows Blender4 + Git LFS. Import only new source detail to original RAI-01, save actual v003 .blend, export actual Blender binary FBX and reimport, render shaded/wireframe in Blender, pin new physical SHA; then independent C01-02 and Unity 6 C01-10. Keep PR Draft, no merge, no new models, ship redesign, blind welding, or cross-project source transfers.
