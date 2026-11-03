# C01-03 — PASS05 / GitHub Actions runner diagnostics

**Issue:** [#33](https://github.com/C8LyNn/Model-Test/issues/33) / [#30](https://github.com/C8LyNn/Model-Test/issues/30)

## Reproduced (real GitHub Actions API)

- A direct [rerun of failed C01-03 jobs](https://github.com/C8LyNn/Model-Test/actions/runs/41095968082) was successfully requested through the GitHub Actions API; **run attempt 2** ended **FAILURE**.
- Read actual `/actions/runs/41095968082/attempts/2/jobs`: **10/10 jobs FAILURE; runner_id=0, runner_name="", steps=[]**.
- Read actual GitHub API `/actions/runs/41095968082/timing`: **Ubuntu billable 0ms**, total job steps executed 0. The workflow lasted only seconds.
- This symptom exists across independent producer and integration workflows, including C01-16 and C01-19. Hence the failed run did not load Blender, read FBX geometry or run Python tests; **source/mesh failure cannot be inferred**.
- Fetching failed job logs returned GitHub redirected object/blob 404 previously. Missing logs alone does not identify the root cause.
- The public [GitHub Status](https://www.githubstatus.com/) reported Actions **Operational** during the check, but this does not rule out repository/account-specific allocation trouble or a limited unreported issue.

**Exact root cause remains UNDETERMINED** — repo permissions available to the ChatGPT GitHub connector do not expose runner/billing/policy administration endpoints. Do NOT claim an outage, exceeded quota, spending-limit problem, GitHub billing suspension or invalid workflow YAML without evidence.

## Owner-only diagnostic checks (no source rewrites needed)

1. Check account/organization **Settings → Billing and licensing → Usage/Budgets / Actions** for available minutes and any spending/payment blocks. A billing or budget state cannot be read via the available connector.
2. Check repository/organization **Settings → Actions → General**: Actions enabled, allowed actions and workflow permissions, runner-group policy, any organization restrictions.
3. Check repository **Settings → Actions → Runners**, the GitHub-hosted runner availability / self-hosted registration and allocated concurrency. The runs request `runs-on: ubuntu-latest`; no runner ever started. Do not infer private runner availability.
4. Inspect the run **Checks / annotations** in the browser to find any administrative or allocation failure message; the API job contains zero steps.
5. If configuration permits, execute one minimal existing manual workflow, not mass reruns. Verify `runner_id>0` and actual step logs before retrying the P19/P16 Blender jobs.
6. If account checks are healthy but allocation still fails, contact GitHub Support attaching run `41095968082`, attempt 2 and `Pass05/CI_RUNNER_DIAGNOSIS.json`.

## Alternative genuine Blender runtime

No local `blender` or Unity executable is installed on the C01-03 host, and this host has no network route for package installation or a connection to the user's Windows PC. **No native Blender/Unity execution was possible here**.

C01-16 producer PRs #12/#28 already contain the existing Windows execution scripts:
- `C01Source/Lighting/MeshRepairPASS04/run_pass04_windows.ps1`
- `C01Source/LightingW02/MeshRepairPASS04/run_pass04_windows.ps1`

C01-19 producer PRs #15/#29 contain native Blender `Source/pass04_triangulate.py` and `.github/workflows/c01-19-pass04.yml` including authoring-specific Blender invocation. Use a real Blender 4.x workstation, run scripts against actual producer sources, preserve and commit only authentic binaries and original-geometry screenshots. These procedures have **not** been run by C01-03.

C01-03 can then recheck source SHA-256 against locked BEFORE and candidate AFTER IDs; C01-02 must independently sign the **new** hydrated binary SHA-256. Re-running a CI job that never acquired a runner cannot demonstrate mesh correctness.

**Status:** runner assignment **FAIL** (reproduced); diagnostic root cause **BLOCKED owner/admin checks**; Blender/Unity **NOT RUN**; C01 PASS05 release **BLOCKED**.
