# C01-17 — Wave 01 repair + Wave 02 delivery: handoff to C01-02 and C01-10

DATE 2026-10-30. Owner C01-17; issue #5; parent #2. All work isolated; no ship structural/scenes changed.

## W01 repair — PR #17 (draft)
- Branch: c01/props-17-controls, verified HEAD e3b7f2fac2be98f3b450aeb2ec2ac9f050e4e206.
- Corrected QA defect C01QA-P1-17-UV0, 49/49 mesh primitives now UV0 and verified after actual FBX reimport.
- Fixed screen emissive face occluded by housing (P17-01), regenerated real previews.
- 3 real Blender .blend + 3 binary FBX + 9 PNG + FBX reimport SHA256 report.
- Actual Blender FBX reimport: P17-01 17 UV0 meshes, P17-02 20, P17-03 12 with preserved LeverPivot; 3/3 PASS.
- Success run: https://github.com/C8LyNn/Model-Test/actions/runs/41073418886
- PR: https://github.com/C8LyNn/Model-Test/pull/17

## W02 production — PR #23 (draft)
- Branch: c01/props-17-wave02, verified HEAD 6e4884231c4b0eab8d3a1aa255ab5fe1f817360f.
- Four real models P17-04 dual-screen bridge station; P17-05 lab/medical diagnostic; P17-06 guarded cutoff; P17-07 removable fuse.
- P17-04 W2.4000 D1.0000 H1.3500 m; 348 tris; 29 UV0 mesh parts.
- P17-05 W0.8500 D0.6085 H1.5000 m; 240 tris; 20 UV0 mesh parts.
- P17-06 W0.5200 D0.2265 H0.7200 m; 156 tris; 13 UV0 mesh parts; CoverPivot + SwitchPivot preserved.
- P17-07 W0.7000 D0.2400 H0.8200 m; 228 tris; 19 UV0 mesh parts; CartridgePivot preserved.
- Generated 4 native Blender .blend, 4 binary FBX and 12 real Blender PNG, plus SHA-256 manifest for 20 binaries.
- Actual Blender FBX round-trip 4/4 PASS; corrected occluded screen faces P17-04/05.
- Success run: https://github.com/C8LyNn/Model-Test/actions/runs/41073534111
- PR: https://github.com/C8LyNn/Model-Test/pull/23

## Independent archive inspection
- Both GitHub Actions artifact ZIPs downloaded; 16 entries for W01, 21 entries for W02; CRC PASS.
- All seven BLEND files have BLENDER-v400 signature; all seven FBX files have Kaydara FBX Binary signature.
- Nine W01 and twelve W02 PNG are true Blender Workbench renders, not Unity screenshots.
- Source glTF carries actual binary buffers, normals, UV0, triangle indices and material slots; C01-17 uses no placeholders in geometry.

## Explicit release blockers
- Native Unity 6 URP prefab binaries: MISSING / NOT RUN. Editor scripts are included in each PR to generate actual prefabs after FBX import.
- Unity import/render, collider validation, movement in Play Mode, 3m corridor and door clearance: NOT RUN.
- C01-02 independent approval: PENDING (not self-approved).
- C01-10 Showcase scene/master prefab: PENDING independent approval.
- C01-01 standards/mounting/pivots approval: PENDING.

## Actions
1. C01-02: independently test both exact HEAD commits, verify FBX mesh GUID/pivots/UV/normal, Unity 6 URP materials, prefab colliders, motion and clearance. Record PASS/FAIL per ID P17-01..P17-07.
2. C01-10: execute menu C01 / Controls / Build Prefabs for W01 and C01 / Controls / Wave02 / Build FBX Prefabs for W02 using Unity 6; commit generated .prefab .mat .meta and capture Unity screenshots.
3. Only after C01-02 acceptance, integrate instances into separate showcase without touching ship architecture; no early merge.

Overall owner geometry and Blender/FBX = PASS; final Unity delivery = BLOCKED until runtime and independent QA.
