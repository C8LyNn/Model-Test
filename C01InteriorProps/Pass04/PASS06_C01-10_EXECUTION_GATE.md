## C01-10 — MESH REPAIR PASS 06 / actual execution gate

**Status: NEEDS_OWNER_ACTION.** The available environment has **no Blender 4.x, Unity 6 Editor or Git LFS binary**. I cannot access the user's Windows desktop, run either application remotely, hydrate private LFS objects, or fabricate native `.blend` / `.fbx` / Unity `.prefab` files. No new mesh repairs and no Unity tests occurred in this C01-10 execution.

### Evidence obtained now, not inferred

- **GitHub Actions prior success:** run #41089779966 allocated runner `1000012711` and ran 11 steps successfully (Blender PASS03).
- **Current failure independent of Blender code:** runs #41098559165 (`ubuntu-latest` and `ubuntu-22.04` smoke) and #41099951538 (`ubuntu-latest` static registry) have `runner_id=0`, blank runner name, **0 steps**, completion in ~2 seconds. So no executable steps ran. The root cause is not confirmed. Repo is private and connector can read workflow runs, but GitHub **Actions permissions / registered runners / billing settings REST endpoints are unavailable via this connection**; no permission or payment setting changed and no fruitless reruns executed.
- **P19 current sources:** PRs #15/#29 still expose unchanged Git LFS OIDs for P19-01/02/05/07/08. Four offline FBX candidates from PASS05 are not native Blender repair and cannot be promoted to production. **Five potential P1 exporter issues unresolved until real Blender revision and C01-02 review.**
- **P16 current sources:** PRs #12/#28 do not contain seven required native `.blend`; previous exporter files are ASCII, not Blender binary FBX. Sources not eligible for final Unity acceptance.
- **Latest independent C01-02 matrix:** 22/36 hydrated original FBX reviewed at source SHA; 14 missing native/hydrated inputs; **0/36 full QA approved**. No new full PASS claimed.

### Changes committed to EXISTING Draft PR #11

- Refreshed `C01InteriorProps/Pass04/source_stage_36.json` to immutable snapshots of current ten producer commits (36 ID rows; NOT independent source approval).
- Updated `C01InteriorProps/Pass04/PASS04_36_MODEL_HANDOFF.csv` 36 source-commit pins to exactly match the manifest, preserving QA failures. No source meshes, ship scenes, hull/corridor/levels or producer PRs changed. No merge.
- Existing `stage_real_fbx.py` (actual binary SHA verification and Git LFS hydration), `Pass04SourceImportAudit.cs` (Unity import, fail-closed QA-only prefabs and isolated inspection scene) remain ready for the **actual machine run**, not self-certified.

### Precise required owner action (one of these paths)

**A — Restore GitHub Actions:** GitHub repo **Settings → Actions → General** (allowed Actions and runners), **Actions → Runners** / GitHub-hosted runner eligibility and job annotations; account **Billing and licensing → Actions usage / Budgets and alerts**. Capture actual on-screen restriction/error, then run an `echo` smoke job. Do not change spending/billing without owner consent. Re-test Blender only if smoke job gets a real runner and non-empty executed steps.

**B — Existing Windows workstation (preferable if Actions remains blocked):** At repository root on an installed Unity + Blender 4.x machine, run these commands:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.0\blender.exe' --version
git lfs version
git lfs pull
py -3 C01InteriorProps/Pass04/stage_real_fbx.py --repo . --apply
```

Update quoted Blender/Unity executable paths to actual installation and do not stage P16 ASCII models as valid binary. Producer C01-19/16 first save genuine changed `.blend`, binary `.fbx` and Blender roundtrip; C01-02 then pins exact final SHA. On the same machine, with a checked-out **Draft PR #11** and source receipts, open Unity 6000.3.14f1 URP, choose menus `C01 > Mesh Repair PASS04 > 00 / 01 / 02`. Save real `36_FBX_UNITY_IMPORT_AUDIT.csv`, `Pass04Quarantine/Prefabs/*_QA_ONLY.prefab`, `Pass04Quarantine/Scenes/C01_PASS04_FBX_Source_Inspection.unity`, Unity logs and real Shaded/Wireframe captures. Test actual unchanged ship clearance separately. **Never promote quarantine to production without C01-02 signoff.**

### Counts for PASS 06 in C01-10

| Metric | Actually executed/accepted |
|---|---:|
| New native Blender mesh repairs authored by C01-10 | 0 |
| New Blender FBX roundtrips in available environment | 0 / NOT RUN |
| Full independent topology QA approved | 0/36 |
| Unity 6 real FBX imports tested | 0 / NOT RUN |
| Unity QA prefabs / scene files generated | 0 / NOT RUN |
| Unresolved exporter risk at P19 exact prior SHA | 5 |

**Final gate: NEEDS_OWNER_ACTION / INFRA_RUNNER_NOT_ALLOCATED / UNITY_NOT_RUN / 0_FULL_QA_PASS.**
