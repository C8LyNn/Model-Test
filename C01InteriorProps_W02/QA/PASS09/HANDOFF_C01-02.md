# C01-17 — PASS09: actual binary repair candidates P17-05; Blender execution blocked

## Physical artifact work, not just audit

Opened **real** source `P17-05.blend` and real Kaydara FBX from previous successfully executed Blender 4.0.2 PASS03. Original immutable SHA256 and file length verified, Blender BHead / DNA1 / Object SDNA checked. On separate, quarantined copies patched **exactly one existing object transform**, with no new geometry, no mesh edits:

- Blender v400: `Object` block SDNA, `LowerDisplayRail.loc[1]` changed -0.1199999973 to -0.1209999993 m. **3 changed bytes** in original 603584-byte native source file; `ENDB`, `DNA1` and all mesh data unchanged. Original SHA `07be57396...` → candidate SHA **`16ad0dffa17f5918e64b009086d16efc7c998703b14f2d43f6fa258bb084d440`**.
- Binary FBX v7400: `Model(LowerDisplayRail) / Properties70 / Lcl Translation.Y` changed -0.1199999973 → -0.1209999973 m. **6 changed bytes**, same 63116-byte FBX. Original SHA `3fa31448...` → candidate SHA **`c2b8f049de4e84697980e53d0f443a77b19ce930ea6b159a10fb5b3df8695c71`**.
- Full parser structural equality across all other FBX nodes **PASS**. 20 source Mesh objects/240 triangles, material and UV0/normal nodes unchanged.
- Actual binary-FBX coplanar triangle overlap recomputation for `DisplayBezel` × `LowerDisplayRail`: **6 pair intersections / area 0.059199984 m² BEFORE → 0 pair intersections AFTER**; cross-object T-junction candidates 0→0.

**CRITICAL gate:** This is a **real file-byte correction, but not native Blender application save/export**. The candidate BLEND might still fail Blender to load, or cached transforms might be stale, because no `bpy` ran. It is QUARANTINED and production `.blend/.fbx` Git-LFS files in PR #23 intentionally **unchanged**. **Blender reopen/save/export/reimport NOT RUN; Unity6 NOT RUN; C01-02 signoff PENDING**. Never describe these candidates as approved final Blender output.

Portable 108735-byte ZIP produced in ChatGPT PASS09 conversation with both actual modified binary candidates, precise SHA+byte offsets, and fail-closed Blender 4.x reopen/re-export/reimport QA; ZIP SHA `0b9b2481e9a7711a59e1d00348c000d4d790cd1cbe32bacbd7be9549db816bfb`. No new model or renderer substitutes.

## Runner diagnosis now corroborated by separate project B01

- C01 private repo W02 `41101698436` FAILED `runner_id=0`, `steps=[]` (same no-run symptom on earlier 2-OS smoke).
- B01 RoboRougelike **public** repo workflow [41106902806](https://github.com/C8LyNn/RoboRougelike/actions/runs/41106902806) really ran on `ubuntu-24.04`: runner_id `1000014911`, **12 steps, SUCCESS**. Hence GitHub Actions hosted execution is globally functional for the same owner; the C01 private repository's entitlement/runner policy/status is the unresolved differentiator. Exact cause unverified. Do NOT make private C01 public, spend budgets or transfer files to B01 as workaround.
- Local executor: no installed Blender/bpy/Git-LFS and no usable external DNS. Cannot execute genuine Blender/Unity here.

## ENV01–ENV05 v002 cross-project lessons (policy only, not asset transfer)

Observed ENV01–05 Draft PRs #288/#290/#291/#289/#293 in B01; their real Blender QA includes native source `.blend` save/reopen, GLB binary verification, mesh manifold/degenerate/UV checks, source+artifact SHA pinned, actual before/after captures, collider/pivot checks as applicable, and independent owner review. B01 Unity gates are separately NOT RUN when Unity activation missing. C01 must keep its **FBX** export/import verification and exact producer SHA gate separate from B01's GLB pipeline. No files or permissions copied.

## Exact owner action / C01-02

Run `RUN_WINDOWS.ps1` from PASS09 portable ZIP on authorized Windows with Blender 4.x; it will physically load candidate BLEND in `bpy`, check true rail world transform and all 20/240 UV0 meshes, **save a new real Blender-authored .blend**, **export a real new binary FBX**, reimport it in clean Blender, hash both new bytes. Only then commit newly authored and actually verified runtime `.blend/.fbx` to existing Draft PR #23, independent C01-02 rechecks final SHA, then C01-10 Unity6. Previous 7/7 PASS03 Blender roundtrips remain valid only for OLD bytes.

**PASS09 counts C01-17:** 1 model received actual quarantined native/FBX binary byte changes; 0 new Blender-saved+exported production models; 0 independent signed full QA; 0 Unity. **NEEDS_OWNER_ACTION.**
