# C01-10 — PASS20 / REAL Unity 6000.3.14f1 URP 17.3.0 — owner-only Windows execution

**Scope:** unchanged signed real P16-01, P17-02, P18-01 from W19. **No merge, no ship scene changes, no new models, no license contents in GitHub/chat/logs.** The script performs an actual Editor run ONLY in **Execute** mode. **Preflight alone is not Unity execution.**

## Blocker confirmed in real GitHub CI

[W19 #41531591861](https://github.com/C8LyNn/Model-Test/actions/runs/41531591861): Linux staging 3/3 PASS; `actual-unity-6-urp` **SKIPPED** due incomplete authorized Unity license configuration; explicit release blocker FAIL. Original 3 physically hydrated FBX plus SHA receipt stored in [artifact #13182701367](https://github.com/C8LyNn/Model-Test/actions/runs/41531591861/artifacts/13182701367). This isolated execution environment has no installed licensed Unity Editor. No Unity import/preflight/PlayMode can honestly be marked PASS here.

**Licensing fact (Unity official current docs):** Unity **Personal** must be activated by logging into **Unity Hub**; manual `.alf`/`.ulf` activation is **not supported for Personal**. Use normal Unity Hub activation on the owner's licensed Windows PC. For authorized paid CI plans follow current Unity/GameCI serial or Unity licensing server documentation; do NOT attempt unsupported Personal activation via a hidden browser setting. Links: https://docs.unity.com/en-us/engine/6000.6/manual/get-started/install-and-upgrade/licenses-and-activation/manual-license-activation/manual-activation-guide and https://game.ci/docs/github/test-runner/.

## Owner Windows procedure — first REAL three native prefabs

**Prerequisites:** Windows 11, active Unity Hub license for THIS user, installed **Unity Editor 6000.3.14f1**, Git for Windows, Git LFS, Python 3, GitHub CLI (`gh`) with authorized access to private `C8LyNn/Model-Test`. No license files or account credentials are requested by this script.

Open PowerShell. Work on a **fresh isolated clone** (not another agent's checkout) of our **existing Draft PR #11 branch**:

```powershell
git clone --branch c01/props-10-showcase-integration https://github.com/C8LyNn/Model-Test.git C01-Unity-W20-QA
Set-Location .\C01-Unity-W20-QA
git lfs install --local
git status --short
(Get-Content .\ProjectSettings\ProjectVersion.txt | Select-String 'm_EditorVersion')
```

Fetch **unchanged original 3 FBX from already completed W19**; no Blender reexport:

```powershell
gh auth status
gh run download 41531591861 --repo C8LyNn/Model-Test --name C01-PASS19-3-REAL-SIGNED-FBX-READY-FOR-UNITY --dir .
```

If that original W19 artifact has expired, use exact immutable producer refs/real Git LFS hydration (not a historical or ASCII model), with the already shipped script:

```powershell
python .\C01InteriorProps\Pass04\stage_real_fbx.py --repo . --apply --ids P16-01 P17-02 P18-01
```

Preflight on **actual physical bytes** (safe; does not launch Editor):

```powershell
& .\C01InteriorProps\Pass20\run_real_unity_windows.ps1 -Mode Preflight -ProjectRoot (Get-Location).Path
```

The script fails on any missing/not-binary source, incorrect file sizes, SHA mismatch, project version or URP package mismatch. Required SHA256:

| ID | Exact FBX SHA-256 | Bytes |
|---|---|---:|
| P16-01 | `c0a782a17a0047e0d578a41e42ac714c0fa0f86c7c4960f4bc10e21a24a278fd` | 48,380 |
| P17-02 | `db49121a520f16ca636626795550b83e8a4df94ded56a7ccb76308520bb7c3f6` | 77,420 |
| P18-01 | `f541d502ba9eaaf5c7a0a7279c44f71f36dd482e3aed3ba0734058dcf1045f6c` | 140,460 |

**ACTUAL LICENSED UNITY 6:** first log into Unity Hub on Windows, confirm active Personal/Pro entitlement, Editor version 6000.3.14f1. Close any other Unity instances using the checkout. Then:

```powershell
& .\C01InteriorProps\Pass20\run_real_unity_windows.ps1 -Mode Execute -ProjectRoot (Get-Location).Path -UnityExe 'C:\Program Files\Unity\Hub\Editor\6000.3.14f1\Editor\Unity.exe'
```

Expected real outputs **only after successful execution**:
- Unity-generated native **3 prefabs**: `Assets/C01InteriorProps/Pass19/Resources/Pass19QA/{P16-01,P17-02,P18-01}.prefab`.
- **Isolated** Unity QA scene: `Assets/C01InteriorProps/Pass19/Generated/Scenes/C01_PASS19_NATIVE_3FBX_QA_ONLY.unity`.
- Real EditMode `EditMode-results.xml`, `EditMode-Editor.log`, PlayMode `PlayMode-results.xml`, `PlayMode-Editor.log` and `C01_10_PASS20_ACTUAL_WINDOWS_RESULT.json` under `C01InteriorProps_QA/PASS20/WindowsUnity/`.
- Runtime Unity-generated material assets and native-mesh import CSV `C01InteriorProps_QA/PASS19/UNITY_ACTUAL_3_NATIVE_PREFABS.csv`.
- The script checks process exit, real Unity test XML `passed >= 1, failed = 0`, 3 actual prefab files and 1 actual scene file; absent evidence is **HOLD**.

For **visual** proof, open only `C01_PASS19_NATIVE_3FBX_QA_ONLY.unity` in the licensed Unity Editor, capture both **Scene and Game** screenshots at 1920×1080 including imported model scale, URP lighting and material, then put PNGs next to results. Do **not** open/mutate production ship scenes for this test. Run screenshot checks against actual meshes; screenshots from source viewers do not count.

### How to hand off proof without disclosing license

In [Draft PR #11](https://github.com/C8LyNn/Model-Test/pull/11) attach result files/screenshots as a private proof ZIP or provide the exact allowed artifact/branch link. Share only Editor version, full three FBX SHA256, test summary, Prefab/Scene asset hashes, sanitized Editor.log, test XML, actual Scene/Game screenshots. **Remove machine paths/user identifiers as needed; never include Unity email/password/serial/`.ulf` or GitHub tokens.** Notify [HQ #36](https://github.com/C8LyNn/Model-Test/issues/36) with real PASS/HOLD and links. C01-02 independent QA must still approve each exact SHA separately before release.

### If the owner instead has authorized paid CI licensing

Configure repo **Settings → Secrets and variables → Actions** with authorized `UNITY_EMAIL`, `UNITY_PASSWORD`, `UNITY_SERIAL` for a serial-based license, or the officially supported GameCI licensing server. Only the repository owner/admin should perform this. Then manually dispatch `C01 PASS19 REAL signed 3 FBX to Unity 6 URP` on our existing Draft branch. The workflow's `UNITY_LICENSE` path must only use a legitimately supported license; **Unity Personal is not manually activated**. Do not print secrets in job logs.

**Release gate:** Until an Editor has actually imported/compiled the three models, produced native prefabs+scene and executed EditMode and PlayMode, `UNITY_NOT_RUN | FINAL_APPROVED 0/36`. Every Windows-only preflight success stays explicitly **physical source verification, NOT Unity PASS**.
