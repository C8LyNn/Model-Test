# C01-15 / PASS03 — Wave 01 Mesh Integrity Handoff

Issue: https://github.com/C8LyNn/Model-Test/issues/30
Producer draft PR: https://github.com/C8LyNn/Model-Test/pull/16

## Measured native source (actual Blender 4.0.2, NOT reconstruction)
| ID | Before V/E/F/T | After V/E/F/T | Accidental topo errors found | Repair |
| --- | --- | --- | --- | --- |
| P15-01 | 288 / 432 / 178 / 508 | 288 / 432 / 178 / 508 | 0 under executed checks | No topology change required |
| P15-02 | 176 / 264 / 120 / 288 | 176 / 264 / 120 / 288 | 0 under executed checks | No topology change required |
| P15-03 | 192 / 288 / 144 / 288 | 192 / 288 / 144 / 288 | 0 under executed checks | No topology change required |

Explicitly tested each mesh in original Blender sources for loose vertices/edges, zero area faces/edges, exact duplicate index faces, non-manifold multi-face edges, boundary edges, and winding inconsistency; all 0 under the executed source audits. Independent parts remain separate. No weld between mesh objects. All source object transforms and parenting preserved. Actual binary FBX re-export and Blender FBX roundtrip preserved triangles, UV0 and material slots (3/3 PASS). Native Blender verification CI: https://github.com/C8LyNn/Model-Test/actions/runs/41088678745

## Versioned evidence
- QA/Pass03/Originals/P15-01..03.blend + matching .fbx are immutable saved BEFORE copies.
- QA/Pass03/P15-XX_mesh_topology_before.json and _after.json provide per named mesh counts and audit findings.
- QA/Pass03/P15-XX_changes.json provides per-ID SHA256 for before and after, actual roundtrip result and changes.
- QA/Pass03/Previews/P15-XX_BEFORE_wire.png, AFTER_wire.png, AFTER_shaded.png, AFTER_detail.png are direct actual-source Blender renders. BEFORE and AFTER appear the same for the three clean source models, correctly.
- QA/Pass03/PASS03_SUMMARY.json contains the aggregate result.

**Important invalidated run:** initial PASS03 run deleted intact polygon faces due to a Python BMesh proxy-identity bug; those changes were rejected. The later clean CI run restored each original from QA/Pass03/Originals, used stable BMVert indices and enforced zero unintended triangle loss. Only the corrected report above is valid.

## QA and acceptance
This is a producer-scoped topology audit, not independent C01-02 acceptance. Robust self-intersection detection and full-scale T-junction scans were NOT RUN where the automated method could not safely certify them. Unity 6 URP real imported prefab/render/physics/ship-clearance: NOT RUN. C01-02 should verify exact original and after SHAs and actual Blender wireframes, run independent checks and sign per asset. C01-10 should perform actual Unity integration when approved. Do not merge PR #16 without independent QA.
