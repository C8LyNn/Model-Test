# C01-01 — MESH REPAIR PASS05 / executed topology standards & runner handoff

**Date:** 2026-10-30. **Owner:** C01-01 (standards, not C01-19 mesh author). **Global:** #33 / #30. **Draft:** PR #31, still unmerged.

## Work actually executed

1. Read PASS05 coordinator instruction #33 comment 6528786325, independent QA PR #13 PASS04 handoff, owner PRs #15/#29 and archived native Blender production artifacts.
2. Inspected GitHub Actions run #41095534379 directly via GitHub REST: failed job had `runner_id=0`, `steps=[]`, empty runner name, approximately 2-second job duration and **0 billable milliseconds**. Other dependent jobs were SKIPPED. These facts establish NO runner allocation / NO Blender execution; they do **not** prove whether billing, account policy, quota or GitHub scheduler is root cause. Public GitHub Status is not an account-specific diagnostic.
3. Local environment check: no Blender executable and no `bpy`; container cannot resolve public network DNS to install it. Unity is also unavailable. Native PASS05 Blender FBX roundtrip and Unity are **NOT RUN**.
4. Ran independent, read-only Python FBX7400 polygon-index analysis on **six actual original archived binary FBX bytes**, including all five P19 P1-risk models and P19-06 control. No reconstructed geometry, no model edits. Both producer archive ZIPs passed CRC; physical binary FBX header and source/FBX SHA256 were recorded. The detailed JSON gives per-mesh polygons, face indices and coordinates of fan-degenerate candidate triangles. No original indexed triangular face was degenerate in these six files.
5. Updated existing topology standard in PR #31: explicit source + FBX triangulation gate for P19-01, P19-02, P19-05, P19-07, P19-08 only; documented intentional opening / separate mesh exceptions. Adjusted GitHub Actions to check Wave01 and Wave02 P19 producer sources in an independent job (no prerequisite native test); new [run #41099146648](https://github.com/C8LyNn/Model-Test/actions/runs/41099146648) still failed **before any runner executed steps**, both independent jobs `runner_id=0`.

## Exact archive and SHA evidence

P19-01 and P19-02: native-source cleanup artifact **12993127556**, successful original producer run [41090102018](https://github.com/C8LyNn/Model-Test/actions/runs/41090102018), source commit `1e1f5e4e2b7819ed75d30207328a22caf16e15dd`.

P19-05, P19-06, P19-07, P19-08: native-source artifact **12993051362**, successful original producer run [41088782744](https://github.com/C8LyNn/Model-Test/actions/runs/41088782744), source commit `a87fb0e9523cfe92d79d6b429cc6c4148a406f41`.

| ID | FBX sha256 | V / faces / T-if-fan | mesh parts | n-gons >4 | degenerate naive-fan tris | status |
|---|---|---|---:|---:|---:|---|
| P19-01 | `47b4d6f2017626b6084584fbf0bad907505eb9e194703032d83af5315c1a4009` | 133 / 78 / 254 | 4 | 38 | 12 | REVIEW_REQUIRED |
| P19-02 | `a42a57d168164cea335de3c9ee175a3074edca4a48b707a14beadbea16a8b6d8` | 118 / 86 / 216 | 5 | 31 | 8 | REVIEW_REQUIRED |
| P19-05 | `64156363cb5007831c243aeea50d5e59c862cc98b27cb12dd2f8af5b3c019892` | 88 / 66 / 148 | 7 | 3 | 1 | FAIL_P1 baseline |
| P19-06 | `d773f2d3c0fe9743a0ad619353766b669386997769eb8a59487b58295c7c3a7d` | 56 / 42 / 84 | 7 | 0 | 0 | no detected fan risk |
| P19-07 | `88b32fe2f5ddf981eecdc0469088f4e23e07c4c605a1db7bb9689a0b6011d585` | 136 / 78 / 252 | 6 | 16 | 19 | FAIL_P1 baseline |
| P19-08 | `cbbea5435f8326e06fb5f43237986594df044c0e3ff94100fc44f856dce35ae2` | 149 / 100 / 282 | 6 | 35 | 7 | FAIL_P1 baseline |

These are source-archive FBX bytes from **prior production**, not newly repaired PASS05 FBX or evidence of actual native Blender/Unity fan triangulation failure. Other QA reports may have different P19-02 numbers due to different producer binary SHA. A zero-area **naive fan** candidate is not an automatically degenerate native Blender triangle.

### Reproducibility

A self-contained downloadable package from this conversation, `C01_01_PASS05_STANDARDS_EVIDENCE.zip`, contains six SHA-pinned original FBX bytes, individual JSON forensic reports, matrix JSON and executable Python stdlib FBX parser. The file is a **diagnostic archive, not a release asset collection**. In the existing PR, `Tools/c01_mesh_repair/triangulation_gate.py` performs true native Blender source plus binary FBX import tests once a runner exists.

## Mandatory next actions, without false automatic activation

- **C01-19 PR #29 + #15:** run existing Blender 4.x source scripts on real .blend P19-05/07/08, then P19-01/02 (and inspect P19-03). Preserve silhouette, UV, materials, pivots, moving parts. Produce changed source and native binary FBX SHA, BEFORE/AFTER wireframe from REAL models and roundtrip output. T-junctions in P19-07/08 are unverified candidates, not an excuse to weld whole objects. P19-06 is not to be retopologized without a confirmed error.
- **C01-16 PR #12 + #28:** seven native .blend and genuine binary FBX still await real Blender execution; ASCII FBX and an unexecuted Blender generator are not substitutes.
- **C01-02 PR #13:** independently re-run SHA-pinned final binaries across all 36; previous last checked baseline was 22/36 indexed exports inspected, 5 P19 export-risk flags, 0/36 full approved. Do not promote based on this C01-01 forensic triage.
- **C01-03 PR #27:** keep SHA-256 archive provenance distinct from future repaired producer commits; no approved state without C01-02 exact-SHA signature.
- **C01-10 PR #11:** real Unity 6 Editor import, native saved prefab/collider checks and route clearance remain NOT RUN.
- **C01-00:** restore account Actions runner availability by checking Settings → Actions → Runners/General and Billing/Usage with required permissions; repeat targeted workflow. The current GitHub app cannot read private account billing policy or run Blender locally.

**Final state:** C01-01 standard UPDATED, 6 real archival FBX scans EXECUTED, 0 PASS05 model source repairs by C01-01, GitHub Actions runner ALLOCATION BLOCKED, Blender NOT RUN, Unity NOT RUN, C01-02 independent acceptance PENDING, entire #30 36/36 gate OPEN. Draft PR #31 no merge, no redesign, no new models, no ship changes.
