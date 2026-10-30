# C01 / DETAIL PASS 16 — engineering reference handoff for Unity import QA

**Role:** C01-10 integrator, not an instruction to clone commercial product geometry.
**Verification date:** 2026-10-30. Public manufacturer's product/catalog pages opened and text verified. **5 source URLs, zero reference images copied or modified.** Source images/CAD and trademarks remain the property of their respective publishers; specific reuse licenses **not verified**. Link only, do not copy CAD, textures or silhouettes 1:1. No material from these reference pages is part of shipped game assets.

## REFERENCE-01 — P17-01 bridge console / keyboard rails
- **Manufacturer/source:** MISUMI, *Install & Maintain Linear Guides*
- **URL:** https://uk.misumi-ec.com/en/techblog/product-info/profile-rail-guides-installation-maintenance/
- **Observed mechanical principle:** A linear guide requires a flat, aligned contact face and a well-defined rail reference surface; surface deformation causes mechanical play and uneven loading.
- **Model-specific check:** P17-01 `KeyboardGuide_L/R` mounting must have meaningful support, align to Keyboard rather than float, and avoid exactly coincident same-facing surfaces. **Actual authoring source PASS16** moved the guide pair in +Z by 1 mm, eliminating the measured coplanar overlap: BEFORE 190.0002 mm² *per guide* at z=-0.065 and z=-0.275, AFTER 0 mm² in the checked pair. That 1mm is the **actual producer's source adjustment**, not copied from MISUMI.
- **Importer acceptance:** Use genuine transformed FBX triangle faces to check same-facing coplanarity, *not* only AABB. Preserve rail mounting part names, normals, UV0 and physical scale.

## REFERENCE-02 — P17-01 keyboard support / clamp design
- **Manufacturer/source:** NBK, *DKBR-AF Keyboard Mounting System — Single Axis Type*
- **URL:** https://www.nbk1560.com/en/products/machine_element/display/DKBR-AF/
- **Observed principle:** Industrial keyboard trays use sheet-metal fixing plates, hinges, clamps, clamp screws and corrosion-resistant coatings to carry loads.
- **Model-specific check:** Existing P17-01 guides, screen bolts and service latches should read as an assembled console with load paths to housing, not purely decorative screw heads. Respect original 1.6m console width, node hierarchy and industrial sci-fi shape.
- **Importer acceptance:** Require exact existing source mesh names and 25 current detailed mesh instances/380 authored triangles; prevent import from silently reverting to original 17/204 binary.

## REFERENCE-03 — P18-03 cargo cart / casters
- **Manufacturer/source:** Blickle, *Castor fitting types*
- **URL:** https://www.blickle.com/guide/fitting-types
- **Observed principle:** Caster attachment may use plates, mounting bolt holes, stem fittings or clamps; fitting must physically transmit load into a supporting frame. Detailed source discusses types/suitability rather than any game-specific wheel dimensions.
- **Model-specific check:** Preserve `Wheel_LB/LF/RB/RF` and `Hub_In/Hub_Out` as wheel children for rotation; keep static `ForkInner/Outer`, `ForkCrown`, `Anchor`, `Axle`, `Gusset`, `CrownBolt` rigidly associated with frame/caster mount. Do not copy factory plate dimensions.
- **Importer acceptance:** Hierarchy and wheel floor contact plus rest-position wheel/upright geometric test; animated 360° sweep and Unity PhysX clearance remain separate NOT RUN native gates.

## REFERENCE-04 — P18-01 crate + P15-03 cabinet / industrial hinge
- **Manufacturer/source:** Southco, *Hinges* manufacturer catalog
- **URL:** https://southco.com/hinges
- **Observed principle:** Exposed/removable/concealed hinge designs select leaf, pin, fastening and service access based on actual door purpose; hinges may be designed for disassembly.
- **Model-specific check:** P18-01 `RearHinge_*_Leaf/Pin/Retainer` should be supported without coincident surface z-fighting; `FrontLatch_*_Lever` needs a functional locking counterpart. P15-03 hinged door parts follow one hinge axis without being fused into the static cabinet. No 1:1 copying.
- **Importer acceptance:** Verify moving parts, independent pivots, material/normal retention, exact source mesh inventory; PlayMode hinge sweep needed before final acceptance.

## REFERENCE-05 — P18-02 rack / support gussets
- **Manufacturer/source:** 80/20 Inc., *Structural Shapes: 45 Degree Gusset Profiles*
- **URL:** https://8020.net/structuralshapes/angledprofiles.html
- **Observed principle:** Sloped gusset profiles/angles reinforce perpendicular framed joints and distribute load into both supporting members, with a purpose-defined section and fasteners.
- **Model-specific check:** P18-02 `BackSupport_0.60/1.48_Gusset_L/R` should truly attach the rear support to the named post, not float. Existing P18-02 sources have four additional gussets. Keep original rack footprint and stackable shelf proportions.
- **Importer acceptance:** Check source and imported mesh contact candidates separately; verify precise triangle intersections when required, not merely positive broadphase AABB. Check z-fighting, UV0 and renderer materials in Unity.

## Source/engine QA contract and copyright qualification
- References inform **construction and attachment logic only**; **NOT** model geometry coordinates or downloadable commercial CAD for reuse. Reference source rights have **not** been audited for redistribution; no embedded images.
- Final required: real authoring-native `.blend`, **Blender-emitted** binary FBX, deterministic source revision and both SHA-256 hashes, source and FBX mesh/UV0/normal checks, shaded/wireframe renders from actual Blender, independent C01-02 approval, then real Unity6 URP importer/prefab/material/pivot and PlayMode tests.
- C01-10 cannot turn the existing cached BEFORE FBX into an AFTER just by modifying its LFS pointer or generating a report.
- Current executor native Blender, Git LFS and Unity6: **NOT RUN**. No ship file changes, no new model IDs, no merging.
