# Geometry re-review — C01 v4.0 T1

Reviewed 2026-10-29. Scope: `f5c9422..c902e88` in `C:/Users/kubap/Desktop/C01_Ship_Multideck_v4.0`.

## Verdict

**APPROVE the scoped coverage fix. Spec verdict: PASS for the previously missing independent surface-coverage requirement. Quality verdict: PASS for this source re-review. No new actionable findings.** The P2 finding in `docs/geometry-review.md` is resolved. This approval covers geometry source and the independent coverage correction; actual Unity import, interaction and lift rides remain separately verified by the primary implementer.

## Assessment

`Tools/validate_ship_v4.py` now builds expected floor and ceiling regions from a literal accepted plan through `reference_surfaces()`. It includes body decks, shared-floor undersides, bow floors and atrium roof, stern galleries and core roof, exterior pads, and shaft exclusions. `surface_audit()` evaluates actual model polygons transformed by placement, at the required surface elevation. It subtracts their union from each expected region and reports residual area and location. Vertical wall/node/hull/frame footprints correctly account for material occupying the plane, so expected surfaces do not demand slabs through structure. The calculation does not derive its expected regions from placement IDs or the generator's `coverage` metadata.

The new empty-model guard catches used models without parts. `coverage=[]` is explicitly rejected, while real geometry remains checked independently of that metadata. The automated mutation test retains placement IDs while emptying and shortening a floor model, and checks the deleted metadata case. Existing deletion tests remain intact.

`Tools/build_ship_v4.py` closes the wall-skin strips between their former ±0.13 m outer faces and the ±0.15 m structural envelope used by slab clipping. The panels now meet the bottom/top metal bands and separately owned end nodes exactly, without introducing an intentional penetration. The two bow rear-corner nodes extend from the 12 m sector roof step to the 12.4 m core-shell top and enter the slab clipping obstacles. Added floor-underside metadata records shared ceiling ownership; it is not used as the independent audit's geometric truth.

## Focused verification

The supplied `QA/layout_v4.json` was inspected: **2250 expected regions, 0 gaps, 0 missing area, PASS**. To avoid repeating the full audit, re-review mutation execution narrowed `reference_surfaces()` in memory to one literal target region for each case, while retaining actual manifest geometry and the unchanged audit implementation. All six undamaged controls passed; every mutation failed with the expected location:

| Unsaved mutation | Expected-region location | Detected missing area |
|---|---|---:|
| Empty model used by `F_L2_6_24` | floor L2 x=6 z=24, y=6.4 | 8.1225 m² |
| Shorten that floor model by half in X | same | 3.8475 m² |
| Shorten `C_L2_6_24` model by half in X | ceiling L2 x=6 z=24, y=12.4 | 3.8475 m² |
| Delete `F_L1_-12_21` | bow floor L1 x=−12 z=21, y=0 | 9 m² |
| Delete `F_L0_78_36` | exterior pad floor L0 x=78 z=36, y=−12.4 | 9 m² |
| Delete `C_CORE_B_-12_21` | core roof above L1 x=−12 z=21, y=12.4 | 9 m² |

These cases establish that intact placement identifiers and intact coverage metadata cannot conceal empty or shortened slabs, and that the previously untested bow/pad/core regions are genuinely included in the independent coverage calculation.

The primary supplied eight passing Python tests and 181 passing actual Blender model round trips; these were not rerun in this scoped re-review. No broad collision audit was repeated. Implementation, manifest, Git index and HEAD were not modified. Only this review document was written.
